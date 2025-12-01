# Testes TDD - Cosmos Astral Engine

## 📋 Visão Geral

Testes criados para validar a lógica matemática e astronômica do Cosmos Astral Engine, garantindo que as regras de validação estejam corretas.

---

## 🧪 Estrutura dos Testes

### 1. `test_cosmos_astral_engine.py`

Arquivo principal de testes com 4 classes principais:

#### TestCosmosAstralEngineValidation
Testa as regras de validação matemática:
- ✅ Limites de distância entre planetas
- ✅ Cálculo de aspectos com orbes corretos
- ✅ Validação geométrica (65° não é oposição)

#### TestTemperamentCalculation
Testa o cálculo de temperamento:
- ✅ Sistema de pontuação (Sol/Lua/Asc = 3 pts)
- ✅ Outros planetas = 1 ponto
- ✅ Validação de "elemento ausente"

#### TestShortestAngularDistance
Testa a função fundamental de cálculo:
- ✅ Distância entre mesmas posições = 0°
- ✅ Distância oposta = 180°
- ✅ Cálculo através de 360°

#### TestCosmosValidationModule
Testa o módulo de validação:
- ✅ `validate_mercury_sun_distance()`
- ✅ `validate_venus_sun_distance()`
- ✅ `validate_venus_mercury_distance()`
- ✅ `validate_aspect()`
- ✅ `calculate_temperament_points()`
- ✅ `validate_temperament_interpretation()`

#### TestCosmosAstralEnginePrompt
Testa o prompt mestre:
- ✅ Contém nome "Cosmos Astral Engine"
- ✅ Contém regras de validação
- ✅ Contém tabela de orbes
- ✅ Contém cálculo de temperamento
- ✅ Contém os 5 passos

---

## 🔧 Módulo de Validação

### `cosmos_validation.py`

Módulo criado para implementar as funções de validação testáveis:

#### Funções Principais:

1. **`validate_mercury_sun_distance()`**
   - Valida distância Mercúrio x Sol (máx 28°)

2. **`validate_venus_sun_distance()`**
   - Valida distância Vênus x Sol (máx 48°)

3. **`validate_venus_mercury_distance()`**
   - Valida distância Vênus x Mercúrio (máx 76°)

4. **`validate_aspect()`**
   - Valida se um aspecto específico existe entre dois planetas

5. **`calculate_temperament_points()`**
   - Calcula pontos de temperamento por elemento

6. **`validate_temperament_interpretation()`**
   - Valida se interpretação de temperamento está correta

---

## ✅ Casos de Teste Críticos

### Limites Astronômicos

1. **Mercúrio x Sol**
   - ✅ Distância de 28° = válida (limite)
   - ✅ Distância de 29° = inválida
   - ✅ Conjunção 0-10° = válida

2. **Vênus x Sol**
   - ✅ Distância de 48° = válida (limite)
   - ✅ Distância de 49° = inválida
   - ✅ Semi-Sextil 30° = válido
   - ✅ Semi-Quadratura 45° = válida

3. **Vênus x Mercúrio**
   - ✅ Distância de 76° = válida (limite)
   - ✅ Distância de 77° = inválida
   - ✅ Sextil = válido

### Orbes de Aspectos

1. **Conjunção (0°)**
   - ✅ Orbe ±8° (0-8° ou 352-360°)
   - ✅ 9° = fora do orbe

2. **Sextil (60°)**
   - ✅ Orbe ±4° (56-64°)
   - ✅ 65° = fora do orbe (não pode ser interpretado como oposição)

3. **Quadratura (90°)**
   - ✅ Orbe ±6° (84-96°)
   - ✅ 97° = fora do orbe

4. **Trígono (120°)**
   - ✅ Orbe ±8° (112-128°)
   - ✅ 129° = fora do orbe

5. **Oposição (180°)**
   - ✅ Orbe ±8° (172-188°)
   - ✅ 189° = fora do orbe

6. **Quincúncio (150°)**
   - ✅ Orbe ±2° (148-152°)
   - ✅ 153° = fora do orbe

### Temperamento

1. **Pontuação**
   - ✅ Sol/Lua/Asc = 3 pontos cada
   - ✅ Outros planetas = 1 ponto cada

2. **Validação de Interpretação**
   - ✅ Não pode dizer "ausente" se elemento tem planetas
   - ✅ Exemplo: Lua, Marte e Vênus em Fogo = 5 pontos (não pode ser "ausente")

---

## 🚀 Como Executar os Testes

```bash
cd backend
source venv/bin/activate
pytest tests/unit/test_cosmos_astral_engine.py -v
```

### Executar apenas testes críticos:

```bash
pytest tests/unit/test_cosmos_astral_engine.py -v -m critical
```

### Executar com cobertura:

```bash
pytest tests/unit/test_cosmos_astral_engine.py --cov=app.services.cosmos_validation --cov-report=html
```

---

## 📊 Cobertura Esperada

Os testes devem cobrir:

- ✅ 100% das regras de validação astronômica
- ✅ 100% dos limites de distância
- ✅ 100% dos orbes de aspectos
- ✅ 100% do cálculo de temperamento
- ✅ 100% das funções do módulo de validação

---

## 📝 Notas

- Todos os testes estão marcados com `@pytest.mark.critical` e `@pytest.mark.unit`
- Testes seguem padrão TDD (Test-Driven Development)
- Cada teste valida uma regra específica do Cosmos Astral Engine
- Módulo `cosmos_validation.py` foi criado para tornar a lógica testável

---

**Data de Criação:** 30/11/2025  
**Status:** ✅ Testes Criados e Prontos para Execução

