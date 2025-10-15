# app.py - VERSÃO MINIMALISTA
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import os
import base64
from PIL import Image
import io

# Configuração da página
st.set_page_config(
    page_title="Analisador Hiperespectral",
    page_icon="🌿",
    layout="wide"
)

st.title("🌿 Analisador de Dados Hiperespectrais")
st.markdown("---")


class SimpleHyperspectralAnalyzer:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()

    def processar_arquivo_nc_simulado(self, arquivo_upload, nome):
        """Processamento simulado para demonstração"""
        try:
            # Ler o arquivo como bytes para simular processamento
            file_bytes = arquivo_upload.getvalue()

            # Criar dados simulados baseados no tamanho do arquivo
            # Quanto maior o arquivo, mais "complexa" a análise
            file_size = len(file_bytes)

            # Gerar dados sintéticos para demonstração
            width, height = 400, 300
            bands = 10  # Número reduzido de bandas para simulação

            # Criar array sintético
            synthetic_data = np.random.rand(bands, height, width) * 1000

            # Simular algumas características reais
            # Banda 0: Vermelho
            synthetic_data[0] += np.random.rand(height, width) * 500
            # Banda 1: Verde
            synthetic_data[1] += np.random.rand(height, width) * 600
            # Banda 2: Azul
            synthetic_data[2] += np.random.rand(height, width) * 400

            return synthetic_data

        except Exception as e:
            st.error(f"Erro no processamento simulado: {e}")
            return None

    def gerar_rgb_simulado(self, dados, nome_saida):
        """Gera imagem RGB a partir de dados simulados"""
        try:
            # Usar as primeiras 3 bandas para RGB
            r_band = dados[0]  # Vermelho
            g_band = dados[1]  # Verde
            b_band = dados[2]  # Azul

            # Combinar bandas
            rgb_data = np.stack([r_band, g_band, b_band], axis=-1)

            # Normalizar
            rgb_normalized = (rgb_data - rgb_data.min()) / (rgb_data.max() - rgb_data.min())
            rgb_normalized = np.clip(rgb_normalized, 0, 1)

            # Salvar imagem
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.imshow(rgb_normalized)
            ax.set_title(f"Imagem RGB - {nome_saida}")
            ax.axis('off')

            # Salvar em buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            plt.close()

            buf.seek(0)
            return buf

        except Exception as e:
            st.error(f"Erro ao gerar RGB: {e}")
            return None

    def calcular_ndvi_simulado(self, dados, nome_saida):
        """Calcula NDVI simulado"""
        try:
            # Simular bandas de vermelho e infravermelho
            red_band = dados[3]  # Banda "vermelha"
            nir_band = dados[7]  # Banda "infravermelho"

            # Calcular NDVI
            ndvi = (nir_band - red_band) / (nir_band + red_band + 1e-8)

            # Plotar
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
            ax.set_title(f"NDVI Simulado - {nome_saida}")
            ax.axis('off')
            plt.colorbar(im, ax=ax, label='NDVI')

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            plt.close()

            buf.seek(0)
            return buf

        except Exception as e:
            st.error(f"Erro no cálculo do NDVI: {e}")
            return None

    def detectar_anomalias_simulado(self, dados_ref, dados_analise, nome_saida):
        """Detecção simples de anomalias"""
        try:
            # Diferença simples entre médias das bandas
            media_ref = np.mean(dados_ref, axis=0)
            media_analise = np.mean(dados_analise, axis=0)

            diferenca = np.abs(media_analise - media_ref)

            # Normalizar
            anomalia_normalizada = (diferenca - diferenca.min()) / (diferenca.max() - diferenca.min())

            # Plotar
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(anomalia_normalizada, cmap='hot', vmin=0, vmax=1)
            ax.set_title(f"Mapa de Anomalias - {nome_saida}")
            ax.axis('off')
            plt.colorbar(im, ax=ax, label='Intensidade da Anomalia')

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            plt.close()

            buf.seek(0)
            return buf

        except Exception as e:
            st.error(f"Erro na detecção de anomalias: {e}")
            return None


def main():
    # Inicializar analisador
    analyzer = SimpleHyperspectralAnalyzer()

    # Sidebar
    with st.sidebar:
        st.header("📁 Upload de Arquivos")

        st.subheader("Área de Referência")
        arquivo_ref = st.file_uploader(
            "Arquivo NetCDF de referência",
            type=['nc'],
            key="ref"
        )

        st.subheader("Área de Análise")
        arquivo_analise = st.file_uploader(
            "Arquivo NetCDF para análise",
            type=['nc'],
            key="analise"
        )

        st.markdown("---")
        st.subheader("🔧 Tipo de Análise")

        analise_tipo = st.selectbox(
            "Selecione o tipo de análise:",
            [
                "Visualização RGB",
                "Análise de Vegetação (NDVI)",
                "Detecção de Anomalias",
                "Comparação Visual"
            ]
        )

        st.markdown("---")
        st.info("""
        **💡 Modo de Demonstração**

        Esta versão usa dados simulados para evitar problemas de compatibilidade.
        """)

    # Conteúdo principal
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("🔄 Processamento")

        if st.button("🚀 Executar Análise", type="primary", use_container_width=True):
            if not arquivo_ref or not arquivo_analise:
                st.warning("⚠️ Faça upload de ambos os arquivos")
                return

            with st.spinner("Processando dados..."):
                # Processar arquivos
                dados_ref = analyzer.processar_arquivo_nc_simulado(arquivo_ref, "Referência")
                dados_analise = analyzer.processar_arquivo_nc_simulado(arquivo_analise, "Análise")

                if dados_ref is None or dados_analise is None:
                    st.error("❌ Erro no processamento dos dados")
                    return

                # Executar análise selecionada
                if analise_tipo == "Visualização RGB":
                    resultado = analyzer.gerar_rgb_simulado(dados_analise, "Área de Análise")
                    st.session_state.resultado = resultado
                    st.session_state.tipo_analise = "RGB"

                elif analise_tipo == "Análise de Vegetação (NDVI)":
                    resultado = analyzer.calcular_ndvi_simulado(dados_analise, "Área de Análise")
                    st.session_state.resultado = resultado
                    st.session_state.tipo_analise = "NDVI"

                elif analise_tipo == "Detecção de Anomalias":
                    resultado = analyzer.detectar_anomalias_simulado(dados_ref, dados_analise, "Análise")
                    st.session_state.resultado = resultado
                    st.session_state.tipo_analise = "Anomalias"

                elif analise_tipo == "Comparação Visual":
                    resultado_ref = analyzer.gerar_rgb_simulado(dados_ref, "Referência")
                    resultado_analise = analyzer.gerar_rgb_simulado(dados_analise, "Análise")
                    st.session_state.resultado_ref = resultado_ref
                    st.session_state.resultado_analise = resultado_analise
                    st.session_state.tipo_analise = "Comparação"

                st.success("✅ Análise concluída!")

    with col2:
        st.header("📊 Resultados")

        if 'resultado' in st.session_state:
            if st.session_state.tipo_analise == "RGB":
                st.subheader("🌄 Visualização RGB")
                st.image(st.session_state.resultado, use_column_width=True)
                st.caption("Imagem colorida simulada a partir das bandas espectrais")

            elif st.session_state.tipo_analise == "NDVI":
                st.subheader("🌿 Índice de Vegetação (NDVI)")
                st.image(st.session_state.resultado, use_column_width=True)
                st.caption("Vermelho: pouca vegetação, Verde: vegetação saudável")

            elif st.session_state.tipo_analise == "Anomalias":
                st.subheader("🔍 Mapa de Anomalias")
                st.image(st.session_state.resultado, use_column_width=True)
                st.caption("Áreas em amarelo/vermelho indicam possíveis anomalias")

        elif 'resultado_ref' in st.session_state and 'resultado_analise' in st.session_state:
            st.subheader("🔄 Comparação Visual")

            col_ref, col_anal = st.columns(2)
            with col_ref:
                st.write("**Área de Referência**")
                st.image(st.session_state.resultado_ref, use_column_width=True)

            with col_anal:
                st.write("**Área de Análise**")
                st.image(st.session_state.resultado_analise, use_column_width=True)

        else:
            st.info("👆 Execute uma análise para ver os resultados aqui")

            # Exemplo de como seria com dados reais
            with st.expander("🧪 Ver exemplo de análise"):
                st.image("https://via.placeholder.com/600x400/4CAF50/FFFFFF?text=Imagem+RGB+de+Exemplo",
                         caption="Exemplo de imagem RGB gerada a partir de dados hiperespectrais")

    # Seção informativa
    with st.expander("📖 Sobre este Sistema"):
        st.markdown("""
        **Sistema de Análise Hiperespectral - Versão de Demonstração**

        Esta é uma versão simplificada que demonstra as funcionalidades do sistema
        usando dados simulados, evitando problemas de compatibilidade em macOS.

        **Funcionalidades demonstradas:**
        - 📁 Upload de arquivos NetCDF
        - 🎨 Geração de imagens RGB a partir de bandas espectrais  
        - 🌿 Cálculo de índices de vegetação (NDVI)
        - 🔍 Detecção de anomalias por comparação
        - 📊 Visualização interativa dos resultados

        **Para usar a versão completa:**
        ```bash
        # Instalar em ambiente Linux ou Windows
        pip install tensorflow spectral scikit-learn rasterio xarray
        ```

        **Próximos passos no desenvolvimento:**
        - Integração com processamento real de dados EMIT
        - Autoencoder para detecção avançada de anomalias
        - Refinamento com máscaras de água e nuvens
        - Análise temporal multi-data
        """)


if __name__ == "__main__":
    main()