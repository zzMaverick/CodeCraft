"""
Backend Flask para processar arquivos NetCDF e gerar mapas de anomalias.
Integrado com o frontend CO₂Vision.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import threading
import shutil

# Adicionar pasta raiz ao path para importar os scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converter import converter_emit_para_envi
from deeplearn import treinar_e_detectar_anomalias
from refinar import refinar_mapa_anomalia
from visualizar import converter_raw_para_rgb

app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend

# ============================================================
# CONFIGURAÇÃO DE PASTAS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pastas de entrada
DIR_TREINO = os.path.join(BASE_DIR, 'data', 'treino')
DIR_ANALISE = os.path.join(BASE_DIR, 'data', 'analise')

# Pastas de saída
CONVERTED_FOLDER = os.path.join(BASE_DIR, 'output', 'converted')
MAPS_FOLDER = os.path.join(BASE_DIR, 'output', 'maps')
VISUALIZATIONS_FOLDER = os.path.join(BASE_DIR, 'output', 'visualizations')

# Criar pastas se não existirem
os.makedirs(DIR_TREINO, exist_ok=True)
os.makedirs(DIR_ANALISE, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs(MAPS_FOLDER, exist_ok=True)
os.makedirs(VISUALIZATIONS_FOLDER, exist_ok=True)

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 2000 * 1024 * 1024  # 2GB
ALLOWED_EXTENSIONS = {'nc'}

# Status do processamento
processing_status = {
    'is_processing': False,
    'progress': 0,
    'current_step': '',
    'error': None,
    'results': None
}

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def update_status(progress, step):
    """Atualiza o status do processamento."""
    global processing_status
    processing_status['progress'] = progress
    processing_status['current_step'] = step
    print(f"[{progress}%] {step}")


def encontrar_arquivo_treino():
    """Encontra o arquivo de treino em data/treino/."""
    arquivos = [f for f in os.listdir(DIR_TREINO) if f.endswith('.nc')]
    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo .nc encontrado em {DIR_TREINO}. "
            f"Coloque o arquivo de treino (037.nc) nesta pasta."
        )
    return os.path.join(DIR_TREINO, arquivos[0])


def process_file():
    """Processa o arquivo NetCDF em thread separada."""
    global processing_status
    
    try:
        processing_status['is_processing'] = True
        processing_status['error'] = None
        
        # Passo 1: Encontrar arquivo de treino
        update_status(5, 'Localizando arquivo de treino...')
        arquivo_treino = encontrar_arquivo_treino()
        print(f"   Arquivo de treino: {os.path.basename(arquivo_treino)}")
        
        # Passo 2: Encontrar arquivo de análise (enviado pelo frontend)
        update_status(10, 'Localizando arquivo de análise...')
        arquivos_analise = [f for f in os.listdir(DIR_ANALISE) if f.endswith('.nc')]
        if not arquivos_analise:
            raise FileNotFoundError("Nenhum arquivo de análise encontrado em data/analise/")
        
        arquivo_analise = os.path.join(DIR_ANALISE, arquivos_analise[0])
        print(f"   Arquivo de análise: {os.path.basename(arquivo_analise)}")
        
        # Passo 3: Converter arquivo de treino (se ainda não existe)
        treino_converted = os.path.join(CONVERTED_FOLDER, 'treino_convertido')
        if not os.path.exists(f"{treino_converted}.hdr"):
            update_status(15, 'Convertendo área de treino (referência)...')
            converter_emit_para_envi(arquivo_treino, treino_converted)
        else:
            update_status(15, 'Área de treino já convertida')
        
        # Passo 4: Converter arquivo de análise
        update_status(25, 'Convertendo arquivo de análise...')
        analise_converted = os.path.join(CONVERTED_FOLDER, 'analise_convertida')
        converter_emit_para_envi(arquivo_analise, analise_converted)
        
        # Passo 5: Treinar modelo e detectar anomalias
        update_status(40, 'Treinando modelo de Deep Learning (pode demorar ~3-5 min)...')
        mapa_bruto_tif = os.path.join(MAPS_FOLDER, 'mapa_anomalia_bruto.tif')
        mapa_bruto_png = os.path.join(MAPS_FOLDER, 'mapa_anomalia_bruto.png')
        
        treinar_e_detectar_anomalias(
            f"{treino_converted}.hdr",
            f"{analise_converted}.hdr",
            mapa_bruto_tif,
            mapa_bruto_png
        )
        
        # Passo 6: Refinar mapa (remover água)
        update_status(80, 'Refinando mapa de anomalias...')
        mapa_refinado = os.path.join(MAPS_FOLDER, 'mapa_anomalia_visual_refinado.png')
        refinar_mapa_anomalia(
            f"{analise_converted}.hdr",
            mapa_bruto_tif,
            mapa_refinado
        )
        
        # Passo 7: Gerar visualização RGB
        update_status(90, 'Gerando visualização RGB...')
        rgb_visivel = os.path.join(VISUALIZATIONS_FOLDER, 'imagem_rgb_visivel.png')
        converter_raw_para_rgb(
            f"{analise_converted}.hdr",
            rgb_visivel
        )
        
        # Passo 8: Calcular estatísticas
        update_status(95, 'Calculando estatísticas...')
        import rasterio
        import numpy as np
        
        with rasterio.open(mapa_bruto_tif) as src:
            data = src.read(1)
            # Calcular percentuais de risco
            threshold_high = np.percentile(data[data > 0], 85)
            threshold_medium = np.percentile(data[data > 0], 50)
            
            high_risk = (np.sum(data > threshold_high) / data.size) * 100
            medium_risk = (np.sum((data > threshold_medium) & (data <= threshold_high)) / data.size) * 100
            low_risk = 100 - high_risk - medium_risk
        
        # Finalizado
        update_status(100, 'Processamento concluído!')
        
        processing_status['results'] = {
            'high_risk': round(high_risk, 1),
            'medium_risk': round(medium_risk, 1),
            'low_risk': round(low_risk, 1),
            'map_file': 'mapa_anomalia_visual_refinado.png',
            'rgb_file': 'imagem_rgb_visivel.png'
        }
        
        # Limpar arquivo de análise após processamento
        os.remove(arquivo_analise)
        print(f"   ✓ Arquivo temporário removido: {os.path.basename(arquivo_analise)}")
        
    except Exception as e:
        processing_status['error'] = str(e)
        print(f"❌ Erro no processamento: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        processing_status['is_processing'] = False


# ============================================================
# ROTAS DA API
# ============================================================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Recebe o arquivo .nc e inicia o processamento."""
    global processing_status
    
    # Verificar se já está processando
    if processing_status['is_processing']:
        return jsonify({'error': 'Já existe um processamento em andamento'}), 400
    
    # Verificar se arquivo foi enviado
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Arquivo vazio'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Apenas arquivos .nc são permitidos'}), 400
    
    # Limpar pasta data/analise/ antes de salvar novo arquivo
    for f in os.listdir(DIR_ANALISE):
        if f.endswith('.nc'):
            os.remove(os.path.join(DIR_ANALISE, f))
    
    # Salvar arquivo em data/analise/
    filename = secure_filename(file.filename)
    filepath = os.path.join(DIR_ANALISE, filename)
    file.save(filepath)
    
    print(f"✓ Arquivo salvo em: {filepath}")
    
    # Resetar status
    processing_status = {
        'is_processing': True,
        'progress': 0,
        'current_step': 'Arquivo recebido',
        'error': None,
        'results': None
    }
    
    # Iniciar processamento em thread separada
    thread = threading.Thread(target=process_file)
    thread.start()
    
    return jsonify({
        'message': 'Arquivo recebido e processamento iniciado',
        'filename': filename
    }), 200


@app.route('/api/status', methods=['GET'])
def get_status():
    """Retorna o status atual do processamento."""
    return jsonify(processing_status), 200


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Faz download dos arquivos gerados."""
    
    # Determinar pasta baseado no tipo de arquivo
    if filename == 'mapa_anomalia_visual_refinado.png':
        file_path = os.path.join(MAPS_FOLDER, filename)
    elif filename == 'imagem_rgb_visivel.png':
        file_path = os.path.join(VISUALIZATIONS_FOLDER, filename)
    else:
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Arquivo ainda não foi gerado'}), 404
    
    return send_file(file_path, as_attachment=True)


@app.route('/api/preview/<filename>', methods=['GET'])
def preview_file(filename):
    """Retorna a imagem para preview no navegador."""
    
    if filename == 'mapa_anomalia_visual_refinado.png':
        file_path = os.path.join(MAPS_FOLDER, filename)
    elif filename == 'imagem_rgb_visivel.png':
        file_path = os.path.join(VISUALIZATIONS_FOLDER, filename)
    else:
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Arquivo ainda não foi gerado'}), 404
    
    # Adicionar headers para evitar cache
    from flask import Response
    with open(file_path, 'rb') as f:
        image_data = f.read()
    
    response = Response(image_data, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


@app.route('/api/reset', methods=['POST'])
def reset_processing():
    """Reseta o status para permitir novo processamento."""
    global processing_status
    
    if processing_status['is_processing']:
        return jsonify({'error': 'Não é possível resetar durante processamento'}), 400
    
    processing_status = {
        'is_processing': False,
        'progress': 0,
        'current_step': '',
        'error': None,
        'results': None
    }
    
    return jsonify({'message': 'Status resetado com sucesso'}), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica se o servidor está online."""
    return jsonify({'status': 'online', 'message': 'Backend funcionando'}), 200


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("CO₂VISION BACKEND - Servidor Flask")
    print("=" * 70)
    print(f"\n📁 Pastas configuradas:")
    print(f"   Treino: {DIR_TREINO}")
    print(f"   Análise (upload): {DIR_ANALISE}")
    print(f"   Mapas: {MAPS_FOLDER}")
    print(f"   Visualizações: {VISUALIZATIONS_FOLDER}")
    
    # Verificar se existe arquivo de treino
    try:
        arquivo_treino = encontrar_arquivo_treino()
        print(f"\n✓ Arquivo de treino encontrado: {os.path.basename(arquivo_treino)}")
    except FileNotFoundError as e:
        print(f"\n⚠️  ATENÇÃO: {e}")
        print("   Coloque o arquivo 037.nc em data/treino/ antes de processar.")
    
    print(f"\n🚀 Servidor rodando em: http://localhost:5001")
    print("=" * 70)
    print("\nAguardando requisições...\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
