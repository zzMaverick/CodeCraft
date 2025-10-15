import numpy as np
import rasterio
from spectral import envi
import matplotlib.pyplot as plt
import os
import glob


def encontrar_banda_mais_proxima(wavelengths, target_wavelength):
    """Encontra o índice da banda cujo comprimento de onda é mais próximo do alvo."""
    idx = np.argmin(np.abs(np.array(wavelengths) - target_wavelength))
    return idx


def refinar_mapa_anomalia(caminho_hdr_original, caminho_tif_anomalia, caminho_saida_final_png):
    """
    Mascara corpos d'água em um mapa de anomalias e reescala o contraste para
    revelar anomalias sutis na vegetação.
    """
    try:
        print("--- Iniciando Refinamento do Mapa de Anomalias ---")

        # --- 1. CALCULAR A MÁSCARA DE ÁGUA USANDO NDWI ---
        print("Passo 1: Calculando Índice de Água (NDWI) para criar máscara...")

        hdr = envi.read_envi_header(caminho_hdr_original)
        img = envi.open(caminho_hdr_original)

        # NDWI usa as bandas Verde e Infravermelho Próximo (NIR)
        try:
            wavelengths = [float(w) for w in hdr['wavelength']]
            green_idx = encontrar_banda_mais_proxima(wavelengths, 550)  # Verde
            nir_idx = encontrar_banda_mais_proxima(wavelengths, 860)  # NIR
            print(f"Usando bandas: Verde (idx {green_idx}) e NIR (idx {nir_idx}) para o NDWI.")
        except KeyError:
            print("AVISO: 'wavelength' não encontrado. Usando índices de banda padrão para EMIT.")
            green_idx, nir_idx = 35, 85  # Índices aproximados para Verde e NIR no EMIT

        green_band = img.read_band(green_idx).astype(float)
        nir_band = img.read_band(nir_idx).astype(float)

        # Evitar divisão por zero
        np.seterr(divide='ignore', invalid='ignore')
        ndwi = (green_band - nir_band) / (green_band + nir_band)

        # Criar a máscara: pixels com NDWI > 0.2 são considerados água
        mascara_agua = ndwi > 0.2
        print(f"Máscara de água criada. {np.count_nonzero(mascara_agua)} pixels de água encontrados.")

        # --- 2. APLICAR A MÁSCARA E REESCALAR O CONTRASTE ---
        print("Passo 2: Aplicando máscara e reescalando contraste...")

        with rasterio.open(caminho_tif_anomalia) as src:
            mapa_anomalia = src.read(1)

        # Aplicar a máscara: onde for água, o valor da anomalia se torna 0
        mapa_anomalia_mascarado = np.where(mascara_agua, 0, mapa_anomalia)

        # Criar uma máscara dos pixels de terra para o cálculo do percentil
        mascara_terra = ~mascara_agua

        # Recalcular o limite de contraste APENAS nos pixels de terra
        vmax = np.percentile(mapa_anomalia_mascarado[mascara_terra], 98)
        print(f"Novo limite de contraste (98º percentil na terra): {vmax:.6f}")

        # Normalizar o mapa com o novo limite
        mapa_anomalia_refinado = np.clip(mapa_anomalia_mascarado, 0, vmax) / vmax

        # --- 3. SALVAR O RESULTADO FINAL ---
        print("Passo 3: Salvando resultado final...")
        # Solução 1: Especificar vmin e vmax para evitar a barra de cores
        plt.imsave(caminho_saida_final_png, mapa_anomalia_refinado, cmap='jet', vmin=0, vmax=1)
        print(f"Sucesso! Mapa final refinado salvo em: '{caminho_saida_final_png}'")

        return True

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado. Verifique os caminhos.")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return False


def encontrar_hdr_correspondente(nome_base, pasta_analise, pasta_processados):
    """
    Encontra o arquivo .hdr original correspondente ao arquivo de resultados
    """
    # Procura primeiro na pasta de análise
    caminho_hdr = os.path.join(pasta_analise, f"{nome_base}.hdr")
    if os.path.exists(caminho_hdr):
        return caminho_hdr

    # Se não encontrar, procura na pasta de processados
    caminho_hdr = os.path.join(pasta_processados, f"{nome_base}.hdr")
    if os.path.exists(caminho_hdr):
        return caminho_hdr

    return None


def processar_todos_resultados(pasta_resultados, pasta_final, pasta_analise='dados_analise',
                               pasta_processados='processados'):
    """
    Processa todos os arquivos .tif da pasta resultados e salva na pasta final
    """
    print("=== PROCESSANDO TODOS OS ARQUIVOS DE RESULTADOS ===")

    # Cria a pasta final se não existir
    os.makedirs(pasta_final, exist_ok=True)

    # Encontra todos os arquivos .tif na pasta resultados
    arquivos_tif = glob.glob(os.path.join(pasta_resultados, "*.tif"))

    if not arquivos_tif:
        print(f"Nenhum arquivo .tif encontrado na pasta: {pasta_resultados}")
        return

    print(f"Encontrados {len(arquivos_tif)} arquivos para processar")

    sucessos = 0
    erros = 0

    for caminho_tif in arquivos_tif:
        try:
            # Extrai o nome base do arquivo (sem _anomalias.tif)
            nome_arquivo = os.path.basename(caminho_tif)
            nome_base = nome_arquivo.replace('_anomalias.tif', '')

            print(f"\n--- PROCESSANDO: {nome_arquivo} ---")

            # Encontra o arquivo .hdr original correspondente
            caminho_hdr_original = encontrar_hdr_correspondente(nome_base, pasta_analise, pasta_processados)

            if not caminho_hdr_original:
                print(f"AVISO: Arquivo .hdr original não encontrado para: {nome_base}")
                print("Tentando encontrar arquivo .hdr genérico...")
                # Tenta encontrar qualquer arquivo .hdr disponível
                arquivos_hdr = glob.glob(os.path.join(pasta_analise, "*.hdr")) + glob.glob(
                    os.path.join(pasta_processados, "*.hdr"))
                if arquivos_hdr:
                    caminho_hdr_original = arquivos_hdr[0]
                    print(f"Usando arquivo .hdr genérico: {os.path.basename(caminho_hdr_original)}")
                else:
                    print("ERRO: Nenhum arquivo .hdr encontrado para processamento.")
                    erros += 1
                    continue

            # Define o caminho de saída
            nome_saida = f"{nome_base}_refinado.png"
            caminho_saida = os.path.join(pasta_final, nome_saida)

            # Processa o arquivo
            sucesso = refinar_mapa_anomalia(caminho_hdr_original, caminho_tif, caminho_saida)

            if sucesso:
                sucessos += 1
            else:
                erros += 1

        except Exception as e:
            print(f"Erro ao processar {caminho_tif}: {e}")
            erros += 1

    print(f"\n=== RESUMO DO PROCESSAMENTO ===")
    print(f"Arquivos processados com sucesso: {sucessos}")
    print(f"Arquivos com erro: {erros}")
    print(f"Total processado: {sucessos + erros}")
    print(f"Resultados finais salvos em: {pasta_final}")


def modo_monitoramento_continuo(pasta_resultados, pasta_final, pasta_analise='dados_analise',
                                pasta_processados='processados', intervalo=30):
    """
    Monitora continuamente a pasta resultados por novos arquivos
    """
    print("=== INICIANDO MONITORAMENTO CONTÍNUO ===")
    print(f"Monitorando: {pasta_resultados}")
    print(f"Saída: {pasta_final}")
    print(f"Verificando a cada {intervalo} segundos...")
    print("Pressione Ctrl+C para parar\n")

    # Cria a pasta final se não existir
    os.makedirs(pasta_final, exist_ok=True)

    # Conjunto para rastrear arquivos já processados
    arquivos_processados = set(glob.glob(os.path.join(pasta_resultados, "*.tif")))

    # Processa arquivos existentes primeiro
    if arquivos_processados:
        print("Processando arquivos existentes...")
        processar_todos_resultados(pasta_resultados, pasta_final, pasta_analise, pasta_processados)
        print("Arquivos existentes processados.\n")

    try:
        while True:
            # Verifica por novos arquivos
            arquivos_atual = set(glob.glob(os.path.join(pasta_resultados, "*.tif")))
            novos_arquivos = arquivos_atual - arquivos_processados

            if novos_arquivos:
                print(f"Encontrados {len(novos_arquivos)} novos arquivos")
                for caminho_tif in novos_arquivos:
                    try:
                        nome_arquivo = os.path.basename(caminho_tif)
                        nome_base = nome_arquivo.replace('_anomalias.tif', '')

                        print(f"\n--- PROCESSANDO NOVO ARQUIVO: {nome_arquivo} ---")

                        # Encontra o arquivo .hdr original correspondente
                        caminho_hdr_original = encontrar_hdr_correspondente(nome_base, pasta_analise, pasta_processados)

                        if caminho_hdr_original:
                            # Define o caminho de saída
                            nome_saida = f"{nome_base}_refinado.png"
                            caminho_saida = os.path.join(pasta_final, nome_saida)

                            # Processa o arquivo
                            sucesso = refinar_mapa_anomalia(caminho_hdr_original, caminho_tif, caminho_saida)

                            if sucesso:
                                arquivos_processados.add(caminho_tif)
                                print(f"Arquivo processado com sucesso: {nome_saida}")
                            else:
                                print(f"Falha ao processar: {nome_arquivo}")
                        else:
                            print(f"Arquivo .hdr original não encontrado para: {nome_base}")

                    except Exception as e:
                        print(f"Erro ao processar novo arquivo {caminho_tif}: {e}")

            # Aguarda antes da próxima verificação
            time.sleep(intervalo)

    except KeyboardInterrupt:
        print("\nParando monitoramento...")
    except Exception as e:
        print(f"Erro no monitoramento: {e}")


# --- COMO USAR O SCRIPT ---
if __name__ == '__main__':
    import time

    # CONFIGURAÇÕES
    PASTA_RESULTADOS = 'resultados'  # Pasta onde estão os .tif gerados pelo deep learning
    PASTA_FINAL = 'final'  # Pasta onde os resultados refinados serão salvos
    PASTA_ANALISE = 'dados_analise'  # Pasta com arquivos originais para análise
    PASTA_PROCESSADOS = 'processados'  # Pasta com arquivos já processados

    MODO_MONITORAMENTO = True  # True para monitorar continuamente, False para processar uma vez

    # Cria as pastas se não existirem
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
    os.makedirs(PASTA_FINAL, exist_ok=True)
    os.makedirs(PASTA_ANALISE, exist_ok=True)
    os.makedirs(PASTA_PROCESSADOS, exist_ok=True)

    print("=== SISTEMA DE REFINAMENTO DE MAPAS DE ANOMALIAS ===")
    print(f"Pasta de resultados: {PASTA_RESULTADOS}")
    print(f"Pasta final: {PASTA_FINAL}")
    print(f"Pasta de análise: {PASTA_ANALISE}")
    print(f"Pasta de processados: {PASTA_PROCESSADOS}")
    print()

    try:
        if MODO_MONITORAMENTO:
            # Modo monitoramento contínuo
            modo_monitoramento_continuo(PASTA_RESULTADOS, PASTA_FINAL, PASTA_ANALISE, PASTA_PROCESSADOS)
        else:
            # Modo processamento único
            processar_todos_resultados(PASTA_RESULTADOS, PASTA_FINAL, PASTA_ANALISE, PASTA_PROCESSADOS)

    except Exception as e:
        print(f"Erro na execução: {e}")