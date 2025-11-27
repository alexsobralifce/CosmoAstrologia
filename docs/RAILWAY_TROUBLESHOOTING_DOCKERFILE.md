# 🔧 Troubleshooting: Railway não encontra Dockerfile

## 🔴 Problema

Railway continua mostrando erro:

```
Dockerfile `Dockerfile` does not exist
```

Mesmo com Root Directory configurado como `backend`.

---

## ✅ Verificações Necessárias

### 1. Verificar Branch Conectada

No Railway:

- Settings → Source → "Branch connected to production"
- Deve estar na mesma branch que você está usando (provavelmente `main`)

**Ação:** Se estiver em outra branch, altere para `main` ou para a branch onde estão os arquivos.

### 2. Verificar se Arquivos Estão no Repositório Remoto

Os arquivos podem estar apenas localmente. Verifique:

```bash
# Ver se o Dockerfile está no repositório
git show HEAD:backend/Dockerfile
```

Se der erro, o arquivo não está no repositório.

**Solução:** Faça commit e push:

```bash
git add backend/Dockerfile backend/.dockerignore backend/railway.json
git commit -m "Add Docker configuration for Railway"
git push origin main
```

### 3. Verificar Caminho do Root Directory

No Railway Settings:

- **Root Directory** deve ser exatamente: `backend`
- **NÃO** deve ser: `/backend` ou `./backend` ou `backend/`
- Apenas: `backend`

### 4. Verificar Se o Railway Está Vendo o Commit Mais Recente

No Railway:

- Deployments → Veja o commit mais recente
- Confirme que é o mesmo commit que tem o Dockerfile

**Se não for:**

- Force um novo deploy
- Ou faça um novo commit/push

### 5. Verificar Estrutura do Repositório

O Railway espera encontrar:

```
backend/
├── Dockerfile       ← Deve estar aqui
├── .dockerignore
├── requirements.txt
├── railway.json
└── app/
```

---

## 🔍 Diagnóstico Passo a Passo

### Passo 1: Confirmar que Dockerfile está no repositório

Execute localmente:

```bash
cd /Users/alexandrerocha/Astrologia2
git show HEAD:backend/Dockerfile
```

**Se funcionar:** O arquivo está no repositório ✅  
**Se der erro:** O arquivo não está no repositório ❌

### Passo 2: Verificar branch no Railway

No Railway Dashboard:

1. Vá para Settings
2. Veja "Branch connected to production"
3. Deve ser `main` (ou a branch que você está usando)

### Passo 3: Forçar Novo Deploy

No Railway:

1. Vá para Deployments
2. Clique em "Redeploy" no deploy mais recente
3. Ou faça um commit vazio e push:
   ```bash
   git commit --allow-empty -m "Trigger Railway deploy"
   git push origin main
   ```

---

## 🆘 Soluções Comuns

### Solução 1: Arquivos não foram pushados

**Sintoma:** Arquivos existem localmente mas não no repositório remoto

**Ação:**

```bash
git add backend/Dockerfile backend/.dockerignore backend/railway.json backend/requirements.txt
git commit -m "Add Railway deployment files"
git push origin main
```

### Solução 2: Branch diferente

**Sintoma:** Railway está conectado a uma branch diferente de `main`

**Ação:**

1. No Railway Settings, mude a branch para `main`
2. Ou faça merge da branch atual para `main`

### Solução 3: Root Directory com caminho errado

**Sintoma:** Root Directory configurado incorretamente

**Ação:**

1. Vá para Settings no Railway
2. Root Directory deve ser apenas: `backend`
3. Remova qualquer barra (`/`) ou ponto (`.`)

### Solução 4: Deletar e Recriar Serviço

**Se nada funcionar:**

1. Delete o serviço no Railway
2. Crie um novo serviço
3. Conecte ao mesmo repositório
4. Configure Root Directory como `backend` desde o início
5. Faça deploy

---

## 📋 Checklist de Verificação

- [ ] Dockerfile existe em `backend/Dockerfile` localmente
- [ ] Dockerfile está commitado no repositório (`git show HEAD:backend/Dockerfile` funciona)
- [ ] Mudanças foram pushadas para o repositório remoto
- [ ] Railway está conectado à branch correta (`main`)
- [ ] Root Directory está configurado como `backend` (sem barras)
- [ ] Fez redeploy após configurar Root Directory

---

## 🎯 Teste Rápido

Para testar se tudo está correto:

1. **Confirme que o arquivo está no repositório:**

   ```bash
   git show HEAD:backend/Dockerfile
   ```

2. **Veja o conteúdo do Dockerfile no repositório:**

   ```bash
   git show HEAD:backend/Dockerfile | head -10
   ```

3. **Se ambos funcionarem:** Os arquivos estão no repositório! ✅

4. **Se der erro:** Faça commit e push dos arquivos

---

## 💡 Dica Final

O Railway pode levar alguns minutos para detectar mudanças. Após:

- Configurar Root Directory
- Fazer push de novos arquivos
- Alterar branch

Aguarde alguns minutos ou force um redeploy manualmente.
