# Backend Flask - CO₂Vision

Backend para processar arquivos NetCDF e gerar mapas de anomalias.

## 🚀 Como Executar

### 1. Preparar arquivo de treino

**IMPORTANTE:** Coloque o arquivo de treino (037.nc) na pasta correta:

```bash
# Da raiz do projeto
cp seu_arquivo_037.nc data/treino/
```

### 2. Instalar dependências do backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Iniciar o servidor

```bash
python3 app.py
```

O servidor estará disponível em `http://localhost:5001`

### 4. Abrir o frontend (em outro terminal)

```bash
cd ../front
python3 -m http.server 8000
```

Acesse: `http://localhost:8000`

## 📁 Estrutura de Pastas

```
CodeCraft/
├── data/
│   ├── treino/             # ← COLOQUE o arquivo 037.nc AQUI
│   └── analise/            # ← Arquivos do frontend vão para cá automaticamente
├── output/
│   ├── converted/          # Arquivos convertidos
│   ├── maps/              # mapa_anomalia_visual_refinado.png
│   └── visualizations/    # imagem_rgb_visivel.png
└── backend/
    ├── app.py             # Servidor Flask
    └── requirements.txt
```

## 🔌 Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/upload` | POST | Envia arquivo .nc (salvo em data/analise/) |
| `/api/status` | GET | Status do processamento |
| `/api/download/<filename>` | GET | Download dos resultados |
| `/api/preview/<filename>` | GET | Preview das imagens |
| `/api/reset` | POST | Resetar status |
| `/api/health` | GET | Health check |

**Base URL:** `http://localhost:5001/api`

## ⚙️ Fluxo de Processamento

1. **Frontend:** Usuário faz upload do `.nc`
2. **Backend:** Salva arquivo em `data/analise/`
3. **Processamento:**
   - Converte arquivo de treino (se necessário)
   - Converte arquivo de análise
   - Treina modelo
   - Detecta anomalias
   - Refina mapa
   - Gera visualização RGB
4. **Limpeza:** Remove arquivo temporário de `data/analise/`
5. **Frontend:** Usuário baixa os 2 resultados

## 🐛 Troubleshooting

**Erro: "Nenhum arquivo .nc encontrado em data/treino/"**
```bash
# Coloque o arquivo de treino:
cp EMIT_*_037.nc data/treino/
```

**Erro: Porta 5001 em uso**
- Mude a porta em `app.py`: `app.run(port=5002)`
- Atualize `API_URL` em `script.js` para `http://localhost:5002/api`

**Erro: CORS**
- Certifique-se de que Flask-CORS está instalado: `pip install Flask-CORS`

**Erro: `python: command not found`**
- Use `python3` em vez de `python`

**Erro: 413 Request Entity Too Large**
- Arquivo >2GB
- Aumente `MAX_CONTENT_LENGTH` em `app.py` linha 43
