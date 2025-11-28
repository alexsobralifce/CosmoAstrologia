# 🔐 Configuração Google OAuth para Vercel - Passo a Passo

Guia rápido e direto sobre o que configurar no Google Cloud Console para que a autenticação funcione no Vercel.

## 🎯 O Que Você Precisa Fazer

### 1. Acessar o Google Cloud Console

1. Vá para: https://console.cloud.google.com/
2. Selecione seu projeto
3. Vá em **APIs & Services** → **Credentials**

### 2. Editar Sua Credencial OAuth 2.0

1. Clique no **OAuth 2.0 Client ID** que você já criou (ou crie um novo)
2. Você verá duas seções importantes:

---

## ✅ **Authorized JavaScript origins**

Adicione **TODAS** as URLs onde seu frontend pode rodar:

### Para Desenvolvimento Local:
```
http://localhost:3000
http://localhost:5173
http://127.0.0.1:3000
http://127.0.0.1:5173
```

### Para Produção (Vercel):
```
https://seu-app.vercel.app
```

**⚠️ IMPORTANTE:**
- Use `https://` para produção (Vercel sempre usa HTTPS)
- Use `http://` para desenvolvimento local
- **NÃO** inclua barra final (`/`) no final da URL
- Adicione a URL **exata** do seu app no Vercel

### Exemplo Completo:
```
http://localhost:3000
http://localhost:5173
https://cosmoastrologia.vercel.app
```

---

## ✅ **Authorized redirect URIs**

Adicione as **MESMAS URLs** do passo anterior:

### Para Desenvolvimento Local:
```
http://localhost:3000
http://localhost:5173
http://127.0.0.1:3000
http://127.0.0.1:5173
```

### Para Produção (Vercel):
```
https://seu-app.vercel.app
```

**⚠️ IMPORTANTE:**
- Mesmas regras do passo anterior
- Mesmas URLs que você adicionou em "JavaScript origins"

### Exemplo Completo:
```
http://localhost:3000
http://localhost:5173
https://cosmoastrologia.vercel.app
```

---

## 🔍 Como Descobrir Sua URL do Vercel

1. Acesse: https://vercel.com
2. Selecione seu projeto
3. Vá em **Settings** → **Domains**
4. Você verá sua URL de produção (ex: `cosmoastrologia.vercel.app`)
5. Use essa URL **exata** no Google Console

**Ou:**
- Olhe na URL quando você acessa seu app
- Copie a URL completa (sem o caminho, apenas o domínio)

---

## 📝 Checklist Rápido

- [ ] Acessei o Google Cloud Console
- [ ] Encontrei/Editei minha credencial OAuth 2.0
- [ ] Adicionei `http://localhost:3000` em **JavaScript origins**
- [ ] Adicionei `http://localhost:5173` em **JavaScript origins**
- [ ] Adicionei `https://meu-app.vercel.app` em **JavaScript origins** (substitua pela sua URL)
- [ ] Adicionei as mesmas URLs em **Redirect URIs**
- [ ] Cliquei em **Save**
- [ ] Aguardei alguns minutos para propagar

---

## ⚠️ Problemas Comuns

### Erro: "redirect_uri_mismatch"

**Causa:** A URL não está exatamente como configurada

**Solução:**
1. Verifique se a URL no erro é **exatamente** igual à que você configurou
2. Verifique se tem `https://` (não `http://`) para produção
3. Verifique se **não** tem barra final (`/`)
4. Adicione a URL exata que aparece no erro

### Erro: "invalid_client"

**Causa:** Client ID não configurado no Vercel

**Solução:**
1. No Vercel, vá em **Settings** → **Environment Variables**
2. Adicione: `VITE_GOOGLE_CLIENT_ID` = seu Client ID
3. Faça **Redeploy** do projeto

### Não funciona em preview deployments

**Causa:** URLs de preview não estão autorizadas

**Solução:**
1. Cada preview deployment do Vercel tem uma URL única
2. Adicione a URL específica do preview em **JavaScript origins**
3. Ou adicione conforme necessário

---

## 🚀 Após Configurar

1. **Salve** as mudanças no Google Console
2. **Aguarde 2-5 minutos** para propagar
3. **Configure no Vercel:**
   - Settings → Environment Variables
   - Adicione: `VITE_GOOGLE_CLIENT_ID` = seu Client ID
4. **Redeploy** no Vercel
5. **Teste** o login com Google

---

## 📸 Exemplo Visual

No Google Cloud Console, você verá algo assim:

```
Authorized JavaScript origins
┌─────────────────────────────────────┐
│ http://localhost:3000               │
│ http://localhost:5173               │
│ https://cosmoastrologia.vercel.app  │
└─────────────────────────────────────┘

Authorized redirect URIs
┌─────────────────────────────────────┐
│ http://localhost:3000               │
│ http://localhost:5173               │
│ https://cosmoastrologia.vercel.app  │
└─────────────────────────────────────┘
```

---

## ✅ Resumo

**O que fazer:**
1. Adicionar URL do Vercel em **Authorized JavaScript origins**
2. Adicionar URL do Vercel em **Authorized redirect URIs**
3. Configurar `VITE_GOOGLE_CLIENT_ID` no Vercel
4. Redeploy

**URLs para adicionar:**
- Desenvolvimento: `http://localhost:3000`, `http://localhost:5173`
- Produção: `https://seu-app.vercel.app`

**Pronto!** 🎉

