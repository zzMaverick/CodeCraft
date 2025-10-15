#!/bin/bash

# Remove arquivos grandes do histórico do Git
echo "🧹 Limpando arquivos grandes do repositório..."

# Voltar para a raiz do projeto
cd /Users/mateusgomes/Documents/CodeCraft

# Remover arquivos do tracking do Git (não deleta do disco)
git rm --cached -r data/treino/*.nc 2>/dev/null
git rm --cached -r data/analise/*.nc 2>/dev/null
git rm --cached -r output/ 2>/dev/null
git rm --cached -r arquivosbrutos/ 2>/dev/null
git rm --cached -r *.nc 2>/dev/null

# Commitar as mudanças
git add .gitignore
git commit -m "chore: adiciona .gitignore e remove arquivos grandes"

echo "✅ Limpeza concluída!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Force push para limpar o remoto:"
echo "      git push origin pronto --force"
echo ""
echo "   2. Ou crie uma nova branch limpa:"
echo "      git checkout -b limpo"
echo "      git push origin limpo"
