# Correção do Erro: Índice RAG Não Carregado

## Data: 02/12/2025

## Problema

Ao buscar interpretação de planetas (ex: Netuno em Peixes na Casa 12), o sistema retornava erro:

```
Erro ao buscar interpretação para Netuno em Peixes na Casa 12. Índice não carregado. Execute load_index() ou process_all_documents() primeiro.
```

## Causa

O erro ocorria quando:
1. O índice RAG não estava carregado (não foi executado o script de build do índice)
2. O sistema tentava buscar no RAG service
3. O método `search()` lançava `ValueError` quando o índice não estava disponível
4. O erro era retornado ao frontend sem tratamento adequado

## Solução Implementada

### 1. Tratamento de Erro no Endpoint `get_planet_interpretation`

**Arquivo:** `backend/app/api/interpretation.py`

**Mudanças:**
- Adicionado tratamento de exceção ao buscar no RAG
- Se o índice não estiver carregado, o sistema continua sem contexto RAG
- Sistema funciona normalmente usando apenas Groq + conhecimento base
- Fallback para LocalKnowledgeBase quando necessário

**Código Adicionado:**
```python
# Tentar buscar no RAG, mas tratar erro se índice não estiver carregado
if rag_service:
    try:
        # Tentar buscar - o método search() lançará ValueError se índice não estiver carregado
        results = rag_service.search(query, top_k=6, expand_query=True)
        # ... processar resultados
    except ValueError as e:
        error_msg = str(e)
        if "não carregado" in error_msg.lower() or "load_index" in error_msg.lower():
            print(f"[PLANET API] ⚠️ Índice RAG não carregado: {error_msg}")
            print(f"[PLANET API] Continuando sem contexto RAG - interpretação será gerada apenas com Groq/conhecimento base")
```

### 2. Fallback para LocalKnowledgeBase

Quando o índice RAG não estiver disponível, o sistema agora:
1. Continua sem contexto RAG
2. Gera interpretação usando apenas Groq (se disponível)
3. Usa LocalKnowledgeBase como fallback se Groq também não estiver disponível

### 3. Tratamento de Exceções Finais

Melhorado o tratamento de exceções para:
- Não retornar erro HTTP quando o índice RAG não está carregado
- Usar fallbacks adequados (LocalKnowledgeBase)
- Apenas retornar erro HTTP se todos os fallbacks falharem

## Resultado

✅ **Sistema agora funciona mesmo sem o índice RAG carregado:**
- Interpretações são geradas usando Groq + conhecimento base
- Não retorna erro ao usuário
- Funciona normalmente mesmo sem o índice RAG

## Para Carregar o Índice RAG (Opcional)

Se quiser melhorar as interpretações com contexto do RAG:

1. **Executar script de build do índice:**
   ```bash
   cd backend
   python scripts/build_rag_index_fastembed.py
   ```

2. **Verificar se o índice foi criado:**
   ```bash
   ls -lh backend/rag_index_fastembed/
   ```

3. **Reiniciar o servidor:**
   O índice será carregado automaticamente na próxima inicialização

## Notas

- O sistema funciona normalmente sem o índice RAG
- O índice RAG é opcional e melhora a qualidade das interpretações
- O sistema usa fallbacks adequados quando o índice não está disponível
- Não é necessário carregar o índice para o sistema funcionar

