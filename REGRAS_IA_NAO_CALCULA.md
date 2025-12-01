# Regras Críticas: IA NÃO Calcula Nada - Tudo Vem da Biblioteca

## Princípio Fundamental

⚠️ **A IA NÃO DEVE CALCULAR NADA. TODOS OS CÁLCULOS SÃO FEITOS PELA BIBLIOTECA PYTHON (SWISS EPHEMERIS/KERYKEION).**

A IA é APENAS um interpretador de textos. Sua única função é ler os dados já calculados e criar interpretações astrológicas baseadas nesses dados.

---

## O Que a Biblioteca Calcula

### 1. Cálculos Astronômicos (Swiss Ephemeris/Kerykeion)
- ✅ Posições planetárias (longitudes eclípticas)
- ✅ Signos e graus de todos os planetas
- ✅ Ascendente, Meio do Céu, Fundo do Céu
- ✅ Nodos Lunares
- ✅ Casas Astrológicas
- ✅ Aspectos planetários (com validação de orbes)

### 2. Cálculos Astrológicos (Código Python)
- ✅ Temperamento (pontos por elemento)
- ✅ Dignidades planetárias (Domicílio, Exaltação, Detrimento, Queda, Peregrino)
- ✅ Regente do mapa (identificação por tabela fixa)
- ✅ Stelliums (3+ planetas no mesmo signo)
- ✅ Validação de aspectos (verificação de limites astronômicos)

---

## O Que a IA NÃO Pode Fazer

### ❌ PROIBIDO - Cálculos Astronômicos
- ❌ Calcular posições planetárias
- ❌ Calcular signos ou graus
- ❌ Calcular aspectos (distâncias angulares)
- ❌ Calcular casas astrológicas
- ❌ Calcular nodos lunares

### ❌ PROIBIDO - Cálculos Astrológicos
- ❌ Calcular temperamento (pontos por elemento)
- ❌ Calcular dignidades planetárias
- ❌ Identificar regente do mapa
- ❌ Identificar stelliums
- ❌ Estimar ou "adivinhar" qualquer dado

### ❌ PROIBIDO - Invenções
- ❌ Inventar aspectos que não estão no bloco pré-calculado
- ❌ Inventar elementos ausentes se o bloco mostra que todos têm pontos
- ❌ Inventar dignidades não listadas no bloco
- ❌ Recalcular qualquer dado já calculado

---

## O Que a IA DEVE Fazer

### ✅ PERMITIDO - Interpretação
- ✅ Ler o bloco "🔒 DADOS PRÉ-CALCULADOS"
- ✅ Usar EXATAMENTE os dados listados no bloco
- ✅ Interpretar os dados de forma psicológica e evolutiva
- ✅ Criar narrativas baseadas nos dados calculados
- ✅ Explicar o significado astrológico dos dados

### ✅ PERMITIDO - Validação (sem recalcular)
- ✅ Verificar se os dados fazem sentido astronomicamente (sem recalcular)
- ✅ Alertar se houver contradições óbvias (mas não recalcular)
- ✅ Validar que está usando os dados corretos do bloco

---

## Fluxo de Dados

```
1. Usuário fornece dados de nascimento
   ↓
2. Biblioteca Python (Swiss Ephemeris) calcula:
   - Posições planetárias
   - Signos e graus
   - Casas astrológicas
   ↓
3. Código Python calcula:
   - Temperamento (pontos por elemento)
   - Dignidades planetárias
   - Regente do mapa
   - Aspectos validados
   ↓
4. Bloco "🔒 DADOS PRÉ-CALCULADOS" é criado
   ↓
5. IA recebe o bloco e APENAS interpreta
   - Lê os dados
   - Cria interpretação textual
   - NÃO calcula nada
```

---

## Exemplos de Uso Correto

### ✅ CORRETO - Temperamento
**Bloco pré-calculado diz:**
```
Fogo: 5 pontos
Água: 8 pontos
ELEMENTO DOMINANTE: Água
```

**IA escreve:**
> "O mapa apresenta predominância do elemento Água, com 8 pontos, seguido pelo elemento Fogo, com 5 pontos..."

### ❌ INCORRETO - Temperamento
**Bloco pré-calculado diz:**
```
Água: 8 pontos
ELEMENTO DOMINANTE: Água
```

**IA escreve (ERRADO):**
> "O mapa apresenta predominância do elemento Fogo..." ❌
> "O elemento Água está ausente..." ❌

### ✅ CORRETO - Aspectos
**Bloco pré-calculado lista:**
```
Sol Trígono Lua
Marte Quadratura Saturno
```

**IA escreve:**
> "O Sol em trígono com a Lua indica harmonia entre essência e emoções. Marte em quadratura com Saturno sugere tensão entre ação e limites..."

### ❌ INCORRETO - Aspectos
**Bloco pré-calculado NÃO lista:**
```
(Nenhum aspecto entre Sol e Plutão)
```

**IA escreve (ERRADO):**
> "O Sol em oposição com Plutão..." ❌ (aspecto não existe no bloco)

---

## Validações Implementadas

### 1. Bloco de Dados Pré-Calculados
- Todos os cálculos são feitos ANTES de enviar para a IA
- Bloco formatado com emojis e formatação clara
- Instruções explícitas de uso

### 2. Prompts Reforçados
- Master prompt proíbe explicitamente cálculos
- Prompts de seção reforçam uso apenas dos dados pré-calculados
- Exemplos corretos e incorretos incluídos

### 3. Validação Obrigatória
- Checklist antes de escrever
- Instruções para localizar e usar dados específicos
- Proibição explícita de recalcular

---

## Arquivos Modificados

1. **`backend/app/api/interpretation.py`**
   - Master prompt (EN e PT) - removidas instruções de cálculo
   - Prompts de seção 'power' - reforçado uso apenas de dados pré-calculados
   - Prompt final enviado ao Groq - validação obrigatória

2. **`backend/app/services/precomputed_chart_engine.py`**
   - Formatação melhorada do bloco de dados pré-calculados
   - Validações explícitas no bloco
   - Lembretes sobre uso correto

---

## Checklist para Desenvolvedores

Ao adicionar novos cálculos ou funcionalidades:

- [ ] O cálculo é feito pela biblioteca Python?
- [ ] O resultado é incluído no bloco "🔒 DADOS PRÉ-CALCULADOS"?
- [ ] O prompt proíbe explicitamente a IA de calcular isso?
- [ ] Há exemplos corretos e incorretos no prompt?
- [ ] A validação obrigatória está implementada?

---

## Status

✅ **Todas as instruções de cálculo foram removidas dos prompts**
✅ **IA é explicitamente proibida de calcular qualquer coisa**
✅ **Todos os dados vêm do bloco pré-calculado**
✅ **Validações obrigatórias implementadas**

---

## Lembrete Final

**A IA é um INTERPRETADOR, não um CALCULADOR.**

Se você ver a IA calculando algo, isso é um BUG que precisa ser corrigido imediatamente.

Tudo deve passar pela biblioteca Python primeiro. A IA apenas lê e interpreta.

