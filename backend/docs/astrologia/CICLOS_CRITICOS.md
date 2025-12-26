# 📘 Ciclos Críticos - Documentação

## 🎯 Visão Geral

A aba **"⏳ Ciclos Críticos"** oferece uma análise completa dos principais marcos astrológicos ao longo da vida, focando em períodos de maturação e transformação profunda.

---

## 🪐 Retorno de Saturno

### O que é?

O **Retorno de Saturno** ocorre aproximadamente a cada **29,5 anos**, quando Saturno retorna à mesma posição que ocupava no momento do nascimento.

### Períodos Críticos:

- **1º Retorno (27-31 anos)**: Transição para a maturidade adulta
- **2º Retorno (56-60 anos)**: Consolidação da sabedoria e legado

### Fases Analisadas:

| Status                 | Descrição                           | Idade      |
| ---------------------- | ----------------------------------- | ---------- |
| `aproximando_primeiro` | Preparação para o 1º retorno        | < 27 anos  |
| `primeiro_ativo`       | **RETORNO ATIVO** - Período crítico | 27-31 anos |
| `entre_retornos`       | Integração e aplicação              | 31-56 anos |
| `segundo_ativo`        | **RETORNO ATIVO** - Sabedoria       | 56-60 anos |
| `pos_segundo`          | Mestria conquistada                 | > 60 anos  |

### Áreas de Vida Afetadas (por Casa):

1. **Casa 1**: Identidade e autoapresentação
2. **Casa 2**: Recursos e autoestima
3. **Casa 3**: Comunicação e aprendizado
4. **Casa 4**: Lar e raízes familiares
5. **Casa 5**: Criatividade e expressão
6. **Casa 6**: Trabalho e saúde
7. **Casa 7**: Relacionamentos e parcerias
8. **Casa 8**: Transformação profunda
9. **Casa 9**: Filosofia e expansão
10. **Casa 10**: Carreira e realização
11. **Casa 11**: Amizades e ideais
12. **Casa 12**: Espiritualidade e inconsciente

### Interpretação Estruturada:

Para cada posição de Saturno, o sistema fornece:

✅ **Desafio Kármico**: O medo/insegurança principal  
✅ **Lição de Saturno**: O que precisa ser aprendido  
✅ **Oportunidade de Mestria**: A recompensa final

### Análise com IA (Groq):

A análise aprofundada cobre:

1. **O Que Está Acontecendo**: Significado do ciclo
2. **Áreas de Vida Afetadas**:

   - 💼 Carreira e Vocação
   - 💖 Relacionamentos e Compromissos
   - 🏠 Família e Responsabilidades
   - 🧠 Saúde Mental e Emocional
   - 💰 Finanças e Segurança Material

3. **Desafios Típicos**: 5 desafios concretos
4. **Ações Práticas**: 7 orientações práticas
5. **Recompensa Final**: Sabedoria e maturidade

---

## 🌟 Ciclo de Júpiter

### O que é?

Ciclo de aproximadamente **12 anos** marcando períodos de **expansão e crescimento**.

### Informações Fornecidas:

- Quantos ciclos já foram completados
- Data do próximo retorno
- Tempo restante até o próximo ciclo
- Júpiter Natal (signo e casa)

### Significado:

Cada retorno de Júpiter traz:

- 🌱 Novas oportunidades
- 📈 Crescimento e expansão
- 🎯 Manifestação de potenciais
- 🌍 Ampliação de horizontes

---

## ⚡ Oposição de Urano (Crise de Meia-Idade)

### O que é?

Por volta dos **42 anos**, Urano em trânsito faz oposição a Urano natal.

### Fases:

| Fase          | Idade | Descrição           |
| ------------- | ----- | ------------------- |
| `pre_crise`   | < 38  | Preparação          |
| `crise_ativa` | 38-46 | **PERÍODO CRÍTICO** |
| `pos_crise`   | > 46  | Integração          |

### Temas:

- ⚡ Questionamento de estruturas rígidas
- 🔓 Busca por liberdade genuína
- 🎭 Alinhamento entre vida externa e verdade interna
- 🔄 Reinvenção pessoal

---

## 🗓️ Linha do Tempo Integrada

Mostra os **próximos ciclos críticos** de forma cronológica:

```
🔥 ATIVO - Oposição de Urano (~2023, 42 anos)
   Tema: Renovação e Autenticidade

🔮 FUTURO - Retorno de Júpiter (~2029, 47 anos)
   Tema: Expansão e Crescimento

🔮 FUTURO - Retorno de Saturno 2º (~2040, 59 anos)
   Tema: Sabedoria e Legado
```

---

## 💡 Orientações Práticas

### ✅ Como Aproveitar os Ciclos:

1. Aceite a natureza transformadora do momento
2. Assuma responsabilidades sem resistência
3. Busque orientação de mentores/terapeutas
4. Cultive paciência e disciplina
5. Documente insights e aprendizados

### ⚠️ Armadilhas a Evitar:

1. Resistir às mudanças necessárias
2. Fugir das responsabilidades
3. Tomar decisões impulsivas
4. Isolar-se completamente
5. Ignorar sinais de esgotamento

---

## 🔧 Implementação Técnica

### Arquitetura:

```
analise_ciclos.py
├── AnalisadorCiclos
│   ├── calcular_idade_atual()
│   ├── calcular_data_retorno()
│   ├── analisar_retorno_saturno()
│   ├── analisar_ciclo_jupiter()
│   ├── analisar_crise_urano()
│   ├── gerar_linha_tempo_ciclos()
│   └── interpretar_saturno_casa()
```

### Dados Utilizados:

- **Do Mapa Natal**:

  - Posição de Saturno (signo, casa, grau)
  - Posição de Júpiter (signo, casa)
  - Posição de Urano (signo, casa)
  - Data de nascimento completa

- **Cálculos**:
  - Idade atual precisa (em anos decimais)
  - Datas de retorno baseadas em períodos orbitais
  - Status do ciclo baseado na idade

---

## 📊 Exemplo de Uso

### Para Francisco Alexandre (20/10/1981):

**Idade Atual**: 44.1 anos

**Retorno de Saturno**:

- 1º Retorno: 2011 (já vivenciado) ✅
- Status: Entre retornos (integração)
- 2º Retorno: ~2040 (aos 59 anos) 🔮
- Saturno Natal: Libra na Casa 10
- Foco: Carreira e Realização Social

**Ciclo de Júpiter**:

- Ciclos completos: 3
- Próximo retorno: Março/2029
- Faltam: 3.4 anos

**Crise de Urano**:

- Fase: **ATIVA** (38-46 anos) 🔥
- Urano Natal: Escorpião
- Tema: Renovação profunda

---

## 🎓 Referências Astrológicas

### Conceitos-Chave:

**Saturno** ♄:

- Planeta do Tempo, Disciplina e Estrutura
- Rege limites, responsabilidades e maturidade
- "Professor Kármico" da astrologia
- Ensina através de desafios e restrições

**Júpiter** ♃:

- Planeta da Expansão e Abundância
- Rege crescimento, oportunidades e sabedoria
- "Grande Benéfico" da astrologia
- Traz sorte e possibilidades

**Urano** ⚢:

- Planeta da Revolução e Liberdade
- Rege mudanças súbitas e autenticidade
- "Despertador Cósmico"
- Quebra padrões obsoletos

---

## 🚀 Próximas Funcionalidades

### Em Desenvolvimento:

1. **Progressões Secundárias**

   - Movimento simbólico dos planetas
   - 1 dia = 1 ano

2. **Retorno Solar Anual**

   - Mapa do aniversário
   - Tendências para o ano pessoal

3. **Trânsitos de Plutão e Netuno**

   - Transformações geracionais
   - Ciclos espirituais longos

4. **Eclipses no Mapa Natal**
   - Pontos de destino
   - Ativações importantes

---

## 📞 Suporte

Para dúvidas sobre interpretação astrológica, consulte:

- Livros de astrologia na pasta `/docs`
- Análise com IA (botão "Análise Aprofundada")
- Consulta com astrólogo profissional

---

**Desenvolvido com ❤️ para autoconhecimento profundo**
