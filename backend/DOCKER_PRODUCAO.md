# 🐳 Containers Atualizados para Produção

## ✅ Atualizações Realizadas

### 1. **Dockerfile** (`backend/Dockerfile`)

#### Melhorias:
- ✅ **Health check endpoint** adicionado
- ✅ **Migrações automáticas** incluídas (diretório `migrations/`)
- ✅ **Multi-stage build** otimizado para produção
- ✅ **Dependências instaladas em batches** para evitar timeout
- ✅ **Runtime otimizado** (apenas dependências necessárias)

#### Health Check:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; import json; r = urllib.request.urlopen('http://localhost:${PORT:-8000}/health', timeout=5); data = json.loads(r.read()); exit(0 if data.get('status') == 'healthy' else 1)" || exit 1
```

### 2. **Health Check Endpoint** (`/health`)

Novo endpoint adicionado em `backend/app/main.py`:

```python
@app.get("/health")
def health_check():
    """Health check endpoint para monitoramento e Docker health checks"""
    try:
        # Verificar conexão com banco de dados
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "service": "astrologia-api"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "service": "astrologia-api"
            }
        )
```

**Benefícios:**
- ✅ Monitoramento de saúde do container
- ✅ Verificação automática de conexão com banco
- ✅ Integração com Railway/Vercel health checks

### 3. **Docker Compose** (`docker-compose.yml`)

#### Variáveis de Ambiente Adicionadas:
- ✅ `SMTP_HOST` - Servidor SMTP
- ✅ `SMTP_PORT` - Porta SMTP (padrão: 587)
- ✅ `SMTP_USERNAME` - Usuário SMTP
- ✅ `SMTP_PASSWORD` - Senha SMTP
- ✅ `EMAIL_FROM` - Email remetente

#### Health Check Configurado:
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; import json; r = urllib.request.urlopen('http://localhost:8000/health', timeout=5); data = json.loads(r.read()); exit(0 if data.get('status') == 'healthy' else 1)"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## 🚀 Deploy no Railway

### Configuração Necessária:

1. **Root Directory:** `backend` (já configurado)

2. **Variáveis de Ambiente Obrigatórias:**
   ```env
   SECRET_KEY=<gerar-chave-segura>
   GROQ_API_KEY=<sua-chave-groq>
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=<seu-email>
   SMTP_PASSWORD=<senha-de-app>
   EMAIL_FROM=noreply@cosmoastral.com.br
   ```

3. **Variáveis Recomendadas:**
   ```env
   DATABASE_URL=<postgresql-url>  # Automático se usar PostgreSQL no Railway
   CORS_ORIGINS=https://seu-frontend.vercel.app
   GOOGLE_CLIENT_ID=<seu-client-id>
   GOOGLE_CLIENT_SECRET=<seu-client-secret>
   ```

### Build e Deploy:

O Railway detectará automaticamente o `Dockerfile` e fará o build:

1. **Build Stage:**
   - Instala dependências em batches
   - Compila extensões (kerykeion, etc)
   - Otimiza para produção

2. **Runtime Stage:**
   - Imagem slim (menor tamanho)
   - Apenas runtime dependencies
   - Health check configurado

3. **Migrações Automáticas:**
   - Tabelas criadas automaticamente
   - Colunas de verificação adicionadas
   - Foreign key constraints corrigidas

---

## ✅ Verificação Pós-Deploy

### 1. Verificar Health Check:

```bash
curl https://seu-backend.railway.app/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "database": "connected",
  "service": "astrologia-api"
}
```

### 2. Verificar Logs:

No Railway, verifique os logs para:
- ✅ `[MIGRATION] ✅ Tabela pending_registrations criada com sucesso!`
- ✅ `[MIGRATION] ✅ Foreign key constraint corrigida com CASCADE!`
- ✅ `INFO:     Uvicorn running on http://0.0.0.0:8000`
- ✅ `[RAG] Índice carregado: X documentos`

### 3. Testar Endpoints:

```bash
# Root endpoint
curl https://seu-backend.railway.app/

# Health check
curl https://seu-backend.railway.app/health

# API endpoint
curl https://seu-backend.railway.app/api/auth/me
```

---

## 📋 Checklist de Deploy

- [ ] Dockerfile atualizado com health check
- [ ] Health check endpoint implementado
- [ ] Variáveis SMTP configuradas no Railway
- [ ] Variáveis de ambiente obrigatórias configuradas
- [ ] Root Directory configurado como `backend`
- [ ] Build bem-sucedido no Railway
- [ ] Health check retornando `healthy`
- [ ] Migrações executadas automaticamente
- [ ] Logs sem erros críticos
- [ ] Endpoints respondendo corretamente

---

## 🔧 Troubleshooting

### Health Check Falhando:

1. **Verificar logs do Railway:**
   - Erro de conexão com banco?
   - Erro ao iniciar servidor?

2. **Verificar variáveis de ambiente:**
   - `DATABASE_URL` está configurada?
   - `SECRET_KEY` está configurada?

3. **Verificar porta:**
   - Railway define `PORT` automaticamente
   - Health check usa `${PORT:-8000}`

### Build Falhando:

1. **Timeout em dependências:**
   - Dependências instaladas em batches
   - Timeout aumentado para ML dependencies (600s)

2. **Erro de compilação:**
   - Build dependencies incluídas (gcc, g++, swig)
   - Runtime dependencies mínimas

---

## 📚 Referências

- [Railway Docker Documentation](https://docs.railway.app/deploy/dockerfiles)
- [Docker Health Checks](https://docs.docker.com/engine/reference/builder/#healthcheck)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

**Status:** ✅ Containers atualizados e prontos para produção

