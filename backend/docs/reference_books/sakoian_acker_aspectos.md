# Aspectos e Geometria Angular - Sakoian & Acker

**Fonte:** Sakoian, Frances & Acker, Louis S. - The Astrologer's Handbook
**Categoria:** sakoian_acker
**Uso na estratégia:** Definições precisas de aspectos (trígonos, quadraturas) e geometria angular para calcular momentos de sorte ou tensão

**IMPORTANTE:** Todos os cálculos astrológicos devem ser feitos usando a biblioteca local (Swiss Ephemeris via kerykeion). 
Nunca invente ou estime cálculos. Use apenas dados calculados e validados pela biblioteca padrão.

---

## Definições de Aspectos (Sakoian & Acker)

### Aspectos Maiores (Major Aspects)

#### Conjunção (0°)
- **Geometria:** Dois corpos celestes no mesmo grau de longitude eclíptica
- **Orbe padrão:** 8° (pode variar por planeta)
- **Natureza:** Intensifica as qualidades dos planetas envolvidos
- **Uso em timing:** Momento de máxima concentração de energia
- **Cálculo:** Diferença angular absoluta entre longitudes < 8°

#### Oposição (180°)
- **Geometria:** Dois corpos celestes em lados opostos do zodíaco
- **Orbe padrão:** 8°
- **Natureza:** Tensão, polaridade, necessidade de equilíbrio
- **Uso em timing:** Momentos de tensão que requerem negociação
- **Cálculo:** Diferença angular absoluta entre 172° e 188°

#### Trígono (120°)
- **Geometria:** Forma um triângulo equilátero no círculo
- **Orbe padrão:** 8°
- **Natureza:** Harmonia, fluidez, facilidade natural
- **Uso em timing:** Momentos de sorte e facilidade (PONTOS POSITIVOS)
- **Cálculo:** Diferença angular absoluta entre 112° e 128°

#### Quadratura (90°)
- **Geometria:** Forma um quadrado no círculo
- **Orbe padrão:** 8°
- **Natureza:** Tensão, desafio, necessidade de ação
- **Uso em timing:** Momentos de tensão (PONTOS NEGATIVOS)
- **Cálculo:** Diferença angular absoluta entre 82° e 98°

#### Sextil (60°)
- **Geometria:** Forma um hexágono no círculo
- **Orbe padrão:** 8°
- **Natureza:** Oportunidade, cooperação, potencial
- **Uso em timing:** Momentos de oportunidade (PONTOS POSITIVOS)
- **Cálculo:** Diferença angular absoluta entre 52° e 68°

### Aspectos Menores

#### Semissextil (30°)
- **Orbe:** 2-3°
- **Natureza:** Conexão sutil, ajuste fino

#### Quincúncio (150°)
- **Orbe:** 2-3°
- **Natureza:** Ajuste, adaptação, necessidade de mudança

## Geometria Angular para Cálculo de Momentos

### Princípios Fundamentais

1. **Precisão Angular:** Aspectos devem ser calculados com precisão matemática usando Swiss Ephemeris
2. **Orbes:** O orbe de 8° é padrão para aspectos maiores, mas pode variar:
   - Sol/Lua: até 10°
   - Planetas pessoais: 8°
   - Planetas lentos: 6-8°
3. **Validação:** Sempre validar se o aspecto está dentro do orbe antes de considerar

### Cálculo de Aspectos para Timing

Para determinar se um momento é favorável ou não:

1. **Calcular posições planetárias** usando Swiss Ephemeris (biblioteca padrão)
2. **Calcular ângulo** entre planeta transitante e ponto natal (casa, planeta, etc.)
3. **Determinar tipo de aspecto** baseado no ângulo:
   - 0° ± 8° = Conjunção
   - 60° ± 8° = Sextil (FAVORÁVEL)
   - 90° ± 8° = Quadratura (DESFAVORÁVEL)
   - 120° ± 8° = Trígono (FAVORÁVEL)
   - 180° ± 8° = Oposição (DESFAVORÁVEL)
4. **Atribuir pontos:**
   - Trígono em casa primária: +10 pontos
   - Sextil em casa primária: +7 pontos
   - Conjunção em casa primária: +8 pontos
   - Quadratura/Oposição: -5 pontos

### Validação Rigorosa

**CRÍTICO:** Antes de considerar um aspecto válido:
1. Calcular diferença angular exata
2. Verificar se está dentro do orbe de 8°
3. Validar que o aspecto está nos preferidos (trígono, sextil, conjunção para ações positivas)
4. NUNCA inventar aspectos que não estão matematicamente dentro do orbe

## Referências para Cálculos

- **Biblioteca padrão:** Swiss Ephemeris (via kerykeion)
- **Orbe padrão:** 8.0° para aspectos maiores
- **Validação:** Sempre verificar diferença angular antes de considerar aspecto válido
