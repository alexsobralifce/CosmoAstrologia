# 📚 Índice de Documentos de Ajuda - Ordenados por Ordem de Uso

Documentos organizados na ordem que devem ser consultados durante o setup e deploy.

## 🚀 Setup e Deploy (Ordem de Execução)

### 01. **01_SETUP_VERCEL_PROJETO_NOVO.md** ⭐ COMECE AQUI
**Quando usar:** Ao adicionar projeto novo no Vercel  
**Conteúdo:**
- Passo a passo completo para conectar repositório
- Configuração de Build Settings
- Variáveis de ambiente necessárias
- Checklist completo

**📍 Use quando:** Você deletou o projeto e vai adicionar de novo

---

### 02. **GOOGLE_OAUTH_SETUP.md**
**Quando usar:** Primeira configuração do Google OAuth  
**Conteúdo:**
- Criar projeto no Google Cloud Console
- Configurar OAuth Consent Screen
- Criar credenciais OAuth 2.0
- Configurar variáveis de ambiente

**📍 Use quando:** Configurando Google OAuth pela primeira vez

---

### 03. **GOOGLE_OAUTH_VERCEL_CONFIG.md** ⚡ RÁPIDO
**Quando usar:** Configurar Google OAuth especificamente para Vercel  
**Conteúdo:**
- O que adicionar no Google Cloud Console
- URLs para adicionar (Authorized JavaScript origins)
- Configuração no Vercel
- Troubleshooting rápido

**📍 Use quando:** Já tem projeto no Vercel e precisa configurar OAuth

---

### 04. **GOOGLE_OAUTH_VERCEL.md**
**Quando usar:** Guia completo de Google OAuth para Vercel  
**Conteúdo:**
- Guia detalhado passo a passo
- Configuração completa
- Verificações e testes
- Problemas comuns e soluções

**📍 Use quando:** Precisa de guia completo e detalhado

---

### 05. **DEPLOY.md**
**Quando usar:** Guia geral de deploy (frontend + backend)  
**Conteúdo:**
- Arquitetura do sistema
- Deploy frontend (Vercel)
- Deploy backend (Railway)
- Configuração completa
- Workflow de desenvolvimento

**📍 Use quando:** Precisa entender todo o processo de deploy

---

### 06. **DEPLOY_CHECKLIST.md**
**Quando usar:** Antes de fazer deploy em produção  
**Conteúdo:**
- Checklist de segurança
- Verificações de configuração
- Testes necessários
- Pós-deploy

**📍 Use quando:** Antes de fazer deploy para produção

---

### 07. **VERCEL_DEPLOY_FRONTEND.md**
**Quando usar:** Deploy específico do frontend no Vercel  
**Conteúdo:**
- Configuração detalhada do Vercel
- Build settings
- Variáveis de ambiente
- Domínios customizados

**📍 Use quando:** Focando apenas no deploy do frontend

---

### 08. **VERCEL_DEPLOY_TROUBLESHOOTING.md**
**Quando usar:** Problemas com deploy no Vercel  
**Conteúdo:**
- Verificações rápidas
- Problemas comuns
- Soluções passo a passo
- Comandos úteis

**📍 Use quando:** Deploy não está funcionando ou não atualiza

---

### 09. **VERCEL_DEPLOY_QUICK_FIX.md** ⚡ RÁPIDO
**Quando usar:** Solução rápida para deploy não atualizar  
**Conteúdo:**
- Solução em 5 minutos
- Checklist essencial
- Comandos rápidos

**📍 Use quando:** Precisa resolver rápido

---

### 10. **VERCEL_REMOVER_RECONECTAR.md**
**Quando usar:** Remover e reconectar projeto no Vercel  
**Conteúdo:**
- Quando remover
- Como remover
- Como reconectar
- O que é perdido/mantido

**📍 Use quando:** Quer começar do zero no Vercel

---

### 11. **VERIFICACAO_GITHUB.md**
**Quando usar:** Verificar se implementações estão no GitHub  
**Conteúdo:**
- Status do repositório
- Implementações confirmadas
- Verificação detalhada
- Próximos passos

**📍 Use quando:** Quer confirmar que tudo está no GitHub

---

### 12. **VERCEL_ERRO_BACKEND_CONNECTION.md** ⚠️ ERRO COMUM
**Quando usar:** Erro "Não foi possível conectar ao backend" no Vercel  
**Conteúdo:**
- Causa do problema
- Como configurar VITE_API_URL
- Verificações necessárias
- Checklist completo

**📍 Use quando:** Frontend no Vercel não consegue conectar ao backend

---

### 13. **VERCEL_ERRO_405_REGISTER.md** ⚠️ ERRO COMUM
**Quando usar:** Erro 405 "Method Not Allowed" ao cadastrar no Vercel  
**Conteúdo:**
- Causa do problema (URL incorreta, CORS, roteamento)
- Como verificar e corrigir VITE_API_URL
- Verificação de CORS no Railway
- Teste direto do endpoint
- Checklist completo

**📍 Use quando:** Erro 405 ao tentar cadastrar usuário no Vercel

---

## 📋 Fluxo Recomendado

### Para Setup Inicial Completo:

1. **01_SETUP_VERCEL_PROJETO_NOVO.md** - Adicionar projeto no Vercel
2. **GOOGLE_OAUTH_SETUP.md** - Configurar Google OAuth
3. **GOOGLE_OAUTH_VERCEL_CONFIG.md** - Configurar URLs no Google Console
4. **DEPLOY_CHECKLIST.md** - Verificar antes de produção

### Para Problemas com Deploy:

1. **VERCEL_DEPLOY_QUICK_FIX.md** - Solução rápida (5 min)
2. Se não resolver: **VERCEL_DEPLOY_TROUBLESHOOTING.md** - Guia completo
3. Se ainda não resolver: **VERCEL_REMOVER_RECONECTAR.md** - Começar do zero

### Para Verificação:

1. **VERIFICACAO_GITHUB.md** - Verificar se código está no GitHub
2. **DEPLOY_CHECKLIST.md** - Checklist completo

---

## 🎯 Documentos por Situação

### 🆕 Primeira Vez
- 01_SETUP_VERCEL_PROJETO_NOVO.md
- GOOGLE_OAUTH_SETUP.md
- DEPLOY.md

### 🔧 Configuração
- GOOGLE_OAUTH_VERCEL_CONFIG.md
- DEPLOY_CHECKLIST.md
- VERCEL_DEPLOY_FRONTEND.md

### 🐛 Problemas
- VERCEL_DEPLOY_QUICK_FIX.md
- VERCEL_DEPLOY_TROUBLESHOOTING.md
- VERCEL_REMOVER_RECONECTAR.md

### ✅ Verificação
- VERIFICACAO_GITHUB.md
- DEPLOY_CHECKLIST.md

---

## 📊 Resumo Rápido

| Situação | Documento | Tempo |
|----------|-----------|-------|
| Adicionar projeto novo | 01_SETUP_VERCEL_PROJETO_NOVO.md | 10 min |
| Configurar Google OAuth | GOOGLE_OAUTH_VERCEL_CONFIG.md | 5 min |
| Deploy não atualiza | VERCEL_DEPLOY_QUICK_FIX.md | 5 min |
| Problemas gerais | VERCEL_DEPLOY_TROUBLESHOOTING.md | 15 min |
| Verificar GitHub | VERIFICACAO_GITHUB.md | 5 min |

---

## 🔗 Links Úteis

- **Vercel Dashboard:** https://vercel.com
- **Google Cloud Console:** https://console.cloud.google.com
- **Repositório GitHub:** https://github.com/alexsobralifce/CosmoAstrologia

---

**Última atualização:** Novembro 2024
