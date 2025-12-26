# Bug Report: Aspectos Incorretos para 12 de Dezembro de 2025

## Problema Reportado

**Data:** 12 de Dezembro de 2025 às 18:00  
**Score Reportado:** 17  
**Aspectos Reportados:**
- Mercúrio em sextil com Casa 10 ❌ **INCORRETO** (Mercúrio não está na lista de planetas benéficos)
- Vênus em sextil com Casa 10 ❌ **INCORRETO** (ângulo 70.58°, fora do orbe)
- Vênus em sextil com Casa 2 ✅ **CORRETO**

## Validação Matemática

### Dados do Usuário
- **Data de nascimento:** 20/10/1981 às 13:30
- **Localização:** -23.5505, -46.6333
- **Ação:** `pedir_aumento`
- **Planetas benéficos:** ['Júpiter', 'Sol', 'Vênus']
- **Cúspides:**
  - Casa 2: 314.080776°
  - Casa 10: 184.393240°

### Resultados para 12/12/2025 18:00

#### Mercúrio
- **Status:** ❌ **NÃO está na lista de planetas benéficos** para `pedir_aumento`
- **Conclusão:** Mercúrio não deveria ser verificado nem reportado

#### Vênus: 254.976383°
- **vs Casa 2:** 59.10° (sextil ✅, +7 pontos)
- **vs Casa 10:** 70.58° (nenhum aspecto ❌) - **10.58° longe de 60°**

### Score Correto

**Score Real:** 7 pontos (1 aspecto válido)  
**Score Reportado:** 17 pontos  
**Diferença:** +10 pontos (2 aspectos inexistentes)

## Análise do Problema

### Aspectos Incorretos

1. **Mercúrio em sextil com Casa 10:**
   - Mercúrio **NÃO** está na lista de planetas benéficos para `pedir_aumento`
   - O código deveria ignorar Mercúrio completamente
   - **Possível causa:** Bug no código ou dados sendo exibidos de outra ação

2. **Vênus em sextil com Casa 10:**
   - O ângulo é **70.58°**, muito longe de 60° (sextil)
   - Diferença de **10.58°** está **bem além** do orbe de 8°
   - **Nenhum aspecto deveria ser detectado**

### Possíveis Causas

1. **Frontend agrupando incorretamente:** Aspectos de outros horários sendo mostrados
2. **Backend retornando dados incorretos:** Cálculo ou validação com bug
3. **Cache de dados antigos:** Dados de outra ação ou data sendo exibidos
4. **Problema de timezone:** Data/hora sendo calculada incorretamente

## Recomendações

1. **Verificar código de agrupamento no frontend:** Garantir que apenas aspectos válidos sejam exibidos
2. **Adicionar validação rigorosa:** Verificar se planetas estão na lista de benéficos antes de calcular
3. **Limpar cache:** Garantir que dados antigos não estejam sendo exibidos
4. **Adicionar logs:** Logar quais aspectos estão sendo detectados para rastrear o problema

## Status

❌ **BUG CONFIRMADO** - Aspectos inexistentes sendo reportados

