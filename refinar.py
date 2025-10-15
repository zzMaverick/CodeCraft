import numpy as np
import rasterio
from spectral import envi
import matplotlib.pyplot as plt


def encontrar_banda_mais_proxima(wavelengths, target_wavelength):
    """Encontra o índice da banda cujo comprimento de onda é mais próximo do alvo."""
    idx = np.argmin(np.abs(np.array(wavelengths) - target_wavelength))
    return idx


def refinar_mapa_anomalia(caminho_hdr_original, caminho_tif_anomalia, caminho_saida_final_png):
    """
    Mascara corpos d'água em um mapa de anomalias e reescala o contraste.
    """
    try:
        # --- 1. CALCULAR A MÁSCARA DE ÁGUA USANDO NDWI ---
        hdr = envi.read_envi_header(caminho_hdr_original)
        img = envi.open(caminho_hdr_original)

        # NDWI usa as bandas Verde e NIR
        try:
            wavelengths = [float(w) for w in hdr['wavelength']]
            green_idx = encontrar_banda_mais_proxima(wavelengths, 550)
            nir_idx = encontrar_banda_mais_proxima(wavelengths, 860)
        except KeyError:
            green_idx, nir_idx = 35, 85

        green_band = img.read_band(green_idx).astype(float)
        nir_band = img.read_band(nir_idx).astype(float)

        np.seterr(divide='ignore', invalid='ignore')
        ndwi = (green_band - nir_band) / (green_band + nir_band)
        mascara_agua = ndwi > 0.2

        # --- 2. APLICAR A MÁSCARA E REESCALAR O CONTRASTE ---
        with rasterio.open(caminho_tif_anomalia) as src:
            mapa_anomalia = src.read(1)

        mapa_anomalia_mascarado = np.where(mascara_agua, 0, mapa_anomalia)
        mascara_terra = ~mascara_agua

        vmax = np.percentile(mapa_anomalia_mascarado[mascara_terra], 98)
        mapa_anomalia_refinado = np.clip(mapa_anomalia_mascarado, 0, vmax) / vmax

        # --- 3. SALVAR O RESULTADO FINAL ---
        plt.imsave(caminho_saida_final_png, mapa_anomalia_refinado, cmap='jet')
        print(f"   ✓ Mapa refinado salvo: {caminho_saida_final_png}")

    except Exception as e:
        print(f"   ✗ Erro ao refinar mapa: {e}")


# --- COMO USAR O SCRIPT ---
if __name__ == '__main__':
    arquivo_hdr = '/Users/mateusgomes/Documents/CodeCraft/output/converted/analise_convertida.hdr'
    mapa_tif = '/Users/mateusgomes/Documents/CodeCraft/output/maps/mapa_anomalia_bruto.tif'
    arquivo_png = '/Users/mateusgomes/Documents/CodeCraft/output/maps/mapa_anomalia_visual_refinado.png'
    refinar_mapa_anomalia(arquivo_hdr, mapa_tif, arquivo_png)