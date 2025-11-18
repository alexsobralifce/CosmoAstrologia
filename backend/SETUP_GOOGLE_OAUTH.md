# Configuração do Google OAuth

## Passo 1: Criar Credenciais no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a **Google+ API**:
   - Vá em "APIs & Services" > "Library"
   - Procure por "Google+ API" ou "Google Identity Services"
   - Clique em "Enable"

4. Configure a tela de consentimento OAuth:
   - Vá em "APIs & Services" > "OAuth consent screen"
   - Selecione "External" (ou Internal se for G Suite)
   - Preencha as informações necessárias:
     - App name: "Astrologia App"
     - User support email: seu email
     - Developer contact: seu email
   - Clique em "Save and Continue"
   - Adicione escopos: `email`, `profile`, `openid`
   - Adicione test users (se estiver em modo de teste)
   - Clique em "Save and Continue"

5. Criar credenciais OAuth:
   - Vá em "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "OAuth client ID"
   - Escolha "Web application"
   - Configure:
     - **Name**: Astrologia Backend
     - **Authorized JavaScript origins**:
       - `http://localhost:8000`
       - `http://localhost:3000`
     - **Authorized redirect URIs**:
       - `http://localhost:8000/api/auth/callback`
   - Clique em "Create"
   - **Copie o Client ID e Client Secret**

## Passo 2: Configurar no Backend

1. Abra o arquivo `.env` na pasta `backend/`

2. Adicione as credenciais:
```env
GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-client-secret-aqui
SECRET_KEY=sua-chave-secreta-aleatoria-aqui-mude-em-producao
```

**Para gerar uma SECRET_KEY segura:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Passo 3: Verificar Configuração

Seu arquivo `.env` deve ter algo como:

```env
# OpenAI API Key para RAG
OPENAI_API_KEY=sk-...

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Google OAuth
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123xyz
SECRET_KEY=uma-chave-muito-segura-aqui-mude-em-producao

# RAG Configuration
RAG_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# PDFs path
PDFS_PATH=../pdf
```

## Passo 4: Testar

1. Reinicie o servidor backend:
```bash
cd backend
python run.py
```

2. Inicie o frontend:
```bash
npm run dev
```

3. Acesse `http://localhost:3000`
4. Complete o onboarding
5. Clique em "Entrar com Google"
6. Você será redirecionado para o Google para autorizar
7. Após autorizar, será redirecionado de volta para o app

## ⚠️ Importante para Produção

- Use uma `SECRET_KEY` diferente e segura em produção
- Configure URLs de produção no Google Cloud Console
- Use HTTPS em produção
- Configure variáveis de ambiente no servidor
- Não commite o arquivo `.env` no git

## Troubleshooting

### Erro: "redirect_uri_mismatch"
- Verifique se o URI de callback está exatamente como configurado no Google Console
- Deve ser: `http://localhost:8000/api/auth/callback`

### Erro: "invalid_client"
- Verifique se o `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` estão corretos
- Certifique-se de que não há espaços extras nas variáveis

### Erro: "access_denied"
- O usuário cancelou a autorização
- Verifique se os escopos estão configurados corretamente

