import xarray as xr
import numpy as np
import os
import time
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading


class EMITFileHandler(FileSystemEventHandler):
    def __init__(self, input_folder, output_folder, processed_files):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.processed_files = processed_files

    def on_created(self, event):
        if event.is_directory:
            return

        if event.src_path.endswith('.nc'):
            print(f"Novo arquivo detectado: {event.src_path}")
            time.sleep(2)  # Espera um pouco para garantir que o arquivo esteja completamente escrito
            self.process_file(event.src_path)

    def on_moved(self, event):
        if event.dest_path.endswith('.nc'):
            print(f"Arquivo movido para a pasta: {event.dest_path}")
            time.sleep(2)
            self.process_file(event.dest_path)

    def process_file(self, file_path):
        if file_path in self.processed_files:
            print(f"Arquivo {file_path} já foi processado anteriormente.")
            return

        try:
            # Gera nome do arquivo de saída baseado no nome do arquivo de entrada
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_base = os.path.join(self.output_folder, base_name)

            converter_emit_para_envi(file_path, output_base)
            self.processed_files.add(file_path)

        except Exception as e:
            print(f"Erro ao processar arquivo {file_path}: {e}")


def converter_emit_para_envi(caminho_arquivo_nc, caminho_saida_base):
    """
    Versão CORRIGIDA: Converte um arquivo NetCDF EMIT L2A para o formato ENVI,
    identificando as dimensões corretamente pelos seus nomes.
    """
    print(f"Iniciando a conversão (versão corrigida) de: '{caminho_arquivo_nc}'...")

    dataset = None
    try:
        # 1. Abrir o arquivo NetCDF com xarray
        dataset = xr.open_dataset(caminho_arquivo_nc)

        if 'reflectance' not in dataset.variables:
            print("Erro: A variável 'reflectance' não foi encontrada.")
            return

        imagem_data = dataset['reflectance']

        # 2. Extrair metadados identificando as dimensões pelos nomes
        # Esta é a correção principal para evitar a troca de eixos.
        try:
            # A ordem esperada é (bands, downtrack, crosstrack)
            bandas = imagem_data.sizes['bands']
            linhas = imagem_data.sizes['downtrack']
            amostras = imagem_data.sizes['crosstrack']
        except KeyError:
            # Plano B se os nomes forem diferentes (ex: x, y, band)
            print("Aviso: Nomes de dimensão padrão não encontrados, tentando inferir...")
            # Encontra a dimensão com 285, que deve ser a de bandas
            band_dim_index = np.where(np.array(imagem_data.shape) == 285)[0][0]

            if band_dim_index == 0:  # (bands, lines, samples)
                bandas, linhas, amostras = imagem_data.shape
            elif band_dim_index == 2:  # (lines, samples, bands)
                linhas, amostras, bandas = imagem_data.shape
            else:
                raise ValueError("Não foi possível determinar a ordem das dimensões da imagem.")

        print(f"Dimensões corretas: {amostras} (amostras) x {linhas} (linhas) x {bandas} (bandas)")

        # 3. Garantir que os dados estejam na ordem correta para salvar em BSQ
        # A ordem para BSQ (Band Sequential) deve ser (bands, lines, samples)
        dados_numpy = imagem_data.transpose('bands', 'downtrack', 'crosstrack').values

        # 4. Criar o cabeçalho (.hdr) com os valores corretos
        tipo_dado_envi = 4  # float32
        byte_order = 0

        # Cria a pasta de saída se não existir
        os.makedirs(os.path.dirname(caminho_saida_base), exist_ok=True)

        caminho_saida_hdr = f"{caminho_saida_base}.hdr"

        header_lines = [
            "ENVI",
            f"description = {{Arquivo EMIT L2A Reflectance (dimensões corrigidas)}}",
            f"samples = {amostras}",
            f"lines   = {linhas}",
            f"bands   = {bandas}",
            "header offset = 0",
            "file type = ENVI Standard",
            f"data type = {tipo_dado_envi}",
            "interleave = bsq",
            f"byte order = {byte_order}",
            "data ignore value = -9999"
        ]

        # Adicionar comprimentos de onda, se disponíveis
        if 'wavelengths' in imagem_data.coords:
            wavelengths = imagem_data.coords['wavelengths'].values
            wavelengths_str = ", ".join(map(str, np.round(wavelengths, 2)))
            header_lines.append(f"wavelength = {{{wavelengths_str}}}")

        header = "\n".join(header_lines) + "\n"

        with open(caminho_saida_hdr, 'w') as f:
            f.write(header)
        print(f"Arquivo de cabeçalho (.hdr) corrigido salvo em: '{caminho_saida_hdr}'")

        # 5. Salvar o arquivo de dados brutos (.raw) com a ordem correta
        caminho_saida_raw = f"{caminho_saida_base}.raw"
        with open(caminho_saida_raw, 'wb') as f:
            dados_numpy.tofile(f)
        print(f"Arquivo de dados brutos (.raw) corrigido salvo em: '{caminho_saida_raw}'")
        print("\nConversão concluída com sucesso!")

    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{caminho_arquivo_nc}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        if dataset:
            dataset.close()


def process_existing_files(input_folder, output_folder, processed_files):
    """Processa todos os arquivos .nc existentes na pasta de entrada"""
    pattern = os.path.join(input_folder, "*.nc")
    existing_files = glob.glob(pattern)

    if not existing_files:
        print(f"Nenhum arquivo .nc encontrado na pasta: {input_folder}")
        return

    print(f"Encontrados {len(existing_files)} arquivos para processar...")

    for file_path in existing_files:
        if file_path in processed_files:
            continue

        try:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_base = os.path.join(output_folder, base_name)

            converter_emit_para_envi(file_path, output_base)
            processed_files.add(file_path)

        except Exception as e:
            print(f"Erro ao processar arquivo existente {file_path}: {e}")


def start_monitoring(input_folder, output_folder):
    """Inicia o monitoramento da pasta para novos arquivos"""
    processed_files = set()

    # Primeiro, processa arquivos existentes
    print("=== PROCESSANDO ARQUIVOS EXISTENTES ===")
    process_existing_files(input_folder, output_folder, processed_files)

    # Depois, inicia o monitoramento
    print("\n=== INICIANDO MONITORAMENTO ===")
    print(f"Monitorando pasta: {input_folder}")
    print(f"Pasta de saída: {output_folder}")
    print("Pressione Ctrl+C para parar o monitoramento...")

    event_handler = EMITFileHandler(input_folder, output_folder, processed_files)
    observer = Observer()
    observer.schedule(event_handler, input_folder, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando monitoramento...")
        observer.stop()

    observer.join()


# --- COMO USAR O SCRIPT ---
if __name__ == '__main__':
    # Configurações
    pasta_entrada = 'arquivosbrutos'  # Pasta onde os arquivos .nc chegam
    pasta_saida = 'arquivoRAW'  # Pasta onde os arquivos convertidos serão salvos

    # Garante que as pastas existem
    os.makedirs(pasta_entrada, exist_ok=True)
    os.makedirs(pasta_saida, exist_ok=True)

    # Instalação da dependência necessária (executar apenas uma vez)
    # pip install watchdog

    start_monitoring(pasta_entrada, pasta_saida)