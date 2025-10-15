#!/bin/bash

# Cria a estrutura de pastas necessária

echo "📁 Criando estrutura de pastas..."

mkdir -p data/treino
mkdir -p data/analise
mkdir -p output/converted
mkdir -p output/maps
mkdir -p output/visualizations
mkdir -p arquivosbrutos

# Criar arquivo README em cada pasta
cat > data/treino/README.txt << 'EOF'
PASTA: data/treino/

Coloque aqui o arquivo NetCDF (.nc) de TREINO:
- Deve ser uma área de vegetação PRESERVADA
- Exemplo: Parque Nacional
- Tamanho esperado: ~1.5-2 GB

Como obter:
1. Acesse: https://search.earthdata.nasa.gov/
2. Busque: "EMIT L2A Reflectance"
3. Escolha uma área preservada
4. Baixe e coloque aqui

Arquivo necessário:
EMIT_L2A_RFL_*_037.nc
EOF

cat > data/analise/README.txt << 'EOF'
PASTA: data/analise/

Esta pasta é usada temporariamente quando você:
- Usa o run_all.py
- Faz upload via interface web

Os arquivos aqui são automaticamente removidos após processamento.
EOF

echo "✅ Estrutura criada!"
echo ""
echo "Próximos passos:"
echo "1. Baixe o arquivo de treino de https://search.earthdata.nasa.gov/"
echo "2. Coloque em data/treino/"
echo "3. Execute: python3 run_all.py"
