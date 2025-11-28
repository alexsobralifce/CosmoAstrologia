# 📍 Onde Pegar o VITE_GOOGLE_CLIENT_ID

## 🎯 Resposta Rápida

O `VITE_GOOGLE_CLIENT_ID` é o **Client ID** do seu projeto no **Google Cloud Console**.

---

## 📋 Passo a Passo Detalhado

### 1️⃣ Acessar o Google Cloud Console

1. **Acesse:** https://console.cloud.google.com/
2. **Faça login** com sua conta Google
3. **Selecione seu projeto** (ou crie um novo se não tiver)

### 2️⃣ Navegar até Credentials

1. **No menu lateral**, clique em **"APIs & Services"** (APIs e Serviços)
2. **Clique em "Credentials"** (Credenciais)

   **Ou acesse diretamente:**
   - https://console.cloud.google.com/apis/credentials

### 3️⃣ Encontrar o OAuth 2.0 Client ID

1. **Procure na lista** por **"OAuth 2.0 Client IDs"**
2. **Clique no nome** do seu Client ID (ex: "Cosmos Astral Web Client")

   **Se não existir:**
   - Clique em **"+ CREATE CREDENTIALS"** (Criar credenciais)
   - Selecione **"OAuth client ID"**
   - Tipo: **"Web application"**
   - Nome: **"Cosmos Astral Web Client"** (ou qualquer nome)
   - Clique em **"Create"** (Criar)

### 4️⃣ Copiar o Client ID

1. **Na tela de detalhes**, você verá:
   - **Client ID:** `xxxxx-xxxxx.apps.googleusercontent.com`
   - **Client Secret:** `xxxxx` (não precisa para o frontend)

2. **Copie o Client ID** completo
   - Formato: `xxxxx-xxxxx.apps.googleusercontent.com`
   - Exemplo: `100874517602-9kjnm8s42j2780albl1eime7dcpqmlpv.apps.googleusercontent.com`

---

## ✅ Onde Usar

### No Vercel (Produção):

1. **Acesse:** https://vercel.com
2. **Selecione seu projeto**
3. **Vá em:** Settings → Environment Variables
4. **Adicione:**
   - **Key:** `VITE_GOOGLE_CLIENT_ID`
   - **Value:** Cole o Client ID que você copiou
   - **Environment:** Selecione todos (Production, Preview, Development)
5. **Clique em Save**

### Localmente (Desenvolvimento):

1. **Crie/edite o arquivo:** `.env.local` na raiz do projeto
2. **Adicione:**
   ```env
   VITE_GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
   ```
3. **Salve o arquivo**

---

## 🔍 Exemplo Visual

No Google Cloud Console, você verá algo assim:

```
OAuth 2.0 Client IDs
┌─────────────────────────────────────────────────────────┐
│ Cosmos Astral Web Client                                 │
│                                                          │
│ Client ID                                                │
│ 100874517602-9kjnm8s42j2780albl1eime7dcpqmlpv.apps... │ ← COPIE ESTE
│                                                          │
│ Client Secret                                            │
│ GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxx                          │
└─────────────────────────────────────────────────────────┘
```

---

## ⚠️ Importante

1. **Não compartilhe** o Client ID publicamente (embora não seja crítico)
2. **O Client Secret** é diferente e deve ser mantido secreto (usado apenas no backend)
3. **Cada projeto** tem seu próprio Client ID
4. **Você pode ter múltiplos** Client IDs (um para desenvolvimento, outro para produção)

---

## 🆘 Não Encontrou?

### Se não tem OAuth Client ID criado:

1. **Vá em:** APIs & Services → Credentials
2. **Clique em:** "+ CREATE CREDENTIALS"
3. **Selecione:** "OAuth client ID"
4. **Se aparecer erro:** Você precisa configurar o OAuth consent screen primeiro

### Se precisa configurar OAuth Consent Screen:

1. **Vá em:** APIs & Services → OAuth consent screen
2. **Escolha:** External (para qualquer usuário) ou Internal (apenas Workspace)
3. **Preencha:**
   - App name: Cosmos Astral (ou qualquer nome)
   - User support email: Seu email
   - Developer contact: Seu email
4. **Clique em:** Save and Continue
5. **Em Scopes:** Adicione `email`, `profile`, `openid`
6. **Clique em:** Save and Continue
7. **Em Test users:** (se External) Adicione emails de teste ou publique
8. **Clique em:** Save and Continue
9. **Volte para:** Credentials → Create OAuth client ID

---

## 📝 Checklist

- [ ] Acessei o Google Cloud Console
- [ ] Naveguei até APIs & Services → Credentials
- [ ] Encontrei ou criei o OAuth 2.0 Client ID
- [ ] Copiei o Client ID completo
- [ ] Configurei no Vercel (Settings → Environment Variables)
- [ ] Configurei localmente (`.env.local`)
- [ ] Fiz redeploy no Vercel (se necessário)

---

## 🔗 Links Úteis

- **Google Cloud Console:** https://console.cloud.google.com/
- **Credentials:** https://console.cloud.google.com/apis/credentials
- **OAuth Consent Screen:** https://console.cloud.google.com/apis/credentials/consent

---

## 🎯 Resumo

**Onde pegar:**
1. Google Cloud Console → APIs & Services → Credentials
2. Clique no OAuth 2.0 Client ID
3. Copie o Client ID (formato: `xxxxx.apps.googleusercontent.com`)

**Onde usar:**
- Vercel: Settings → Environment Variables → `VITE_GOOGLE_CLIENT_ID`
- Local: `.env.local` → `VITE_GOOGLE_CLIENT_ID=...`

**Pronto!** 🎉

