# Astrologia - Sistema de Mapas Astrais

Sistema completo para cálculo e visualização de mapas astrais com interface moderna e cálculos astronômicos precisos.

## 🚀 Início Rápido

### Opção 1: Scripts Automáticos (Recomendado)

**Linux/Mac:**

```bash
# Iniciar apenas o backend
./scripts/start-backend.sh

# Iniciar frontend e backend juntos
./scripts/start-all.sh
```

**Windows:**

```powershell
# Iniciar apenas o backend
.\scripts\start-backend.ps1

# Iniciar frontend e backend juntos
.\scripts\start-all.ps1
```

### Opção 2: Manual

#### Backend

```bash
cd backend

# Criar e ativar ambiente virtual (primeira vez)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
python run.py
```

O backend estará disponível em: `http://localhost:8000` Documentação da API: `http://localhost:8000/docs`

#### Frontend

```bash
# Instalar dependências (primeira vez)
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

O frontend estará disponível em: `http://localhost:5173`

## 📋 Requisitos

- **Python 3.8+**
- **Node.js 18+**
- **npm ou yarn**

## 🗄️ Banco de Dados

O banco de dados SQLite é criado automaticamente na primeira execução em `backend/astrologia.db`.

## ⚙️ Configuração de Variáveis de Ambiente

### Desenvolvimento Local

**Backend:**
1. Copie `backend/.env.example` para `backend/.env`
2. Configure `SECRET_KEY` e `GROQ_API_KEY`

**Frontend:**
1. Copie `.env.local.example` para `.env.local`
2. Configure `VITE_API_URL=http://localhost:8000`

📚 **Guia completo:** [docs/CONFIGURACAO_LOCAL.md](./docs/CONFIGURACAO_LOCAL.md)

### Produção

- **Backend (Railway):** Configure variáveis no painel do Railway
- **Frontend (Vercel):** Configure `VITE_API_URL` no painel do Vercel

📚 **Resumo rápido:** [docs/VARIAVEIS_AMBIENTE_RESUMO.md](./docs/VARIAVEIS_AMBIENTE_RESUMO.md)

## 🔧 Estrutura do Projeto

```
Astrologia/
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── api/      # Endpoints da API
│   │   ├── core/     # Configurações e banco de dados
│   │   ├── models/   # Modelos SQLAlchemy e schemas
│   │   └── services/ # Serviços (cálculos astrológicos)
│   ├── requirements.txt
│   └── run.py
├── src/              # Frontend React + TypeScript
│   ├── components/   # Componentes React
│   ├── services/     # Serviços de API
│   ├── utils/        # Utilitários
│   ├── i18n/         # Internacionalização
│   └── styles/       # Estilos globais
├── docs/             # Documentação do projeto
├── tests/            # Arquivos de teste
├── scripts/          # Scripts de automação
└── package.json
```

## 🌟 Funcionalidades

- ✅ Cálculo preciso de mapas astrais usando PyEphem
- ✅ Autenticação com JWT
- ✅ Registro de usuários com dados de nascimento
- ✅ Cálculo automático de signos (Sol, Lua, Ascendente)
- ✅ Interface moderna e responsiva
- ✅ Suporte a temas claro/escuro

## 📚 API Endpoints

- `POST /api/auth/register` - Registrar novo usuário
- `GET /api/auth/me` - Obter usuário atual
- `GET /api/auth/birth-chart` - Obter mapa astral do usuário

## 🐛 Troubleshooting

### Backend não inicia

- Verifique se a porta 8000 está livre
- Certifique-se de que todas as dependências estão instaladas
- Verifique os logs em `backend.log`

### Frontend não conecta ao backend

- Certifique-se de que o backend está rodando em `http://localhost:8000`
- Verifique a variável `VITE_API_URL` no `.env.local` (deve ser `http://localhost:8000`)
- Reinicie o servidor de desenvolvimento após mudar variáveis

### Erro de banco de dados

- Delete `backend/astrologia.db` e reinicie o servidor para recriar o banco

## 📝 Licença

Este projeto é privado.
