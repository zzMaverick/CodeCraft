# ⚡ Quick Start - 5 Minutos

Guia super rápido para quem tem pressa.

## 1️⃣ Instalar (2 min)

```bash
# Clonar
git clone https://github.com/seu-usuario/CodeCraft.git
cd CodeCraft

# Criar ambiente
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar
pip install -r requirements.txt
```

## 2️⃣ Preparar Dados (1 min)

```bash
# Criar pastas
mkdir -p data/treino data/analise

# Copiar arquivo de treino
cp /caminho/para/seu/arquivo_037.nc data/treino/
```

## 3️⃣ Rodar (2 min)

### Terminal 1:
```bash
cd backend
python3 app.py
```

### Terminal 2:
```bash
cd front
python3 -m http.server 8000
```

### Navegador:
```
http://localhost:8000
```

**Pronto! 🎉** Faça upload do seu arquivo `.nc` e aguarde o resultado.

---

## ❌ Deu erro?

Veja o [INSTALACAO.md](INSTALACAO.md) completo.
