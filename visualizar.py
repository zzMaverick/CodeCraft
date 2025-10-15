import numpy as np
from spectral import envi
import matplotlib.pyplot as plt


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
        # 1. Ler o cabeçalho para obter metadados
        hdr = envi.read_envi_header(caminho_arquivo_hdr)
        img = envi.open(caminho_arquivo_hdr)

        # 2. Encontrar as bandas RGB
        try:
            wavelengths = [float(w) for w in hdr['wavelength']]
            red_idx = encontrar_banda_mais_proxima(wavelengths, 650)
            green_idx = encontrar_banda_mais_proxima(wavelengths, 550)
            blue_idx = encontrar_banda_mais_proxima(wavelengths, 450)
        except KeyError:
            # Usar índices padrão para EMIT
            red_idx, green_idx, blue_idx = 40, 25, 15

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
        print(f"   ✓ Imagem RGB salva: {caminho_saida_rgb}")

    except Exception as e:
        print(f"   ✗ Erro ao gerar RGB: {e}")


# --- COMO USAR O SCRIPT ---
if __name__ == '__main__':
    arquivo_hdr_entrada = '/Users/mateusgomes/Documents/CodeCraft/output/converted/analise_convertida.hdr'
    arquivo_png_saida = '/Users/mateusgomes/Documents/CodeCraft/output/visualizations/imagem_rgb_visivel.png'
    converter_raw_para_rgb(arquivo_hdr_entrada, arquivo_png_saida)