# ❌ Erro: Dockerfile não encontrado no Railway

## 🔴 Problema

```
Build › Build image
Dockerfile `Dockerfile` does not exist
```

O Railway está procurando o `Dockerfile` na **raiz do repositório**, mas ele está em `backend/Dockerfile`.

---

## ✅ Solução: Configurar Root Directory

Você precisa dizer ao Railway onde procurar os arquivos do backend.

### 📍 Passo a Passo no Railway Dashboard

1. **Acesse seu projeto no Railway**

   - Vá para https://railway.app
   - Selecione seu projeto

2. **Selecione o serviço Backend**

   - Clique no serviço do backend (ou crie um novo se necessário)

3. **Vá para Settings (Configurações)**

   - Clique na aba **"Settings"** no menu lateral ou superior

4. **Configure o Root Directory**

   - Role até encontrar **"Root Directory"**
   - No campo, digite: `backend`
   - Clique em **"Save"** ou **"Update"**

5. **Faça um novo deploy**
   - Vá para a aba **"Deployments"**
   - Clique em **"Redeploy"** ou faça um novo commit/push

---

## 🖼️ Visualização

**Antes (errado):**

```
Railway procura em: /
├── package.json  ← Encontrou isso primeiro
├── src/
└── backend/
    └── Dockerfile  ← Não procura aqui!
```

**Depois (correto):**

```
Root Directory: backend
Railway procura em: backend/
├── Dockerfile  ← Encontra aqui! ✅
├── requirements.txt
├── app/
└── ...
```

---

## 🔍 Verificando se Funcionou

Após configurar o Root Directory, quando você fizer deploy, deve ver nos logs:

```
Building Docker image...
Step 1/8 : FROM python:3.11-slim
```

**NÃO** deve aparecer:

```
Dockerfile `Dockerfile` does not exist
```

---

## 🆘 Alternativas (se não funcionar)

### Opção 1: Verificar se o Root Directory foi salvo

1. Vá para Settings do serviço Backend
2. Confirme que **"Root Directory"** mostra `backend`
3. Se estiver vazio ou com `/`, digite `backend` novamente

### Opção 2: Verificar arquivo railway.json

O arquivo `backend/railway.json` já está configurado corretamente, mas o Railway precisa do Root Directory configurado no dashboard também.

### Opção 3: Deletar e recriar o serviço

Se nada funcionar:

1. Delete o serviço Backend no Railway
2. Crie um novo serviço
3. **Na hora de criar**, configure o Root Directory como `backend`
4. Conecte ao repositório novamente

---

## 📝 Checklist

- [ ] Acessei o Railway Dashboard
- [ ] Entrei no serviço Backend
- [ ] Fui para Settings
- [ ] Configurei Root Directory como `backend`
- [ ] Salvei as alterações
- [ ] Fiz um novo deploy
- [ ] O build agora encontra o Dockerfile

---

## 🎯 Resultado Esperado

Após configurar corretamente:

- ✅ Railway encontra `backend/Dockerfile`
- ✅ Build inicia com sucesso
- ✅ Imagem Docker é criada
- ✅ Backend inicia corretamente

---

## 📚 Referências

- [Railway Root Directory Documentation](https://docs.railway.app/develop/variables#root-directory)
- [Railway Dockerfile Guide](https://docs.railway.app/deploy/dockerfiles)
