# 🔧 Troubleshooting: Deploy no Vercel não atualiza

Guia para resolver quando o redeploy no Vercel não mostra as mudanças.

## 🔍 Verificações Rápidas

### 1. Mudanças foram commitadas e pushadas?

```bash
# Verificar se há mudanças não commitadas
git status

# Se houver mudanças, commitar:
git add .
git commit -m "Descrição das mudanças"
git push origin main
```

**⚠️ IMPORTANTE:** O Vercel só faz deploy do que está no GitHub. Se você fez mudanças localmente mas não commitou, elas não vão aparecer.

### 2. Verificar se o deploy foi bem-sucedido

1. Acesse: https://vercel.com
2. Selecione seu projeto
3. Vá em **Deployments**
4. Verifique o último deploy:
   - ✅ Verde = Sucesso
   - ❌ Vermelho = Erro (clique para ver logs)

### 3. Limpar cache do Vercel

O Vercel pode estar usando cache. Para forçar rebuild:

1. No Vercel, vá em **Deployments**
2. Clique nos **três pontos** do último deploy
3. Selecione **Redeploy**
4. Marque **"Use existing Build Cache"** como **DESMARCADO**
5. Clique em **Redeploy**

### 4. Limpar cache do navegador

O navegador pode estar mostrando versão antiga:

**Chrome/Edge:**
- `Ctrl+Shift+R` (Windows) ou `Cmd+Shift+R` (Mac) = Hard refresh
- Ou: DevTools (F12) → Network → Marque "Disable cache"

**Firefox:**
- `Ctrl+F5` (Windows) ou `Cmd+Shift+R` (Mac)

**Safari:**
- `Cmd+Option+R`

### 5. Verificar variáveis de ambiente

As variáveis de ambiente precisam estar configuradas:

1. No Vercel: **Settings** → **Environment Variables**
2. Verifique se estão configuradas:
   - `VITE_API_URL`
   - `VITE_GOOGLE_CLIENT_ID`
3. Se faltar, adicione e faça **Redeploy**

### 6. Verificar logs do build

1. No Vercel: **Deployments**
2. Clique no deploy
3. Vá em **Build Logs**
4. Procure por erros ou avisos

## 🚨 Problemas Comuns

### Problema: "Build successful mas mudanças não aparecem"

**Causas possíveis:**
- Cache do navegador
- Cache do Vercel
- Mudanças não foram commitadas

**Solução:**
1. Limpar cache do navegador (passo 4)
2. Redeploy sem cache (passo 3)
3. Verificar se mudanças foram commitadas (passo 1)

### Problema: "Build falha"

**Causas possíveis:**
- Erro de sintaxe
- Dependências faltando
- Variáveis de ambiente não configuradas

**Solução:**
1. Verificar logs do build (passo 6)
2. Testar build localmente: `npm run build`
3. Corrigir erros encontrados
4. Fazer commit e push novamente

### Problema: "Variáveis de ambiente não funcionam"

**Causas possíveis:**
- Variáveis não configuradas no Vercel
- Nome da variável incorreto
- Redeploy não foi feito após adicionar variáveis

**Solução:**
1. Verificar variáveis no Vercel (passo 5)
2. Nomes devem começar com `VITE_` para variáveis do frontend
3. Fazer redeploy após adicionar variáveis

### Problema: "Mudanças aparecem localmente mas não no Vercel"

**Causas possíveis:**
- Mudanças não foram commitadas
- Branch errado (Vercel pode estar deployando outra branch)
- Cache

**Solução:**
1. Verificar branch: `git branch`
2. Verificar se mudanças foram commitadas: `git status`
3. Fazer push: `git push origin main`
4. Verificar qual branch o Vercel está usando (Settings → Git)

## ✅ Checklist de Verificação

Antes de reportar problema, verifique:

- [ ] Mudanças foram commitadas (`git status` mostra "nothing to commit")
- [ ] Mudanças foram pushadas (`git log` mostra seus commits)
- [ ] Build local funciona (`npm run build` sem erros)
- [ ] Deploy no Vercel foi bem-sucedido (verde)
- [ ] Cache do navegador foi limpo
- [ ] Variáveis de ambiente estão configuradas
- [ ] Redeploy foi feito após mudanças

## 🔄 Processo Correto de Deploy

1. **Fazer mudanças localmente**
2. **Testar localmente** (`npm run dev`)
3. **Testar build** (`npm run build`)
4. **Commitar mudanças:**
   ```bash
   git add .
   git commit -m "Descrição"
   git push origin main
   ```
5. **Aguardar deploy automático** (ou fazer manual)
6. **Verificar deploy** no Vercel
7. **Testar em produção**

## 🛠️ Comandos Úteis

```bash
# Verificar status do Git
git status

# Ver últimas mudanças commitadas
git log --oneline -5

# Ver diferenças não commitadas
git diff

# Testar build local
npm run build

# Limpar build local
rm -rf build
npm run build
```

## 📞 Ainda não funciona?

Se após todos os passos ainda não funcionar:

1. **Verificar logs do Vercel** - pode ter erro que não está visível
2. **Verificar console do navegador** - pode ter erro JavaScript
3. **Comparar build local vs Vercel:**
   - Build local: `npm run build` → verificar `build/`
   - Comparar com o que o Vercel gerou

4. **Verificar configuração do Vercel:**
   - Settings → General → Build & Development Settings
   - Verificar se está usando `npm run build`
   - Verificar se Output Directory é `build`

## 💡 Dicas

- **Sempre commitar antes de fazer deploy**
- **Sempre testar build local antes de push**
- **Limpar cache do navegador ao testar**
- **Aguardar alguns minutos após deploy** (propagação CDN)
- **Usar modo anônimo/privado** para testar sem cache

