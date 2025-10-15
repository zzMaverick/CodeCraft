"""
Script automatizado para executar todo o pipeline de detecção de anomalias.
Organiza os arquivos em pastas estruturadas.
"""

import os
from converter import converter_emit_para_envi
from deeplearn import treinar_e_detectar_anomalias
from refinar import refinar_mapa_anomalia
from visualizar import converter_raw_para_rgb

# ============================================================
# CONFIGURAÇÃO - ESTRUTURA DE PASTAS
# ============================================================

# Diretório base
BASE_DIR = '/Users/mateusgomes/Documents/CodeCraft'

# Pastas de entrada
DIR_TREINO = os.path.join(BASE_DIR, 'data', 'treino')
DIR_ANALISE = os.path.join(BASE_DIR, 'data', 'analise')

# Pastas de saída
DIR_CONVERTED = os.path.join(BASE_DIR, 'output', 'converted')
DIR_MAPS = os.path.join(BASE_DIR, 'output', 'maps')
DIR_VISUALIZATIONS = os.path.join(BASE_DIR, 'output', 'visualizations')

# ============================================================

def criar_estrutura_pastas():
    """Cria a estrutura de pastas necessária."""
    pastas = [DIR_TREINO, DIR_ANALISE, DIR_CONVERTED, DIR_MAPS, DIR_VISUALIZATIONS]
    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)
    print("✓ Estrutura de pastas criada/verificada.")


def encontrar_arquivo_nc(diretorio, descricao):
    """Encontra o primeiro arquivo .nc em um diretório."""
    arquivos = [f for f in os.listdir(diretorio) if f.endswith('.nc')]
    if not arquivos:
        print(f"ERRO: Nenhum arquivo .nc encontrado em {diretorio}")
        print(f"Por favor, coloque o arquivo de {descricao} na pasta: {diretorio}")
        return None
    if len(arquivos) > 1:
        print(f"AVISO: Múltiplos arquivos .nc encontrados. Usando: {arquivos[0]}")
    return os.path.join(diretorio, arquivos[0])


def executar_pipeline():
    """Executa todo o pipeline de análise."""
    
    print("=" * 70)
    print("PIPELINE DE DETECÇÃO DE ANOMALIAS - CodeCraft")
    print("=" * 70)
    
    # Criar estrutura de pastas
    criar_estrutura_pastas()
    
    # Encontrar arquivos de entrada
    print("\n[0/6] Localizando arquivos de entrada...")
    arquivo_treino_nc = encontrar_arquivo_nc(DIR_TREINO, "TREINO (área preservada)")
    arquivo_analise_nc = encontrar_arquivo_nc(DIR_ANALISE, "ANÁLISE (área alvo)")
    
    if not arquivo_treino_nc or not arquivo_analise_nc:
        print("\n❌ Pipeline cancelado. Organize os arquivos corretamente.")
        return
    
    print(f"   Treino: {os.path.basename(arquivo_treino_nc)}")
    print(f"   Análise: {os.path.basename(arquivo_analise_nc)}")
    
    # Definir nomes dos arquivos intermediários e finais
    treino_base = os.path.join(DIR_CONVERTED, 'treino_convertido')
    analise_base = os.path.join(DIR_CONVERTED, 'analise_convertida')
    
    # ETAPA 1: Converter arquivo de treino
    print("\n[1/6] Convertendo arquivo de TREINO (área preservada)...")
    converter_emit_para_envi(arquivo_treino_nc, treino_base)
    
    # ETAPA 2: Converter arquivo de análise
    print("\n[2/6] Convertendo arquivo de ANÁLISE (área alvo)...")
    converter_emit_para_envi(arquivo_analise_nc, analise_base)
    
    # ETAPA 3: Treinar modelo e detectar anomalias
    print("\n[3/6] Treinando modelo e detectando anomalias...")
    arquivo_tif = os.path.join(DIR_MAPS, 'mapa_anomalia_bruto.tif')
    arquivo_png_bruto = os.path.join(DIR_MAPS, 'mapa_anomalia_bruto.png')
    
    treinar_e_detectar_anomalias(
        f"{treino_base}.hdr",
        f"{analise_base}.hdr",
        arquivo_tif,
        arquivo_png_bruto
    )
    
    # ETAPA 4: Refinar mapa de anomalias
    print("\n[4/6] Refinando mapa de anomalias (removendo água)...")
    arquivo_png_refinado = os.path.join(DIR_MAPS, 'mapa_anomalia_visual_refinado.png')
    
    refinar_mapa_anomalia(
        f"{analise_base}.hdr",
        arquivo_tif,
        arquivo_png_refinado
    )
    
    # ETAPA 5: Gerar visualização RGB da área de análise
    print("\n[5/6] Gerando visualização RGB da área de análise...")
    arquivo_rgb = os.path.join(DIR_VISUALIZATIONS, 'imagem_rgb_visivel.png')
    
    converter_raw_para_rgb(
        f"{analise_base}.hdr",
        arquivo_rgb
    )
    
    # ETAPA 6: Gerar visualização RGB da área de treino (opcional)
    print("\n[6/6] Gerando visualização RGB da área de treino...")
    arquivo_rgb_treino = os.path.join(DIR_VISUALIZATIONS, 'imagem_rgb_treino.png')
    
    converter_raw_para_rgb(
        f"{treino_base}.hdr",
        arquivo_rgb_treino
    )
    
    # Resumo final
    print("\n" + "=" * 70)
    print("✓ PIPELINE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print("\n📂 ARQUIVOS GERADOS:")
    print(f"\n   📊 MAPAS DE ANOMALIAS:")
    print(f"      • {arquivo_png_refinado}")
    print(f"      • {arquivo_tif} (GeoTIFF para GIS)")
    print(f"\n   🖼️  VISUALIZAÇÕES RGB:")
    print(f"      • {arquivo_rgb} (área de análise)")
    print(f"      • {arquivo_rgb_treino} (área de treino)")
    print(f"\n   📁 Todos os arquivos em: {BASE_DIR}/output/")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    executar_pipeline()
