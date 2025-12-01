# 🔧 Solução: Docker Build Timeout no Railway

## 🔴 Problema

O build do Docker está dando timeout durante a instalação de dependências Python, especialmente nas etapas:
- `RUN apt-get update && apt-get install...` (build-essential)
- `RUN pip install -r requirements.txt` (dependências Python)

## ✅ Soluções Implementadas

### 1. Dockerfile Otimizado

O `Dockerfile` foi otimizado com:

#### Melhorias de Cache
- ✅ Dependências copiadas primeiro (melhor cache de layers)
- ✅ Upgrade de pip/setuptools/wheel antes de instalar dependências
- ✅ Instalação em duas etapas: dependências core primeiro, ML depois

#### Timeouts e Retries
- ✅ `--timeout=600` (10 minutos) para cada pacote
- ✅ `--retries=5` para tentar novamente em caso de falha
- ✅ Fallback: se ML dependencies falharem, continua o build

#### Otimizações de Build
- ✅ Multi-stage build (builder + runtime)
- ✅ Apenas runtime dependencies na imagem final
- ✅ `.dockerignore` otimizado para excluir arquivos desnecessários

### 2. Dockerfile Alternativo

Criado `Dockerfile.optimized` como alternativa caso o principal ainda dê timeout:
- Instala todas as dependências de uma vez
- Timeout estendido para 600 segundos
- Mais simples, mas pode ser mais lento

## 🚀 Como Usar

### Opção 1: Dockerfile Principal (Recomendado)

O `Dockerfile` atual já está otimizado. Se ainda der timeout:

1. Verifique se o Railway está usando o Dockerfile correto
2. Aumente o timeout do build no Railway (se possível)
3. Use o `Dockerfile.optimized` como alternativa

### Opção 2: Dockerfile Otimizado Alternativo

Se o build principal ainda falhar:

```bash
# No Railway, configure para usar Dockerfile.optimized
# Ou renomeie temporariamente:
mv Dockerfile Dockerfile.original
mv Dockerfile.optimized Dockerfile
```

### Opção 3: Reduzir Dependências (Último Recurso)

Se ainda assim der timeout, você pode criar um `requirements-prod.txt` com apenas dependências essenciais:

```txt
# requirements-prod.txt (apenas dependências críticas)
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
pydantic==2.10.0
pydantic-settings==2.6.0
pydantic[email]==2.10.0
python-jose[cryptography]==3.3.0
bcrypt==4.2.0
python-multipart==0.0.12
ephem==4.1.5
kerykeion>=5.3.0
pytz>=2024.1
timezonefinder>=6.4.1
email-validator==2.2.0
psycopg2-binary>=2.9.0
PyPDF2==3.0.1
numpy<2.0
groq>=0.4.1
google-auth>=2.0.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.2.0
# Remover temporariamente se necessário:
# fastembed>=0.2.0
# llama-index>=0.13.6
# llama-index-embeddings-huggingface>=0.1.0
```

E modificar o Dockerfile para usar `requirements-prod.txt`.

## 📋 Verificações no Railway

### 1. Configurações de Build

No Railway Dashboard:
- **Root Directory:** `backend`
- **Dockerfile Path:** `backend/Dockerfile` (ou deixar vazio se na raiz do backend)
- **Build Command:** (deixar vazio, Railway detecta Dockerfile automaticamente)

### 2. Timeout do Build

O Railway geralmente tem timeout de:
- **Plano Free:** ~10-15 minutos
- **Plano Pro:** ~20-30 minutos

Se o build demorar mais que isso, considere:
- Usar plano pago (mais tempo de build)
- Reduzir dependências
- Usar imagens pré-buildadas

### 3. Logs do Build

Verifique os logs do Railway para identificar onde está travando:
- Se travar em `apt-get update`: problema de rede/conexão
- Se travar em `pip install`: dependência específica demorando
- Se travar em `COPY . .`: muitos arquivos sendo copiados

## 🔍 Troubleshooting

### Build trava em "Installing build dependencies"

**Solução:** Já otimizado no Dockerfile. Se persistir:
- Verifique conexão de rede do Railway
- Tente usar `Dockerfile.optimized`

### Build trava em "Installing Python packages"

**Solução:** 
1. Verifique qual pacote está demorando (veja logs)
2. Se for `llama-index` ou `fastembed`, considere instalar depois
3. Use `Dockerfile.optimized` que tem timeout maior

### Build completa mas aplicação não inicia

**Solução:**
1. Verifique logs de runtime (não build)
2. Verifique variáveis de ambiente
3. Verifique se `rag_index_llamaindex/` foi copiado

### Erro "Module not found" em runtime

**Solução:**
1. Verifique se todas as dependências estão em `requirements.txt`
2. Verifique se o build instalou tudo corretamente
3. Veja logs do builder stage

## 📊 Comparação de Dockerfiles

| Aspecto | Dockerfile | Dockerfile.optimized |
|---------|-----------|---------------------|
| Estratégia | 2 etapas (core + ML) | 1 etapa (tudo junto) |
| Cache | Melhor | Boa |
| Timeout | 600s por etapa | 600s total |
| Complexidade | Média | Baixa |
| Recomendado para | Builds que falham | Builds muito lentos |

## ✅ Checklist de Verificação

Antes de fazer deploy:

- [ ] `.dockerignore` está otimizado
- [ ] `Dockerfile` usa multi-stage build
- [ ] Timeouts configurados (600s)
- [ ] Retries configurados (5x)
- [ ] Root Directory no Railway: `backend`
- [ ] Logs do build verificados
- [ ] Build completa sem erros
- [ ] Aplicação inicia corretamente

## 🎯 Próximos Passos

Se o build ainda der timeout após essas otimizações:

1. **Contatar suporte do Railway** para aumentar timeout
2. **Usar build local** e fazer push da imagem para Docker Hub
3. **Reduzir dependências** removendo temporariamente ML libraries
4. **Usar Railway Buildpacks** em vez de Dockerfile (se disponível)

---

**Última atualização:** $(date)

