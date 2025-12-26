# 🔐 Configurar Google OAuth para Desenvolvimento Local

Este guia explica como configurar o Google OAuth para funcionar localmente e resolver o erro "origin_mismatch".

---

## 🐛 Problema

Ao tentar fazer login com Google localmente, você recebe o erro:

```
Erro 400: origin_mismatch
Acesso bloqueado: erro de autorização
Não é possível fazer login no app porque ele não obedece à política do OAuth 2.0 do Google.
```

**Causa:** A URL local do seu app não está registrada no Google Cloud Console como uma origem JavaScript autorizada.

---

## ✅ Solução

### Passo 1: Identificar a URL Local

O frontend pode estar rodando em uma destas URLs:
- `http://localhost:5173` (Vite padrão)
- `http://localhost:3000`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

**Verifique qual porta está sendo usada:**
```bash
# Se estiver rodando o frontend, veja no terminal qual porta está sendo usada
npm run dev
# Ou
vite
```

### Passo 2: Acessar Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Selecione seu projeto (ou crie um novo)
3. Vá em **APIs & Services** → **Credentials** (Credenciais)

### Passo 3: Encontrar ou Criar OAuth 2.0 Client ID

1. Na lista de credenciais, procure por **OAuth 2.0 Client IDs**
2. Se não existir, clique em **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Se já existir, clique no Client ID para editar

### Passo 4: Configurar Authorized JavaScript Origins

1. Na seção **Authorized JavaScript origins**, clique em **+ ADD URI**
2. Adicione **TODAS** as URLs locais que você pode usar:

```
http://localhost:5173
http://localhost:3000
http://localhost:3001
http://localhost:3002
http://127.0.0.1:5173
http://127.0.0.1:3000
http://127.0.0.1:3001
http://127.0.0.1:3002
```

**⚠️ IMPORTANTE:**
- Use `http://` (não `https://`) para desenvolvimento local
- Não inclua barra final (`/`) nas URLs
- Adicione todas as variações que você pode usar

### Passo 5: Configurar Authorized Redirect URIs (se necessário)

Se você estiver usando redirect (não apenas o botão do Google Identity Services), adicione também:

```
http://localhost:5173
http://localhost:3000
http://127.0.0.1:5173
http://127.0.0.1:3000
```

### Passo 6: Salvar e Obter Client ID

1. Clique em **SAVE** (Salvar)
2. Copie o **Client ID** (formato: `xxxxx.apps.googleusercontent.com`)

### Passo 7: Configurar no Projeto

#### Frontend (`.env.local` ou `.env`)

Crie ou edite o arquivo `.env.local` na raiz do projeto:

```bash
VITE_GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
```

**Exemplo:**
```bash
VITE_GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
```

#### Backend (opcional, se usar server-side OAuth)

No arquivo `backend/.env`:

```bash
GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-client-secret-aqui
```

### Passo 8: Reiniciar o Servidor

Após configurar:

1. **Frontend:** Pare e reinicie o servidor de desenvolvimento
   ```bash
   # Pare o servidor (Ctrl+C)
   # Reinicie
   npm run dev
   ```

2. **Backend:** Se mudou variáveis, reinicie também
   ```bash
   # No diretório backend
   python run.py
   ```

### Passo 9: Testar

1. Acesse o app em `http://localhost:5173` (ou a porta que você usa)
2. Clique no botão "Fazer Login com o Google"
3. Deve funcionar sem o erro `origin_mismatch`

---

## 🔍 Verificar Configuração

### Verificar se a variável está configurada:

No console do navegador (F12), execute:

```javascript
console.log('Google Client ID:', import.meta.env.VITE_GOOGLE_CLIENT_ID);
```

Deve mostrar o Client ID configurado.

### Verificar no Google Cloud Console:

1. Vá em **APIs & Services** → **Credentials**
2. Clique no seu OAuth 2.0 Client ID
3. Verifique se as URLs estão listadas em **Authorized JavaScript origins**

---

## 🐛 Troubleshooting

### Erro persiste após configurar

1. **Limpe o cache do navegador:**
   - Chrome: Ctrl+Shift+Delete (Windows) ou Cmd+Shift+Delete (Mac)
   - Ou use modo anônimo/privado

2. **Verifique se a URL exata está registrada:**
   - A URL deve ser **exatamente** igual (incluindo porta)
   - `http://localhost:5173` ≠ `http://localhost:3000`

3. **Verifique se salvou no Google Cloud Console:**
   - As mudanças podem levar alguns segundos para propagar

4. **Verifique se está usando o Client ID correto:**
   - O Client ID deve corresponder ao projeto no Google Cloud Console

### Erro: "redirect_uri_mismatch"

Se você receber este erro, adicione também as URLs em **Authorized redirect URIs**.

### Múltiplos ambientes

Se você tem diferentes ambientes (dev, staging, prod), crie **Client IDs separados** para cada um:

- **Desenvolvimento:** `http://localhost:5173`
- **Staging:** `https://staging.seudominio.com`
- **Produção:** `https://seudominio.com`

---

## 📚 Recursos

- **Google Cloud Console:** https://console.cloud.google.com/
- **Documentação OAuth 2.0:** https://developers.google.com/identity/protocols/oauth2
- **Google Identity Services:** https://developers.google.com/identity/gsi/web

---

## ✅ Checklist

- [ ] URLs locais adicionadas em **Authorized JavaScript origins**
- [ ] Client ID copiado do Google Cloud Console
- [ ] `VITE_GOOGLE_CLIENT_ID` configurado no `.env.local`
- [ ] Servidor de desenvolvimento reiniciado
- [ ] Testado no navegador
- [ ] Erro `origin_mismatch` resolvido

---

✨ **Configuração concluída!** O Google OAuth deve funcionar localmente agora.

