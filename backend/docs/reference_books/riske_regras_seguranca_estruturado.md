# Regras de Segurança - Kris Brandt Riske

**Fonte:** Riske, Kris Brandt - Llewellyn's Complete Book of Astrology
**Categoria:** riske
**Uso na estratégia:** Regras de segurança como Mercúrio Retrógrado e Lua Fora de Curso, usados como filtros de "não agir"

**IMPORTANTE:** Todos os cálculos astrológicos devem ser feitos usando a biblioteca local (Swiss Ephemeris via kerykeion). 
Nunca invente ou estime cálculos. Use apenas dados calculados e validados pela biblioteca padrão.

---

## Mercúrio Retrógrado

### Definição e Características

- **Frequência:** Ocorre três a quatro vezes por ano
- **Duração:** Aproximadamente três semanas cada vez
- **Efeitos:** Interrompe comunicação, causa atrasos, resulta em mal-entendidos
- **Problemas comuns:**
  - Correios mal direcionados
  - Falhas mecânicas
  - Confusão em relação a datas e instruções
  - Problemas de comunicação

### Regra de Segurança: "NÃO AGIR"

**Durante Mercúrio Retrógrado, EVITAR:**
- Iniciar novos projetos importantes
- Assinar contratos importantes
- Fazer compras grandes
- Iniciar relacionamentos novos
- Tomar decisões importantes baseadas em comunicação

### Vantagens do Mercúrio Retrógrado

Apesar da má reputação, Mercúrio Retrógrado pode ser benéfico:
- Empresas de software frequentemente lançam produtos durante este período
- Período ideal para revisar, refletir e reavaliar
- Bom para completar projetos pendentes

### Como Utilizar Mercúrio Retrógrado

Para aproveitar o retrógrado em benefício pessoal:

1. **Usar efeméride para identificar datas-chave:**
   - Determinar quando Mercúrio fica retrógrado
   - Determinar quando Mercúrio se torna direto
   - Encontrar os graus em que essas transições ocorrem
   - Observar os períodos de sombra antes e depois do retrógrado

2. **Exemplo prático:**
   - Se Mercúrio fica retrógrado em 11° Câncer no dia 15 de junho
   - E se torna direto em 2° Câncer no dia 9 de julho
   - Enviar aplicações de emprego entre 30 de maio e 15 de junho
   - Esperar resultados de 9 de julho a 23 de julho

### Cálculo de Mercúrio Retrógrado

**IMPORTANTE:** Usar biblioteca local (Swiss Ephemeris) para determinar:
1. Quando Mercúrio está retrógrado (velocidade negativa)
2. Graus de entrada e saída da retrogradação
3. Períodos de sombra (quando Mercúrio passa pelos mesmos graus)

**Regra de segurança:** Se Mercúrio está retrógrado no momento calculado, **PENALIZAR** o score ou **EVITAR** recomendar o momento.

---

## Lua Fora de Curso (Void of Course)

### Definição e Características

- **Duração:** Geralmente dura de algumas horas a até dois dias
- **Teoria geral:** Qualquer coisa iniciada durante a Lua Fora de Curso é improvável de ser concluída
- **Efeito:** Ações tomadas nesse período tendem a carecer de direção e podem não levar a resultados bem-sucedidos

### Regra de Segurança: "NÃO AGIR"

**Durante Lua Fora de Curso, EVITAR:**
- Iniciar novos projetos ou empreendimentos importantes
- Tomar decisões importantes
- Assinar contratos
- Iniciar relacionamentos novos
- Qualquer ação que requeira conclusão ou resultado definido

### O Que Fazer Durante Lua Fora de Curso

Embora projetos maiores não sejam aconselháveis, você pode:
- Envolver-se em tarefas rotineiras
- Refletir sobre objetivos
- Trabalhar em atividades que não exigem resultados imediatos
- Entregar declarações de impostos ou dar más notícias (tarefas que não requerem conclusão positiva)
- Engajar-se em reflexão, tarefas secundárias ou atividades que já estão em andamento

### Casos Especiais

**Pessoas nascidas durante Lua Fora de Curso:**
- Demonstram tenacidade e determinação notáveis
- Têm potencial para alcançar sucesso significativo
- Podem não reconhecer limitações
- O sucesso reflete como a tenacidade pode contrabalançar a ideia tradicional de falta de conclusão

### Cálculo de Lua Fora de Curso

**IMPORTANTE:** Usar biblioteca local (Swiss Ephemeris) para determinar:
1. Quando a Lua faz seu último aspecto maior antes de mudar de signo
2. Período entre o último aspecto e a mudança de signo
3. Se a Lua está Fora de Curso no momento calculado

**Regra de segurança:** Se a Lua está Fora de Curso no momento calculado, **PENALIZAR** o score em -3 pontos ou **EVITAR** recomendar o momento.

### Implementação no Sistema

No cálculo de "Melhores Momentos":
1. **Verificar Lua Fora de Curso** usando `calculate_moon_void_of_course()`
2. **Se is_void == True:**
   - Reduzir score em -3 pontos
   - Adicionar warning: "⚠️ Lua Fora de Curso"
   - Considerar evitar recomendar o momento se score ficar muito baixo

3. **Verificar Mercúrio Retrógrado:**
   - Calcular velocidade de Mercúrio usando Swiss Ephemeris
   - Se velocidade < 0, Mercúrio está retrógrado
   - Considerar evitar recomendar o momento ou reduzir score significativamente

---

## Resumo das Regras de Segurança

### Filtros de "NÃO AGIR"

1. **Lua Fora de Curso:** Penalizar -3 pontos, adicionar warning
2. **Mercúrio Retrógrado:** Considerar evitar ou reduzir score significativamente
3. **Aspectos tensos de planetas desfavoráveis:** Penalizar -5 pontos por aspecto

### Validação

**CRÍTICO:** Antes de recomendar um momento:
1. Calcular Lua Fora de Curso usando biblioteca local
2. Verificar se Mercúrio está retrógrado usando biblioteca local
3. Validar que não há aspectos tensos de planetas a evitar
4. NUNCA inventar ou estimar esses cálculos - usar apenas dados da biblioteca padrão

---

## Referências para Cálculos

- **Biblioteca padrão:** Swiss Ephemeris (via kerykeion)
- **Função Lua Fora de Curso:** `calculate_moon_void_of_course()` em `moon_void_calculator.py`
- **Validação:** Sempre calcular usando coordenadas geográficas e data/hora precisas

