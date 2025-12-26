# 🔒 Padrão de Implementação: Revolução Solar

## 📋 Princípio Fundamental

> **A IA APENAS ORGANIZA E INTERPRETA CÁLCULOS REALIZADOS PELO SISTEMA**
>
> **NADA VAI PARA O FRONTEND SEM ESTAR CALCULADO E VALIDADO**

---

## 🎯 Arquitetura de Validação

### Fluxo Obrigatório (Nunca Fuja Deste Padrão)

```
┌─────────────────────────────────────────────────────────┐
│ 1. VALIDAÇÃO DE PARÂMETROS DE ENTRADA                    │
│    - Validar data, hora, coordenadas, ano                │
│    - Retornar HTTP 400 se inválido                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. CÁLCULO USANDO BIBLIOTECA (Swiss Ephemeris)          │
│    - calculate_birth_chart() → Mapa Natal                │
│    - calculate_solar_return() → Revolução Solar           │
│    - NUNCA aceitar dados do frontend sem recalcular      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. VALIDAÇÃO DOS DADOS CALCULADOS                        │
│    - validate_calculated_chart_data()                    │
│    - Verificar campos obrigatórios                       │
│    - Verificar signos válidos                             │
│    - Retornar HTTP 500 se inválido                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. EXTRAÇÃO E VALIDAÇÃO DE DADOS ESPECÍFICOS             │
│    - Extrair dados do mapa natal                          │
│    - Extrair dados da revolução solar                    │
│    - Validar que dados essenciais estão presentes        │
│    - Separar claramente: Natal vs Revolução Solar         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. BUSCA NO RAG (Contexto para IA)                       │
│    - Buscar conhecimento astrológico                      │
│    - Incluir técnicas complementares                     │
│    - Limitar contexto relevante                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 6. INTERPRETAÇÃO COM IA (Apenas Organização)             │
│    - Prompt com dados CALCULADOS e VALIDADOS              │
│    - Instruções claras para separar Natal vs RS          │
│    - IA apenas organiza e interpreta (NÃO calcula)        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 7. RETORNO AO FRONTEND                                   │
│    - Apenas dados calculados e validados                 │
│    - Interpretação baseada em cálculos reais             │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Implementação Passo a Passo

### 1. Validação de Parâmetros de Entrada

```python
from app.services.calculation_validator import validate_astrological_parameters

# VALIDAÇÃO 1: Validar parâmetros de entrada
birth_date = None
if request.birth_date:
    try:
        birth_date = datetime.fromisoformat(request.birth_date.replace('Z', '+00:00'))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de data inválido: {str(e)}"
        )

# Validar todos os parâmetros
is_valid, error_msg, validated_params = validate_astrological_parameters(
    birth_date=birth_date,
    birth_time=request.birth_time,
    latitude=request.latitude,
    longitude=request.longitude,
    target_year=request.target_year
)

if not is_valid:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Parâmetros inválidos: {error_msg}"
    )
```

**Regras:**

- ✅ Sempre validar antes de calcular
- ✅ Retornar HTTP 400 para parâmetros inválidos
- ✅ Mensagens de erro claras e específicas

---

### 2. Cálculo Usando Biblioteca (OBRIGATÓRIO)

```python
from app.services.swiss_ephemeris_calculator import (
    calculate_birth_chart,
    calculate_solar_return
)

# OBRIGATÓRIO: Sempre recalcular usando biblioteca
# NUNCA aceitar dados do frontend sem recalcular
if not (birth_date and request.birth_time and
        request.latitude is not None and request.longitude is not None):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Dados completos de nascimento são obrigatórios"
    )

# Normalizar datetime (remover timezone se presente)
if birth_date.tzinfo is not None:
    birth_date_naive = birth_date.replace(tzinfo=None)
else:
    birth_date_naive = birth_date

# Calcular Mapa Natal
natal_chart = calculate_birth_chart(
    birth_date=birth_date_naive,
    birth_time=request.birth_time,
    latitude=request.latitude,
    longitude=request.longitude
)

# Calcular Revolução Solar
recalculated_data = calculate_solar_return(
    birth_date=birth_date_naive,
    birth_time=request.birth_time,
    latitude=request.latitude,
    longitude=request.longitude,
    target_year=request.target_year
)
```

**Regras:**

- ✅ **SEMPRE** recalcular usando biblioteca
- ✅ **NUNCA** aceitar dados do frontend sem recalcular
- ✅ Usar Swiss Ephemeris (kerykeion) como fonte única de verdade
- ✅ Normalizar datetimes antes de calcular

---

### 3. Validação dos Dados Calculados

```python
from app.services.calculation_validator import validate_calculated_chart_data

# Validar mapa natal calculado
is_valid_natal, error_natal = validate_calculated_chart_data(natal_chart)
if not is_valid_natal:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Erro ao validar mapa natal: {error_natal}"
    )

# Validar revolução solar calculada
is_valid_solar, error_solar = validate_calculated_chart_data(recalculated_data)
if not is_valid_solar:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Dados calculados inválidos: {error_solar}"
    )
```

**Regras:**

- ✅ Validar **TODOS** os dados calculados
- ✅ Retornar HTTP 500 para erros de cálculo/validação
- ✅ Verificar campos obrigatórios e signos válidos

---

### 4. Extração e Validação de Dados Específicos

```python
# Extrair dados validados do mapa natal
natal_sun_sign = natal_chart.get("sun_sign")
natal_sun_house = natal_chart.get("sun_house")
natal_ascendant = natal_chart.get("ascendant_sign")
natal_moon_sign = natal_chart.get("moon_sign")
natal_moon_house = natal_chart.get("moon_house")

# Validar que dados essenciais do mapa natal foram calculados
if not natal_sun_sign or not natal_ascendant or not natal_moon_sign:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Dados essenciais do mapa natal não foram calculados corretamente"
    )

# Extrair dados validados da revolução solar
solar_return_ascendant = recalculated_data.get("ascendant_sign")
solar_return_sun_house = recalculated_data.get("sun_house")
solar_return_sun_sign = recalculated_data.get("sun_sign")
solar_return_moon_sign = recalculated_data.get("moon_sign")
solar_return_moon_house = recalculated_data.get("moon_house")

# Validar que dados essenciais da revolução solar foram calculados
if not solar_return_ascendant or solar_return_sun_house is None:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Dados essenciais da Revolução Solar não foram calculados corretamente"
    )

# Calcular idade corretamente
target_year = request.target_year or datetime.now().year
birth_year = birth_date_naive.year
age = target_year - birth_year
```

**Regras:**

- ✅ Extrair dados **APENAS** dos cálculos validados
- ✅ Validar que dados essenciais estão presentes
- ✅ Separar claramente: Mapa Natal vs Revolução Solar
- ✅ Calcular idade corretamente

---

### 5. Busca no RAG (Contexto para IA)

```python
from app.services.rag_service_fastembed import get_rag_service

rag_service = get_rag_service()

# Buscar contexto do RAG - Expandido para incluir outras técnicas
queries = [
    # Revolução Solar (principal)
    f"revolução solar retorno solar {solar_return_ascendant} casa {solar_return_sun_house}",
    f"casa {solar_return_sun_house} astrologia revolução solar significado interpretação",

    # Técnicas Complementares
    f"progressões secundárias revolução solar complemento técnicas previsão",
    f"retorno saturno jupiter revolução solar integração análise",
    f"trânsitos revolução solar ano {target_year} previsão astrológica",
    f"direções primárias profecção anual revolução solar",

    # Contexto específico
    f"ascendente {solar_return_ascendant} revolução solar interpretação",
    f"lua {solar_return_moon_sign} casa {solar_return_moon_house} revolução solar",
]

all_rag_results = []
if rag_service:
    for q in queries:
        try:
            results = rag_service.search(q, top_k=6, expand_query=True)
            all_rag_results.extend(results)
        except Exception as e:
            print(f"[WARNING] Erro ao buscar no RAG: {e}")

# Remover duplicatas e limitar contexto
seen_texts = set()
unique_results = []
for result in sorted(all_rag_results, key=lambda x: x.get('score', 0), reverse=True):
    text_key = result.get('text', '')[:100]
    if text_key not in seen_texts:
        seen_texts.add(text_key)
        unique_results.append(result)
        if len(unique_results) >= 15:
            break

context_text = "\n\n".join([doc.get('text', '') for doc in unique_results[:12] if doc.get('text')])
```

**Regras:**

- ✅ Buscar contexto relevante no RAG
- ✅ Incluir técnicas complementares
- ✅ Limitar contexto para evitar sobrecarga
- ✅ Tratar erros de busca graciosamente

---

### 6. Interpretação com IA (Apenas Organização)

```python
from app.services.ai_provider_service import get_ai_provider

provider = get_ai_provider()

if not provider:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Serviço de IA não disponível"
    )

# Prompt do Sistema - Instruções Críticas
system_prompt = """Você é um Astrólogo Sênior especializado em Revolução Solar e técnicas complementares de previsão astrológica.

IMPORTANTE: Você DEVE sempre separar claramente os dados do MAPA NATAL dos dados da REVOLUÇÃO SOLAR. NUNCA confunda ou misture esses dados.

Além da Revolução Solar, você conhece outras técnicas astrológicas relevantes:
- Progressões Secundárias (evolução interna ao longo do tempo)
- Retorno de Saturno (maturidade e responsabilidades, ~29.5 anos)
- Retorno de Júpiter (expansão e oportunidades, ~12 anos)
- Trânsitos (influências atuais dos planetas)
- Direções Primárias (eventos importantes, 1 grau = 1 ano)
- Profecção Anual (foco anual por casa astrológica)

Quando apropriado e se o contexto de referência mencionar, você pode sugerir brevemente como outras técnicas podem complementar a análise da Revolução Solar, mas mantenha o foco principal na Revolução Solar."""

# Prompt do Usuário - Dados Calculados e Validados
user_prompt = f"""Dados para Análise da Revolução Solar de {target_year}:

=== MAPA NATAL (Dados de Nascimento) ===
- Idade em {target_year}: {age} anos
- Signo Solar: {natal_sun_sign} (Casa {natal_sun_house if natal_sun_house else 'N/A'})
- Ascendente: {natal_ascendant}
- Lua: {natal_moon_sign} (Casa {natal_moon_house if natal_moon_house else 'N/A'})

=== REVOLUÇÃO SOLAR {target_year} (Dados do Ano) ===
- Ascendente: {solar_return_ascendant}
- Sol: {solar_return_sun_sign} na Casa {solar_return_sun_house}
- Lua: {solar_return_moon_sign} na Casa {solar_return_moon_house}

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_text[:4000] if context_text else "Informações gerais sobre revolução solar e técnicas complementares."}

Forneça uma interpretação completa e detalhada da revolução solar.

INSTRUÇÕES CRÍTICAS:
1. SEMPRE separe claramente os dados do MAPA NATAL dos dados da REVOLUÇÃO SOLAR
2. NUNCA atribua dados da Revolução Solar ao Mapa Natal (ex: se a Lua da RS está em Aquário, isso NÃO significa que a Lua natal está em Aquário)
3. Use os dados do Mapa Natal apenas como contexto de fundo
4. Foque principalmente na Revolução Solar e seus significados para o ano {target_year}
5. Se o contexto mencionar outras técnicas (Progressões, Retorno de Saturno/Júpiter, Trânsitos, Direções, Profecção), você pode mencionar brevemente como elas podem complementar esta análise
6. Ao final, adicione uma nota sobre outras técnicas astrológicas disponíveis que podem enriquecer a análise
7. Seja específico e prático, evitando generalidades
8. Calcule a idade corretamente: {age} anos em {target_year}"""

# Gerar interpretação
interpretation_text = provider.generate_text(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    temperature=0.7,
    max_tokens=4000
)
```

**Regras:**

- ✅ **IA APENAS organiza e interpreta** - NUNCA calcula
- ✅ Passar **APENAS** dados calculados e validados
- Instruções claras para separar Mapa Natal vs Revolução Solar
- ✅ Exemplos do que NÃO fazer
- ✅ Limitar tokens e temperatura

---

### 7. Retorno ao Frontend

```python
from app.api.interpretation import SourceItem, InterpretationResponse

sources_list = [
    SourceItem(
        source=r.get('source', 'knowledge_base'),
        page=r.get('page', 1),
        relevance=r.get('score', 0.5)
    )
    for r in unique_results[:5]
]

return InterpretationResponse(
    interpretation=interpretation_text,
    sources=sources_list,
    query_used=f"Revolução Solar {solar_return_ascendant} Casa {solar_return_sun_house}",
    generated_by=provider.get_provider_name()
)
```

**Regras:**

- ✅ Retornar **APENAS** dados calculados e validados
- ✅ Interpretação baseada em cálculos reais
- ✅ Incluir fontes do RAG
- ✅ Formato padronizado de resposta

---

## ⚠️ Regras Críticas (NUNCA Violar)

### 1. **NUNCA aceitar dados do frontend sem recalcular**

```python
# ❌ ERRADO
solar_return_ascendant = request.solar_return_ascendant

# ✅ CORRETO
recalculated_data = calculate_solar_return(...)
solar_return_ascendant = recalculated_data.get("ascendant_sign")
```

### 2. **SEMPRE validar antes de calcular**

```python
# ❌ ERRADO
result = calculate_solar_return(birth_date, birth_time, lat, lng)

# ✅ CORRETO
is_valid, error, _ = validate_astrological_parameters(...)
if not is_valid:
    raise HTTPException(400, detail=error)
result = calculate_solar_return(...)
```

### 3. **SEMPRE validar dados calculados antes de usar**

```python
# ❌ ERRADO
interpretation = generate_interpretation(calculated_data)

# ✅ CORRETO
is_valid, error = validate_calculated_chart_data(calculated_data)
if not is_valid:
    raise HTTPException(500, detail=error)
interpretation = generate_interpretation(calculated_data)
```

### 4. **SEMPRE usar biblioteca de cálculos (Swiss Ephemeris)**

```python
# ❌ ERRADO (inventar dados)
data = {"sun_sign": "Leão", "moon_sign": "Câncer"}

# ✅ CORRETO (calcular com biblioteca)
from app.services.swiss_ephemeris_calculator import calculate_birth_chart
data = calculate_birth_chart(birth_date, birth_time, lat, lng)
```

### 5. **IA APENAS organiza e interpreta - NUNCA calcula**

```python
# ❌ ERRADO (IA calculando)
prompt = "Calcule a posição do Sol na Revolução Solar..."

# ✅ CORRETO (IA interpretando dados calculados)
prompt = f"Dados calculados: Sol na Casa {solar_return_sun_house}. Interprete..."
```

### 6. **SEMPRE separar Mapa Natal vs Revolução Solar**

```python
# ❌ ERRADO (misturar dados)
prompt = f"Lua: {moon_sign} Casa {moon_house}"

# ✅ CORRETO (separar claramente)
prompt = f"""
=== MAPA NATAL ===
Lua: {natal_moon_sign} Casa {natal_moon_house}

=== REVOLUÇÃO SOLAR ===
Lua: {solar_return_moon_sign} Casa {solar_return_moon_house}
"""
```

---

## 📊 Checklist de Implementação

Para cada nova funcionalidade de Revolução Solar:

- [ ] Validação de parâmetros de entrada implementada
- [ ] Cálculo usando biblioteca (Swiss Ephemeris) implementado
- [ ] Validação de dados calculados implementada
- [ ] Extração e validação de dados específicos implementada
- [ ] Separação clara: Mapa Natal vs Revolução Solar
- [ ] Busca no RAG para contexto
- [ ] Prompt da IA com instruções críticas
- [ ] IA apenas organiza e interpreta (não calcula)
- [ ] Retorno ao frontend apenas com dados calculados e validados
- [ ] Testes com dados reais
- [ ] Documentação atualizada

---

## 🔍 Validações Específicas da Revolução Solar

### Validação do Timing Exato

Baseado na pesquisa, o Sol pode retornar à posição natal no dia anterior ou posterior ao aniversário. O sistema já calcula o momento exato usando `calculate_solar_return()`.

### Validação da Posição do Sol

Após calcular, verificar que o Sol da Revolução Solar está na mesma posição do Sol natal (dentro de uma tolerância de minutos/segundos).

### Validação de Localização

A Revolução Solar deve ser calculada para a localização atual (não necessariamente a de nascimento), mas o sistema atual usa a localização de nascimento. Isso pode ser expandido no futuro.

---

## 📚 Referências

- `backend/app/services/calculation_validator.py` - Validador de parâmetros
- `backend/app/services/chart_validator.py` - Validador de mapas
- `backend/app/services/swiss_ephemeris_calculator.py` - Biblioteca de cálculos
- `backend/app/api/interpretation.py` - Implementação do endpoint
- `docs/PADRAO_VALIDACAO_CALCULOS.md` - Padrão geral de validação

---

**Última atualização:** 2024  
**Status:** ✅ Padrão implementado e documentado  
**Regra de Ouro:** A IA APENAS organiza e interpreta. NADA vai para o frontend sem estar calculado e validado.
