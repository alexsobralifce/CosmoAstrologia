# 🔧 Erro 405: "Method Not Allowed" no Cadastro

## 🚨 Problema

Erro no Vercel ao tentar cadastrar:
```
POST cosmoastrologia-production.up.railway.app/api/auth/register
405 Method Not Allowed
```

## 🔍 Causa

O erro 405 significa que o método HTTP (POST) não está sendo aceito pelo endpoint. Possíveis causas:

1. **URL do backend incorreta** - Falta `https://` na URL
2. **Problema de roteamento no Railway** - O Railway pode estar bloqueando ou redirecionando
3. **CORS bloqueando** - Requisições podem estar sendo bloqueadas
4. **Endpoint não encontrado** - Problema de roteamento no backend

## ✅ Solução

### Passo 1: Verificar URL do Backend no Vercel

1. Acesse: https://vercel.com
2. Selecione seu projeto
3. Vá em **Settings** → **Environment Variables**
4. Verifique `VITE_API_URL`:
   - ✅ **Correto:** `https://cosmoastrologia-production.up.railway.app`
   - ❌ **Errado:** `cosmoastrologia-production.up.railway.app` (sem `https://`)
   - ❌ **Errado:** `http://cosmoastrologia-production.up.railway.app` (usando `http://`)

**⚠️ IMPORTANTE:** A URL deve começar com `https://` e não ter barra final (`/`)

### Passo 2: Verificar Backend no Railway

1. Acesse: https://railway.app
2. Selecione seu projeto backend
3. Vá em **Settings** → **Networking**
4. Verifique se o **Public Domain** está ativo
5. Copie a URL exata (deve ser algo como `https://cosmoastrologia-production.up.railway.app`)

### Passo 3: Testar Endpoint Diretamente

Teste se o endpoint está acessível:

```bash
curl -X POST https://cosmoastrologia-production.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","name":"Test","birth_data":{"name":"Test","birth_date":"2000-01-01T00:00:00Z","birth_time":"12:00","birth_place":"Test","latitude":0,"longitude":0}}'
```

**Resposta esperada:**
- ✅ `200 OK` ou `400 Bad Request` (se dados inválidos) = Endpoint funciona
- ❌ `405 Method Not Allowed` = Problema no backend
- ❌ `404 Not Found` = Endpoint não existe
- ❌ `Connection refused` = Backend não está rodando

### Passo 4: Verificar CORS no Backend

No Railway, verifique a variável `CORS_ORIGINS`:

1. Vá em **Variables**
2. Procure por `CORS_ORIGINS`
3. Deve incluir a URL do Vercel:
   ```
   https://seu-app.vercel.app
   ```
4. Se não existir, adicione:
   - **Key:** `CORS_ORIGINS`
   - **Value:** `https://seu-app.vercel.app` (substitua pela sua URL do Vercel)
   - Pode ter múltiplas URLs separadas por vírgula

### Passo 5: Verificar Logs do Railway

1. No Railway, vá em **Deployments**
2. Clique no último deploy
3. Veja os **Logs**
4. Procure por erros relacionados a `/api/auth/register`

### Passo 6: Redeploy

Após fazer mudanças:

1. **No Vercel:**
   - Vá em **Deployments**
   - Clique nos 3 pontos do último deploy
   - Selecione **Redeploy**

2. **No Railway:**
   - O Railway faz redeploy automático quando você muda variáveis
   - Ou force um redeploy manualmente

## 🔍 Verificação Rápida

### Checklist

- [ ] `VITE_API_URL` no Vercel começa com `https://`
- [ ] `VITE_API_URL` não tem barra final (`/`)
- [ ] URL do backend está correta e acessível
- [ ] `CORS_ORIGINS` no Railway inclui URL do Vercel
- [ ] Backend está rodando no Railway
- [ ] Teste direto do endpoint funciona
- [ ] Redeploy feito após mudanças

## 🎯 Solução Rápida

Se o problema persistir, tente:

1. **Verificar URL exata:**
   ```bash
   # No terminal, teste:
   curl https://cosmoastrologia-production.up.railway.app/
   # Deve retornar: {"message":"Astrologia API"}
   ```

2. **Atualizar VITE_API_URL no Vercel:**
   - Remova a variável
   - Adicione novamente com `https://` no início
   - Faça redeploy

3. **Verificar se backend está respondendo:**
   - Acesse: `https://cosmoastrologia-production.up.railway.app/`
   - Deve mostrar: `{"message":"Astrologia API"}`

## ⚠️ Problemas Comuns

### Erro persiste após configurar

**Solução:**
1. Verificar se fez **Redeploy** no Vercel
2. Verificar se a URL está **exatamente** como configurada
3. Testar endpoint diretamente com `curl`
4. Verificar logs do Railway

### Backend não responde

**Solução:**
1. Verificar se o backend está rodando no Railway
2. Verificar logs do Railway para erros
3. Verificar se há problemas de dependências
4. Tentar fazer redeploy do backend

### CORS Error

**Solução:**
1. Verificar `CORS_ORIGINS` no Railway
2. Deve incluir URL do Vercel: `https://seu-app.vercel.app`
3. Fazer redeploy do backend após atualizar

## 📝 Resumo

**O que fazer:**
1. Verificar `VITE_API_URL` no Vercel (deve ter `https://`)
2. Verificar `CORS_ORIGINS` no Railway (deve incluir URL do Vercel)
3. Testar endpoint diretamente
4. Verificar logs do Railway
5. Fazer redeploy

**URLs corretas:**
- Frontend (Vercel): `https://seu-app.vercel.app`
- Backend (Railway): `https://cosmoastrologia-production.up.railway.app`
- `VITE_API_URL`: `https://cosmoastrologia-production.up.railway.app` (sem barra final)

