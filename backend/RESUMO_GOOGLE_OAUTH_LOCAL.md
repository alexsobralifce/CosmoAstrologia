# ⚡ Resumo Rápido: Configurar Google OAuth Localmente

## 🐛 Problema

Erro: `origin_mismatch` - A URL local não está registrada no Google Cloud Console.

## ✅ Solução Rápida

### 1. Adicionar URL no Google Cloud Console

1. Acesse: https://console.cloud.google.com/apis/credentials
2. Clique no seu **OAuth 2.0 Client ID**
3. Em **Authorized JavaScript origins**, adicione:
   ```
   http://localhost:3000
   http://localhost:5173
   http://127.0.0.1:3000
   http://127.0.0.1:5173
   ```
4. Clique em **SAVE**

### 2. Configurar Client ID no Projeto

Crie/edite `.env.local` na raiz do projeto:

```bash
VITE_GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
```

### 3. Reiniciar Servidor

```bash
# Pare o servidor (Ctrl+C) e reinicie
npm run dev
```

### 4. Testar

Acesse `http://localhost:3000` e tente fazer login com Google.

---

## 📚 Guia Completo

Veja: `backend/CONFIGURAR_GOOGLE_OAUTH_LOCAL.md`

---

## 🔍 Verificar URL Atual

No console do navegador (F12):

```javascript
console.log('URL atual:', window.location.origin);
```

Adicione essa URL exata no Google Cloud Console.

