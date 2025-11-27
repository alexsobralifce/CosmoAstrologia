# 🚂 Configuração do Railway - Backend

## ⚠️ Problema: Railway rodando Caddy em vez do Backend Python

Se você vê logs do Caddy em vez do seu backend Python, o Railway está detectando o projeto errado. Isso acontece porque o Railway pode estar olhando para a raiz do repositório (que tem `package.json` do frontend) em vez da pasta `backend/`.

---

## ✅ Solução: Configurar o Root Directory

### Opção 1: Configurar no Painel do Railway (Recomendado)

1. Acesse seu projeto no Railway
2. Clique no serviço do **backend**
3. Vá na aba **"Settings"** (Configurações)
4. Role até **"Root Directory"** (Diretório Raiz)
5. Defina como: `backend`
6. Salve as alterações
7. Faça um novo deploy

### Opção 2: Usar Arquivo de Configuração

Já foi criado o arquivo `backend/railway.json` que configura o Railway para usar Docker.

---

## 🔧 Verificando a Configuração

Após configurar, você deve ver nos logs:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**NÃO** deve ver logs do Caddy como:
```
[inf]  Starting Container
[inf]  server running
```

---

## 📁 Estrutura Esperada

O Railway deve estar configurado para olhar para:
```
backend/
├── Dockerfile          ← Railway precisa encontrar isso
├── .dockerignore
├── requirements.txt
├── app/
├── docs/
└── rag_index.pkl
```

---

## 🛠️ Passos Completos de Configuração

### 1. No Railway Dashboard:

1. Vá para **Seu Projeto** → **Backend Service**
2. **Settings** → **Root Directory**: `backend`
3. **Variables** → Adicione as variáveis de ambiente (veja `RAILWAY_VARIAVEIS_AMBIENTE.md`)
4. Clique em **"Redeploy"** ou faça um novo commit

### 2. Verificar o Deploy:

1. Vá para a aba **"Deployments"**
2. Clique no deploy mais recente
3. Veja os **Logs** - deve aparecer logs do Python/FastAPI, não do Caddy

### 3. Testar o Endpoint:

```bash
curl https://seu-backend.railway.app/
```

Deve retornar:
```json
{"message": "Astrologia API"}
```

---

## 🆘 Troubleshooting

### Problema: Ainda vendo logs do Caddy

**Solução:**
1. Verifique se o **Root Directory** está configurado como `backend`
2. Verifique se o `Dockerfile` existe em `backend/Dockerfile`
3. Force um novo deploy deletando e recriando o serviço

### Problema: Erro "Dockerfile not found"

**Solução:**
1. Certifique-se de que o `Dockerfile` está commitado no repositório
2. Verifique se o Root Directory está correto
3. Veja se o `.dockerignore` não está excluindo o Dockerfile (ele não deve)

### Problema: Backend não inicia

**Solução:**
1. Verifique os logs completos no Railway
2. Certifique-se de que as variáveis de ambiente estão configuradas
3. Verifique se o `PORT` está sendo usado corretamente (o Railway define automaticamente)

---

## 📝 Checklist de Deploy

- [ ] Root Directory configurado como `backend`
- [ ] `Dockerfile` existe em `backend/Dockerfile`
- [ ] Variável `SECRET_KEY` configurada
- [ ] Variável `GROQ_API_KEY` configurada
- [ ] Variável `CORS_ORIGINS` configurada (com URL do frontend)
- [ ] `DATABASE_URL` configurado (se usar Postgres)
- [ ] Logs mostram Python/FastAPI, não Caddy
- [ ] Endpoint `/` retorna `{"message": "Astrologia API"}`

---

## 🔗 Referências

- [Railway Root Directory](https://docs.railway.app/develop/variables#root-directory)
- [Railway Dockerfile Guide](https://docs.railway.app/deploy/dockerfiles)

