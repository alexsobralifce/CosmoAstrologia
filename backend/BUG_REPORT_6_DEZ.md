# Bug Report: Aspectos Incorretos para 6 de Dezembro de 2025

## Problema Reportado

**Data:** 6 de Dezembro de 2025  
**Score Reportado:** 28  
**Aspectos Reportados:**
- Sol em sextil com Casa 2 ✅
- Vênus em sextil com Casa 2 ✅
- Sol em sextil com Casa 10 ❌ **INCORRETO**
- Vênus em sextil com Casa 10 ✅

## Validação Matemática

### Dados do Usuário
- **Data de nascimento:** 20/10/1981 às 13:30
- **Localização:** -23.5505, -46.6333
- **Ação:** `pedir_aumento`
- **Cúspides:**
  - Casa 2: 314.080776°
  - Casa 10: 184.393240°

### Resultados por Horário

#### 00:00
- **Sol:** 254.107282°
  - vs Casa 2: 59.97° (sextil ✅, +7 pontos)
  - vs Casa 10: 69.71° (nenhum aspecto ❌)
- **Vênus:** 246.484352°
  - vs Casa 2: 67.60° (sextil ✅, +7 pontos)
  - vs Casa 10: 62.09° (sextil ✅, +7 pontos)
- **Score Real:** 21 (não 28)

#### 06:00
- **Sol:** 254.364137°
  - vs Casa 2: 59.72° (sextil ✅, +7 pontos)
  - vs Casa 10: 69.97° (nenhum aspecto ❌)
- **Vênus:** 246.800643°
  - vs Casa 2: 67.28° (sextil ✅, +7 pontos)
  - vs Casa 10: 62.41° (sextil ✅, +7 pontos)
- **Score Real:** 21 (não 28)

#### 12:00
- **Sol:** 254.617924°
  - vs Casa 2: 59.46° (sextil ✅, +7 pontos)
  - vs Casa 10: 70.22° (nenhum aspecto ❌) - **10.22° longe de 60°**
- **Vênus:** 247.114932°
  - vs Casa 2: 66.97° (sextil ✅, +7 pontos)
  - vs Casa 10: 62.72° (sextil ✅, +7 pontos)
- **Score Real:** 21 (não 28)

#### 18:00
- **Sol:** 254.868426°
  - vs Casa 2: 59.21° (sextil ✅, +7 pontos)
  - vs Casa 10: 70.48° (nenhum aspecto ❌)
- **Vênus:** 247.427547°
  - vs Casa 2: 66.65° (sextil ✅, +7 pontos)
  - vs Casa 10: 63.03° (sextil ✅, +7 pontos)
- **Score Real:** 21 (não 28)

## Análise do Problema

### Aspecto Incorreto: Sol em sextil com Casa 10

**Para TODOS os horários:**
- O Sol está a **~70°** da Casa 10
- A diferença para sextil (60°) é de **~10°**
- Isso está **FORA do orbe de 8°**
- **Nenhum aspecto deveria ser detectado**

### Score Correto

**Score Real:** 21 pontos (3 aspectos válidos × 7 pontos cada)  
**Score Reportado:** 28 pontos (4 aspectos × 7 pontos cada)  
**Diferença:** +7 pontos (um aspecto inexistente)

## Causa Raiz

O sistema está reportando um aspecto que **NÃO existe**:
- O Sol **NÃO** está em sextil com a Casa 10 em nenhum horário de 6/12/2025
- O ângulo está em ~70°, muito longe de 60° (sextil)
- A diferença de 10.22° está **bem além** do orbe de 8°

### Possíveis Causas

1. **Frontend agrupando incorretamente:** O frontend pode estar coletando aspectos de diferentes horários e mostrando todos, mesmo que alguns não existam em todos os horários
2. **Backend retornando dados incorretos:** O backend pode estar detectando aspectos incorretamente (mas a validação mostra que não)
3. **Cache de dados antigos:** Dados antigos podem estar sendo exibidos
4. **Bug no agrupamento por data:** O código que agrupa momentos por data pode estar incluindo aspectos que não pertencem àquela data

## Recomendações

1. **Verificar código de agrupamento no frontend:** Garantir que apenas aspectos que existem em pelo menos um momento do dia sejam exibidos
2. **Adicionar validação no frontend:** Verificar se os aspectos realmente pertencem àquela data antes de exibir
3. **Limpar cache:** Garantir que dados antigos não estejam sendo exibidos
4. **Adicionar logs:** Logar quais aspectos estão sendo detectados em cada momento para rastrear o problema

## Status

❌ **BUG CONFIRMADO** - Aspecto inexistente sendo reportado

