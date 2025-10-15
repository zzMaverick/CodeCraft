import numpy as np
import os
import glob
import time
import shutil

# Configuração para evitar problemas no macOS
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Tentativa de import com fallback
try:
    import tensorflow as tf
    from tensorflow import keras

    TENSORFLOW_AVAILABLE = True
    print("TensorFlow carregado com sucesso")
except Exception as e:
    print(f"TensorFlow não disponível: {e}")
    TENSORFLOW_AVAILABLE = False

try:
    from spectral import envi

    SPECTRAL_AVAILABLE = True
    print("Spectral carregado com sucesso")
except Exception as e:
    print(f"Spectral não disponível: {e}")
    SPECTRAL_AVAILABLE = False

try:
    from sklearn.preprocessing import MinMaxScaler

    SKLEARN_AVAILABLE = True
    print("Scikit-learn carregado com sucesso")
except Exception as e:
    print(f"Scikit-learn não disponível: {e}")
    SKLEARN_AVAILABLE = False

try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
    print("Matplotlib carregado com sucesso")
except Exception as e:
    print(f"Matplotlib não disponível: {e}")
    MATPLOTLIB_AVAILABLE = False

try:
    import rasterio

    RASTERIO_AVAILABLE = True
    print("Rasterio carregado com sucesso")
except Exception as e:
    print(f"Rasterio não disponível: {e}")
    RASTERIO_AVAILABLE = False


def carregar_dados_hdr(caminho_hdr):
    """Carrega dados de arquivo HDR"""
    try:
        img = envi.open(caminho_hdr).load()
        return img
    except Exception as e:
        print(f"Erro ao carregar arquivo HDR: {e}")
        raise


def detectar_anomalias_simples(dados_treino, dados_analise):
    """Método simplificado para detecção de anomalias sem TensorFlow"""
    print("Usando método simplificado de detecção de anomalias...")

    # Calcula média e desvio padrão dos dados de treino
    media_treino = np.mean(dados_treino, axis=0)
    std_treino = np.std(dados_treino, axis=0)

    # Evita divisão por zero
    std_treino[std_treino == 0] = 1e-8

    # Calcula Z-score para dados de análise
    z_scores = np.abs((dados_analise - media_treino) / std_treino)

    # Média do Z-score por pixel
    anomalias = np.mean(z_scores, axis=1)

    return anomalias


def criar_modelo_autoencoder(num_bands):
    """Cria modelo autoencoder sem warnings"""
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(num_bands,)))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(32, activation='relu'))
    model.add(keras.layers.Dense(16, activation='relu'))
    model.add(keras.layers.Dense(32, activation='relu'))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(num_bands, activation='sigmoid'))

    model.compile(optimizer='adam', loss='mse')
    return model


def treinar_e_detectar_anomalias(caminho_hdr_treino, caminho_hdr_analise, caminho_saida_tif, caminho_saida_png):
    """
    Versão MODIFICADA: Usa TensorFlow se disponível, caso contrário usa método simplificado
    """
    try:
        # Verifica dependências mínimas
        if not all([SPECTRAL_AVAILABLE, SKLEARN_AVAILABLE, MATPLOTLIB_AVAILABLE]):
            print("Bibliotecas essenciais não disponíveis. Verifique a instalação.")
            return

        # --- 1. PREPARAÇÃO DOS DADOS ---
        print("--- Fase de Preparação de Dados ---")
        print(f"Carregando dados de treinamento: '{caminho_hdr_treino}'")
        img_treino = carregar_dados_hdr(caminho_hdr_treino)
        h_t, w_t, num_bands = img_treino.shape
        dados_pixels_treino = img_treino.reshape((h_t * w_t, num_bands))

        print(f"Carregando dados de análise: '{caminho_hdr_analise}'")
        img_analise = carregar_dados_hdr(caminho_hdr_analise)
        h_a, w_a, _ = img_analise.shape
        dados_pixels_analise = img_analise.reshape((h_a * w_a, num_bands))

        # Processa dados válidos
        nodata_val = -9999
        mask_validos_treino = (dados_pixels_treino != nodata_val).all(axis=1) & (dados_pixels_treino.sum(axis=1) > 0)
        mask_validos_analise = (dados_pixels_analise != nodata_val).all(axis=1) & (dados_pixels_analise.sum(axis=1) > 0)

        dados_treino_validos = dados_pixels_treino[mask_validos_treino]
        dados_analise_validos = dados_pixels_analise[mask_validos_analise]

        # Normalização
        scaler = MinMaxScaler()
        x_train = scaler.fit_transform(dados_treino_validos)
        dados_analise_normalizados = scaler.transform(dados_analise_validos)

        print(f"Dados preparados: Treino={len(x_train)}, Análise={len(dados_analise_validos)}")

        # --- 2. DETECÇÃO DE ANOMALIAS ---
        print("\n--- Fase de Detecção de Anomalias ---")

        if TENSORFLOW_AVAILABLE:
            try:
                # Método com Autoencoder (TensorFlow)
                print("Usando Autoencoder (TensorFlow) para detecção...")
                autoencoder = criar_modelo_autoencoder(num_bands)

                # Treinamento rápido
                autoencoder.fit(x_train, x_train, epochs=10, batch_size=256, shuffle=True, verbose=0)

                # Predição
                pixels_reconstruidos = autoencoder.predict(dados_analise_normalizados, verbose=0)
                mse_erro = np.mean(np.power(dados_analise_normalizados - pixels_reconstruidos, 2), axis=1)

            except Exception as e:
                print(f"Erro no TensorFlow, usando método simplificado: {e}")
                mse_erro = detectar_anomalias_simples(x_train, dados_analise_normalizados)
        else:
            # Método simplificado
            mse_erro = detectar_anomalias_simples(x_train, dados_analise_normalizados)

        # --- 3. PROCESSAMENTO DOS RESULTADOS ---
        print("Processando resultados...")
        mapa_anomalia_final = np.full(h_a * w_a, 0.0)
        mapa_anomalia_final[mask_validos_analise] = mse_erro
        mapa_anomalia_final = mapa_anomalia_final.reshape((h_a, w_a))

        # Normalização para visualização
        vmax = np.percentile(mapa_anomalia_final, 98)
        mapa_anomalia_norm = np.clip(mapa_anomalia_final, 0, vmax) / vmax

        # --- 4. SALVANDO RESULTADOS ---
        print("\n--- Salvando Resultados ---")

        # Salva PNG
        fig = plt.figure(figsize=(12, 8))
        fig.patch.set_alpha(0)  # Fundo transparente
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        ax.imshow(mapa_anomalia_norm, cmap='jet')
        plt.savefig(caminho_saida_png, bbox_inches='tight', pad_inches=0, dpi=150, transparent=True)
        plt.close(fig)
        print(f"Visualização PNG salva em: '{caminho_saida_png}'")

        # Tenta salvar GeoTIFF se rasterio disponível
        if RASTERIO_AVAILABLE:
            try:
                caminho_raw_analise = caminho_hdr_analise.replace('.hdr', '.raw')
                with rasterio.open(caminho_raw_analise) as src_ref:
                    transform = src_ref.transform
                    crs = src_ref.crs

                with rasterio.open(
                        caminho_saida_tif, 'w', driver='GTiff',
                        height=h_a, width=w_a, count=1, dtype=rasterio.float32,
                        crs=crs, transform=transform
                ) as dst:
                    dst.write(mapa_anomalia_final.astype(rasterio.float32), 1)
                print(f"Mapa GeoTIFF salvo em: '{caminho_saida_tif}'")
            except Exception as e:
                print(f"Erro ao salvar GeoTIFF: {e}")
        else:
            # Salva como numpy array se rasterio não disponível
            caminho_npy = caminho_saida_tif.replace('.tif', '.npy')
            np.save(caminho_npy, mapa_anomalia_final)
            print(f"Dados de anomalias salvos como numpy array: '{caminho_npy}'")

        print("\nProcesso concluído com sucesso!")

    except Exception as e:
        print(f"Erro no processamento: {e}")


def selecionar_melhor_treino(pasta_treino):
    """
    Seleciona o melhor arquivo para treino da pasta de treino
    Pode ser expandido para lógica mais sofisticada
    """
    arquivos_treino = glob.glob(os.path.join(pasta_treino, "*.hdr"))

    if not arquivos_treino:
        return None

    # Por enquanto, retorna o primeiro arquivo
    # Você pode adicionar lógica para selecionar o "melhor" arquivo
    return arquivos_treino[0]


def processar_arquivo_analise(caminho_hdr_analise, pasta_saida, caminho_hdr_treino):
    """Processa um arquivo de análise usando um arquivo de treino específico"""
    try:
        if not os.path.exists(caminho_hdr_analise):
            print(f"Arquivo .hdr não encontrado: {caminho_hdr_analise}")
            return False

        # Verifica arquivo .raw correspondente
        caminho_raw = caminho_hdr_analise.replace('.hdr', '.raw')
        if not os.path.exists(caminho_raw):
            print(f"Arquivo .raw não encontrado: {caminho_raw}")
            return False

        # Verifica arquivo de treino
        if not os.path.exists(caminho_hdr_treino):
            print(f"Arquivo de treino não encontrado: {caminho_hdr_treino}")
            return False

        # Cria pasta de saída
        os.makedirs(pasta_saida, exist_ok=True)

        # Gera nomes de saída
        nome_base = os.path.splitext(os.path.basename(caminho_hdr_analise))[0]
        arquivo_tif_saida = os.path.join(pasta_saida, f"{nome_base}_anomalias.tif")
        arquivo_png_saida = os.path.join(pasta_saida, f"{nome_base}_anomalias.png")

        print(f"\n=== PROCESSANDO ANÁLISE: {caminho_hdr_analise} ===")
        print(f"Usando treino: {os.path.basename(caminho_hdr_treino)}")

        treinar_e_detectar_anomalias(caminho_hdr_treino, caminho_hdr_analise, arquivo_tif_saida, arquivo_png_saida)
        return True

    except Exception as e:
        print(f"Erro ao processar arquivo de análise: {e}")
        return False


def processar_todos_arquivos_analise(pasta_analise, pasta_saida, pasta_treino):
    """Processa todos os arquivos de análise usando arquivos de treino"""
    print("=== PROCESSANDO ARQUIVOS DE ANÁLISE ===")

    # Seleciona o melhor arquivo para treino
    caminho_hdr_treino = selecionar_melhor_treino(pasta_treino)

    if not caminho_hdr_treino:
        print(f"ERRO: Nenhum arquivo de treino encontrado em: {pasta_treino}")
        return

    print(f"Arquivo de treino selecionado: {os.path.basename(caminho_hdr_treino)}")

    # Processa arquivos de análise
    arquivos_analise = glob.glob(os.path.join(pasta_analise, "*.hdr"))

    if not arquivos_analise:
        print(f"Nenhum arquivo de análise encontrado em: {pasta_analise}")
        return

    print(f"Encontrados {len(arquivos_analise)} arquivos de análise")

    for arquivo_analise in arquivos_analise:
        processar_arquivo_analise(arquivo_analise, pasta_saida, caminho_hdr_treino)


def mover_arquivo_processado(caminho_arquivo, pasta_processados):
    """Move arquivo processado para pasta de processados"""
    try:
        # Cria pasta de processados se não existir
        os.makedirs(pasta_processados, exist_ok=True)

        # Move tanto .hdr quanto .raw
        base_name = os.path.splitext(caminho_arquivo)[0]
        arquivo_hdr = base_name + '.hdr'
        arquivo_raw = base_name + '.raw'

        if os.path.exists(arquivo_hdr):
            shutil.move(arquivo_hdr, os.path.join(pasta_processados, os.path.basename(arquivo_hdr)))
        if os.path.exists(arquivo_raw):
            shutil.move(arquivo_raw, os.path.join(pasta_processados, os.path.basename(arquivo_raw)))

        print(f"Arquivo movido para processados: {os.path.basename(arquivo_hdr)}")

    except Exception as e:
        print(f"Erro ao mover arquivo processado: {e}")


def monitorar_pasta_analise(pasta_analise, pasta_saida, pasta_treino, pasta_processados, intervalo=10):
    """
    Monitora pasta de análise por novos arquivos
    """
    print("=== INICIANDO SISTEMA DE DETECÇÃO DE ANOMALIAS ===")
    print(f"Pasta de treino: {pasta_treino}")
    print(f"Pasta de análise: {pasta_analise}")
    print(f"Pasta de saída: {pasta_saida}")
    print(f"Pasta de processados: {pasta_processados}")
    print(f"Verificando novos arquivos a cada {intervalo} segundos...")
    print("Pressione Ctrl+C para parar\n")

    # Processa arquivos existentes primeiro
    processar_todos_arquivos_analise(pasta_analise, pasta_saida, pasta_treino)

    # Move arquivos processados
    arquivos_processados = glob.glob(os.path.join(pasta_analise, "*.hdr"))
    for arquivo in arquivos_processados:
        mover_arquivo_processado(arquivo, pasta_processados)

    # Conjunto para rastrear arquivos já processados
    arquivos_processados_set = set()

    print(f"\n=== INICIANDO MONITORAMENTO ===")
    print("Aguardando novos arquivos de análise... (Ctrl+C para parar)")

    # Seleciona arquivo de treino (uma vez só)
    caminho_hdr_treino = selecionar_melhor_treino(pasta_treino)

    if not caminho_hdr_treino:
        print("ERRO: Nenhum arquivo de treino disponível. Monitoramento cancelado.")
        return

    try:
        while True:
            # Verifica por novos arquivos na pasta de análise
            arquivos_atual = set(glob.glob(os.path.join(pasta_analise, "*.hdr")))
            novos_arquivos = arquivos_atual - arquivos_processados_set

            for arquivo_analise in novos_arquivos:
                # Verifica se o arquivo .raw correspondente existe
                arquivo_raw = arquivo_analise.replace('.hdr', '.raw')
                if os.path.exists(arquivo_raw):
                    print(f"Novo arquivo de análise detectado: {os.path.basename(arquivo_analise)}")

                    # Processa o arquivo
                    sucesso = processar_arquivo_analise(arquivo_analise, pasta_saida, caminho_hdr_treino)

                    if sucesso:
                        # Move para pasta de processados
                        mover_arquivo_processado(arquivo_analise, pasta_processados)
                        arquivos_processados_set.add(arquivo_analise)
                else:
                    print(f"Aguardando arquivo .raw correspondente para: {arquivo_analise}")

            # Aguarda antes da próxima verificação
            time.sleep(intervalo)

    except KeyboardInterrupt:
        print("\nParando monitoramento...")
    except Exception as e:
        print(f"Erro no monitoramento: {e}")


def modo_processamento_unico(pasta_analise, pasta_saida, pasta_treino, pasta_processados):
    """
    Modo único: processa todos os arquivos e termina
    """
    print("=== MODO PROCESSAMENTO ÚNICO ===")
    processar_todos_arquivos_analise(pasta_analise, pasta_saida, pasta_treino)

    # Move arquivos processados
    arquivos_processados = glob.glob(os.path.join(pasta_analise, "*.hdr"))
    for arquivo in arquivos_processados:
        mover_arquivo_processado(arquivo, pasta_processados)

    print("Processamento concluído.")


# --- EXECUÇÃO PRINCIPAL ---
if __name__ == '__main__':
    # CONFIGURAÇÕES DAS PASTAS
    PASTA_TREINO = 'dados_treino'  # Arquivos para treinar o modelo
    PASTA_ANALISE = 'arquivoRAW'  # Arquivos para processar/análise
    PASTA_SAIDA = 'resultados'  # Resultados do processamento
    PASTA_PROCESSADOS = 'processados'  # Arquivos já processados (movidos da pasta análise)

    MODO_MONITORAMENTO = True  # True para monitorar continuamente, False para processar uma vez

    # Cria diretórios se não existirem
    os.makedirs(PASTA_TREINO, exist_ok=True)
    os.makedirs(PASTA_ANALISE, exist_ok=True)
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    os.makedirs(PASTA_PROCESSADOS, exist_ok=True)

    print("=== CONFIGURAÇÃO DAS PASTAS ===")
    print(f"Treino: {PASTA_TREINO} - Coloque aqui os arquivos de referência 'saudáveis'")
    print(f"Análise: {PASTA_ANALISE} - Coloque aqui os arquivos para processar")
    print(f"Saída: {PASTA_SAIDA} - Resultados serão salvos aqui")
    print(f"Processados: {PASTA_PROCESSADOS} - Arquivos processados serão movidos para aqui")
    print()

    try:
        if MODO_MONITORAMENTO:
            # Modo monitoramento contínuo
            monitorar_pasta_analise(PASTA_ANALISE, PASTA_SAIDA, PASTA_TREINO, PASTA_PROCESSADOS, intervalo=10)
        else:
            # Modo processamento único
            modo_processamento_unico(PASTA_ANALISE, PASTA_SAIDA, PASTA_TREINO, PASTA_PROCESSADOS)

    except Exception as e:
        print(f"Erro na execução: {e}")