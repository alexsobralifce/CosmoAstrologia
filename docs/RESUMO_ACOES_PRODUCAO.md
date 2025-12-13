# 📋 Resumo: Ações Necessárias para Produção

## ✅ Correções de Código Aplicadas

### 1. ✅ Código de Debug Removido

- **Arquivo:** `src/components/landing-page.tsx`
- **Ação:** Removido fetch para servidor de debug local
- **Status:** ✅ Concluído

### 2. ✅ API_BASE_URL Melhorado

- **Arquivo:** `src/services/api.ts`
- **Ação:** Implementada função `getApiBaseUrl()` com:
  - Prioridade para `NEXT_PUBLIC_API_URL`
  - Fallback para desenvolvimento local
  - Log de erro se não configurado em produção
- **Status:** ✅ Concluído

---

## ⚠️ Ações Necessárias ANTES do Deploy

### Frontend (Vercel) - Variáveis de Ambiente

#### 1. `NEXT_PUBLIC_API_URL` ⚠️ OBRIGATÓRIO

```
Valor: https://seu-backend.railway.app
```

**Como configurar:**

1. Acesse https://vercel.com/dashboard
2. Selecione seu projeto
3. Settings → Environment Variables
4. Adicione:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** URL do seu backend no Railway
   - **Environment:** Production, Preview, Development

#### 2. `NEXT_PUBLIC_GOOGLE_CLIENT_ID` (se usar OAuth)

```
Valor: xxxxx-xxxxx.apps.googleusercontent.com
```

**Como configurar:**

- Mesmo processo acima
- Use o Client ID do Google Cloud Console

---

### Backend (Railway) - Variáveis de Ambiente

#### 1. `SECRET_KEY` ⚠️ OBRIGATÓRIO

```bash
# Gerar chave segura:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Como configurar:**

1. Acesse https://railway.app/dashboard
2. Selecione seu projeto
3. Variables → + New Variable
4. Adicione:
   - **Key:** `SECRET_KEY`
   - **Value:** (cole a chave gerada)

#### 2. `GROQ_API_KEY` ⚠️ OBRIGATÓRIO

```
Valor: gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Onde obter:** https://console.groq.com/

#### 3. `CORS_ORIGINS` ⚠️ OBRIGATÓRIO

```
Valor: https://seu-app.vercel.app,https://www.seu-dominio.com
```

**⚠️ IMPORTANTE:**

- Use a URL exata do seu frontend no Vercel
- Separe múltiplas URLs por vírgula (sem espaços)
- Use `https://` (não `http://`)
- Não inclua barra final (`/`)

#### 4. `DATABASE_URL` (Recomendado)

- **Railway:** Definida automaticamente ao adicionar serviço PostgreSQL
- **Ação:** Adicionar serviço PostgreSQL no Railway (se ainda não tiver)

#### 5. `BREVO_API_KEY` (Recomendado para emails)

```
Valor: xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Onde obter:** https://app.brevo.com/settings/keys/api

#### 6. `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` (Opcional)

- Mesmo Client ID do frontend
- Client Secret do Google Cloud Console

---

## 📝 Checklist Rápido

### Antes do Deploy

- [ ] `NEXT_PUBLIC_API_URL` configurado no Vercel
- [ ] `NEXT_PUBLIC_GOOGLE_CLIENT_ID` configurado no Vercel (se usar OAuth)
- [ ] `SECRET_KEY` gerado e configurado no Railway
- [ ] `GROQ_API_KEY` configurado no Railway
- [ ] `CORS_ORIGINS` configurado no Railway com URL do frontend
- [ ] `DATABASE_URL` configurado (PostgreSQL no Railway)
- [ ] `BREVO_API_KEY` configurado no Railway (se usar emails)
- [ ] `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` configurados no Railway (se usar OAuth)

### Testes

- [ ] `npm run build` executa sem erros
- [ ] Backend inicia sem erros
- [ ] Testes passam

### Deploy

- [ ] Código commitado e pushado
- [ ] Vercel conectado ao GitHub
- [ ] Railway conectado ao GitHub
- [ ] Deploy automático configurado

### Pós-Deploy

- [ ] Frontend acessível
- [ ] Backend acessível em `/docs`
- [ ] Teste de login funciona
- [ ] Teste de registro funciona
- [ ] Sem erros de CORS no console

---

## 🚨 Problemas Comuns e Soluções

### "NEXT_PUBLIC_API_URL não está configurado!"

- **Solução:** Configure `NEXT_PUBLIC_API_URL` no Vercel e faça novo deploy

### Erro de CORS no console

- **Solução:** Adicione a URL exata do frontend no `CORS_ORIGINS` do Railway

### Frontend não consegue conectar ao backend

- **Solução:** Verifique que `NEXT_PUBLIC_API_URL` está correto e reinicie o deploy

### Google OAuth não funciona

- **Solução:** Verifique que `NEXT_PUBLIC_GOOGLE_CLIENT_ID` (frontend) e `GOOGLE_CLIENT_ID` (backend) são iguais

---

## 📚 Documentação Completa

Para mais detalhes, consulte:

- [ATUALIZACOES_PRODUCAO.md](./ATUALIZACOES_PRODUCAO.md) - Documentação completa
- [DEPLOY_CHECKLIST.md](./DEPLOY_CHECKLIST.md) - Checklist detalhado
- [VERIFICACAO_PRODUCAO.md](./VERIFICACAO_PRODUCAO.md) - Verificação de requisitos

---

**Última atualização:** 2024
