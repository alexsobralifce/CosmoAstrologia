# Seções do Mapa Astral Completo

## Visão Geral

O sistema gera um mapa astral completo com **6 seções principais**, cada uma focada em aspectos específicos da personalidade e do destino astrológico.

---

## Seções Disponíveis

### 1. 🔥 **power** - A Estrutura de Poder (Temperamento e Motivação)

**Foco:** Análise dos elementos (Fogo, Terra, Ar, Água) e do regente do mapa.

**Conteúdo:**
- Distribuição de elementos no mapa
- Elemento dominante e ausente
- Regente do mapa e sua posição
- Qualidades (Cardinal, Fixo, Mutável)
- Motivações básicas da personalidade

**Dados Utilizados:**
- Todos os planetas e seus elementos
- Ascendente e seu regente
- Cálculo matemático de pontos por elemento

---

### 2. ⭐ **triad** - A Tríade Fundamental (O Núcleo da Personalidade)

**Foco:** Análise profunda de Sol, Lua e Ascendente.

**Conteúdo:**
- Sol (vontade consciente, essência)
- Lua (necessidades emocionais, instintos)
- Ascendente (máscara social, modo de ação)
- Dinâmica entre os três
- Conflitos e harmonias na tríade

**Dados Utilizados:**
- Signos de Sol, Lua e Ascendente
- Casas onde estão posicionados
- Aspectos entre eles (se houver)

---

### 3. 🎯 **personal** - Dinâmica Pessoal e Ferramentas

**Foco:** Planetas pessoais (Mercúrio, Vênus, Marte) e como a pessoa processa e age.

**Conteúdo:**
- Mercúrio (comunicação, processamento mental)
- Vênus (valores, amor, atração)
- Marte (ação, conquista, luta)
- Dignidades de cada planeta
- Como esses planetas interagem

**Dados Utilizados:**
- Signos e casas de Mercúrio, Vênus e Marte
- Dignidades planetárias
- Aspectos entre planetas pessoais

---

### 4. 🏠 **houses** - Análise Setorial Avançada (Vida Prática e Casas)

**Foco:** Casas astrológicas e áreas específicas da vida.

**Conteúdo:**
- Casas principais (2, 4, 6, 7, 10)
- Regentes das casas
- Planetas nas casas
- Conexões entre casas via regentes
- Áreas de vida: finanças, lar, trabalho, relacionamentos, carreira

**Dados Utilizados:**
- Signos nas cúspides das casas
- Regentes das casas
- Planetas posicionados nas casas
- Meio do Céu (MC)

---

### 5. 🌙 **karma** - Expansão, Estrutura e Karma

**Foco:** Planetas sociais (Júpiter, Saturno), transpessoais (Urano, Netuno, Plutão) e pontos kármicos.

**Conteúdo:**
- Júpiter (expansão, crescimento, filosofia)
- Saturno (limites, responsabilidade, estrutura)
- Urano, Netuno, Plutão (transformação, espiritualidade, evolução)
- Nodos Lunares (Nodo Norte = destino, Nodo Sul = passado)
- Quíron (ferida que cura)
- Lilith (força visceral, insubmissão)

**Dados Utilizados:**
- Signos e casas de planetas sociais e transpessoais
- Posições dos Nodos Lunares
- Posição de Quíron
- Dignidades dos planetas

---

### 6. 🎨 **synthesis** - Síntese e Orientação Estratégica

**Foco:** Visão geral, pontos fortes, desafios e conselhos finais.

**Conteúdo:**
- Síntese de todas as análises anteriores
- Pontos fortes a explorar
- Desafios e cuidados
- Conselho final estratégico
- Frase de poder (mantra do mapa)

**Dados Utilizados:**
- Todas as informações das seções anteriores
- Stelliums (3+ planetas no mesmo signo)
- Aspectos principais
- Contradições e tensões do mapa

---

## Fluxo de Geração

```
1. Recebe dados de nascimento
   ↓
2. Calcula mapa astral (Swiss Ephemeris)
   ↓
3. Gera bloco pré-calculado (temperamento, dignidades, regente)
   ↓
4. Para cada seção:
   a. Gera prompt específico
   b. Busca contexto no RAG
   c. Envia para Groq com validação
   d. Retorna interpretação
   ↓
5. Retorna todas as seções juntas
```

---

## Validações Implementadas

### ✅ Consistência de Temperamento
- Mesmo bloco pré-calculado usado em todas as seções
- Valores de elementos devem ser idênticos em todas as menções

### ✅ Consistência de Dignidades
- Dignidades devem corresponder exatamente ao bloco pré-calculado
- Não pode inventar ou confundir dignidades

### ✅ Validação de Dados Pré-Calculados
- Temperamento calculado matematicamente
- Dignidades identificadas por tabela fixa
- Regente identificado por tabela fixa
- Elementos mapeados por tabela fixa

---

## Endpoints

### Gerar Todas as Seções
```
POST /api/interpretation/full-birth-chart/all
```

### Gerar Seção Específica
```
POST /api/interpretation/full-birth-chart/section
Body: {
  "section": "power" | "triad" | "personal" | "houses" | "karma" | "synthesis",
  ...
}
```

---

## Exemplo de Uso

```python
import requests

data = {
    "name": "Maria Silva",
    "birthDate": "15/03/1990",
    "birthTime": "14:30",
    "birthPlace": "São Paulo, SP, Brasil",
    "language": "pt",
    "sunSign": "Peixes",
    "moonSign": "Leão",
    "ascendant": "Aquário",
    # ... outros dados
}

response = requests.post(
    "http://localhost:8000/api/interpretation/full-birth-chart/all",
    json=data
)

result = response.json()
sections = result['sections']

for section in sections:
    print(f"{section['section']}: {section['title']}")
    print(section['content'][:200])
```

---

## Teste

Execute o script de teste:

```bash
cd backend
python3 test_full_birth_chart.py
```

O script irá:
1. Gerar todas as 6 seções
2. Validar consistência do temperamento
3. Validar consistência das dignidades
4. Salvar resultado em arquivo JSON

