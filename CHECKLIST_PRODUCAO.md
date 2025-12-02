# ✅ CHECKLIST DE PRODUÇÃO - CosmoAstral

## 📊 Status Atual do Sistema

### ✅ **Funcionalidades Implementadas:**
- ✅ Sistema de autenticação (email/senha + Google OAuth)
- ✅ **Verificação de email com código de 6 dígitos (1 minuto de expiração)** ⭐ NOVO
- ✅ **Email só é salvo no banco após validação do código** ⭐ NOVO
- ✅ **Tabela pending_registrations para registros temporários** ⭐ NOVO
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
O sistema criará automaticamente todas as tabelas e colunas necessárias na primeira execução:

**Tabelas que serão criadas:**
- `users` (com novas colunas de verificação)
- `birth_charts`
- `pending_registrations` ⭐ NOVA - Armazena registros temporários até verificação

**Colunas novas na tabela `users`:**
- `email_verified` (BOOLEAN)
- `verification_code` (TEXT)
- `verification_code_expires` (TIMESTAMP)

**Opção 1: Automático (recomendado)**
- O sistema detecta e cria automaticamente na primeira execução
- Verifique os logs: `[MIGRATION] ✅ Tabela pending_registrations criada com sucesso!`

**Opção 2: SQL manual (se necessário)**
```sql
-- Colunas na tabela users
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code_expires TIMESTAMP;
ALTER TABLE users ALTER COLUMN is_active SET DEFAULT FALSE;

-- Tabela pending_registrations
CREATE TABLE IF NOT EXISTS pending_registrations (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR,
    name VARCHAR,
    verification_code VARCHAR NOT NULL,
    verification_code_expires TIMESTAMP NOT NULL,
    birth_chart_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pending_registrations_email ON pending_registrations(email);
CREATE INDEX IF NOT EXISTS idx_pending_registrations_expires ON pending_registrations(verification_code_expires);
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
- [ ] Tabela `pending_registrations` criada
- [ ] Colunas de verificação na tabela `users` criadas
- [ ] Foreign key constraint `birth_charts_user_id_fkey` com `ON DELETE CASCADE` (corrigido automaticamente)
- [ ] Build do Docker funcionando
- [ ] Health check endpoint (`/health`) funcionando
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
   - **Nova tabela `PendingRegistration`** para armazenar registros temporários ⭐
   - Endpoint `/register` modificado: **NÃO cria usuário**, apenas `PendingRegistration`
   - Endpoint `/verify-email` modificado: **Cria usuário apenas após validação do código**
   - Endpoint `/resend-verification` para reenviar código
   - Serviço de email configurado com retry automático (STARTTLS + SSL)
   - **Google OAuth**: Cria usuário diretamente (sem verificação) ⭐

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
   - **Email só é salvo no banco após verificação** ⭐

4. **Fluxo de Registro:**
   - Usuário preenche formulário → Cria `PendingRegistration` (não cria `User`)
   - Envia código por email
   - Usuário digita código → Valida e **cria `User` e `BirthChart`**
   - Deleta `PendingRegistration`

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

