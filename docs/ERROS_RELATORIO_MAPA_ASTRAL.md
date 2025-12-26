# Análise de Erros no Relatório de Mapa Astral

## Data: 02/12/2025

## Erros Identificados no Relatório de Necio de Lima Veras

### 1. ❌ INCONSISTÊNCIA CRÍTICA: Temperamento com Valores Diferentes

**Problema:** O relatório apresenta valores completamente diferentes para os elementos em seções diferentes:

**Primeira menção (seção inicial):**
- Água: 8 pontos
- Fogo: 5 pontos
- Terra: 2 pontos
- Ar: 2 pontos
- **ELEMENTO DOMINANTE: Água**

**Segunda menção (seção "Estratégia de Tomada de Decisão"):**
- Fogo: 1 ponto
- Terra: 10 pontos
- Ar: 4 pontos
- Água: 2 pontos
- **ELEMENTO DOMINANTE: Terra**

**Causa Raiz:** A IA está ignorando o bloco pré-calculado e inventando seus próprios valores, ou diferentes seções estão recebendo dados diferentes.

**Impacto:** CRÍTICO - Invalida completamente a análise de temperamento.

---

### 2. ❌ ERRO DE DIGNIDADE: Sol em Virgem

**Problema:** O relatório menciona "Sol em Virgem, em Domicílio" quando o correto é "Sol em Virgem: PEREGRINO".

**Evidências no relatório:**
- ✅ CORRETO: "Sol: em Virgem (Terra) - PEREGRINO" (no bloco pré-calculado)
- ❌ ERRADO: "O Sol em Virgem, em Domicílio" (na interpretação)
- ❌ ERRADO: "Sol em Virgem, em Domicílio" (mencionado novamente)

**Justificativa Astrológica:**
- Sol tem domicílio em **Leão** (não Virgem)
- Mercúrio tem domicílio em **Virgem** (não Sol)
- Portanto, Sol em Virgem é **PEREGRINO** (não tem dignidade nem debilidade forte)

**Causa Raiz:** A IA está inventando dignidades ou confundindo regências.

---

### 3. ⚠️ INCONSISTÊNCIA: Múltiplas Menções de Dignidades Diferentes

**Problema:** O relatório menciona dignidades diferentes para o mesmo planeta em lugares diferentes.

**Exemplo:**
- Bloco pré-calculado diz: "Sol em Virgem: PEREGRINO"
- Interpretação diz: "Sol em Virgem, em Domicílio"

**Causa Raiz:** A IA não está seguindo rigorosamente o bloco pré-calculado.

---

## Análise Técnica

### Como o Sistema Deveria Funcionar

1. **Cálculo Pré-Computado:**
   - `calculate_temperament_from_chart()` calcula os pontos matematicamente
   - `get_planet_dignity()` identifica dignidades usando tabela fixa
   - `create_precomputed_data_block()` gera o bloco com TODOS os dados

2. **Prompt para IA:**
   - O bloco pré-calculado é inserido no prompt
   - Instruções explícitas para usar APENAS esses dados
   - Proibição de recalcular ou inventar

3. **Geração de Interpretação:**
   - A IA deveria ler o bloco pré-calculado
   - Usar EXATAMENTE os valores fornecidos
   - NÃO recalcular ou inventar

### Onde Está Falhando

1. **Múltiplas Seções:**
   - Cada seção (`power`, `triad`, `personal`, etc.) é gerada separadamente
   - Cada seção recebe o mesmo bloco pré-calculado
   - Mas a IA pode estar "esquecendo" ou ignorando o bloco em seções diferentes

2. **Prompt Não Suficientemente Enfático:**
   - Embora haja instruções, a IA ainda está inventando valores
   - Pode ser necessário reforçar ainda mais as instruções

3. **Validação Pós-Geração Ausente:**
   - Não há validação para verificar se a IA seguiu o bloco pré-calculado
   - Erros só são detectados quando o usuário lê o relatório

---

## Soluções Propostas

### 1. ✅ Reforçar Instruções no Prompt

**Ação:** Adicionar validação obrigatória no início de cada seção do prompt:

```
⚠️⚠️⚠️ VALIDAÇÃO OBRIGATÓRIA ANTES DE ESCREVER ⚠️⚠️⚠️

ANTES de escrever qualquer texto sobre temperamento ou dignidades:

1. LOCALIZE o bloco "🔒 DADOS PRÉ-CALCULADOS" abaixo
2. LEIA os valores EXATOS de temperamento
3. LEIA as dignidades EXATAS de cada planeta
4. COPIE esses valores para sua memória de trabalho
5. USE APENAS esses valores - NÃO recalcule, NÃO invente

SE você não encontrar um valor no bloco pré-calculado:
- NÃO invente
- NÃO estime
- NÃO mencione a dignidade/elemento

VALIDAÇÃO FINAL:
Antes de finalizar o texto, verifique:
- Cada menção de temperamento corresponde EXATAMENTE ao bloco?
- Cada menção de dignidade corresponde EXATAMENTE ao bloco?
- Se houver qualquer dúvida, REMOVA a menção
```

### 2. ✅ Adicionar Validação Pós-Geração

**Ação:** Criar função que valida o texto gerado contra o bloco pré-calculado:

```python
def validate_generated_text(text: str, precomputed_data: str) -> Dict[str, Any]:
    """
    Valida se o texto gerado está consistente com os dados pré-calculados.
    
    Returns:
        Dict com erros encontrados e sugestões de correção
    """
    errors = []
    warnings = []
    
    # Extrair valores do bloco pré-calculado
    temperament_points = extract_temperament_from_block(precomputed_data)
    dignities = extract_dignities_from_block(precomputed_data)
    
    # Validar temperamento no texto gerado
    text_temperament = extract_temperament_from_text(text)
    if text_temperament != temperament_points:
        errors.append({
            'type': 'temperament_mismatch',
            'expected': temperament_points,
            'found': text_temperament,
            'message': 'Temperamento no texto não corresponde ao bloco pré-calculado'
        })
    
    # Validar dignidades no texto gerado
    text_dignities = extract_dignities_from_text(text)
    for planet, expected_dignity in dignities.items():
        if planet in text_dignities:
            found_dignity = text_dignities[planet]
            if found_dignity != expected_dignity:
                errors.append({
                    'type': 'dignity_mismatch',
                    'planet': planet,
                    'expected': expected_dignity,
                    'found': found_dignity,
                    'message': f'Dignidade de {planet} no texto não corresponde ao bloco pré-calculado'
                })
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }
```

### 3. ✅ Garantir Consistência Entre Seções

**Ação:** Criar função que garante que o mesmo bloco pré-calculado seja usado em todas as seções:

```python
def generate_all_sections_with_consistent_data(request: FullBirthChartRequest):
    """
    Gera todas as seções usando o MESMO bloco pré-calculado.
    """
    # Calcular bloco UMA VEZ
    validated_chart, validation_summary, precomputed_data = _validate_chart_request(request, lang)
    
    # Gerar todas as seções com o MESMO bloco
    sections = []
    for section in ['power', 'triad', 'personal', 'houses', 'karma', 'synthesis']:
        request.section = section
        result = generate_section_with_precomputed_data(
            request, 
            precomputed_data,  # ← MESMO bloco para todas
            validation_summary
        )
        sections.append(result)
    
    return sections
```

### 4. ✅ Adicionar Exemplos de Erro no Prompt

**Ação:** Incluir exemplos explícitos de erros comuns no prompt:

```
❌ ERROS PROIBIDOS (NUNCA FAÇA ISSO):

1. ❌ Dizer "Sol em Virgem está em Domicílio" quando o bloco diz "PEREGRINO"
   ✅ CORRETO: "Sol em Virgem está PEREGRINO, o que significa..."

2. ❌ Dizer "Água: 8 pontos, Fogo: 5 pontos" quando o bloco diz "Terra: 10 pontos, Fogo: 1 ponto"
   ✅ CORRETO: Usar EXATAMENTE os valores do bloco

3. ❌ Inventar dignidades não mencionadas no bloco
   ✅ CORRETO: Se não estiver no bloco, não mencione a dignidade
```

---

## Implementação Imediata

### Prioridade 1: Reforçar Prompt (CRÍTICO)

**Arquivo:** `backend/app/api/interpretation.py`
**Função:** `_get_master_prompt()`

Adicionar seção de validação obrigatória no início do prompt.

### Prioridade 2: Validação Pós-Geração (ALTA)

**Arquivo:** `backend/app/api/interpretation.py`
**Função:** Nova função `validate_generated_text()`

Chamar após cada geração de seção e registrar erros.

### Prioridade 3: Garantir Consistência (MÉDIA)

**Arquivo:** `backend/app/api/interpretation.py`
**Função:** `generate_full_birth_chart()`

Garantir que o mesmo bloco pré-calculado seja usado em todas as seções.

---

## Teste de Validação

Após implementar as correções, testar com o mesmo mapa:

**Dados de Teste:**
- Nome: Necio de Lima Veras
- Data: 29/08/1981 às 06:00
- Local: Parnaíba, PI, Brasil

**Validações Esperadas:**
1. ✅ Temperamento deve ser CONSISTENTE em todas as seções
2. ✅ Dignidades devem corresponder EXATAMENTE ao bloco pré-calculado
3. ✅ Sol em Virgem deve ser mencionado como PEREGRINO (não Domicílio)
4. ✅ Nenhuma menção de valores inventados

---

## Conclusão

O problema principal é que a IA está ignorando o bloco pré-calculado e inventando valores. As soluções propostas reforçam:

1. **Instruções mais explícitas** no prompt
2. **Validação automática** após geração
3. **Consistência garantida** entre seções
4. **Exemplos de erros** para evitar confusão

Implementar essas correções deve resolver os erros identificados.

