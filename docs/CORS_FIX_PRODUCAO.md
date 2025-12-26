# 🔧 Correção de CORS em Produção

## Problema

O frontend em `https://www.cosmoastral.com.br` não consegue fazer requisições para o backend em `https://cosmoastrologia-production.up.railway.app` devido a erro de CORS.

## Solução Implementada

O código agora **automaticamente adiciona** os domínios de produção às origens permitidas:

- `https://www.cosmoastral.com.br`
- `https://cosmoastral.com.br`
- `http://www.cosmoastral.com.br` (caso use HTTP)
- `http://cosmoastral.com.br` (caso use HTTP)

## Configuração Manual (Opcional)

Se quiser configurar manualmente no Railway, adicione a variável de ambiente:

```
CORS_ORIGINS=https://www.cosmoastral.com.br,https://cosmoastral.com.br
```

**Nota:** O código já adiciona esses domínios automaticamente, então não é necessário configurar manualmente, mas pode ser útil para adicionar outros domínios.

## Verificação

Ao iniciar o backend, você verá no console:

```
================================================================================
🌐 CORS Configuration:
   Allowed Origins: ['http://localhost:5173', ..., 'https://www.cosmoastral.com.br', ...]
================================================================================
```

Isso confirma que os domínios de produção estão incluídos.

## Teste

Após o deploy, teste fazendo uma requisição do frontend. O erro de CORS deve desaparecer.

