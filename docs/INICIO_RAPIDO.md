# 🚀 Guia de Início Rápido

## Iniciar Backend e Frontend Juntos

```bash
./start-all.sh
```

Este script irá:
- Limpar processos antigos nas portas 8000 e 3000
- Iniciar o backend na porta 8000
- Iniciar o frontend na porta 3000
- Mostrar os logs de ambos

## Iniciar Apenas o Backend

```bash
./start-backend.sh
```

## Iniciar Apenas o Frontend

```bash
npm run dev
```

## URLs

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Solução de Problemas

### Porta já em uso

Se você receber erro "Address already in use", execute:

```bash
# Matar processos na porta 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Matar processos na porta 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

### Dependências não instaladas

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
npm install
```

## Ver Logs

- **Backend**: `tail -f backend.log`
- **Frontend**: `tail -f frontend.log`

