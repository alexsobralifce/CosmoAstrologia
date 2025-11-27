# 🚀 Como Criar o Serviço Backend no Railway

## 📍 Situação

Você está no projeto "CosmoAstrologia" no Railway, mas ainda não tem um serviço backend criado. Vamos criar agora!

---

## ✅ Passo a Passo para Criar o Backend

### 1. Criar Novo Serviço

Na tela atual do Railway (aba "Deployments"):

1. **Procure o botão "New" ou "+"**
   - Geralmente está no canto superior direito ou no meio da tela
   - Pode aparecer como "New Service", "Add Service" ou um ícone de "+"

2. **Selecione a opção "GitHub Repo" ou "Deploy from GitHub"**
   - Isso vai conectar o repositório do GitHub ao Railway

### 2. Conectar o Repositório

1. **Autorize o Railway no GitHub** (se necessário)
   - Você pode precisar autorizar o Railway a acessar seus repositórios

2. **Selecione o repositório correto**
   - Procure por "Astrologia2" ou o nome do seu repositório
   - Se não encontrar, verifique se o repositório está no GitHub e é acessível

### 3. Configurar o Serviço Backend

Depois de conectar o repositório, você verá opções de configuração:

1. **Nome do Serviço**
   - Nomeie como: `backend` ou `api-backend`

2. **Root Directory** ⚠️ IMPORTANTE!
   - Configure como: `backend`
   - Isso faz o Railway procurar arquivos na pasta `backend/`

3. **Build Command**
   - Deixe em branco (o Dockerfile vai cuidar disso)

4. **Start Command**
   - Deixe em branco (o Dockerfile já tem o CMD configurado)

5. **Framework Preset**
   - Selecione "Docker" ou "Other"

### 4. Detectar Dockerfile

O Railway deve detectar automaticamente o `Dockerfile` em `backend/Dockerfile` se o Root Directory estiver configurado como `backend`.

---

## 🔧 Configuração Alternativa (se não aparecer Root Directory)

Se você não ver a opção "Root Directory" na criação:

1. **Crie o serviço normalmente**
2. **Vá para Settings** (aba ao lado de "Deployments")
3. **Configure Root Directory como `backend`**
4. **Salve**
5. **Faça deploy novamente**

---

## 📝 Após Criar o Serviço

### 1. Adicionar Variáveis de Ambiente

Vá para a aba **"Variables"** e adicione:

```
SECRET_KEY = [sua chave secreta]
GROQ_API_KEY = [sua chave Groq]
CORS_ORIGINS = https://seu-frontend.vercel.app
```

### 2. Conectar ao PostgreSQL (se já tiver)

Se você já tem um serviço PostgreSQL:
- Vá para o serviço PostgreSQL
- Clique em "Connect" ou "Generate Variable"
- Selecione o serviço backend
- A variável `DATABASE_URL` será adicionada automaticamente

### 3. Verificar Deploy

Vá para a aba **"Deployments"** e veja se o build está funcionando.

---

## 🎯 Estrutura Esperada no Railway

Depois de criar, você deve ter:

```
CosmoAstrologia (Projeto)
├── backend (Serviço) ← Você precisa criar este
│   ├── Root Directory: backend
│   ├── Dockerfile detectado
│   └── Variáveis de ambiente configuradas
└── PostgreSQL (Serviço) ← Se você já criou
```

---

## 🆘 Problemas Comuns

### Não encontro o botão "New"

**Solução:** 
- Procure por um ícone de "+" ou "Add"
- Ou clique em "New Service" no menu lateral

### Não vejo opção de Root Directory

**Solução:**
- Crie o serviço primeiro
- Depois vá para Settings e configure o Root Directory

### Railway não detecta o Dockerfile

**Solução:**
- Verifique se o Root Directory está como `backend`
- Confirme que o arquivo `backend/Dockerfile` existe no repositório
- Faça commit e push se ainda não fez

---

## 📚 Próximos Passos

Após criar o serviço backend:

1. ✅ Configure Root Directory como `backend`
2. ✅ Adicione variáveis de ambiente
3. ✅ Conecte ao PostgreSQL (se tiver)
4. ✅ Aguarde o build completar
5. ✅ Verifique os logs para confirmar que está funcionando

---

## 💡 Dica

Se você já tem o PostgreSQL rodando, após criar o backend:
- Vá para o serviço PostgreSQL
- Clique em "Variables" ou "Connect"
- Conecte ao serviço backend
- A `DATABASE_URL` será compartilhada automaticamente

