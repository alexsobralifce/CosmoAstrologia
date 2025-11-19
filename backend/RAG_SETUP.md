# Sistema RAG para Interpretação Astrológica

## Visão Geral

Este sistema RAG (Retrieval-Augmented Generation) permite consultar os PDFs de astrologia na pasta `docs/` para gerar interpretações personalizadas dos mapas astrais dos usuários.

## Instalação

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

As dependências RAG incluem:
- `sentence-transformers`: Modelo de embeddings multilíngue
- `scikit-learn`: Cálculo de similaridade
- `PyPDF2`: Extração de texto de PDFs
- `numpy`: Operações numéricas

### 2. Construir o Índice RAG

Execute o script para processar todos os PDFs e criar o índice:

```bash
cd backend
python build_rag_index.py
```

Este script irá:
1. Processar todos os PDFs em `backend/docs/`
2. Extrair texto e dividir em chunks
3. Criar embeddings usando modelo multilíngue
4. Salvar o índice em `backend/rag_index.pkl`

**Tempo estimado**: 5-15 minutos dependendo do número de PDFs.

## Uso

### API Endpoints

#### 1. Obter Interpretação

```http
POST /api/interpretation
Content-Type: application/json

{
  "planet": "Sol",
  "sign": "Libra",
  "house": null,
  "aspect": null,
  "custom_query": null
}
```

**Exemplos:**

```json
// Sol em Libra
{
  "planet": "Sol",
  "sign": "Libra"
}

// Mercúrio na Casa 3
{
  "planet": "Mercúrio",
  "house": 3
}

// Query customizada
{
  "custom_query": "ascendente em aquário significado"
}
```

**Resposta:**

```json
{
  "interpretation": "[Fonte: arquivo.pdf, Página 42]\nTexto da interpretação...",
  "sources": [
    {
      "source": "arquivo.pdf",
      "page": 42,
      "relevance": 0.85
    }
  ],
  "query_used": "Sol em Libra"
}
```

#### 2. Buscar Documentos

```http
GET /api/interpretation/search?query=ascendente%20em%20aquário&top_k=5
```

#### 3. Status do Sistema

```http
GET /api/interpretation/status
```

Retorna:
```json
{
  "available": true,
  "document_count": 1234,
  "has_dependencies": true
}
```

### Uso em Python

```python
from app.services.rag_service import get_rag_service

# Obter serviço RAG
rag = get_rag_service()

# Buscar interpretação
result = rag.get_interpretation(
    planet="Sol",
    sign="Libra"
)

print(result['interpretation'])
```

## Estrutura

```
backend/
├── app/
│   ├── services/
│   │   └── rag_service.py      # Serviço RAG principal
│   └── api/
│       └── interpretation.py    # Endpoints da API
├── docs/                        # PDFs de astrologia
├── build_rag_index.py           # Script para construir índice
├── rag_index.pkl                # Índice gerado (não versionado)
└── requirements.txt             # Dependências
```

## Como Funciona

1. **Processamento**: PDFs são lidos e divididos em chunks de ~500 caracteres
2. **Embeddings**: Cada chunk é convertido em um vetor usando modelo multilíngue
3. **Armazenamento**: Embeddings são salvos em `rag_index.pkl`
4. **Consulta**: Query do usuário é convertida em embedding e comparada com chunks
5. **Retorno**: Top-K chunks mais similares são retornados com metadados

## Modelo de Embeddings

O sistema usa `paraphrase-multilingual-MiniLM-L12-v2`, que:
- Suporta português e outros idiomas
- É otimizado para similaridade semântica
- Funciona offline (não precisa de API key)

## Atualização do Índice

Para reprocessar os PDFs após adicionar novos documentos:

```bash
rm backend/rag_index.pkl
python backend/build_rag_index.py
```

## Troubleshooting

### Erro: "Dependências RAG não disponíveis"
```bash
pip install sentence-transformers scikit-learn PyPDF2 numpy
```

### Erro: "Índice não encontrado"
Execute `python backend/build_rag_index.py` para criar o índice.

### PDFs não estão sendo processados
- Verifique se os PDFs estão em `backend/docs/`
- Verifique se os PDFs não estão corrompidos
- Alguns PDFs podem ser imagens escaneadas (não têm texto extraível)

### Performance lenta
- O primeiro carregamento do modelo pode demorar (~30s)
- Consultas subsequentes são rápidas (<1s)
- Considere usar GPU se disponível (instalação automática pelo sentence-transformers)

## Integração com Frontend

O frontend pode chamar a API assim:

```typescript
// src/services/api.ts
async getInterpretation(params: {
  planet?: string;
  sign?: string;
  house?: number;
  aspect?: string;
  custom_query?: string;
}) {
  return await this.request('/api/interpretation', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}
```

## Próximos Passos

- [ ] Adicionar cache de consultas frequentes
- [ ] Suporte para PDFs com imagens (OCR)
- [ ] Interface web para visualizar documentos
- [ ] Métricas de qualidade das respostas
- [ ] Suporte para múltiplos idiomas de consulta

