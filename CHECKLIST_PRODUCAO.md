# ✅ CHECKLIST DE PRODUÇÃO - CosmoAstral

## 📊 Status Atual do Sistema

### ✅ **Funcionalidades Implementadas:**
- ✅ Sistema de autenticação (email/senha + Google OAuth)
- ✅ **Verificação de email com código de 6 dígitos (1 minuto de expiração)** ⭐ NOVO
- ✅ Cálculo de mapas astrais
- ✅ Interpretações com IA (Groq)
- ✅ Sistema RAG para conhecimento astrológico
- ✅ Dashboard completo
- ✅ Todas as funcionalidades principais

### ✅ **Código:**
- ✅ Sem erros de linter
- ✅ Tipos TypeScript corretos
- ✅ Tratamento de erros implementado
- ✅ Validações de dados

---

## 🚨 **AÇÕES CRÍTICAS ANTES DE PRODUÇÃO**

### 1. **Variáveis de Ambiente no Railway (Backend)**

#### ⚠️ **OBRIGATÓRIAS:**
```bash
SECRET_KEY=<gerar-chave-segura>
GROQ_API_KEY=<sua-chave-groq>
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<seu-email-gmail>
SMTP_PASSWORD=<senha-de-app-gmail>  # ⚠️ NÃO use senha normal!
EMAIL_FROM=<seu-email>
```

#### 🔧 **RECOMENDADAS:**
```bash
DATABASE_URL=<postgresql-url>  # Se usar PostgreSQL no Railway
CORS_ORIGINS=https://seu-frontend.vercel.app,https://www.cosmoastral.com.br
GOOGLE_CLIENT_ID=<seu-client-id>  # Se usar Google OAuth
GOOGLE_CLIENT_SECRET=<seu-client-secret>
```

#### 📝 **Gerar SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. **Banco de Dados**

#### ⚠️ **IMPORTANTE:**
- **SQLite (dev):** Funciona localmente, mas **NÃO recomendado para produção**
- **PostgreSQL (produção):** **OBRIGATÓRIO** para produção no Railway

#### 🔧 **Como configurar PostgreSQL no Railway:**
1. Adicione serviço PostgreSQL no Railway
2. Conecte ao serviço Backend
3. A variável `DATABASE_URL` será criada automaticamente
4. **Execute migração do banco:**
   ```bash
   # O SQLAlchemy criará as tabelas automaticamente na primeira execução
   # Mas você pode forçar criando um script de migração
   ```

#### ⚠️ **MIGRAÇÃO DO BANCO:**
As novas colunas (`email_verified`, `verification_code`, `verification_code_expires`) precisam ser criadas no PostgreSQL de produção.

**Opção 1: SQLAlchemy automático (recomendado)**
- O sistema criará automaticamente na primeira execução

**Opção 2: SQL manual**
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code_expires DATETIME;
ALTER TABLE users ALTER COLUMN is_active SET DEFAULT FALSE;
```

### 3. **Configuração SMTP para Produção**

#### ⚠️ **Gmail - Senha de App:**
1. Ative **autenticação de 2 fatores** no Gmail
2. Crie uma **"Senha de app"** em: https://myaccount.google.com/apppasswords
3. **Use essa senha** no `SMTP_PASSWORD` (não a senha normal da conta)

#### 🔧 **Alternativas Recomendadas para Produção:**
- **SendGrid** (100 emails/dia grátis)
- **Amazon SES** (escala)
- **Mailgun** (confiável)

### 4. **Frontend (Vercel)**

#### ⚠️ **Variáveis de Ambiente:**
```bash
VITE_API_URL=https://seu-backend.railway.app
VITE_GOOGLE_CLIENT_ID=<seu-client-id>  # Se usar Google OAuth
```

---

## ✅ **CHECKLIST FINAL**

### Backend (Railway)
- [ ] `SECRET_KEY` configurado (não usar padrão)
- [ ] `GROQ_API_KEY` configurado
- [ ] `SMTP_HOST` configurado
- [ ] `SMTP_USERNAME` configurado
- [ ] `SMTP_PASSWORD` configurado (senha de app do Gmail)
- [ ] `EMAIL_FROM` configurado
- [ ] `DATABASE_URL` apontando para PostgreSQL
- [ ] `CORS_ORIGINS` com URLs do frontend
- [ ] Banco de dados migrado (tabelas criadas)
- [ ] Build do Docker funcionando
- [ ] Logs sem erros críticos

### Frontend (Vercel)
- [ ] `VITE_API_URL` apontando para backend de produção
- [ ] Build sem erros
- [ ] Testes de registro funcionando
- [ ] Modal de verificação de email aparecendo
- [ ] Fluxo completo de verificação testado

### Testes Funcionais
- [ ] Registro de novo usuário → Email enviado
- [ ] Modal de verificação aparece
- [ ] Código de 6 dígitos funciona
- [ ] Contador de 60 segundos funciona
- [ ] Reenvio de código funciona
- [ ] Verificação bem-sucedida → Token criado
- [ ] Login após verificação funciona
- [ ] Google OAuth funciona (se configurado)
- [ ] Cálculo de mapas astrais funciona
- [ ] Interpretações com IA funcionam

### Segurança
- [ ] `SECRET_KEY` não é o padrão
- [ ] CORS configurado corretamente
- [ ] Senhas hashadas (bcrypt)
- [ ] Tokens JWT com expiração
- [ ] Validação de dados no backend
- [ ] Rate limiting (se implementado)

---

## 🧪 **TESTES RECOMENDADOS ANTES DE PRODUÇÃO**

### 1. **Teste de Registro Completo:**
```bash
# 1. Registrar novo usuário
# 2. Verificar se email foi enviado
# 3. Abrir modal de verificação
# 4. Digitar código recebido
# 5. Verificar se token foi criado
# 6. Verificar se redirecionou para dashboard
```

### 2. **Teste de Reenvio:**
```bash
# 1. Aguardar expiração do código (60s)
# 2. Clicar em "Reenviar código"
# 3. Verificar se novo email foi enviado
# 4. Digitar novo código
# 5. Verificar se funcionou
```

### 3. **Teste de Código Inválido:**
```bash
# 1. Digitar código errado
# 2. Verificar mensagem de erro
# 3. Tentar novamente com código correto
```

### 4. **Teste de Código Expirado:**
```bash
# 1. Aguardar 60 segundos
# 2. Tentar usar código antigo
# 3. Verificar mensagem de expiração
# 4. Reenviar código
```

---

## 📋 **RESUMO DO QUE FOI IMPLEMENTADO**

### ✅ **Sistema de Verificação de Email:**
1. **Backend:**
   - Campos novos no modelo User (`email_verified`, `verification_code`, `verification_code_expires`)
   - Endpoint `/register` modificado para enviar email
   - Endpoint `/verify-email` para verificar código
   - Endpoint `/resend-verification` para reenviar código
   - Serviço de email configurado

2. **Frontend:**
   - Modal de verificação criado
   - Integração com fluxo de registro
   - Contador de 60 segundos
   - Função de reenvio
   - Tratamento de erros

3. **Configuração:**
   - Variáveis SMTP no `.env`
   - Tempo de expiração: 1 minuto
   - Código de 6 dígitos

---

## ⚠️ **PONTOS DE ATENÇÃO**

### 1. **Banco de Dados:**
- ⚠️ **SQLite não é recomendado para produção**
- ✅ **Use PostgreSQL no Railway**
- ⚠️ **Execute migração das novas colunas**

### 2. **SMTP:**
- ⚠️ **Gmail requer senha de app** (não senha normal)
- ⚠️ **Teste envio de email antes de produção**
- ✅ **Considere SendGrid para produção** (mais confiável)

### 3. **Segurança:**
- ⚠️ **Nunca commite `.env` no Git**
- ⚠️ **Use SECRET_KEY forte**
- ⚠️ **Configure CORS corretamente**

### 4. **Performance:**
- ⚠️ **Teste com múltiplos usuários**
- ⚠️ **Monitore logs do Railway**
- ⚠️ **Configure rate limiting se necessário**

---

## 🚀 **PRÓXIMOS PASSOS**

1. ✅ **Configurar variáveis no Railway**
2. ✅ **Configurar PostgreSQL no Railway**
3. ✅ **Executar migração do banco**
4. ✅ **Testar registro completo em produção**
5. ✅ **Monitorar logs**
6. ✅ **Fazer deploy do frontend no Vercel**

---

## ✅ **CONCLUSÃO**

O sistema está **TECNICAMENTE PRONTO** para produção, mas requer:

1. ⚠️ **Configuração adequada das variáveis de ambiente**
2. ⚠️ **Migração do banco de dados para PostgreSQL**
3. ⚠️ **Testes completos em ambiente de staging**

**Recomendação:** Faça um deploy de teste primeiro, teste todas as funcionalidades, e só depois faça o deploy final para produção.

