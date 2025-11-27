# Componentes de Guia Pessoal - Documentação

## Visão Geral

Três novos componentes foram criados para a aba "Seu Guia Pessoal" do dashboard de astrologia:

1. **ChartRulerSection** - Mostra o regente do mapa natal
2. **DailyAdviceSection** - Conselhos diários baseados em trânsitos
3. **FutureTransitsSection** - Timeline de trânsitos futuros

---

## 1. ChartRulerSection

### Propósito
Exibe o planeta regente do ascendente e explica sua posição e influência no mapa natal.

### Props

```typescript
interface ChartRulerSectionProps {
  ascendant: string;      // Signo do Ascendente (ex: "Virgem", "Leão")
  ruler: string;          // Planeta regente (ex: "Mercúrio", "Sol")
  rulerSign: string;      // Signo onde o regente está (ex: "Sagitário")
  rulerHouse: number;     // Casa onde o regente está (1-12)
}
```

### Exemplo de Uso

```tsx
<ChartRulerSection
  ascendant="Virgem"
  ruler="Mercúrio"
  rulerSign="Sagitário"
  rulerHouse={3}
/>
```

### Lógica de Regentes

| Ascendente | Planeta Regente |
|------------|----------------|
| Áries | Marte |
| Touro | Vênus |
| Gêmeos | Mercúrio |
| Câncer | Lua |
| Leão | Sol |
| Virgem | Mercúrio |
| Libra | Vênus |
| Escorpião | Plutão (moderno) / Marte (tradicional) |
| Sagitário | Júpiter |
| Capricórnio | Saturno |
| Aquário | Urano (moderno) / Saturno (tradicional) |
| Peixes | Netuno (moderno) / Júpiter (tradicional) |

---

## 2. DailyAdviceSection

### Propósito
Fornece conselhos práticos baseados nos trânsitos diários, incluindo:
- Posição da Lua (sempre visível)
- Mercúrio Retrógrado (condicional)
- Lua Fora de Curso/Void of Course (condicional)

### Props

```typescript
interface DailyAdviceSectionProps {
  moonSign: string;              // Signo da Lua em trânsito hoje
  moonHouse: number;             // Casa onde a Lua transita (1-12)
  isMercuryRetrograde?: boolean; // Se Mercúrio está retrógrado
  isMoonVoidOfCourse?: boolean;  // Se Lua está void of course
  voidEndsAt?: string;           // Horário que termina (ex: "16:30")
}
```

### Exemplos de Uso

#### Dia Normal
```tsx
<DailyAdviceSection
  moonSign="Leão"
  moonHouse={5}
  isMercuryRetrograde={false}
  isMoonVoidOfCourse={false}
/>
```

#### Mercúrio Retrógrado Ativo
```tsx
<DailyAdviceSection
  moonSign="Câncer"
  moonHouse={11}
  isMercuryRetrograde={true}
  isMoonVoidOfCourse={false}
/>
```

#### Lua Void of Course
```tsx
<DailyAdviceSection
  moonSign="Gêmeos"
  moonHouse={3}
  isMercuryRetrograde={false}
  isMoonVoidOfCourse={true}
  voidEndsAt="18:45"
/>
```

#### Dia Intenso (Tudo Ativo)
```tsx
<DailyAdviceSection
  moonSign="Peixes"
  moonHouse={12}
  isMercuryRetrograde={true}
  isMoonVoidOfCourse={true}
  voidEndsAt="14:20"
/>
```

### Conselhos por Casa (Lua)

| Casa | Tema | Conselho |
|------|------|----------|
| 1 | Identidade | Foco em si mesmo, novos começos |
| 2 | Finanças | Estabilidade financeira, valorizar recursos |
| 3 | Comunicação | Conversas, estudos, conexão com irmãos |
| 4 | Lar | Família, cuidar do espaço pessoal |
| 5 | Criatividade | Hobbies, romance, expressão pessoal |
| 6 | Rotina | Organização, saúde, produtividade |
| 7 | Parcerias | Colaborações, negociações |
| 8 | Transformação | Intimidade, recursos compartilhados |
| 9 | Filosofia | Viagens, estudos superiores |
| 10 | Carreira | Metas profissionais, reputação |
| 11 | Amizades | Networking, grupos, humanitarismo |
| 12 | Espiritualidade | Solitude, meditação, reflexão |

---

## 3. FutureTransitsSection

### Propósito
Exibe uma timeline vertical de trânsitos futuros de planetas lentos (Júpiter, Saturno, Urano, Netuno, Plutão).

### Props

```typescript
interface Transit {
  id: string;
  type: 'jupiter' | 'saturn-return' | 'uranus' | 'neptune' | 'pluto';
  title: string;
  planet: string;
  timeframe: string;
  description: string;
  isActive?: boolean;
}

interface FutureTransitsSectionProps {
  transits?: Transit[];  // Opcional - usa dados de exemplo se não fornecido
}
```

### Exemplo de Uso

#### Com Dados Padrão
```tsx
<FutureTransitsSection />
```

#### Com Dados Customizados
```tsx
const myTransits = [
  {
    id: '1',
    type: 'jupiter',
    title: 'Júpiter em Gêmeos',
    planet: 'Júpiter',
    timeframe: 'Maio 2024 - Maio 2025',
    description: 'Júpiter transita sua Casa 10...',
    isActive: true
  },
  // ... mais trânsitos
];

<FutureTransitsSection transits={myTransits} />
```

### Tipos de Trânsitos e Cores

| Tipo | Cor | Significado |
|------|-----|-------------|
| jupiter | Dourado (#E8B95A) | Expansão, sorte, crescimento |
| saturn-return | Marrom (#8B7355) | Amadurecimento, lições de vida |
| uranus | Turquesa (#4ECDC4) | Mudança, inovação, liberdade |
| neptune | Roxo (#9B59B6) | Espiritualidade, ilusão, criatividade |
| pluto | Vermelho (#E74C3C) | Transformação profunda, poder |

---

## Integração no Dashboard

Os três componentes são usados na aba "Seu Guia Pessoal" do Advanced Dashboard:

```tsx
<TabsContent value="guide" className="space-y-8">
  <ChartRulerSection
    ascendant="Virgem"
    ruler="Mercúrio"
    rulerSign="Sagitário"
    rulerHouse={3}
  />

  <DailyAdviceSection
    moonSign="Câncer"
    moonHouse={11}
    isMercuryRetrograde={true}
    isMoonVoidOfCourse={false}
  />

  <FutureTransitsSection />
</TabsContent>
```

---

## Design System

### Componentes Base Utilizados
- **AstroCard** - Cards glassmorphic com bordas douradas
- **Badge** - Tags para status e categorias
- **UI Icons** - Ícones do Lucide React
- **Zodiac Icons** - Ícones customizados dos 12 signos
- **Planet Icons** - Ícones customizados dos 10 planetas

### Paleta de Cores
- **Accent (Dourado)**: #E8B95A - Usado para destaques e ações positivas
- **Destructive (Vermelho)**: Usado para alertas (ex: Mercúrio Retrógrado)
- **Muted**: Usado para elementos neutros (ex: Lua Void of Course)

### Tipografia
- **Títulos**: Playfair Display (serifada, elegante)
- **Corpo**: Inter (sans-serif, limpa)

---

## Próximos Passos / Melhorias Futuras

1. **Integração com API Real**: Conectar com efemérides astronômicas reais
2. **Cálculo Automático**: Calcular regente baseado no ascendente automaticamente
3. **Notificações**: Alertas quando Mercúrio entra em retrógrado
4. **Personalização**: Permitir usuário escolher quais trânsitos quer ver
5. **Histórico**: Salvar trânsitos passados para análise
6. **Export**: Permitir exportar timeline em PDF

---

## Referências

Baseado em conceitos astrológicos do livro mencionado no prompt original, incluindo:
- Regentes dos mapas astrais
- Trânsitos diários (Lua, Mercúrio Retrógrado, Void of Course)
- Trânsitos de longo prazo (planetas lentos)
- Conselhos práticos de "fazer" e "não fazer"
