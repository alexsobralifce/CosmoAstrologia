# 🔒 Padrão de Validação de Cálculos Astrológicos

## 📋 Princípios Fundamentais

**TODAS as técnicas astrológicas devem seguir este padrão:**

1. ✅ **Validar parâmetros de entrada** antes de qualquer cálculo
2. ✅ **Calcular usando biblioteca** (Swiss Ephemeris via kerykeion)
3. ✅ **Validar dados calculados** antes de usar
4. ✅ **Usar IA apenas para interpretação** dos dados já calculados e validados

---

## 🔄 Fluxo Obrigatório

```
┌─────────────────────────────────────────────────────────┐
│ 1. VALIDAÇÃO DE PARÂMETROS DE ENTRADA                   │
│    - Data de nascimento válida                          │
│    - Hora de nascimento válida (HH:MM)                  │
│    - Coordenadas válidas (-90 a 90, -180 a 180)          │
│    - Ano alvo válido (se aplicável)                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. CÁLCULO USANDO BIBLIOTECA (Swiss Ephemeris)         │
│    - calculate_solar_return()                           │
│    - calculate_birth_chart()                             │
│    - calculate_future_transits()                         │
│    - etc.                                                │
│    ⚠️ NUNCA aceitar dados do frontend sem recalcular    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. VALIDAÇÃO DOS DADOS CALCULADOS                       │
│    - Campos obrigatórios presentes                       │
│    - Signos válidos (12 signos do zodíaco)              │
│    - Graus dentro do range (0-30)                        │
│    - Casas válidas (1-12)                                │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. INTERPRETAÇÃO COM IA (se dados válidos)              │
│    - Buscar contexto no RAG                             │
│    - Gerar interpretação com IA                          │
│    - Retornar interpretação + fontes                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Validações Implementadas

### 1. Validação de Parâmetros (`calculation_validator.py`)

#### `validate_birth_date(birth_date: datetime)`

- ✅ Data não pode ser no futuro
- ✅ Data não pode ser antes de 1800
- ✅ Data não pode ser mais de 100 anos no futuro

#### `validate_birth_time(birth_time: str)`

- ✅ Formato deve ser "HH:MM"
- ✅ Hora entre 00-23
- ✅ Minuto entre 00-59

#### `validate_coordinates(latitude: float, longitude: float)`

- ✅ Latitude entre -90 e 90 graus
- ✅ Longitude entre -180 e 180 graus
- ✅ Ambos devem ser números

#### `validate_target_year(target_year: int, birth_year: int)`

- ✅ Ano alvo não pode ser antes do nascimento
- ✅ Ano alvo não pode ser mais de 100 anos após nascimento

#### `validate_astrological_parameters(...)`

- ✅ Valida todos os parâmetros de uma vez
- ✅ Retorna erros consolidados
- ✅ Retorna parâmetros validados

### 2. Validação de Dados Calculados

#### `validate_calculated_chart_data(chart_data: Dict)`

- ✅ Campos obrigatórios presentes (sun_sign, moon_sign, ascendant_sign)
- ✅ Signos são válidos (12 signos do zodíaco)
- ✅ Dados não estão vazios ou None

#### `ensure_calculation_before_interpretation(...)`

- ✅ Executa função de cálculo
- ✅ Valida dados calculados
- ✅ Retorna erro se cálculo ou validação falhar

---

## 🔧 Exemplo de Implementação

### Antes (❌ INCORRETO):

```python
# Aceita dados do frontend sem validar ou recalcular
solar_return_ascendant = request.solar_return_ascendant
solar_return_sun_house = request.solar_return_sun_house

# Usa dados não validados diretamente na IA
interpretation = generate_interpretation(...)
```

### Depois (✅ CORRETO):

```python
# 1. Validar parâmetros
is_valid, error_msg, validated_params = validate_astrological_parameters(
    birth_date=birth_date,
    birth_time=request.birth_time,
    latitude=request.latitude,
    longitude=request.longitude,
    target_year=request.target_year
)

if not is_valid:
    raise HTTPException(status_code=400, detail=error_msg)

# 2. Calcular usando biblioteca (OBRIGATÓRIO)
recalculated_data, calc_error = ensure_calculation_before_interpretation(
    calculate_solar_return,
    validate_calculated_chart_data,
    birth_date=birth_date,
    birth_time=request.birth_time,
    latitude=request.latitude,
    longitude=request.longitude,
    target_year=request.target_year
)

if calc_error or not recalculated_data:
    raise HTTPException(status_code=500, detail=calc_error)

# 3. Extrair dados validados
solar_return_ascendant = recalculated_data.get("ascendant_sign")
solar_return_sun_house = recalculated_data.get("sun_house")

# 4. Validar dados essenciais
if not solar_return_ascendant or solar_return_sun_house is None:
    raise HTTPException(status_code=500, detail="Dados essenciais não calculados")

# 5. Usar dados validados na IA
interpretation = generate_interpretation(...)
```

---

## ⚠️ Regras Críticas

### 1. **NUNCA aceitar dados do frontend sem recalcular**

```python
# ❌ ERRADO
solar_return_ascendant = request.solar_return_ascendant

# ✅ CORRETO
recalculated_data = calculate_solar_return(...)
solar_return_ascendant = recalculated_data.get("ascendant_sign")
```

### 2. **SEMPRE validar parâmetros antes de calcular**

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

---

## 📊 Técnicas que Seguem o Padrão

### ✅ Implementadas Corretamente:

1. **Revolução Solar** ✅

   - Valida parâmetros
   - Recalcula usando `calculate_solar_return()`
   - Valida dados calculados
   - Usa IA apenas para interpretação

2. **Trânsitos** ✅

   - Valida parâmetros
   - Calcula usando `calculate_future_transits()`
   - Valida aspectos calculados
   - Usa IA apenas para interpretação

3. **Mapa Astral Completo** ✅
   - Valida parâmetros
   - Calcula usando `calculate_birth_chart()`
   - Valida dados calculados
   - Usa IA apenas para interpretação

### ⚠️ Precisam Atualização:

1. **Progressões Secundárias** (quando implementar)

   - Deve seguir o mesmo padrão
   - Validar parâmetros
   - Calcular usando biblioteca
   - Validar dados
   - Usar IA para interpretação

2. **Retorno Lunar** (quando implementar)

   - Deve seguir o mesmo padrão

3. **Direções Primárias** (quando implementar)
   - Deve seguir o mesmo padrão

---

## 🔍 Checklist para Novas Técnicas

Ao implementar uma nova técnica astrológica, verificar:

- [ ] Validação de parâmetros de entrada implementada
- [ ] Cálculo usando biblioteca (Swiss Ephemeris) implementado
- [ ] Validação de dados calculados implementada
- [ ] Erros de validação retornam HTTP 400 (Bad Request)
- [ ] Erros de cálculo retornam HTTP 500 (Internal Server Error)
- [ ] IA usada apenas para interpretação (não para cálculo)
- [ ] Dados do frontend nunca aceitos sem recalcular
- [ ] Documentação atualizada

---

## 📚 Referências

- `backend/app/services/calculation_validator.py` - Validador de parâmetros
- `backend/app/services/chart_validator.py` - Validador de mapas calculados
- `backend/app/services/swiss_ephemeris_calculator.py` - Biblioteca de cálculos
- `backend/app/api/interpretation.py` - Exemplos de implementação

---

**Última atualização:** 2024  
**Status:** ✅ Padrão implementado e documentado
