# Sistema de Astrologia - Mapa Astral Completo

Sistema completo de cálculo e interpretação de mapas astrológicos com backend Python usando RAG e frontend React/TypeScript.

## 🚀 Funcionalidades

### Frontend
- ✅ Interface moderna e responsiva
- ✅ **Autenticação com Google OAuth**
- ✅ Cálculo de mapa astral em tempo real
- ✅ Visualização interativa do mapa natal (wheel)
- ✅ Interpretações detalhadas de planetas, casas e aspectos
- ✅ Trânsitos diários e futuros
- ✅ Sistema de regente do mapa
- ✅ Análise de elementos e modalidades
- ✅ Tema claro/escuro

### Backend
- ✅ **Autenticação Google OAuth com JWT**
- ✅ Cálculo preciso usando Swiss Ephemeris
- ✅ Sistema RAG para interpretações baseadas em documentos PDF
- ✅ API REST completa com FastAPI
- ✅ Cálculo de trânsitos planetários
- ✅ Suporte a múltiplos documentos astrológicos

## 📁 Estrutura do Projeto

```
Astrologia/
├── backend/              # Backend Python
│   ├── app/
│   │   ├── api/         # Endpoints da API
│   │   ├── core/        # Configurações
│   │   ├── models/      # Schemas Pydantic
│   │   └── services/    # Lógica de negócio
│   ├── requirements.txt
│   ├── SETUP_GOOGLE_OAUTH.md
│   └── run.py
├── src/                  # Frontend React
│   ├── components/      # Componentes React
│   ├── services/        # Serviços de API
│   ├── hooks/           # React Hooks
│   └── ...
└── pdf/                 # Documentos PDF para RAG
```

## 🚀 Script de Inicialização Rápida

Use o script `start.sh` (Linux/Mac) ou `start.bat` (Windows) para iniciar ou parar os serviços:

```bash
# Linux/Mac
./start.sh

# Windows (PowerShell)
.\start.ps1

# Windows (CMD)
start.bat
```

**Como funciona:**
- Se os serviços estiverem rodando → para ambos
- Se os serviços estiverem parados → inicia ambos
- Mostra PIDs dos processos e logs em tempo real
- Pressione Ctrl+C para parar

## 🛠️ Instalação e Configuração

### Backend

1. Navegue até a pasta do backend:
```bash
cd backend
```

2. Crie um ambiente virtual (opcional mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
# Crie o arquivo .env na pasta backend/
cp .env.example .env  # Se existir
# Ou crie manualmente
```

Edite o arquivo `.env`:
```env
# OpenAI API Key para RAG
OPENAI_API_KEY=sk-sua-chave-aqui

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Google OAuth (OBRIGATÓRIO)
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-client-secret
SECRET_KEY=uma-chave-secreta-aleatoria-aqui

# RAG Configuration
RAG_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# PDFs path
PDFS_PATH=../pdf
```

**⚠️ IMPORTANTE: Configurar Google OAuth**

Veja o arquivo `backend/SETUP_GOOGLE_OAUTH.md` para instruções detalhadas de como obter as credenciais do Google OAuth.

5. Execute o servidor:
```bash
python run.py
```

O backend estará disponível em `http://localhost:8000`

### Frontend

1. Instale as dependências:
```bash
npm install
```

2. Execute o frontend:
```bash
npm run dev
```

O frontend estará disponível em `http://localhost:3000`

## 📚 Documentação da API

Acesse `http://localhost:8000/docs` para ver a documentação interativa do Swagger.

### Principais Endpoints

**Autenticação:**
- `GET /api/auth/login` - Inicia login com Google
- `GET /api/auth/callback` - Callback do Google OAuth
- `GET /api/auth/me` - Informações do usuário atual
- `POST /api/auth/logout` - Logout

**Charts:**
- `POST /api/charts/calculate` - Calcula mapa astral completo

**Interpretations:**
- `POST /api/interpretations/planet/{planet_name}` - Interpretação de planeta
- `POST /api/interpretations/house/{house_number}` - Interpretação de casa
- `POST /api/interpretations/aspect` - Interpretação de aspecto
- `POST /api/interpretations/chart-ruler` - Interpretação do regente do mapa

**Transits:**
- `POST /api/transits/daily` - Trânsitos diários
- `POST /api/transits/future` - Trânsitos futuros

## 🔧 Tecnologias

### Backend
- **FastAPI** - Framework web moderno e rápido
- **Swiss Ephemeris** - Cálculos astronômicos precisos
- **Authlib** - OAuth 2.0 e OpenID Connect
- **python-jose** - JWT tokens
- **LangChain** - Framework para RAG
- **ChromaDB** - Banco de dados vetorial
- **OpenAI** - Modelos de linguagem (opcional)

### Frontend
- **React** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool
- **React Router** - Roteamento
- **Tailwind CSS** - Estilização
- **Radix UI** - Componentes acessíveis

## 📖 Como Usar

1. **Configure o Google OAuth** (veja `backend/SETUP_GOOGLE_OAUTH.md`)
2. Inicie o backend na porta 8000
3. Inicie o frontend na porta 3000
4. Acesse `http://localhost:3000`
5. Preencha os dados de nascimento no onboarding
6. Clique em "Entrar com Google" para autenticar
7. O sistema calculará automaticamente o mapa astral
8. Explore as diferentes seções:
   - **Seu Guia Pessoal**: Regente do mapa, trânsitos diários e futuros
   - **Visão Geral**: Elementos, modalidades, forças e desafios
   - **Planetas**: Interpretações detalhadas de cada planeta
   - **Casas**: Análise das 12 casas astrológicas
   - **Aspectos**: Interpretações dos aspectos planetários

## 🔍 Sistema RAG

O sistema usa RAG (Retrieval-Augmented Generation) para gerar interpretações baseadas nos documentos PDF na pasta `pdf/`. 

- Se você configurar `OPENAI_API_KEY`, o sistema usará GPT para gerar interpretações avançadas
- Sem a chave, o sistema usará interpretações fallback baseadas em regras

## 🔐 Autenticação

O sistema usa Google OAuth 2.0 para autenticação:

1. Usuário clica em "Entrar com Google"
2. É redirecionado para o Google para autorizar
3. Após autorizar, retorna com um token JWT
4. O token é armazenado no localStorage
5. Todas as requisições seguintes incluem o token no header `Authorization`

## 📝 Notas

- O Swiss Ephemeris precisa dos arquivos de efemérides. Eles geralmente são instalados automaticamente com o pacote Python.
- Os documentos PDF devem estar na pasta `pdf/` relativa ao backend
- O sistema RAG processa os PDFs na primeira inicialização
- **Frontend roda na porta 3000**
- **Backend roda na porta 8000**

## 🤝 Contribuindo

Este é um projeto em desenvolvimento. Sinta-se à vontade para contribuir!

## 📄 Licença

[Adicione sua licença aqui]
