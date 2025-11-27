# 🚀 Deploy do Frontend no Vercel

## 📋 Pré-requisitos

- ✅ Conta no Vercel (https://vercel.com)
- ✅ Repositório no GitHub (já tem: `alexsobralifce/CosmoAstrologia`)
- ✅ Backend rodando no Railway (para obter a URL da API)

---

## 🎯 Passo a Passo

### 1. Obter URL do Backend no Railway

Antes de fazer deploy no Vercel, você precisa da URL do backend:

1. **No Railway Dashboard:**
   - Vá para o serviço do backend
   - Clique em **Settings**
   - Role até **"Generate Domain"** ou veja a URL pública
   - Exemplo: `https://seu-backend.railway.app`

**Anote esta URL!** Você vai precisar dela.

---

### 2. Conectar Repositório no Vercel

1. **Acesse https://vercel.com**

   - Faça login com sua conta GitHub

2. **Criar Novo Projeto:**

   - Clique em **"Add New..."** → **"Project"**
   - Ou vá para https://vercel.com/new

3. **Importar Repositório:**

   - Selecione o repositório: `alexsobralifce/CosmoAstrologia`
   - Se não aparecer, clique em **"Adjust GitHub App Permissions"** e autorize

4. **Configurar Projeto:**
   - **Framework Preset:** Vercel detecta automaticamente (Vite)
   - **Root Directory:** Deixe em branco (a raiz do repositório)
   - **Build Command:** `npm run build` (Vercel detecta automaticamente)
   - **Output Directory:** `build` (conforme `vite.config.ts`)

---

### 3. Configurar Variáveis de Ambiente

**Antes de fazer deploy**, configure as variáveis de ambiente:

1. **Na tela de configuração do projeto**, role até **"Environment Variables"**

2. **Adicione a variável:**

   ```
   Nome: VITE_API_URL
   Valor: https://seu-backend.railway.app
   ```

   ⚠️ **IMPORTANTE:** Substitua `https://seu-backend.railway.app` pela URL real do seu backend no Railway!

3. **Selecione os ambientes:**
   - ✅ Production
   - ✅ Preview
   - ✅ Development

---

### 4. Fazer Deploy

1. **Clique em "Deploy"**

   - O Vercel vai:
     - Instalar dependências (`npm install`)
     - Fazer o build (`npm run build`)
     - Fazer deploy

2. **Aguarde o build completar** (geralmente 1-3 minutos)

3. **Você receberá uma URL:** `https://seu-app.vercel.app`

---

## ⚙️ Configurações Adicionais

### Configurar CORS no Backend

Após obter a URL do Vercel, atualize o CORS no backend:

1. **No Railway:**

   - Vá para Variables do backend
   - Edite `CORS_ORIGINS`:

   ```
   https://seu-app.vercel.app,https://www.seu-dominio.com
   ```

   - Ou se tiver múltiplos ambientes:

   ```
   https://seu-app.vercel.app,https://seu-app-git-main-seu-usuario.vercel.app
   ```

2. **Redeploy do backend** para aplicar as mudanças

---

## 🔍 Verificar se Está Funcionando

### 1. Teste a URL do Vercel

Acesse: `https://seu-app.vercel.app`

Deve carregar o frontend normalmente.

### 2. Verificar Conexão com Backend

Abra o Console do Navegador (F12) e verifique:

- ✅ Não deve ter erros de CORS
- ✅ Requisições para a API devem funcionar
- ✅ Verifique se está usando a URL correta do backend

### 3. Testar Funcionalidades

- ✅ Login/Registro
- ✅ Dashboard
- ✅ Cálculos astrológicos

---

## 🔄 Deploys Automáticos

O Vercel faz deploy automático quando você:

- Faz push para a branch `main` (production)
- Abre um Pull Request (preview)
- Faz push para outras branches (preview)

---

## 📝 Estrutura de Deploy

```
GitHub (main branch)
  ↓
Vercel detecta push
  ↓
Instala dependências (npm install)
  ↓
Build (npm run build)
  ↓
Deploy para https://seu-app.vercel.app
```

---

## 🆘 Troubleshooting

### Problema: Build falha

**Possíveis causas:**

- Dependências não instaladas
- Erros de TypeScript
- Erros de build do Vite

**Solução:**

1. Verifique os logs do build no Vercel
2. Teste localmente: `npm run build`
3. Corrija os erros e faça push novamente

### Problema: Frontend não conecta ao backend

**Possíveis causas:**

- Variável `VITE_API_URL` não configurada
- URL do backend incorreta
- CORS não configurado no backend

**Solução:**

1. Verifique se `VITE_API_URL` está nas Environment Variables
2. Confirme que a URL do backend está correta
3. Verifique CORS no backend (deve incluir a URL do Vercel)

### Problema: Erro 404 em rotas

**Possível causa:**

- Rotas do React Router não configuradas no Vercel

**Solução:** Crie um arquivo `vercel.json` na raiz do projeto:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Problema: Variáveis de ambiente não funcionam

**Causa:**

- Variáveis de ambiente no Vercel precisam ter prefixo `VITE_`
- Build precisa ser refeito após adicionar variáveis

**Solução:**

1. Certifique-se que a variável começa com `VITE_` (ex: `VITE_API_URL`)
2. Faça um novo deploy após adicionar variáveis

---

## 🎨 Domínio Customizado (Opcional)

1. **No Vercel Dashboard:**
   - Vá para Settings → Domains
   - Adicione seu domínio customizado
   - Configure DNS conforme instruções do Vercel

---

## 📋 Checklist Final

- [ ] Conta Vercel criada
- [ ] Repositório conectado ao Vercel
- [ ] URL do backend no Railway obtida
- [ ] Variável `VITE_API_URL` configurada no Vercel
- [ ] CORS configurado no backend (incluindo URL do Vercel)
- [ ] Build completou com sucesso
- [ ] Frontend carrega corretamente
- [ ] Conexão com backend funcionando
- [ ] Login/Registro testado

---

## 🎉 Pronto!

Seu frontend está no ar! 🚀

**URLs:**

- Frontend: `https://seu-app.vercel.app`
- Backend: `https://seu-backend.railway.app`

---

## 💡 Dicas

1. **Preview Deploys:** Cada PR gera uma URL de preview única
2. **Analytics:** Ative Vercel Analytics para monitorar performance
3. **Cache:** O Vercel faz cache automático de assets estáticos
4. **SSL:** HTTPS é automático no Vercel

---

## 📚 Referências

- [Documentação Vercel](https://vercel.com/docs)
- [Vite Deploy Guide](https://vitejs.dev/guide/static-deploy.html#vercel)
