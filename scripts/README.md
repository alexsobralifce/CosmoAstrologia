# Scripts

Esta pasta contém scripts de automação e utilitários do projeto.

## Scripts Disponíveis

### Inicialização

- **start-backend.sh** / **start-backend.ps1** - Inicia apenas o backend
- **start-all.sh** / **start-all.ps1** - Inicia frontend e backend juntos

### Utilitários

- **build_rag_index_fastembed.py** - Constrói o índice RAG usando FastEmbed
- **quick_backend_check.sh** - Verificação rápida do backend

### Verificação de Qualidade

- **backend/scripts/check_syntax.py** - Verifica a sintaxe de todos os arquivos Python antes do deploy

## Uso

### Linux/Mac
```bash
./scripts/start-backend.sh
./scripts/start-all.sh
```

### Windows
```powershell
.\scripts\start-backend.ps1
.\scripts\start-all.ps1
```

### Verificação de Sintaxe (Antes do Deploy)
```bash
cd backend
python3 scripts/check_syntax.py
```
Este script verifica todos os arquivos Python no diretório `app/` para garantir que não há erros de sintaxe antes do deploy.

