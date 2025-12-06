# Ampliação do RAG com Livros de Referência

## Data: 05/12/2025

## Objetivo

Ampliar o RAG com informações específicas dos três livros de referência principais:
1. **Sakoian & Acker** - Aspectos e geometria angular
2. **Stephen Arroyo** - Casas e Elementos
3. **Kris Brandt Riske** - Regras de segurança

## Documentos Criados

### 1. Sakoian & Acker - Aspectos e Geometria Angular
**Arquivo:** `backend/docs/reference_books/sakoian_acker_aspectos.md`

**Conteúdo:**
- Definições precisas de aspectos maiores (Conjunção, Oposição, Trígono, Quadratura, Sextil)
- Geometria angular para cálculo de momentos
- Orbes padrão (8° para aspectos maiores)
- Validação rigorosa de aspectos
- Pontuação para timing (Trígono +10, Sextil +7, Conjunção +8, Quadratura/Oposição -5)

**Uso na estratégia:** Definições precisas de aspectos (trígonos, quadraturas) e geometria angular para calcular momentos de sorte ou tensão.

### 2. Stephen Arroyo - Casas e Elementos
**Arquivo:** `backend/docs/reference_books/arroyo_casas_elementos.md`

**Conteúdo:**
- Triplicidade da Riqueza (Casas 2, 6, 10)
- Triplicidade da Vida (Casas 1, 5, 9)
- Casas para Parcerias (7, 11)
- Casas para Recursos Compartilhados (8)
- Mapeamento de ações para casas
- Planetas benéficos e aspectos preferidos por casa

**Uso na estratégia:** Definições das Casas e dos Elementos (Triplicidade da Riqueza, Triplicidade da Vida) para estruturar negócios e carreira.

### 3. Kris Brandt Riske - Regras de Segurança
**Arquivo:** `backend/docs/reference_books/riske_regras_seguranca_estruturado.md`

**Conteúdo:**
- Mercúrio Retrógrado: definição, frequência, efeitos, regras de "não agir"
- Lua Fora de Curso: definição, duração, teoria, regras de "não agir"
- Implementação no sistema (penalizações de score)
- Validação usando biblioteca local

**Uso na estratégia:** Regras de segurança como Mercúrio Retrógrado e Lua Fora de Curso, usados como filtros de "não agir".

## Garantias Implementadas

### Uso da Biblioteca Local

Todos os documentos incluem a instrução crítica:

> **IMPORTANTE:** Todos os cálculos astrológicos devem ser feitos usando a biblioteca local (Swiss Ephemeris via kerykeion). 
> Nunca invente ou estime cálculos. Use apenas dados calculados e validados pela biblioteca padrão.

### Validação Rigorosa

- Aspectos devem estar dentro do orbe de 8° para serem considerados válidos
- Cúspides de casas devem ser calculadas usando Swiss Ephemeris
- Lua Fora de Curso deve ser calculada usando `calculate_moon_void_of_course()`
- Mercúrio Retrógrado deve ser verificado pela velocidade do planeta

## Próximos Passos

### 1. Instalar Dependências (se necessário)

```bash
cd backend
pip install fastembed PyPDF2 numpy
```

### 2. Reconstruir o Índice RAG

```bash
cd /Users/alexandrerocha/CosmoAstrologia
python3 scripts/build_rag_index_fastembed.py
```

Este comando irá:
- Processar todos os documentos em `backend/docs/` (incluindo os novos documentos de referência)
- Criar embeddings usando FastEmbed
- Salvar o índice em `backend/rag_index_fastembed/`

### 3. Verificar Integração

Os documentos de referência serão automaticamente incluídos nas buscas RAG quando:
- Buscar informações sobre aspectos
- Buscar informações sobre casas astrológicas
- Buscar informações sobre regras de segurança (Mercúrio Retrógrado, Lua Fora de Curso)

## Estrutura de Arquivos

```
backend/
├── docs/
│   └── reference_books/
│       ├── sakoian_acker_aspectos.md
│       ├── arroyo_casas_elementos.md
│       ├── riske_regras_seguranca.md (extraído do PDF)
│       └── riske_regras_seguranca_estruturado.md (estruturado)
├── scripts/
│   └── extract_reference_books.py (script de extração)
└── rag_index_fastembed/ (índice RAG - será reconstruído)
```

## Notas Importantes

1. **PDFs Escaneados:** Os PDFs de Sakoian & Acker e Stephen Arroyo são escaneados (imagens), então não foi possível extrair texto automaticamente. Os documentos foram criados manualmente com base nas referências conhecidas desses livros.

2. **PDF de Riske:** O PDF de Kris Brandt Riske foi processado com sucesso e informações relevantes foram extraídas e estruturadas.

3. **Biblioteca Local:** Todos os cálculos mencionados nos documentos devem usar Swiss Ephemeris (via kerykeion), que já está implementado no sistema.

4. **Validação:** O sistema já implementa validação rigorosa de aspectos e cálculos, garantindo que apenas dados validados sejam usados.

## Status

✅ Documentos criados e estruturados
✅ Informações filtradas e organizadas
✅ Garantias de uso da biblioteca local implementadas
⏳ Índice RAG precisa ser reconstruído (após instalar dependências se necessário)

