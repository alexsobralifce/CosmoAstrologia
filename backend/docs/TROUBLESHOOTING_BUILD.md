# 🔧 Troubleshooting: Erros de Build

## 🔴 Erro: "exit code: 1" no pip install

### Diagnóstico

Este erro significa que alguma dependência falhou ao instalar. Para identificar qual:

### Solução 1: Usar Dockerfile.debug

```bash
cd backend
docker build -t debug-build -f Dockerfile.debug .
```

Este Dockerfile mostra logs detalhados e identifica qual pacote está falhando.

### Solução 2: Instalar em Batches (Dockerfile.build-local atualizado)

O `Dockerfile.build-local` agora instala em batches menores e mostra qual batch falhou:

```bash
docker build -t seu-usuario/cosmoastrologia:latest -f Dockerfile.build-local .
```

Cada batch mostra uma mensagem de erro específica se falhar.

### Solução 3: Usar requirements-prod-fixed.txt

Se houver conflitos de versão, use `requirements-prod-fixed.txt` que tem versões específicas testadas:

```dockerfile
# No Dockerfile, mude:
COPY requirements-prod-fixed.txt requirements.txt
```

---

## 🔍 Problemas Comuns

### 1. Conflito de Versões NumPy

**Erro:** `numpy` incompatível com outras dependências

**Solução:** Use `numpy==1.26.4` (versão específica) em vez de `numpy<2.0`

### 2. FastEmbed (substitui LlamaIndex)

**Nota:** FastEmbed é mais leve e rápido que LlamaIndex, não requer configuração especial de Pydantic

### 3. FastEmbed requer NumPy primeiro

**Erro:** FastEmbed falha porque NumPy não está instalado

**Solução:** Instalar NumPy antes de FastEmbed (já feito no Dockerfile)

**Nota:** FastEmbed substituiu LlamaIndex - é mais leve e rápido

### 4. Build dependencies faltando

**Erro:** Falha ao compilar extensões C

**Solução:** Garantir que `build-essential`, `gcc`, `g++` estão instalados (já no Dockerfile)

---

## ✅ Checklist de Verificação

Antes de fazer build:

- [ ] `requirements-prod.txt` existe e está correto
- [ ] Python 3.11 está sendo usado
- [ ] Build dependencies estão instaladas (gcc, g++)
- [ ] Pip está atualizado

Para debug:

- [ ] Use `Dockerfile.debug` para ver logs detalhados
- [ ] Verifique qual batch falhou no `Dockerfile.build-local`
- [ ] Tente `requirements-prod-fixed.txt` se houver conflitos

---

## 🎯 Próximos Passos

1. **Se build local falhar:**
   - Use `Dockerfile.debug` para ver erro completo
   - Identifique qual pacote está falhando
   - Verifique se há conflitos de versão

2. **Se houver conflito de versão:**
   - Use `requirements-prod-fixed.txt`
   - Ou ajuste versões manualmente

3. **Se build local funcionar:**
   - Push para Docker Hub
   - Configure Railway para usar Docker Hub

---

**Última atualização:** $(date)

