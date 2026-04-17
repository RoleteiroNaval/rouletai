# 🧹 LIMPEZA DE PROJETO - Arquivos a Organizar

## 🚨 PARA REMOVER
- **Pasta `.env1ts/`** - Use `.env` na raiz
- **Arquivos Python** na raiz devem ir para `legacy/`

## 📁 ESTRUTURA RECOMENDADA
```
legacy/
├── python/          # main_playtech.py, etc.
├── pytest/          # requirements.txt, etc.
├── config/          # .env antigo, etc.
└── docs/            # README antigo, etc.
```

## ✅ O QUE MANTÉR
- `vision-pro/` - Frontend React
- `server/` - Backend Node.js
- `shared/` - Schemas compartilhados
- `.env` - Configuração atual
- `package.json` - Scripts Node.js

## 🛠️ SCRIPTS DE LIMPEZA
```bash
# Criar estrutura legacy
mkdir -p legacy/{python,pytest,config,docs}

# Mover arquivos Python
mv *.py legacy/python/ 2>/dev/null || true
mv requirements.txt legacy/pytest/ 2>/dev/null || true
mv .env.example legacy/config/ 2>/dev/null || true

# Remover pasta problemática
rm -rf .env1ts/
```

## 🎯 RESULTADO FINAL
Projeto limpo focado em **Node.js + React + TypeScript** com compatibilidade Python em `legacy/`.