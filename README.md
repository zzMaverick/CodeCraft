# CodeCraft - Detector de Anomalias com Deep Learning

Sistema de detecção de anomalias em imagens hiperespectrais usando Autoencoder.

## 📚 Documentação

- **[INSTALACAO.md](INSTALACAO.md)** ← 🔧 Guia completo de instalação (COMECE AQUI!)
- **[QUICK_START.md](QUICK_START.md)** ← ⚡ Instalação rápida (5 minutos)
- **[GUIA_ANALISE.md](GUIA_ANALISE.md)** ← 📘 Como funciona e como analisar resultados

## ⚠️ IMPORTANTE: Arquivos de Dados

Os arquivos NetCDF (.nc) **NÃO estão incluídos** no repositório pois são muito grandes (>1GB).

**Você precisa baixar os dados separadamente:**

1. Acesse: https://search.earthdata.nasa.gov/
2. Busque por: "EMIT L2A Reflectance"
3. Escolha uma área preservada (para treino)
4. Baixe e coloque em `data/treino/`

**Arquivo de treino necessário:**
- Nome: `EMIT_L2A_RFL_*_037.nc` (qualquer arquivo EMIT)
- Tamanho: ~1.5-2 GB
- Tipo: Área de vegetação preservada

## 🌐 Interface Web

### Executar com Interface Gráfica

1. **Iniciar o backend:**
```bash
cd backend
pip install -r requirements.txt
python3 app.py
```

2. **Abrir o frontend (em outro terminal):**
```bash
cd front
python3 -m http.server 8000
```

3. **Acessar:** `http://localhost:8000`

4. **Usar:**
   - Arraste/selecione seu arquivo `.nc` (máx: 2GB)
   - Aguarde o processamento (~5-10 min)
   - Baixe os 2 arquivos gerados:
     - `mapa_anomalia_visual_refinado.png`
     - `imagem_rgb_visivel.png`

**⚠️ Nota:** Na primeira vez, a seção "Análise Comparativa" estará vazia. As imagens aparecerão após processar o primeiro arquivo.

## 🗂️ Estrutura de Pastas

```
CodeCraft/
├── data/
│   ├── treino/              # 📥 COLOQUE o arquivo .nc de TREINO aqui (037)
│   └── analise/             # 📥 COLOQUE o arquivo .nc para ANÁLISE aqui
├── output/
│   ├── converted/           # Arquivos .hdr/.raw intermediários
│   ├── maps/               # 📊 Mapas de anomalias refinados (RESULTADO)
│   └── visualizations/     # 🖼️ Imagens RGB (RESULTADO)
├── converter.py
├── deeplearn.py
├── refinar.py
├── visualizar.py
├── run_all.py              # ⭐ Execute este!
└── requirements.txt
```

## 🚀 Como Usar (3 Passos Simples)

### 1. Organize seus arquivos

```bash
# Criar pastas
mkdir -p data/treino data/analise

# Mover arquivos .nc
mv EMIT_*_037.nc data/treino/      # Arquivo de treino (área preservada)
mv EMIT_*.nc data/analise/          # Arquivo para análise
```

### 2. Instalar dependências (primeira vez)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Executar o pipeline completo

```bash
python3 run_all.py
```

## 📊 Resultados Gerados

Após a execução, você terá:

```
output/
├── maps/
│   └── mapa_anomalia_visual_refinado.png  ← 🎯 ESTE É O PRINCIPAL!
└── visualizations/
    ├── imagem_rgb_visivel.png             ← Visualização da área analisada
    └── imagem_rgb_treino.png              ← Visualização da área de treino
```

**Você precisa apenas do arquivo `mapa_anomalia_visual_refinado.png`** - ele já está:
- ✅ Sem corpos d'água
- ✅ Com contraste otimizado
- ✅ Anomalias em vermelho/amarelo

## ❗ Solução de Problemas

### Erro: Arquivo não encontrado
Verifique se os arquivos .nc estão nas pastas corretas:
```bash
ls data/treino/    # Deve mostrar o arquivo 037
ls data/analise/   # Deve mostrar o arquivo para análise
```

### Porta 5000 em uso (AirPlay no Mac)
O backend agora usa a porta **5001**. Se ainda assim houver conflito:
```bash
# Desabilitar AirPlay Receiver:
# System Settings → General → AirDrop & Handoff → AirPlay Receiver → Off
```

### Python 3.13 não funciona
Instale Python 3.11:
```bash
brew install python@3.11
python3.11 -m venv .venv
```

### Comando `python` não encontrado
Use `python3` em todos os comandos:
```bash
python3 app.py
python3 -m http.server 8000
```

### Erro de memória
Edite `deeplearn.py` linha 45 e mude `batch_size=256` para `batch_size=64`

### Erro: 413 Request Entity Too Large
Arquivo muito grande (>2GB). Opções:
```bash
# 1. Reduzir tamanho do arquivo NetCDF
# 2. Aumentar limite no backend (app.py linha 43):
app.config['MAX_CONTENT_LENGTH'] = 3000 * 1024 * 1024  # 3GB
```

### Imagens de exemplo não aparecem
É normal na primeira execução. Faça upload de um arquivo .nc para gerar os resultados.