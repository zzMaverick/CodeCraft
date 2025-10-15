import numpy as np
from spectral import envi
import matplotlib.pyplot as plt
import os
import glob
import time


def encontrar_banda_mais_proxima(wavelengths, target_wavelength):
    """Encontra o índice da banda cujo comprimento de onda é mais próximo do alvo."""
    idx = np.argmin(np.abs(np.array(wavelengths) - target_wavelength))
    return idx


def converter_raw_para_rgb(caminho_arquivo_hdr, caminho_saida_rgb):
    """
    Lê um arquivo hiperespectral ENVI (.raw + .hdr) e o converte para uma imagem
    RGB visível (.png) com aprimoramento de contraste.
    """
    try:
        # Verifica se o arquivo .hdr existe
        if not os.path.exists(caminho_arquivo_hdr):
            print(f"Arquivo .hdr não encontrado: {caminho_arquivo_hdr}")
            return False

        # Verifica se o arquivo .raw correspondente existe
        caminho_raw = caminho_arquivo_hdr.replace('.hdr', '.raw')
        if not os.path.exists(caminho_raw):
            print(f"Arquivo .raw não encontrado: {caminho_raw}")
            return False

        print(f"\n--- PROCESSANDO: {os.path.basename(caminho_arquivo_hdr)} ---")

        # 1. Ler o cabeçalho para obter metadados
        hdr = envi.read_envi_header(caminho_arquivo_hdr)
        img = envi.open(caminho_arquivo_hdr)

        # 2. TENTAR encontrar as bandas RGB usando comprimentos de onda
        try:
            wavelengths = [float(w) for w in hdr['wavelength']]

            red_target = 650
            green_target = 550
            blue_target = 450

            red_idx = encontrar_banda_mais_proxima(wavelengths, red_target)
            green_idx = encontrar_banda_mais_proxima(wavelengths, green_target)
            blue_idx = encontrar_banda_mais_proxima(wavelengths, blue_target)

            print("--- Seleção de Bandas por Comprimento de Onda ---")
            print(f"Banda Vermelha (R): Índice {red_idx} @ {wavelengths[red_idx]:.2f} nm")
            print(f"Banda Verde   (G): Índice {green_idx} @ {wavelengths[green_idx]:.2f} nm")
            print(f"Banda Azul    (B): Índice {blue_idx} @ {wavelengths[blue_idx]:.2f} nm")

        except KeyError:
            # SE FALHAR (KeyError: 'wavelength'), usar bandas padrão para EMIT
            print("\nAVISO: Informação de 'wavelength' não encontrada no arquivo .hdr.")
            print("Usando índices de banda padrão para o sensor EMIT (285 bandas).")

            # Estas são estimativas seguras para o sensor EMIT
            red_idx = 40
            green_idx = 25
            blue_idx = 15

            print("--- Seleção de Bandas por Índices Padrão ---")
            print(f"Banda Vermelha (R): Índice {red_idx}")
            print(f"Banda Verde   (G): Índice {green_idx}")
            print(f"Banda Azul    (B): Índice {blue_idx}")

        # 3. Ler os dados das bandas RGB selecionadas
        rgb_data = img.read_bands([red_idx, green_idx, blue_idx])

        nodata_val = float(hdr.get('data ignore value', -9999))
        rgb_data[rgb_data == nodata_val] = 0

        # 4. Aprimoramento de Contraste
        p2, p98 = np.percentile(rgb_data, (2, 98))
        rgb_stretched = np.clip(rgb_data, p2, p98)
        rgb_normalized = (rgb_stretched - p2) / (p98 - p2)
        rgb_final = (rgb_normalized * 255).astype(np.uint8)

        # 5. Salvar a imagem RGB final
        plt.imsave(caminho_saida_rgb, rgb_final)
        print(f"Sucesso! Imagem RGB visível salva em: '{caminho_saida_rgb}'")
        return True

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{caminho_arquivo_hdr}'")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return False


def processar_todos_arquivos_raw(pasta_entrada, pasta_saida):
    """
    Processa todos os arquivos .hdr/.raw da pasta de entrada
    """
    print("=== PROCESSANDO TODOS OS ARQUIVOS RAW PARA RGB ===")

    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)

    # Encontra todos os arquivos .hdr na pasta de entrada
    arquivos_hdr = glob.glob(os.path.join(pasta_entrada, "*.hdr"))

    if not arquivos_hdr:
        print(f"Nenhum arquivo .hdr encontrado na pasta: {pasta_entrada}")
        return

    print(f"Encontrados {len(arquivos_hdr)} arquivos para processar")

    sucessos = 0
    erros = 0

    for caminho_hdr in arquivos_hdr:
        # Verifica se o arquivo .raw correspondente existe
        caminho_raw = caminho_hdr.replace('.hdr', '.raw')
        if not os.path.exists(caminho_raw):
            print(f"AVISO: Arquivo .raw não encontrado para: {caminho_hdr}")
            erros += 1
            continue

        # Gera nome de saída
        nome_base = os.path.splitext(os.path.basename(caminho_hdr))[0]
        caminho_saida = os.path.join(pasta_saida, f"{nome_base}_rgb.png")

        # Processa o arquivo
        sucesso = converter_raw_para_rgb(caminho_hdr, caminho_saida)

        if sucesso:
            sucessos += 1
        else:
            erros += 1

    print(f"\n=== RESUMO DO PROCESSAMENTO ===")
    print(f"Arquivos processados com sucesso: {sucessos}")
    print(f"Arquivos com erro: {erros}")
    print(f"Total: {sucessos + erros}")
    print(f"Imagens RGB salvas em: {pasta_saida}")


def monitorar_pasta_raw(pasta_entrada, pasta_saida, intervalo=10):
    """
    Monitora continuamente a pasta de entrada por novos arquivos .hdr/.raw
    """
    print("=== INICIANDO MONITORAMENTO DE ARQUIVOS RAW ===")
    print(f"Pasta de entrada: {pasta_entrada}")
    print(f"Pasta de saída: {pasta_saida}")
    print(f"Verificando novos arquivos a cada {intervalo} segundos...")
    print("Pressione Ctrl+C para parar\n")

    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)

    # Processa arquivos existentes primeiro
    processar_todos_arquivos_raw(pasta_entrada, pasta_saida)

    # Conjunto para rastrear arquivos já processados
    arquivos_processados = set(glob.glob(os.path.join(pasta_entrada, "*.hdr")))

    print(f"\n=== INICIANDO MONITORAMENTO ===")
    print("Aguardando novos arquivos... (Ctrl+C para parar)")

    try:
        while True:
            # Verifica por novos arquivos
            arquivos_atual = set(glob.glob(os.path.join(pasta_entrada, "*.hdr")))
            novos_arquivos = arquivos_atual - arquivos_processados

            for caminho_hdr in novos_arquivos:
                # Verifica se o arquivo .raw correspondente existe
                caminho_raw = caminho_hdr.replace('.hdr', '.raw')
                if os.path.exists(caminho_raw):
                    print(f"Novo arquivo detectado: {os.path.basename(caminho_hdr)}")

                    # Gera nome de saída
                    nome_base = os.path.splitext(os.path.basename(caminho_hdr))[0]
                    caminho_saida = os.path.join(pasta_saida, f"{nome_base}_rgb.png")

                    # Processa o arquivo
                    sucesso = converter_raw_para_rgb(caminho_hdr, caminho_saida)

                    if sucesso:
                        arquivos_processados.add(caminho_hdr)
                        print(f"Arquivo processado com sucesso: {nome_base}_rgb.png")
                    else:
                        print(f"Falha ao processar: {os.path.basename(caminho_hdr)}")
                else:
                    print(f"Aguardando arquivo .raw correspondente para: {caminho_hdr}")

            # Aguarda antes da próxima verificação
            time.sleep(intervalo)

    except KeyboardInterrupt:
        print("\nParando monitoramento...")
    except Exception as e:
        print(f"Erro no monitoramento: {e}")


def modo_processamento_unico(pasta_entrada, pasta_saida):
    """
    Modo único: processa todos os arquivos e termina
    """
    print("=== MODO PROCESSAMENTO ÚNICO ===")
    processar_todos_arquivos_raw(pasta_entrada, pasta_saida)
    print("Processamento concluído.")


# --- EXECUÇÃO PRINCIPAL ---
if __name__ == '__main__':
    # CONFIGURAÇÕES
    PASTA_ENTRADA = 'processados'  # Pasta com arquivos .hdr/.raw originais
    PASTA_SAIDA = 'final'  # Pasta onde as imagens RGB serão salvas

    MODO_MONITORAMENTO = True  # True para monitorar continuamente, False para processar uma vez

    # Cria diretórios se não existirem
    os.makedirs(PASTA_ENTRADA, exist_ok=True)
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    print("=== CONVERSOR RAW PARA RGB ===")
    print(f"Pasta de entrada: {PASTA_ENTRADA}")
    print(f"Pasta de saída: {PASTA_SAIDA}")
    print()

    try:
        if MODO_MONITORAMENTO:
            # Modo monitoramento contínuo
            monitorar_pasta_raw(PASTA_ENTRADA, PASTA_SAIDA, intervalo=10)
        else:
            # Modo processamento único
            modo_processamento_unico(PASTA_ENTRADA, PASTA_SAIDA)

    except Exception as e:
        print(f"Erro na execução: {e}")