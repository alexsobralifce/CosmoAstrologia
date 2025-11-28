# Estrutura de Metadados para RAG
## Guia de Tags e Metadados para Indexação Precisa

Este documento define a estrutura de metadados que deve ser aplicada a TODOS os documentos do RAG para permitir busca precisa e recuperação de informações específicas.

---

## FORMATO DE METADADOS

Os metadados devem ser incluídos no início de cada seção/chunk usando o formato:

**METADADOS:** `tipo:[categoria]`, `[campo]:[valor]`, `[campo]:[valor]`

---

## CATEGORIAS DE METADADOS

### 1. DEFINIÇÃO (Planetas, Signos, Casas)

**Formato:** `tipo:planeta`, `nome:[nome]`, `topico:[tópico]`

**Exemplo:**
```
**METADADOS:** `tipo:planeta`, `nome:marte`, `topico:impulso_acao`, `categoria:definicao`
```

**Aplicável para:**
- Definições de planetas
- Definições de signos
- Definições de casas
- Pontos astrológicos (Ascendente, MC, etc.)

---

### 2. COMBINAÇÃO (Planeta + Signo)

**Formato:** `tipo:planeta_signo`, `planeta:[nome]`, `signo:[nome]`

**Exemplo:**
```
**METADADOS:** `tipo:planeta_signo`, `planeta:sol`, `signo:leao`
```

**Aplicável para:**
- Sol em Áries, Sol em Touro, etc.
- Lua em Gêmeos, Lua em Câncer, etc.
- Todas as 144 combinações planeta-signo

---

### 3. POSIÇÃO (Planeta + Casa)

**Formato:** `tipo:planeta_casa`, `planeta:[nome]`, `casa:[número]`

**Exemplo:**
```
**METADADOS:** `tipo:planeta_casa`, `planeta:saturno`, `casa:7`
```

**Aplicável para:**
- Sol na Casa 1, Lua na Casa 4, etc.
- Todas as combinações planeta-casa
- Interpretações específicas por casa

---

### 4. ASPECTO (Relação entre Planetas)

**Formato:** `tipo:aspecto`, `planeta1:[nome]`, `planeta2:[nome]`, `qualidade:[harmonico|tenso|neutro]`

**Exemplo:**
```
**METADADOS:** `tipo:aspecto`, `planeta1:sol`, `planeta2:lua`, `qualidade:tensao`
```

**Aplicável para:**
- Conjunção Sol-Lua
- Quadratura Vênus-Marte
- Trígono Júpiter-Saturno
- Oposição, Sextil, etc.

**Qualidades:**
- `harmonico`: Trígono, Sextil
- `tenso`: Quadratura, Oposição
- `neutro`: Conjunção (depende dos planetas)

---

### 5. DIGNIDADE (Força Planetária)

**Formato:** `tipo:dignidade`, `planeta:[nome]`, `estado:[domicilio|exaltacao|exilio|queda]`, `signo:[nome]`

**Exemplo:**
```
**METADADOS:** `tipo:dignidade`, `planeta:venus`, `estado:exilio`, `signo:aries`
```

**Aplicável para:**
- Planetas em domicílio
- Planetas em exaltação
- Planetas em exílio
- Planetas em queda
- Análises de força planetária

---

### 6. KÁRMICO (Pontos Kármicos)

**Formato:** `tipo:ponto_karmico`, `nome:[nodo_norte|nodo_sul|quiron|lilith|parte_fortuna]`, `tema:[missao_vida|ferida_cura|insubmissao|alegria]`

**Exemplo:**
```
**METADADOS:** `tipo:ponto_karmico`, `nome:nodo_norte`, `tema:missao_vida`
```

**Aplicável para:**
- Nodos Lunares (Norte e Sul)
- Quíron
- Lilith
- Parte da Fortuna
- Interpretações por signo e casa

---

### 7. ELEMENTO (Balanço de Elementos)

**Formato:** `tipo:balanceamento`, `elemento:[fogo|terra|ar|agua]`, `estado:[excesso|falta|equilibrado]`

**Exemplo:**
```
**METADADOS:** `tipo:balanceamento`, `elemento:fogo`, `estado:excesso`
```

**Aplicável para:**
- Análise de distribuição de elementos
- Excessos e faltas
- Conselhos de equilíbrio

---

### 8. REGENTE (Regência de Casas)

**Formato:** `tipo:regente_casa`, `casa:[número]`, `regente:[nome_planeta]`, `posicao_regente:[casa]` (opcional)

**Exemplo:**
```
**METADADOS:** `tipo:regente_casa`, `casa:2`, `regente:venus`, `posicao_regente:10`
```

**Aplicável para:**
- Regentes das cúspides
- Análise de regentes
- Posição dos regentes

---

### 9. COMPARAÇÃO (Casas vs Casas)

**Formato:** `tipo:comparacao`, `casa:[número]`, `casa:[número]`, `tema:[vocacao_vs_rotina|financas_vocacao]`

**Exemplo:**
```
**METADADOS:** `tipo:comparacao`, `casa:6`, `casa:10`, `tema:vocacao_vs_rotina`
```

**Aplicável para:**
- Casa 6 vs Casa 10 (rotina vs vocação)
- Casa 2 vs Casa 8 (recursos próprios vs compartilhados)
- Outras comparações relevantes

---

### 10. CONCEITO GERAL

**Formato:** `tipo:conceito`, `categoria:[entidade_fundamental|combinatoria|analise_setorial]`

**Exemplo:**
```
**METADADOS:** `tipo:conceito`, `categoria:entidade_fundamental`
```

**Aplicável para:**
- Definições gerais
- Conceitos fundamentais
- Introduções a tópicos

---

## REGRAS DE APLICAÇÃO

1. **Cada chunk relevante deve ter metadados** no início
2. **Use múltiplas tags** quando o conteúdo aborda vários temas
3. **Seja específico** - quanto mais específico, melhor a recuperação
4. **Use valores padronizados** - siga os formatos exatos acima
5. **Inclua sempre o tipo** - é o identificador principal

---

## EXEMPLOS COMPLETOS

### Exemplo 1: Definição de Planeta
```
**METADADOS:** `tipo:planeta`, `nome:marte`, `topico:acao`, `topico:impulso_acao`, `categoria:definicao`

### ♂ MARTE - Ação, Desejo, Energia
Marte representa...
```

### Exemplo 2: Combinação Planeta-Signo
```
**METADADOS:** `tipo:planeta_signo`, `planeta:sol`, `signo:leao`

**Sol em Leão:** Criatividade, orgulho, generosidade...
```

### Exemplo 3: Posição Planeta-Casa
```
**METADADOS:** `tipo:planeta_casa`, `planeta:saturno`, `casa:7`

**Saturno na Casa 7:** Relacionamentos sérios, responsabilidade...
```

### Exemplo 4: Aspecto
```
**METADADOS:** `tipo:aspecto`, `planeta1:sol`, `planeta2:lua`, `qualidade:tensao`

**Quadratura Sol-Lua:** Desafio entre identidade e emoções...
```

### Exemplo 5: Dignidade
```
**METADADOS:** `tipo:dignidade`, `planeta:venus`, `estado:exilio`, `signo:aries`

**Vênus em Exílio (Áries):** Precisa aprender diplomacia...
```

### Exemplo 6: Ponto Kármico
```
**METADADOS:** `tipo:ponto_karmico`, `nome:nodo_norte`, `tema:missao_vida`, `signo:aries`

**Nodo Norte em Áries:** Missão de independência...
```

### Exemplo 7: Regente de Casa
```
**METADADOS:** `tipo:regente_casa`, `casa:2`, `regente:venus`, `posicao_regente:10`

**Regente da Casa 2 (Vênus) na Casa 10:** Ganha dinheiro através da vocação...
```

---

## BENEFÍCIOS

Com essa estrutura de metadados:

1. **Busca Precisa:** O RAG pode encontrar exatamente o que precisa
2. **Menos Repetições:** Evita recuperar informação duplicada
3. **Contexto Rico:** Cada chunk tem contexto claro sobre o que contém
4. **Filtros Eficientes:** Pode filtrar por tipo antes da busca semântica
5. **Melhor Síntese:** LLM recebe informação mais organizada e precisa

---

## APLICAÇÃO NOS DOCUMENTOS

Todos os documentos RAG devem seguir esta estrutura:
- `ENTIDADES_FUNDAMENTAIS_ASTROLOGIA.md` - Definições com metadados
- `COMBINATORIA_INTERPRETATIVA.md` - Combinações com metadados
- `DIGNIDADES_DEBILIDADES_FORCA_PLANETARIA.md` - Dignidades com metadados
- `PONTOS_KARMICOS_EVOLUTIVOS.md` - Pontos kármicos com metadados
- `ANALISE_SETORIAL_AVANCADA_CASAS.md` - Análise setorial com metadados
- `ASPECTOS_E_CONEXOES.md` - Aspectos com metadados

