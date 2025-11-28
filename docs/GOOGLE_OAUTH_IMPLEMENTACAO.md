# 🔐 Implementação do Google OAuth Real

## ✅ Mudanças Implementadas

### 1. **Frontend**

#### `index.html`

- ✅ Adicionado script do Google Identity Services (`https://accounts.google.com/gsi/client`)

#### `src/components/auth-portal.tsx`

- ✅ Implementado `handleGoogleCallback` para processar resposta do Google OAuth
- ✅ Inicialização automática do Google Identity Services
- ✅ Renderização automática do botão do Google quando `VITE_GOOGLE_CLIENT_ID` está configurado
- ✅ Fallback para modal simulado se Google Identity Services não estiver disponível
- ✅ Fluxo completo:
  - Usuário clica no botão → Abre popup do Google
  - Usuário faz login → Sistema captura email automaticamente
  - Sistema verifica no banco → Dashboard ou Onboarding

#### `src/components/google-onboarding.tsx`

- ✅ Nome agora é opcional (usa email como fallback)
- ✅ Texto atualizado para indicar que nome é opcional

#### `src/services/api.ts`

- ✅ Adicionado método `verifyGoogleToken()` para verificar token com backend

### 2. **Backend**

#### `backend/app/api/auth.py`

- ✅ Criado endpoint `/api/auth/google/verify` para verificar token JWT do Google
- ✅ Suporta validação oficial (com `google-auth`) ou decodificação manual (fallback)
- ✅ Retorna email, name, picture e google_id

#### `backend/requirements.txt`

- ✅ Adicionadas dependências: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`

## 🔧 Configuração Necessária

### 📖 Guia Completo

**Para instruções detalhadas passo a passo, consulte:** 👉 **[GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md)** - Guia completo com screenshots e troubleshooting

### Resumo Rápido:

1. **Obter Google Client ID:**

   - Acesse [Google Cloud Console](https://console.cloud.google.com/)
   - Crie projeto → Configure OAuth → Crie credenciais
   - Copie Client ID e Client Secret

2. **Configurar Variáveis de Ambiente:**

   **Frontend (`.env.local` na raiz do projeto):**

   ```env
   VITE_GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
   ```

   **Backend (`backend/.env`):**

   ```env
   GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=seu-client-secret-aqui
   ```

3. **Adicionar URLs no Google Cloud Console:**
   - Origens JavaScript autorizadas: `http://localhost:5173`, `https://seu-app.vercel.app`
   - URIs de redirecionamento: Mesmas URLs acima

**Nota**: O Client ID do frontend deve ser o mesmo do backend (ou usar IDs diferentes para web e backend, dependendo da configuração do Google).

## 🚀 Como Funciona Agora

### Fluxo Completo:

1. **Usuário clica no botão Google**

   - Se `VITE_GOOGLE_CLIENT_ID` estiver configurado: Botão do Google Identity Services é renderizado automaticamente
   - Se não estiver: Usa botão customizado que abre modal simulado

2. **Autenticação Google (OAuth Real)**

   - Popup do Google abre
   - Usuário faz login com email e senha do Google
   - Google retorna token JWT (credential)

3. **Verificação do Token**

   - Frontend envia token para `/api/auth/google/verify`
   - Backend decodifica token e extrai: email, name, picture, google_id
   - Backend retorna dados do usuário

4. **Autenticação no Sistema**

   - Frontend chama `/api/auth/google` com email, name, google_id
   - Backend verifica se usuário existe no banco:
     - **Se existe E tem mapa astral**: `needs_onboarding=False` → Vai direto para dashboard
     - **Se existe mas NÃO tem mapa**: `needs_onboarding=True` → Vai para onboarding
     - **Se não existe**: Cria usuário → `needs_onboarding=True` → Vai para onboarding

5. **Onboarding (se necessário)**
   - Nome é opcional (já vem do Google)
   - Usuário preenche: Data de nascimento, Hora, Local
   - Sistema calcula mapa astral
   - Vai para dashboard

## 🧪 Como Testar

### Sem Google Client ID (Modo Simulação):

1. Não configure `VITE_GOOGLE_CLIENT_ID`
2. Clique no botão Google
3. Modal simulado abre
4. Digite email manualmente
5. Sistema funciona normalmente (mas sem OAuth real)

### Com Google Client ID (OAuth Real):

1. Configure `VITE_GOOGLE_CLIENT_ID` no frontend
2. Configure `GOOGLE_CLIENT_ID` no backend
3. Clique no botão Google
4. Popup do Google abre
5. Faça login com conta Google
6. Sistema captura email automaticamente
7. Verifica no banco e redireciona conforme necessário

## 📝 Notas Importantes

1. **Fallback Inteligente**: Se Google Identity Services não estiver disponível ou não configurado, o sistema usa modal simulado automaticamente

2. **Decodificação Manual**: O backend pode decodificar tokens JWT manualmente mesmo sem `google-auth` instalado (usando base64)

3. **Validação Oficial**: Se `google-auth` estiver instalado e `GOOGLE_CLIENT_ID` configurado, o backend valida o token oficialmente com Google

4. **Nome Opcional**: No onboarding, o nome é opcional. Se não preenchido, usa email como fallback

5. **Verificação no Banco**: O sistema sempre verifica se o usuário existe e se tem mapa astral antes de decidir o fluxo

## 🔍 Debug

Para ver logs do fluxo:

- Frontend: Console do navegador mostra `[AUTH]` logs
- Backend: Terminal mostra `[GOOGLE_AUTH]` logs

## ⚠️ Próximos Passos (Opcional)

1. Adicionar campo `google_id` na tabela `users` do banco
2. Salvar `google_id` quando criar usuário via Google
3. Permitir login apenas com Google ID (sem email) no futuro
