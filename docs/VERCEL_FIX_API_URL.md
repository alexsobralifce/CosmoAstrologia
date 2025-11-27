# 🔧 Fix: Frontend conectando ao localhost em vez do Railway

## 🔴 Problema

O frontend está tentando conectar a:
```
http://localhost:8000
```

Mas deveria conectar a:
```
https://seu-backend.railway.app
```

## ✅ Causa

A variável de ambiente `VITE_API_URL` não está configurada no Vercel, então o frontend está usando o valor padrão (`http://localhost:8000`).

---

## 🎯 Solução: Configurar Variável de Ambiente no Vercel

### Passo 1: Obter URL do Backend

1. **No Railway Dashboard:**
   - Acesse o serviço do backend
   - Vá para **Settings** → **Networking**
   - Ou veja a URL pública no topo da página
   - Exemplo: `https://cosmoastrologia-production.up.railway.app`

**Anote esta URL!**

### Passo 2: Adicionar Variável no Vercel

1. **No Vercel Dashboard:**
   - Acesse https://vercel.com
   - Selecione seu projeto
   - Vá para **Settings** (no topo)
   - No menu lateral, clique em **Environment Variables**

2. **Adicionar Variável:**
   - Clique em **"Add New"**
   - **Key (Nome):** `VITE_API_URL`
   - **Value (Valor):** Cole a URL do backend do Railway
     - Exemplo: `https://cosmoastrologia-production.up.railway.app`
     - ⚠️ **NÃO** inclua barra final (`/`)
     - ⚠️ Use `https://` (não `http://`)
   - **Environment:** Selecione todos:
     - ✅ Production
     - ✅ Preview
     - ✅ Development

3. **Salvar:**
   - Clique em **Save** ou **Add**

### Passo 3: Fazer Redeploy

⚠️ **IMPORTANTE:** Variáveis de ambiente só são aplicadas em novos deploys!

**Opção A - Redeploy Manual:**
1. Vá para **Deployments**
2. Clique nos **três pontos** do último deploy
3. Clique em **Redeploy**
4. Selecione **"Use existing Build Cache"** (opcional)
5. Clique em **Redeploy**

**Opção B - Trigger Automático:**
1. Faça um commit qualquer (pode ser vazio)
2. Faça push para o GitHub
3. O Vercel vai fazer deploy automaticamente

### Passo 4: Verificar

Após o redeploy:

1. **Acesse o frontend:**
   - Ex: `https://seu-app.vercel.app`

2. **Abra o Console do Navegador (F12):**
   - Vá para **Console**
   - Tente fazer cadastro/login
   - Veja as mensagens de log

3. **Verifique as requisições:**
   - Vá para a aba **Network**
   - Faça uma ação (cadastro, login, etc.)
   - Veja a URL das requisições
   - **Deve ser:** `https://seu-backend.railway.app/api/...`
   - **NÃO deve ser:** `http://localhost:8000/...`

---

## 🔍 Debug

### Verificar se a variável está configurada:

1. **No Vercel Dashboard:**
   - Settings → Environment Variables
   - Deve aparecer `VITE_API_URL` na lista
   - Valor deve ser a URL do Railway

### Verificar se foi aplicada:

1. **Após fazer redeploy:**
   - Abra o Console do navegador
   - Você verá logs como:
     ```
     [API] Fazendo requisição para: https://seu-backend.railway.app/api/...
     ```
   - Se ainda aparecer `localhost`, a variável não foi aplicada

### Se ainda não funcionar:

1. **Verifique o nome da variável:**
   - Deve ser exatamente: `VITE_API_URL`
   - Com `VITE_` no início (obrigatório para Vite)

2. **Verifique o formato da URL:**
   - ✅ Correto: `https://seu-backend.railway.app`
   - ❌ Errado: `https://seu-backend.railway.app/` (com barra)
   - ❌ Errado: `http://seu-backend.railway.app` (sem SSL)

3. **Verifique se fez redeploy:**
   - Variáveis só são aplicadas em novos deploys
   - Verifique o timestamp do deploy (deve ser após adicionar a variável)

---

## 📋 Checklist

- [ ] URL do backend obtida do Railway
- [ ] Variável `VITE_API_URL` adicionada no Vercel
- [ ] Valor da variável está correto (URL completa do Railway)
- [ ] Variável selecionada para todos os ambientes (Production, Preview, Development)
- [ ] Redeploy do frontend feito
- [ ] Testado e funcionando

---

## 🎉 Resultado Esperado

Após configurar corretamente:

✅ Frontend faz requisições para: `https://seu-backend.railway.app`  
❌ NÃO faz mais para: `http://localhost:8000`

As requisições devem funcionar e você conseguirá:
- ✅ Cadastrar usuários
- ✅ Fazer login
- ✅ Usar todas as funcionalidades do app

---

## 💡 Dica

**Para desenvolvimento local:**
- Crie um arquivo `.env.local` na raiz:
  ```
  VITE_API_URL=http://localhost:8000
  ```
- Isso só funciona localmente
- No Vercel, use a variável de ambiente configurada

---

## 🆘 Se Ainda Não Funcionar

1. **Limpe o cache do navegador**
2. **Teste em aba anônima**
3. **Verifique os logs do build no Vercel** (pode ter erros)
4. **Verifique se o backend está rodando** (teste a URL diretamente no navegador)

