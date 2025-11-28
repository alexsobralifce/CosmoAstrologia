# Estrutura RAG Reorganizada para Astrologia
## Documentação da Nova Organização dos Documentos

---

## VISÃO GERAL

A estrutura do RAG foi reorganizada para permitir consultas mais precisas e interpretações baseadas em:

1. **Entidades Fundamentais** (Blocos de Construção)
2. **Combinatória Interpretativa** (Sintaxe Astrológica)
3. **Dinâmica e Força** (Astrologia Clássica)
4. **Aspectos Planetários** (Conversa entre Astros)
5. **Pontos Kármicos e Evolutivos** (Nível da Alma)

---

## DOCUMENTOS ESTRUTURADOS

### 1. ENTIDADES_FUNDAMENTAIS_ASTROLOGIA.md

**Conteúdo:**
- Definições isoladas de Planetas (O "O Quê")
- Definições de Signos (O "Como") - por Elemento, Qualidade e Polaridade
- Definições de Casas (O "Onde") - por Hemisférios e Tipos

**Uso RAG:**
- Consultas base para entender conceitos antes de interpretar
- Chunks específicos para cada planeta, signo e casa

**Metadados sugeridos:**
- `tipo: entidade_fundamental`
- `categoria: planeta | signo | casa`
- `nome: [nome específico]`

---

### 2. COMBINATORIA_INTERPRETATIVA.md

**Conteúdo:**
- Planetas nos Signos (144 combinações)
- Planetas nas Casas (interpretação por área de vida)
- Regentes das Cúspides (os "donos" das casas)

**Uso RAG:**
- Consultas específicas para combinações exatas
- Exemplo: "Mercúrio em Libra na Casa 3"

**Metadados sugeridos:**
- `tipo: combinatoria`
- `subtipo: planeta_signo | planeta_casa | regente_cuspide`
- `planeta: [nome]`
- `signo: [nome]` (para planeta_signo)
- `casa: [número]` (para planeta_casa)

---

### 3. DIGNIDADES_DEBILIDADES_FORCA_PLANETARIA.md

**Conteúdo:**
- Dignidades Essenciais (Domicílio, Exaltação, Triplicidade)
- Debilidades (Exílio, Queda)
- Retrogradação (significados por planeta)
- Balanço de Elementos (excesso/falta e como equilibrar)

**Uso RAG:**
- Avaliação técnica da força planetária
- Conselhos práticos de equilíbrio energético

**Metadados sugeridos:**
- `tipo: dignidade | retrogradacao | balanceamento`
- `estado: domicilio | exaltacao | exilio | queda | retrogrado`
- `planeta: [nome]`
- `signo: [nome]`
- `elemento: fogo | terra | ar | agua` (para balanceamento)

---

### 4. ASPECTOS_E_CONEXOES.md

**Conteúdo:**
- Definições de Aspectos (Conjunção, Quadratura, Trígono, etc.)
- Intercâmbios Planetários (interpretações por par)
- Aspectos Harmônicos vs. Desarmônicos

**Uso RAG:**
- Consultas sobre relações entre planetas
- Interpretação de dinâmicas planetárias

**Metadados sugeridos:**
- `tipo: aspecto`
- `planeta1: [nome]`
- `planeta2: [nome]`
- `qualidade: harmonico | tenso | neutro`

---

### 5. PONTOS_KARMICOS_EVOLUTIVOS.md

**Conteúdo:**
- Nodos Lunares (Norte e Sul) por Signo e Casa
- Quíron por Signo e Casa
- Lilith por Signo e Casa
- Parte da Fortuna

**Uso RAG:**
- Consultas sobre evolução da alma
- Interpretação de padrões kármicos

**Metadados sugeridos:**
- `tipo: ponto_karmico`
- `subtipo: nodo_norte | nodo_sul | quiron | lilith | parte_fortuna`
- `signo: [nome]`
- `casa: [número]`

---

### 6. NODOS_LUNARES_GUIA_COMPLETO.md

**Conteúdo:**
- Guia detalhado sobre nodos lunares
- Interpretações profundas por eixo

**Uso RAG:**
- Consultas detalhadas sobre nodos
- Exemplos práticos de interpretação

---

### 7. BASE_CONHECIMENTO_HIERARQUICA.md

**Conteúdo:**
- Visão geral hierárquica
- Informações complementares

**Uso RAG:**
- Consultas gerais
- Contexto adicional

---

## COMO O RAG DEVE USAR ESSES DOCUMENTOS

### 1. Busca Hierárquica

Quando uma consulta chega:

1. **Primeiro:** Buscar definições fundamentais (se necessário)
2. **Segundo:** Buscar combinações específicas (planeta+signo, planeta+casa)
3. **Terceiro:** Buscar dignidades/força planetária
4. **Quarto:** Buscar aspectos (se aplicável)
5. **Quinto:** Buscar pontos kármicos (se aplicável)

### 2. Metadados para Busca

O sistema RAG deve usar metadados para:
- Filtrar resultados relevantes
- Priorizar informações técnicas quando necessário
- Combinar múltiplas fontes para síntese

### 3. Síntese de Informações

O LLM deve:
- Usar definições fundamentais como base
- Aplicar combinações específicas
- Considerar força planetária (dignidades)
- Integrar aspectos e dinâmicas
- Incluir contexto kármico quando relevante

---

## REBUILD DO ÍNDICE

Após adicionar novos documentos, é necessário reconstruir o índice:

```bash
cd scripts
python3 build_rag_index.py
```

---

## EXEMPLOS DE CONSULTAS ESPERADAS

### Consulta 1: "Mercúrio em Libra na Casa 3"
**Chunks relevantes:**
- ENTIDADES: Definição de Mercúrio, Libra, Casa 3
- COMBINATORIA: Mercúrio em Libra, Mercúrio na Casa 3
- DIGNIDADES: Condição de Mercúrio em Libra

### Consulta 2: "Vênus em Queda"
**Chunks relevantes:**
- ENTIDADES: Definição de Vênus
- DIGNIDADES: Vênus em Queda (Virgem), significado

### Consulta 3: "Nodo Norte em Áries"
**Chunks relevantes:**
- PONTOS_KARMICOS: Nodo Norte em Áries, eixo Áries/Libra
- NODOS_LUNARES: Guia detalhado do eixo

---

## ATUALIZAÇÕES FUTURAS

- Adicionar mais combinações específicas conforme necessário
- Expandir interpretações de aspectos
- Adicionar mais exemplos práticos
- Criar chunks menores para melhor recuperação

