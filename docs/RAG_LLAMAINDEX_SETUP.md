# Sistema RAG com LlamaIndex e BGE

## Visão Geral

Esta é a nova implementação do sistema RAG usando **LlamaIndex** como framework de construção e **BGE (BAAI General Embedding)** via Hugging Face para embeddings. Esta estrutura foi criada para substituir a implementação legacy após validação.

## Vantagens da Nova Implementação

- **LlamaIndex**: Framework robusto com abstrações otimizadas para RAG
- **BGE Model**: Modelos de embeddings de alta qualidade do Hugging Face
- **Melhor Manutenibilidade**: Código mais organizado e fácil de manter
- **Escalabilidade**: Suporta grandes volumes de documentos
- **Flexibilidade**: Fácil trocar modelos e componentes

## Instalação

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

As novas dependências incluem:
- `llama-index>=0.10.0`: Framework principal
- `llama-index-embeddings-huggingface>=0.1.0`: Integração com modelos Hugging Face
- `sentence-transformers`: Instalado automaticamente como dependência

### 2. Construir o Índice RAG

Execute o script para processar todos os documentos e criar o índice:

```bash
cd backend
python ../scripts/build_rag_index_llamaindex.py
```

Ou diretamente:

```bash
python scripts/build_rag_index_llamaindex.py
```

Este script irá:
1. Processar todos os PDFs e Markdowns em `backend/docs/`
2. Extrair texto e dividir em chunks otimizados
3. Criar embeddings usando modelo BGE do Hugging Face
4. Salvar o índice em `backend/rag_index_llamaindex/`

**Tempo estimado**: 5-15 minutos dependendo do número de documentos.

## Configuração

### Alternar entre Implementações

O sistema permite alternar entre a implementação legacy e a nova implementação LlamaIndex através da configuração `RAG_IMPLEMENTATION`.

#### Via Arquivo .env

Crie ou edite o arquivo `backend/.env`:

```env
# Usar nova implementação LlamaIndex
RAG_IMPLEMENTATION=llamaindex

# Ou usar implementação legacy (padrão)
RAG_IMPLEMENTATION=legacy
```

#### Via Variável de Ambiente

```bash
export RAG_IMPLEMENTATION=llamaindex
```

### Modelo BGE

Por padrão, o sistema usa `BAAI/bge-small-en-v1.5`. Para usar outro modelo, edite o arquivo `backend/app/services/rag_service_llamaindex.py`:

```python
rag_service = RAGServiceLlamaIndex(
    docs_path=str(docs_path),
    index_path=str(index_path),
    bge_model_name="BAAI/bge-base-en-v1.5"  # Modelo maior e mais preciso
)
```

Modelos BGE disponíveis:
- `BAAI/bge-small-en-v1.5` (padrão, mais rápido)
- `BAAI/bge-base-en-v1.5` (mais preciso)
- `BAAI/bge-large-en-v1.5` (mais preciso, mais lento)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilíngue)

## Uso

A API permanece a mesma, independente da implementação usada. O sistema usa automaticamente a implementação configurada.

### Endpoints da API

Todos os endpoints existentes continuam funcionando:

- `POST /api/interpretation` - Interpretação geral
- `POST /api/interpretation/planet` - Interpretação de planeta
- `POST /api/interpretation/chart-ruler` - Interpretação do regente do mapa
- `POST /api/interpretation/aspect` - Interpretação de aspecto

### Uso Programático

```python
from app.services.rag_service_wrapper import get_rag_service

# Obtém o serviço RAG configurado (legacy ou LlamaIndex)
rag_service = get_rag_service()

# Usar normalmente
interpretation = rag_service.get_interpretation(
    planet="Sol",
    sign="Libra",
    use_groq=True
)
```

## Estrutura de Arquivos

```
backend/
├── app/
│   ├── services/
│   │   ├── rag_service.py              # Implementação legacy
│   │   ├── rag_service_llamaindex.py   # Nova implementação
│   │   └── rag_service_wrapper.py      # Wrapper para alternar
│   └── core/
│       └── config.py                   # Configuração RAG_IMPLEMENTATION
├── docs/                               # Documentos a processar
├── rag_index.pkl                       # Índice legacy (pickle)
└── rag_index_llamaindex/              # Índice novo (diretório)
```

## Migração da Implementação Legacy

### Passo a Passo

1. **Instalar dependências**:
   ```bash
   pip install llama-index llama-index-embeddings-huggingface
   ```

2. **Construir novo índice**:
   ```bash
   python scripts/build_rag_index_llamaindex.py
   ```

3. **Testar nova implementação**:
   - Configure `RAG_IMPLEMENTATION=llamaindex` no `.env`
   - Teste os endpoints da API
   - Compare resultados com a implementação legacy

4. **Validar resultados**:
   - Verifique qualidade das interpretações
   - Compare performance
   - Teste com diferentes tipos de consultas

5. **Após aprovação**:
   - A implementação legacy pode ser removida
   - Remover `rag_service.py` (após backup)
   - Remover `rag_index.pkl` (após backup)
   - Simplificar `rag_service_wrapper.py`

## Troubleshooting

### Erro: "LlamaIndex não disponível"

**Solução**: Instale as dependências:
```bash
pip install llama-index llama-index-embeddings-huggingface
```

### Erro: "Modelo BGE não encontrado"

**Solução**: O modelo será baixado automaticamente na primeira execução. Certifique-se de ter conexão com a internet.

### Erro: "Índice não encontrado"

**Solução**: Execute o script de build:
```bash
python scripts/build_rag_index_llamaindex.py
```

### Performance Lenta

**Soluções**:
- Use modelo BGE menor (`bge-small-en-v1.5`)
- Reduza `top_k` nas buscas
- Use GPU se disponível (configuração automática do Hugging Face)

## Próximos Passos

Após validação da nova implementação:
1. Remover código legacy
2. Otimizar configurações
3. Adicionar métricas de performance
4. Implementar cache de embeddings
5. Adicionar suporte a mais formatos de documento

## Notas Técnicas

- O índice LlamaIndex é salvo como diretório (não arquivo pickle)
- Os embeddings são calculados usando o modelo BGE configurado
- A busca usa similaridade de cosseno otimizada pelo LlamaIndex
- O sistema mantém compatibilidade total com a API existente

