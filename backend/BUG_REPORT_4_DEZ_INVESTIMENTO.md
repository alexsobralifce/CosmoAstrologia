# Bug Report - 4 de Dezembro de 2025 (Investimento)

## Data: 05/12/2025

## Problema Identificado

O frontend está exibindo aspectos para 4/12/2025 que **não existem** no backend.

### Dados Exibidos no Frontend:
- **Data:** 4 de Dezembro de 2025
- **Score:** 17
- **Aspectos:**
  - Vênus em sextil com Casa 2
  - Vênus em trígono com Casa 8

### Validação Matemática (Backend):

#### 4 de Dezembro de 2025 (Todos os horários: 00:00, 06:00, 12:00, 18:00)
- **Vênus vs Casa 2:** Ângulo 69.17°-70.11° (diferença 9.17°-10.11° do sextil de 60°)
  - ❌ **FORA DO ORBE** (8.0°)
- **Vênus vs Casa 8:** Ângulo 109.89°-110.83° (diferença 9.89°-10.83° do trígono de 120°)
  - ❌ **FORA DO ORBE** (8.0°)
- **Score calculado:** 0 (nenhum aspecto válido)

#### 6 de Dezembro de 2025 (Backend retorna)
- **Score:** 17
- **Aspectos:**
  - ✅ Vênus em sextil com Casa 2
  - ✅ Vênus em trígono com Casa 8

### Conclusão

**Backend está CORRETO:**
- 4/12: 0 momentos (score 0, nenhum aspecto válido)
- 6/12: Score 17 com os aspectos corretos

**Frontend está INCORRETO:**
- Exibe aspectos de 6/12 como se fossem de 4/12
- Possível problema de agrupamento por data ou timezone

## Possíveis Causas

1. **Problema de timezone:** A data pode estar sendo interpretada incorretamente devido a diferenças de timezone
2. **Agrupamento incorreto:** O código de agrupamento pode estar misturando dados de diferentes datas
3. **Cache persistente:** Dados antigos podem estar sendo exibidos mesmo após limpar cache

## Correções Implementadas

1. ✅ Adicionados logs detalhados para rastrear:
   - Resposta da API
   - Agrupamento por data
   - Momentos em cada grupo
   - Aspectos coletados
   - Resultado final

2. ✅ Validação adicional: Apenas momentos com `score > 0` e `aspects.length > 0` são agrupados

3. ✅ Logs de aviso para momentos ignorados

## Próximos Passos

1. **Abrir console do navegador** (F12) e verificar os logs ao carregar a seção
2. **Verificar se há problema de timezone** na interpretação das datas
3. **Confirmar que apenas momentos válidos** estão sendo agrupados

