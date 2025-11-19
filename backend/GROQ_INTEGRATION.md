# Integração Groq com Sistema RAG

## Visão Geral

O sistema RAG agora utiliza o Groq para gerar interpretações astrológicas mais coerentes e estruturadas baseadas nos documentos recuperados.

## Como Funciona

1. **RAG (Retrieval)**: Busca documentos relevantes nos PDFs usando busca semântica
2. **Groq (Generation)**: Sintetiza os documentos encontrados em uma interpretação coerente e estruturada

## Configuração

### 1. Adicionar Chave API no .env

```bash
# backend/.env
GROQ_API_KEY=sua_chave_aqui
```

### 2. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

A dependência `groq==0.4.1` já está incluída no `requirements.txt`.

## Uso

### Via API

```bash
# Interpretação com Groq (padrão)
curl -X POST http://localhost:8000/api/interpretation \
  -H "Content-Type: application/json" \
  -d '{
    "planet": "Sol",
    "sign": "Libra",
    "use_groq": true
  }'

# Interpretação apenas com RAG (sem Groq)
curl -X POST http://localhost:8000/api/interpretation \
  -H "Content-Type: application/json" \
  -d '{
    "planet": "Sol",
    "sign": "Libra",
    "use_groq": false
  }'
```

### Resposta

```json
{
  "interpretation": "Interpretação gerada pelo Groq baseada nos documentos...",
  "sources": [
    {
      "source": "arquivo.pdf",
      "page": 42,
      "relevance": 0.85
    }
  ],
  "query_used": "Sol em Libra",
  "generated_by": "groq"
}
```

O campo `generated_by` pode ser:
- `"groq"`: Interpretação gerada pelo Groq
- `"rag_only"`: Apenas documentos concatenados (sem Groq)
- `"none"`: Nenhum documento encontrado

## Modelo Usado

O sistema usa o modelo `llama-3.1-70b-versatile` do Groq, que é:
- Rápido (inferência em segundos)
- Multilíngue (suporta português)
- Eficiente (boa relação custo/performance)

## Fallback Automático

Se o Groq não estiver disponível ou houver erro:
- O sistema automaticamente retorna os documentos sem processamento
- Nenhum erro é lançado, apenas um warning é logado

## Teste

Execute o script de teste:

```bash
python backend/test_groq_integration.py
```

Este script verifica:
- Se a chave API está configurada
- Se o índice RAG está carregado
- Se o Groq está funcionando
- Compara interpretações com e sem Groq

## Vantagens do Groq

1. **Interpretações Coerentes**: Sintetiza múltiplos documentos em uma resposta única
2. **Estruturado**: Organiza a informação de forma clara e lógica
3. **Contextual**: Considera todos os documentos relevantes juntos
4. **Rápido**: Inferência em segundos
5. **Baseado em Documentos**: Usa apenas informações dos PDFs fornecidos

## Troubleshooting

### Erro: "Cliente Groq não disponível"
- Verifique se `GROQ_API_KEY` está no `.env`
- Verifique se a chave é válida
- Execute: `pip install groq`

### Erro: "Erro ao gerar interpretação com Groq"
- O sistema automaticamente usa fallback (RAG apenas)
- Verifique os logs para detalhes do erro
- Pode ser problema de conexão ou quota da API

### Interpretações muito curtas
- Aumente `max_tokens` no método `_generate_with_groq` (atualmente 2000)
- Ajuste `temperature` para mais criatividade (atualmente 0.7)

## Próximos Passos

- [ ] Cache de interpretações frequentes
- [ ] Suporte para múltiplos modelos do Groq
- [ ] Métricas de qualidade das interpretações
- [ ] Ajuste fino de prompts baseado em feedback

