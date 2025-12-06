# Bug Report: Aspectos Incorretos para 28 de Dezembro de 2025 (Primeiro Encontro)

## Problema Reportado

**Data:** 28 de Dezembro de 2025 às 18:00  
**Ação:** `primeiro_encontro`  
**Score Reportado:** 32  
**Aspectos Reportados:** 6 aspectos

## Validação Matemática

### Dados do Usuário
- **Data de nascimento:** 20/10/1981 às 13:30
- **Localização:** -23.5505, -46.6333
- **Ação:** `primeiro_encontro`
- **Casas primárias:** [5, 7]
- **Casas secundárias:** [1, 11]
- **Planetas benéficos:** ['Vênus', 'Júpiter', 'Lua']

### Resultados para 28/12/2025 18:00

#### Lua: 20.308426°
- **vs Casa 1 (SECUNDÁRIA):** 96.23° (quadratura ❌, não está nos preferidos)
- **vs Casa 5 (PRIMÁRIA):** 23.77° (nenhum aspecto ❌) - **23.77° longe de 0° (conjunção)**
- **vs Casa 7 (PRIMÁRIA):** 83.77° (quadratura ❌, não está nos preferidos)
- **vs Casa 11 (SECUNDÁRIA):** 165.92° (nenhum aspecto ❌)

#### Vênus: 275.115914°
- **vs Casa 1 (SECUNDÁRIA):** 8.96° (nenhum aspecto ❌) - **8.96° longe de 0° (conjunção)**
- **vs Casa 5 (PRIMÁRIA):** 128.96° (nenhum aspecto ❌) - **8.96° longe de 120° (trígono)**
- **vs Casa 7 (PRIMÁRIA):** 171.04° (nenhum aspecto ❌)
- **vs Casa 11 (SECUNDÁRIA):** 60.72° (sextil ✅, +3 pontos)

### Aspectos Reportados vs Reais

| Aspecto Reportado | Status | Ângulo Real | Diferença do Alvo |
|-------------------|--------|-------------|-------------------|
| Lua em conjunção com Casa 5 | ❌ INCORRETO | 23.77° | 23.77° > 8° |
| Vênus em trígono com Casa 5 | ❌ INCORRETO | 128.96° | 8.96° > 8° |
| Lua em sextil com Casa 7 | ❌ INCORRETO | 83.77° | 23.77° > 8° |
| Lua em trígono com Casa 1 | ❌ INCORRETO | 96.23° | 23.77° > 8° |
| Vênus em conjunção com Casa 1 | ❌ INCORRETO | 8.96° | 0.96° (quase, mas ainda fora) |
| Vênus em sextil com Casa 11 | ✅ CORRETO | 60.72° | 0.72° ≤ 8° |

### Score Correto

**Score Real:** 3 pontos (1 aspecto válido)  
**Score Reportado:** 32 pontos  
**Score Esperado (se todos os aspectos fossem válidos):** 37 pontos  
**Diferença:** +29 pontos (5 aspectos inexistentes)

## Análise do Problema

### Aspectos Incorretos

1. **Lua em conjunção com Casa 5:**
   - Ângulo real: 23.77°
   - Diferença de 0°: 23.77° > 8.0°
   - **Status:** ❌ FORA DO ORBE

2. **Vênus em trígono com Casa 5:**
   - Ângulo real: 128.96°
   - Diferença de 120°: 8.96° > 8.0°
   - **Status:** ❌ FORA DO ORBE (muito próximo, mas ainda fora)

3. **Lua em sextil com Casa 7:**
   - Ângulo real: 83.77°
   - Diferença de 60°: 23.77° > 8.0°
   - **Status:** ❌ FORA DO ORBE

4. **Lua em trígono com Casa 1:**
   - Ângulo real: 96.23°
   - Diferença de 120°: 23.77° > 8.0°
   - **Status:** ❌ FORA DO ORBE

5. **Vênus em conjunção com Casa 1:**
   - Ângulo real: 8.96°
   - Diferença de 0°: 8.96° > 8.0°
   - **Status:** ❌ FORA DO ORBE (muito próximo, mas ainda fora)

6. **Vênus em sextil com Casa 11:**
   - Ângulo real: 60.72°
   - Diferença de 60°: 0.72° ≤ 8.0°
   - **Status:** ✅ CORRETO

## Conclusão

**5 de 6 aspectos reportados estão INCORRETOS.** O sistema está reportando aspectos que não estão dentro do orbe de 8° configurado.

### Possíveis Causas

1. **Orbe maior sendo usado em algum lugar:** Algum código pode estar usando orbe maior que 8°
2. **Agrupamento incorreto no frontend:** Aspectos de outros horários sendo mostrados
3. **Cache de dados antigos:** Dados de outras datas sendo exibidos
4. **Bug no cálculo de aspectos:** A função `get_aspect_type` pode estar retornando aspectos incorretos

## Status

❌ **BUG CRÍTICO CONFIRMADO** - 83% dos aspectos reportados estão incorretos

