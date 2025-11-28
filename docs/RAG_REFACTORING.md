# 🔄 Refatoração e Melhorias do RAG

## Melhorias Implementadas

### 1. **Busca Expandida (`expand_query`)**
- O método `search()` agora suporta busca expandida
- Cria múltiplas variações da query automaticamente
- Para sinastria: busca por cada signo individualmente
- Para planetas: adiciona termos relacionados (significado, interpretação)
- Para casas: adiciona termos relacionados (área vida, significado)
- Para aspectos: adiciona termos relacionados (relação planetas, dinâmica)

### 2. **Ampliação da Coleta de Informações**
- **top_k padrão aumentado**:
  - Karma/Trânsitos: 8 → 20 documentos
  - Aspectos: 8 → 15 documentos
  - Sinastria: 8 → 18 documentos
  - Geral: 8 → 12 documentos

### 3. **Múltiplas Queries Automáticas**
- Sistema agora faz múltiplas buscas com variações da query
- Remove duplicatas mantendo os melhores scores
- Combina resultados de diferentes variações para contexto mais rico

### 4. **Melhor Acesso ao Índice**
- Busca expandida ativada por padrão em `get_interpretation()`
- Chart ruler agora usa busca expandida com top_k=10 por query
- Trânsitos usam busca expandida com top_k=5

### 5. **Remoção de Duplicatas Inteligente**
- Remove documentos com texto muito similar
- Mantém apenas os melhores scores
- Limita resultados finais ao top_k solicitado

## Como Funciona a Busca Expandida

### Exemplo: Sinastria "Libra + Escorpião"

1. **Query original**: "sinastria compatibilidade Libra Escorpião"
2. **Queries expandidas geradas**:
   - "Libra características personalidade relacionamento"
   - "Libra em relacionamentos compatibilidade"
   - "Escorpião características personalidade relacionamento"
   - "Escorpião em relacionamentos compatibilidade"
3. **Busca**: Cada query busca top_k*2 documentos
4. **Combinação**: Remove duplicatas e mantém top_k melhores
5. **Resultado**: Contexto muito mais rico para o Groq

### Exemplo: Planeta "Sol em Libra"

1. **Query original**: "Sol em Libra significado"
2. **Queries expandidas**:
   - "Sol em Libra significado astrologia"
   - "Sol em Libra interpretação mapa astral"
3. **Resultado**: Mais contexto sobre o planeta e o signo

## Melhorias no Chart Ruler

- Busca expandida ativada (top_k=10 por query)
- Múltiplas queries (3-5) para coleta máxima
- Fallback com busca expandida (top_k=15)
- Até 15 documentos únicos coletados

## Melhorias nos Trânsitos

- Busca expandida ativada
- top_k aumentado de 3 para 5
- Melhor contexto para interpretações de trânsitos

## Como Recompilar o Índice

```bash
cd backend
python3 scripts/build_rag_index.py
```

Ou se estiver na raiz:

```bash
cd backend
python3 ../scripts/build_rag_index.py
```

## Resultados Esperados

- **Mais contexto**: 2-3x mais documentos coletados
- **Melhor qualidade**: Variações da query capturam mais nuances
- **Menos "Nenhum documento encontrado"**: Busca expandida encontra mais resultados
- **Interpretações mais ricas**: Groq recebe mais contexto para gerar respostas

## Próximos Passos

1. Adicionar documentos PDF/Markdown na pasta `backend/docs/`
2. Recompilar o índice com `python3 scripts/build_rag_index.py`
3. Testar buscas e verificar melhorias na coleta de informações

