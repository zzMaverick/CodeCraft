# 📦 Guia para Obter os Dados

## Por que os arquivos .nc não estão no repositório?

Os arquivos NetCDF são muito grandes (1.5-2 GB cada) e excedem o limite do GitHub (100 MB).

---

## 🌍 Como Baixar os Dados

### Opção 1: NASA Earthdata (Oficial)

1. **Criar conta:**
   - Acesse: https://urs.earthdata.nasa.gov/
   - Registre-se (gratuito)

2. **Buscar dados EMIT:**
   - Acesse: https://search.earthdata.nasa.gov/
   - Busque: `EMIT L2A Reflectance`
   - Filtre por:
     - Data: Últimos 6 meses
     - Área: Escolha um parque nacional (ex: Parque das Emas, Brasil)

3. **Baixar:**
   - Selecione um arquivo
   - Clique em "Download"
   - Salve em `data/treino/`

### Opção 2: Usar dados de exemplo

Se você tem dificuldade em baixar, entre em contato:
- **Email:** contato@codecraft.com
- **Issue no GitHub:** https://github.com/seu-usuario/CodeCraft/issues

---

## 📁 Estrutura de Dados Necessária

Após baixar, organize assim:

```
CodeCraft/
├── data/
│   ├── treino/
│   │   └── EMIT_L2A_RFL_001_20250902T123826_2524508_037.nc  ← Arquivo de treino
│   └── analise/
│       └── (arquivos via upload no site)
```

---

## 🔍 Características do Arquivo Ideal

**Para Treino (data/treino/):**
- ✅ Área de vegetação preservada (parque nacional)
- ✅ Sem nuvens ou pouca cobertura de nuvens
- ✅ Formato: EMIT L2A Reflectance (.nc)
- ✅ Tamanho: ~1.5-2 GB

**Para Análise:**
- Qualquer área que você queira analisar
- Mesmo formato (EMIT L2A .nc)
- Pode ter diferentes características

---

## ❓ FAQ

**P: Posso usar outros sensores além do EMIT?**
R: O código está otimizado para EMIT. Outros sensores requerem adaptações.

**P: Quanto tempo leva o download?**
R: Depende da internet, mas geralmente 10-30 minutos por arquivo.

**P: Posso usar uma área diferente para treino?**
R: Sim! Qualquer área de vegetação preservada serve. O importante é ser uma área "saudável" que servirá de referência.

**P: O que é EMIT?**
R: Earth Surface Mineral Dust Source Investigation - sensor da NASA que captura imagens hiperespectrais (224 bandas).

---

## 🔗 Links Úteis

- **NASA EMIT:** https://earth.jpl.nasa.gov/emit/
- **Earthdata Search:** https://search.earthdata.nasa.gov/
- **Documentação EMIT:** https://lpdaac.usgs.gov/data/get-started-data/collection-overview/missions/emit-overview/

---

**Dúvidas?** Abra uma issue no GitHub!
