# 🔗 Como Conectar Frontend (Vercel) com Backend (Railway)

## 📋 Pré-requisitos

- ✅ Frontend deployado no Vercel
- ✅ Backend deployado no Railway
- ✅ URL do backend do Railway (ex: `https://seu-backend.railway.app`)

---

## 🎯 Passo 1: Obter URL do Backend no Railway

1. **No Railway Dashboard:**
   - Acesse o serviço do backend
   - Vá para **Settings** → **Networking**
   - Ou veja a URL pública no topo da página
   - Exemplo: `https://cosmoastrologia-production.up.railway.app`

**Anote esta URL!** Você vai precisar dela.

---

## 🎯 Passo 2: Configurar Variável de Ambiente no Vercel

O frontend usa a variável `VITE_API_URL` para se conectar ao backend.

### 2.1. No Vercel Dashboard:

1. **Acesse seu projeto no Vercel:**
   - https://vercel.com
   - Selecione seu projeto

2. **Vá para Settings:**
   - Clique em **Settings** na barra superior
   - No menu lateral, clique em **Environment Variables**

3. **Adicione a variável:**
   - **Key (Nome):** `VITE_API_URL`
   - **Value (Valor):** `https://seu-backend.railway.app`
     - ⚠️ **Substitua** `https://seu-backend.railway.app` pela URL real do seu backend!
   - **Environment:** Selecione todos:
     - ✅ Production
     - ✅ Preview  
     - ✅ Development

4. **Salve:**
   - Clique em **Save** ou **Add**

### 2.2. Exemplo:

```
Nome: VITE_API_URL
Valor: https://cosmoastrologia-production.up.railway.app
Ambientes: Production, Preview, Development
```

⚠️ **IMPORTANTE:** 
- O nome da variável **DEVE** começar com `VITE_` para o Vite poder usá-la
- Não inclua barra final (`/`) na URL
- Use `https://` (não `http://`)

---

## 🎯 Passo 3: Configurar CORS no Backend (Railway)

O backend precisa permitir requisições do frontend do Vercel.

### 3.1. Obter URL do Frontend no Vercel:

1. **No Vercel Dashboard:**
   - Seu projeto → **Deployments**
   - Veja a URL do deploy (ex: `https://cosmo-astrologia.vercel.app`)

### 3.2. Configurar CORS no Railway:

1. **No Railway Dashboard:**
   - Acesse o serviço do backend
   - Vá para **Variables**

2. **Editar CORS_ORIGINS:**
   - Se já existir, clique para editar
   - Se não existir, adicione uma nova variável

3. **Valor:**
   ```
   https://seu-app.vercel.app,https://seu-app-git-main-seu-usuario.vercel.app
   ```
   
   **Exemplo completo:**
   ```
   https://cosmo-astrologia.vercel.app,https://cosmo-astrologia-git-main-alexsobralifce.vercel.app,http://localhost:5173,http://localhost:3000
   ```

   **Formato:** URLs separadas por vírgula, sem espaços extras

4. **Salve** e faça um **redeploy** do backend

---

## 🎯 Passo 4: Fazer Redeploy

### 4.1. Frontend (Vercel):

Após adicionar a variável de ambiente:

1. **Opção A - Automático:**
   - Faça um commit vazio ou altere qualquer arquivo
   - Faça push para o GitHub
   - O Vercel fará deploy automaticamente

2. **Opção B - Manual:**
   - Vá para **Deployments**
   - Clique nos três pontos do último deploy
   - Clique em **Redeploy**

### 4.2. Backend (Railway):

Após atualizar `CORS_ORIGINS`:

1. Vá para **Deployments**
2. Clique em **Redeploy** no último deploy
3. Aguarde o deploy completar

---

## ✅ Verificação

### 1. Teste a Conexão:

1. **Acesse o frontend no Vercel:**
   - Ex: `https://seu-app.vercel.app`

2. **Abra o Console do Navegador (F12):**
   - Vá para a aba **Console**
   - Tente fazer login ou qualquer ação que chame a API

3. **Verifique:**
   - ✅ Não deve aparecer erros de CORS
   - ✅ Requisições devem aparecer no **Network** tab
   - ✅ As requisições devem ir para a URL do Railway

### 2. Verificar no Network Tab:

1. Abra **DevTools** (F12)
2. Vá para a aba **Network**
3. Faça uma ação (login, etc.)
4. Veja as requisições:
   - **URL:** Deve ser `https://seu-backend.railway.app/api/...`
   - **Status:** Deve ser `200` (sucesso) ou outro código válido
   - **CORS:** Não deve ter erro de CORS

### 3. Teste de CORS:

Se você ver este erro no console:
```
Access to fetch at 'https://backend.railway.app' from origin 'https://frontend.vercel.app' 
has been blocked by CORS policy
```

**Significa que:**
- CORS não está configurado corretamente
- A URL do frontend não está em `CORS_ORIGINS`
- Faça redeploy do backend após atualizar

---

## 🔍 Debug

### Problema: Frontend não conecta ao backend

**Verificações:**

1. **Variável de ambiente configurada?**
   - Vercel Dashboard → Settings → Environment Variables
   - Deve ter `VITE_API_URL` configurada
   - Valor deve ser a URL do backend (com `https://`)

2. **Variável foi aplicada?**
   - Faça um redeploy após adicionar variável
   - Variáveis só são aplicadas em novos deploys

3. **URL do backend está correta?**
   - Teste no navegador: `https://seu-backend.railway.app/`
   - Deve retornar: `{"message": "Astrologia API"}`

4. **CORS configurado?**
   - Railway → Variables → `CORS_ORIGINS`
   - Deve incluir a URL do Vercel
   - Faça redeploy do backend

### Problema: Erro 404

**Causa:** URL do backend incorreta ou endpoint não existe

**Solução:**
- Verifique se a URL está correta
- Teste a URL diretamente no navegador
- Verifique os logs do backend no Railway

### Problema: Erro de CORS

**Causa:** Frontend não está na lista de CORS_ORIGINS

**Solução:**
1. Adicione a URL do Vercel em `CORS_ORIGINS` no Railway
2. Inclua todas as variantes:
   - `https://seu-app.vercel.app`
   - `https://seu-app-git-main-usuario.vercel.app` (preview)
3. Faça redeploy do backend

---

## 📋 Checklist Completo

- [ ] URL do backend obtida do Railway
- [ ] Variável `VITE_API_URL` configurada no Vercel
- [ ] URL do frontend obtida do Vercel
- [ ] `CORS_ORIGINS` configurado no Railway (incluindo URL do Vercel)
- [ ] Redeploy do frontend feito (para aplicar variável)
- [ ] Redeploy do backend feito (para aplicar CORS)
- [ ] Teste de conexão realizado
- [ ] Console do navegador verificado (sem erros)
- [ ] Network tab verificado (requisições funcionando)

---

## 🎉 Resultado Final

Após configurar tudo:

✅ **Frontend no Vercel:** `https://seu-app.vercel.app`  
✅ **Backend no Railway:** `https://seu-backend.railway.app`  
✅ **Conectados e funcionando!**

O frontend vai fazer requisições para o backend automaticamente usando a variável `VITE_API_URL`.

---

## 💡 Dica

**Para desenvolvimento local:**
- Crie um arquivo `.env.local` na raiz do projeto:
  ```
  VITE_API_URL=http://localhost:8000
  ```
- O Vite vai usar isso automaticamente
- **NÃO commite** este arquivo (ele já deve estar no `.gitignore`)

---

## 📚 Referências

- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)

