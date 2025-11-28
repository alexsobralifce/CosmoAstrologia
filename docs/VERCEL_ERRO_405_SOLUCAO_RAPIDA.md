# ⚡ Solução Rápida: Erro 405 no Cadastro

## 🚨 Problema

```
POST cosmoastrologia-production.up.railway.app/api/auth/register
405 Method Not Allowed
```

## ✅ Solução em 3 Passos

### 1️⃣ Verificar URL no Vercel

**No Vercel:**
1. Settings → Environment Variables
2. Procure `VITE_API_URL`
3. **Deve ser:** `https://cosmoastrologia-production.up.railway.app`
4. **NÃO pode ser:** 
   - `cosmoastrologia-production.up.railway.app` (sem `https://`)
   - `http://cosmoastrologia-production.up.railway.app` (usando `http://`)
   - `https://cosmoastrologia-production.up.railway.app/` (com barra final)

### 2️⃣ Verificar CORS no Railway

**No Railway:**
1. Variables → Procure `CORS_ORIGINS`
2. Deve incluir: `https://seu-app.vercel.app`
3. Se não existir, adicione:
   - **Key:** `CORS_ORIGINS`
   - **Value:** `https://seu-app.vercel.app` (substitua pela sua URL do Vercel)

### 3️⃣ Redeploy

**No Vercel:**
1. Deployments → 3 pontos → Redeploy

**No Railway:**
- Redeploy automático ao atualizar variáveis

## 🔍 Teste Rápido

Teste se o endpoint funciona:

```bash
curl -X POST https://cosmoastrologia-production.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","name":"Test","birth_data":{"name":"Test","birth_date":"2000-01-01T00:00:00Z","birth_time":"12:00","birth_place":"Test","latitude":0,"longitude":0}}'
```

**Se retornar 200 ou 400:** Endpoint funciona ✅  
**Se retornar 405:** Problema no backend ❌

## 📝 Checklist

- [ ] `VITE_API_URL` no Vercel começa com `https://`
- [ ] `VITE_API_URL` não tem barra final
- [ ] `CORS_ORIGINS` no Railway inclui URL do Vercel
- [ ] Redeploy feito no Vercel
- [ ] Teste direto do endpoint funciona

## 🆘 Ainda não funciona?

1. Verifique logs do Railway
2. Verifique se backend está rodando
3. Teste endpoint diretamente com `curl`
4. Veja documento completo: `VERCEL_ERRO_405_REGISTER.md`

