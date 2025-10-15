# 🚀 Guia de Instalação - CodeCraft

Guia completo para rodar o projeto em qualquer máquina do zero.

---

## 📋 Pré-requisitos

Antes de começar, você precisa ter instalado:

### 1. Python 3.9 - 3.12 (NÃO use 3.13)

**Windows:**
```bash
# Baixe do site oficial
https://www.python.org/downloads/
# Durante instalação, marque "Add Python to PATH"
```

**Mac:**
```bash
# Instalar Python 3.11 via Homebrew
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### 2. Git (para clonar o projeto)

**Windows:** https://git-scm.com/download/win

**Mac:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

---

## 📥 Passo 1: Obter o Projeto

### Opção A: Clonar do Git (recomendado)

```bash
git clone https://github.com/seu-usuario/CodeCraft.git
cd CodeCraft
```

### Opção B: Download Manual

1. Baixe o arquivo ZIP do projeto
2. Extraia para uma pasta (ex: `C:\CodeCraft` ou `~/CodeCraft`)
3. Abra o terminal nessa pasta

---

## 🔧 Passo 2: Configurar Ambiente Virtual

### Windows (PowerShell/CMD)

```powershell
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.venv\Scripts\activate

# Se der erro de execução no PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Mac / Linux

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate
```

**✅ Confirme que o ambiente está ativo:**
- Você verá `(.venv)` no início da linha do terminal

---

## 📦 Passo 3: Instalar Dependências

Com o ambiente virtual ativo:

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar todas as dependências
pip install -r requirements.txt
```

**⏱️ Tempo estimado:** 5-10 minutos (depende da internet)

**⚠️ Se houver erros:**

**Mac M1/M2 com TensorFlow:**
```bash
pip install tensorflow-macos tensorflow-metal
```

**Erro com numpy no Windows:**
```bash
pip install numpy --upgrade
```

---

## 📁 Passo 4: Preparar Arquivos de Dados

### 4.1. Criar Estrutura de Pastas

```bash
mkdir -p data/treino data/analise
```

**Windows:**
```powershell
mkdir data\treino
mkdir data\analise
```

### 4.2. Adicionar Arquivo de Treino

**IMPORTANTE:** Você precisa de um arquivo NetCDF (.nc) de área preservada para treinar o modelo.

```bash
# Copie seu arquivo de treino (ex: 037.nc) para:
data/treino/EMIT_L2A_RFL_001_20250902T123826_2524508_037.nc
```

**Onde conseguir:**
- NASA EMIT: https://search.earthdata.nasa.gov/
- Escolha uma área de vegetação preservada (ex: parque nacional)

---

## ⚡ Passo 5: Executar o Sistema

Você tem 2 opções:

### Opção A: Interface Web (Recomendado)

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python3 app.py

# Windows:
python app.py
```

**Aguarde ver:** `🚀 Servidor rodando em: http://localhost:5001`

**Terminal 2 - Frontend:**
```bash
cd front
python3 -m http.server 8000

# Windows:
python -m http.server 8000
```

**Acesse no navegador:** http://localhost:8000

### Opção B: Linha de Comando

```bash
# Ative o ambiente virtual
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Execute o pipeline
python3 run_all.py

# Windows:
python run_all.py
```

---

## 🎯 Passo 6: Usar o Sistema

### Via Interface Web:

1. Acesse http://localhost:8000
2. Vá até a seção "Demo"
3. Arraste/selecione seu arquivo `.nc` (área para análise)
4. Aguarde processamento (~5-10 minutos)
5. Visualize resultados na seção "Análise Comparativa"
6. Baixe os arquivos se quiser

### Via Linha de Comando:

```bash
# 1. Coloque arquivo de análise em data/analise/
cp seu_arquivo.nc data/analise/

# 2. Execute
python3 run_all.py

# 3. Resultados em:
# output/maps/mapa_anomalia_visual_refinado.png
# output/visualizations/imagem_rgb_visivel.png
```

---

## 🔍 Verificar Instalação

Execute este teste rápido:

```bash
python3 -c "import xarray, tensorflow, spectral, rasterio; print('✅ Todas as bibliotecas OK!')"
```

**Windows:**
```powershell
python -c "import xarray, tensorflow, spectral, rasterio; print('✅ Todas as bibliotecas OK!')"
```

Se não houver erros, está tudo certo! ✅

---

## 🐛 Solução de Problemas Comuns

### Erro: `ModuleNotFoundError: No module named 'xxx'`

**Solução:**
```bash
# Certifique-se de ativar o ambiente virtual
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Reinstale dependências
pip install -r requirements.txt
```

### Erro: `python: command not found` (Mac/Linux)

**Solução:** Use `python3` em vez de `python`
```bash
python3 --version
```

### Erro: Porta 5001 ou 8000 em uso

**Solução:**
```bash
# Backend: mude a porta em backend/app.py (última linha)
app.run(debug=True, host='0.0.0.0', port=5002)

# Frontend: use outra porta
python3 -m http.server 8001
```

### Erro: TensorFlow não funciona no Mac M1/M2

**Solução:**
```bash
pip uninstall tensorflow
pip install tensorflow-macos tensorflow-metal
```

### Erro: Memória insuficiente durante processamento

**Solução:** Edite `deeplearn.py` linha ~45:
```python
# Mude de:
autoencoder.fit(x_train, x_train, epochs=50, batch_size=256, ...)

# Para:
autoencoder.fit(x_train, x_train, epochs=50, batch_size=64, ...)
```

### Erro: Arquivo de treino não encontrado

**Solução:**
```bash
# Verifique se o arquivo está no local correto
ls data/treino/  # Mac/Linux
dir data\treino  # Windows

# Deve mostrar um arquivo .nc
```

---

## 📂 Estrutura de Pastas Final

Após instalação correta, você terá:

```
CodeCraft/
├── .venv/                  # Ambiente virtual (não commitar)
├── data/
│   ├── treino/
│   │   └── EMIT_*_037.nc   # Arquivo de treino (você adiciona)
│   └── analise/            # Arquivo de análise vai aqui temporariamente
├── output/                 # Resultados gerados (criado automaticamente)
│   ├── converted/
│   ├── maps/
│   └── visualizations/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── front/
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── converter.py
├── deeplearn.py
├── refinar.py
├── visualizar.py
├── run_all.py
├── requirements.txt
├── README.md
└── INSTALACAO.md          # Este arquivo
```

---

## ✅ Checklist Final

Antes de usar, confirme:

- [ ] Python 3.9-3.12 instalado (`python3 --version`)
- [ ] Ambiente virtual criado e ativado (`(.venv)` visível)
- [ ] Dependências instaladas (`pip list` mostra tensorflow, xarray, etc)
- [ ] Arquivo de treino em `data/treino/`
- [ ] Backend rodando (http://localhost:5001)
- [ ] Frontend rodando (http://localhost:8000)

---

## 📚 Próximos Passos

Depois da instalação:

1. Leia o [GUIA_ANALISE.md](GUIA_ANALISE.md) para entender os resultados
2. Leia o [README.md](README.md) para uso avançado
3. Veja exemplos de uso no backend/README.md

---

## 🆘 Precisa de Ajuda?

1. **Erros durante instalação:** Abra uma issue no GitHub
2. **Dúvidas sobre uso:** Consulte GUIA_ANALISE.md
3. **Problemas com dependências:** Veja seção "Solução de Problemas" acima

---

**Versão:** 1.0  
**Última Atualização:** Janeiro 2025  
**Sistema Testado em:** Windows 10/11, macOS (Intel & M1/M2), Ubuntu 20.04/22.04
