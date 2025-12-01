# 🔧 Correções para Produção

## Problemas Identificados e Corrigidos

### 1. ✅ CORS não funcionando em erros 500

**Problema:** Quando o backend retorna erro 500, o middleware CORS não adiciona os headers, causando erro de CORS no frontend.

**Solução:** Adicionados exception handlers que garantem que headers CORS sejam adicionados mesmo em caso de erro.

### 2. ✅ RAG_SERVICE_URL usando localhost em produção

**Problema:** O RAG service está tentando conectar em `http://localhost:8001` em produção, o que não funciona.

**Solução:** 
- Adicionado warning crítico quando detecta localhost em produção
- Log mostra claramente qual URL está sendo usada
- Instruções para configurar corretamente

## Configuração Necessária no Railway

### Variáveis de Ambiente Obrigatórias:

1. **RAG_SERVICE_URL** (CRÍTICO)
   ```
   RAG_SERVICE_URL=https://seu-rag-service.railway.app
   ```
   - Substitua `seu-rag-service.railway.app` pela URL real do seu RAG service no Railway
   - Se o RAG service estiver no mesmo projeto Railway, pode usar o nome do serviço interno
   - **NÃO use localhost em produção!**

2. **GROQ_API_KEY** (Obrigatório)
   ```
   GROQ_API_KEY=gsk_sua_chave_aqui
   ```

3. **SECRET_KEY** (Obrigatório)
   ```
   SECRET_KEY=sua_chave_secreta_gerada
   ```

4. **CORS_ORIGINS** (Opcional - já adicionado automaticamente)
   ```
   CORS_ORIGINS=https://www.cosmoastral.com.br,https://cosmoastral.com.br
   ```
   - O código já adiciona automaticamente os domínios de produção
   - Só configure se quiser adicionar outros domínios

## Como Encontrar a URL do RAG Service no Railway

1. No Railway Dashboard, vá para o serviço do RAG
2. Vá em **Settings** → **Networking**
3. Copie a URL pública (ex: `https://rag-service-production.up.railway.app`)
4. Use essa URL na variável `RAG_SERVICE_URL` do backend

## Verificação

Após configurar, verifique os logs do backend ao iniciar:

1. **CORS Configuration:**
   ```
   ================================================================================
   🌐 CORS Configuration:
      Allowed Origins: [..., 'https://www.cosmoastral.com.br', ...]
   ================================================================================
   ```

2. **RAG Client:**
   ```
   [RAG-Client] Inicializando cliente RAG com URL: https://seu-rag-service.railway.app
   ```

3. **Se RAG_SERVICE_URL estiver errado:**
   ```
   ================================================================================
   🚨 ERRO CRÍTICO: RAG_SERVICE_URL está usando localhost em produção!
      URL atual: http://localhost:8001
      Configure RAG_SERVICE_URL no Railway com a URL do RAG service
   ================================================================================
   ```

## Próximos Passos

1. ✅ Configure `RAG_SERVICE_URL` no Railway
2. ✅ Faça deploy do backend
3. ✅ Verifique os logs para confirmar que está usando a URL correta
4. ✅ Teste o frontend - erros de CORS e RAG devem desaparecer

