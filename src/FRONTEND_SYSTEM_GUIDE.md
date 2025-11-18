# 🌟 Guia Completo do Frontend - Sistema de Astrologia Premium

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura da Aplicação](#arquitetura-da-aplicação)
3. [Estrutura de Pastas](#estrutura-de-pastas)
4. [Fluxo de Navegação](#fluxo-de-navegação)
5. [Páginas e Views](#páginas-e-views)
6. [Sistema de Design](#sistema-de-design)
7. [Componentes Principais](#componentes-principais)
8. [Componentes de UI (ShadCN)](#componentes-de-ui-shadcn)
9. [Gerenciamento de Estado](#gerenciamento-de-estado)
10. [Sistema de Temas](#sistema-de-temas)
11. [Bibliotecas e Dependências](#bibliotecas-e-dependências)
12. [Dados Mockados](#dados-mockados)
13. [Animações e Efeitos](#animações-e-efeitos)
14. [Responsividade](#responsividade)
15. [Boas Práticas](#boas-práticas)

---

## 🎯 Visão Geral

### O que é este sistema?

Um **sistema web premium de astrologia** que permite aos usuários:
- Criar conta e fazer login (e-mail ou Google)
- Calcular seu mapa astral pessoal
- Visualizar interpretações detalhadas
- Receber conselhos diários personalizados
- Acompanhar trânsitos planetários

### Estética e Identidade Visual

**Conceito:** Místico-Profissional
- **Paleta:** Azul-marinho cósmico + Dourado âmbar
- **Tipografia:** Playfair Display (serifada) + Inter (sans-serif)
- **Efeitos:** Glassmorphism, gradientes, animações suaves
- **Temas:** Noturno (escuro) e Diurno (claro)

### Stack Tecnológico

- **Framework:** React 18 com TypeScript
- **Styling:** Tailwind CSS v4.0
- **UI Components:** ShadCN/UI
- **Icons:** Lucide React
- **Charts:** Recharts
- **Date Handling:** date-fns
- **Notifications:** Sonner
- **Build:** Vite

---

## 🏗️ Arquitetura da Aplicação

### Estrutura de Alto Nível

```
App.tsx (Entry Point)
   ├── ThemeProvider (Context de Tema)
   │      └── AppContent (Lógica de Navegação)
   │             ├── Landing Page
   │             ├── Auth Portal
   │             ├── Onboarding
   │             ├── Dashboard
   │             ├── Interpretation Page
   │             └── Style Guide
   └── Toaster (Notificações Globais)
```

### Padrões Arquiteturais

1. **Component-Based:** Tudo é componente reutilizável
2. **Single Source of Truth:** Estado centralizado no App.tsx
3. **Composition over Inheritance:** Componentes compostos
4. **Props Drilling Controlado:** Máximo 2-3 níveis
5. **Separation of Concerns:** Lógica separada de apresentação

---

## 📁 Estrutura de Pastas

### `/` (Raiz)

```
/
├── App.tsx                    # Entry point e roteamento
├── FRONTEND_SYSTEM_GUIDE.md   # Este guia
├── QUICK_START_AUTH.md        # Guia de teste de autenticação
├── Attributions.md            # Créditos e atribuições
├── components/                # Todos os componentes
├── guidelines/                # Diretrizes de desenvolvimento
└── styles/                    # CSS global e variáveis
```

### `/components` (Componentes Customizados)

```
/components
├── AUTH_FLOWS_README.md           # Doc de autenticação
├── GUIDE_COMPONENTS_README.md     # Doc dos componentes de guia
│
├── advanced-dashboard.tsx         # Dashboard principal (5 abas)
├── interpretation-page.tsx        # Página de interpretação de tópicos
├── onboarding.tsx                 # Fluxo de coleta de dados (5 steps)
├── auth-portal.tsx                # Login e cadastro
├── auth-loader.tsx                # Loader místico de autenticação
├── dashboard.tsx                  # Dashboard antigo (depreciado)
│
├── birth-chart-wheel.tsx          # Roda do mapa astral (circular)
├── element-chart.tsx              # Gráfico de elementos (radar)
├── chart-ruler-section.tsx        # Seção do regente do mapa
├── daily-advice-section.tsx       # Conselhos diários
├── daily-advice-demo.tsx          # Demo de conselhos
├── future-transits-section.tsx    # Timeline de trânsitos
│
├── astro-button.tsx               # Botão dourado customizado
├── astro-card.tsx                 # Card glassmorphic
├── astro-input.tsx                # Input com label e validação
│
├── zodiac-icons.tsx               # 12 ícones de signos
├── planet-icons.tsx               # 10 ícones de planetas
├── aspect-icons.tsx               # Ícones de aspectos astrológicos
├── ui-icons.tsx                   # Ícones de UI (lucide)
│
├── theme-provider.tsx             # Context de tema
├── theme-toggle.tsx               # Botão de alternar tema
│
├── figma/                         # Componentes Figma
│   └── ImageWithFallback.tsx      # Imagem com fallback (protegido)
│
└── ui/                            # ShadCN UI components
    └── (47 componentes)
```

### `/styles` (Estilos Globais)

```
/styles
└── globals.css    # Variáveis CSS, tipografia, animações, temas
```

### `/guidelines` (Diretrizes)

```
/guidelines
└── Guidelines.md  # Diretrizes de desenvolvimento
```

---

## 🗺️ Fluxo de Navegação

### Mapa de Navegação Completo

```
┌─────────────────┐
│  Landing Page   │ ← Ponto de entrada
└────────┬────────┘
         │ [Calcular Mapa]
         ↓
┌─────────────────┐
│   Auth Portal   │ ← Login/Cadastro/Google
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ↓         ↓
[Novo]    [Existente]
    │         │
    ↓         └──────→ [Tem Mapa?] ──┐
┌──────────┐              │          │
│Onboarding│ ←────────────┘          │
└────┬─────┘                         │
     │                               │
     └───────────────┬───────────────┘
                     ↓
            ┌────────────────┐
            │   Dashboard    │ ← Hub principal
            │   (5 abas)     │
            └────────┬───────┘
                     │
            ┌────────┴────────┐
            │                 │
            ↓                 ↓
    [Ver Interpretação]   [Navegação]
            │                 │
            ↓                 ↓
    ┌──────────────┐   ┌──────────┐
    │Interpretation│   │Outras    │
    │     Page     │   │Páginas   │
    └──────────────┘   └──────────┘
```

### Estados de Navegação (AppView)

```typescript
type AppView = 
  | 'landing'        // Landing page inicial
  | 'auth'           // Portal de autenticação
  | 'onboarding'     // Coleta de dados de nascimento
  | 'dashboard'      // Dashboard principal
  | 'interpretation' // Página de interpretação
  | 'style-guide';   // Guia de estilo (demo)
```

---

## 📄 Páginas e Views

### 1. Landing Page

**Arquivo:** `App.tsx` (linha ~70)
**Rota:** `/` (view: 'landing')

**Propósito:** Primeira impressão e captação

**Elementos:**
- Hero com logo estelar
- Título: "Descubra Seu Mapa Astral"
- Descrição da proposta de valor
- CTA principal: "Calcular Meu Mapa Astral"
- CTA secundário: "Ver Design System"
- 3 cards de features:
  - Interpretações Detalhadas
  - Visualização Interativa
  - Experiência Premium
- Fundo cósmico com 50 estrelas animadas

**Interações:**
- Clicar CTA → vai para Auth Portal
- Clicar "Ver Design System" → vai para Style Guide

---

### 2. Auth Portal

**Arquivo:** `/components/auth-portal.tsx`
**Rota:** `/auth` (view: 'auth')

**Propósito:** Autenticação inteligente com 3 fluxos

**Elementos:**
- Toggle Login/Cadastro (tabs no topo)
- Logo central (estrela dourada)
- Formulário dinâmico:
  - **Modo Criar Conta:**
    - Input: E-mail
    - Input: Senha (com toggle show/hide)
    - Input: Confirmar Senha (validação visual)
    - Botão: "Continuar"
  - **Modo Entrar:**
    - Input: E-mail
    - Input: Senha
    - Link: "Esqueceu a senha?"
    - Botão: "Acessar meu Mapa"
- Divisor: "ou continue com"
- Botão: Login com Google
- Rodapé: Links de termos/privacidade
- Card de demonstração (credenciais de teste)
- Fundo: 50 estrelas piscando + gradientes pulsantes

**Fluxos:**
1. **Cadastro (Fluxo 1):**
   - Valida e-mail único
   - Valida senha ≥ 6 chars
   - Valida senhas coincidentes
   - → Onboarding

2. **Login (Fluxo 2):**
   - Valida credenciais
   - Se tem mapa → Dashboard
   - Se não tem mapa → Onboarding

3. **Google (Fluxo 3):**
   - Simula OAuth
   - Se novo → Onboarding (com dados pré-preenchidos)
   - Se existente → Dashboard

**Validações:**
- E-mail: regex padrão RFC 5322
- Senha: mínimo 6 caracteres
- Confirmação: igualdade exata
- Feedback: toast notifications coloridos

**Documentação:** `components/AUTH_FLOWS_README.md`

---

### 3. Onboarding (Coleta de Dados)

**Arquivo:** `/components/onboarding.tsx`
**Rota:** `/onboarding` (view: 'onboarding')

**Propósito:** Coletar dados de nascimento para calcular mapa

**Estrutura:** Wizard de 5 passos

**Step 1: Nome**
- Input: Nome Completo
- Se veio do Google: nome pré-preenchido
- Badge: "Conta conectada: email@gmail.com"

**Step 2: Data de Nascimento**
- Popover com Calendar (ShadCN)
- Dropdown de ano (1900 - ano atual)
- Validação: não pode ser futura

**Step 3: Hora de Nascimento**
- Input type="time"
- Tooltip: "A hora exata é essencial para Ascendente e Casas"
- Link expansível: "Não sabe a hora exata?"

**Step 4: Local de Nascimento**
- Input: Cidade, Estado
- Ícone de busca (simulado)
- Card explicativo: importância da lat/long

**Step 5: Confirmação/Login**
- Resumo dos dados
- Mensagem: "Seu mapa está quase pronto!"
- Botão: "Gerar Mapa Astral"

**Navegação:**
- Botões: "Voltar" / "Próximo"
- Progress bar (5 barrinhas douradas)
- Validação por step (botão desabilitado se inválido)

**Interação Final:**
- Loader místico (3 segundos)
- → Dashboard

---

### 4. Dashboard (Advanced)

**Arquivo:** `/components/advanced-dashboard.tsx`
**Rota:** `/dashboard` (view: 'dashboard')

**Propósito:** Hub principal do sistema

**Layout:**
- Header fixo:
  - Saudação: "Olá, [Nome]!"
  - Dados de nascimento
  - Botão: Theme Toggle
- Tabs (5 abas):
  1. **Visão Geral**
  2. **Posições Planetárias**
  3. **Aspectos**
  4. **Seu Guia Pessoal** ⭐ NOVO
  5. **Configurações**

#### Aba 1: Visão Geral

**Componentes:**
- Saudação personalizada
- Trio de signos (card destaque):
  - Sol em [Signo]
  - Lua em [Signo]
  - Ascendente em [Signo]
- BirthChartWheel (roda circular do mapa)
- ElementChart (gráfico radar de elementos)
- Grid de 12 casas astrológicas

#### Aba 2: Posições Planetárias

**Componentes:**
- 10 cards de planetas (Sol, Lua, Mercúrio... Plutão)
- Para cada planeta:
  - Ícone colorido
  - Nome do planeta
  - Posição: [Signo] [Graus]°
  - Botão: "Ver Interpretação" → InterpretationPage

#### Aba 3: Aspectos

**Componentes:**
- Lista de aspectos astrológicos
- Para cada aspecto:
  - Ícone do tipo (conjunção, oposição, trígono...)
  - Descrição: [Planeta1] [Aspecto] [Planeta2]
  - Orbe: [X]°
  - Badge: tipo de aspecto (maior/menor)
  - Botão: "Ver Interpretação"

#### Aba 4: Seu Guia Pessoal ⭐ NOVO

**Seções:**

**4.1 Regente do Mapa (ChartRulerSection)**
- Card destaque do planeta regente
- Ícone grande do planeta
- Descrição: influência do regente
- Visualização da posição (casa + signo)

**4.2 Conselhos do Dia (DailyAdviceSection)**
- Trânsitos da Lua hoje:
  - Lua em [Signo]
  - Descrição e conselho
- Alerta: Mercúrio Retrógrado (se aplicável)
  - Badge vermelho
  - Datas: início - fim
  - Orientações
- Alerta: Lua Fora de Curso (se aplicável)
  - Badge laranja
  - Horário de início/fim
  - Recomendações

**4.3 Próximos Trânsitos (FutureTransitsSection)**
- Timeline de trânsitos futuros (6 meses)
- Apenas planetas lentos: Saturno, Urano, Netuno, Plutão
- Para cada trânsito:
  - Data
  - Planeta + aspecto + planeta natal
  - Tipo de impacto
  - Descrição breve

**Documentação:** `components/GUIDE_COMPONENTS_README.md`

#### Aba 5: Configurações

**Opções:**
- Toggle: Sistema de Casas (Placidus, Whole Sign...)
- Toggle: Zodíaco (Tropical, Sideral)
- Toggle: Tema (Dia/Noite)
- Botão: Baixar Mapa (PDF)
- Botão: Compartilhar

---

### 5. Interpretation Page

**Arquivo:** `/components/interpretation-page.tsx`
**Rota:** `/interpretation` (view: 'interpretation')

**Propósito:** Leitura aprofundada de um tópico específico

**Estrutura:**
- Header:
  - Botão: ← Voltar ao Mapa
  - Título: [Tópico]
  - Theme Toggle
- Hero:
  - Ícone grande do tópico
  - Título principal
  - Subtítulo
- Seções de conteúdo:
  1. **O que significa?**
  2. **Na sua vida**
  3. **Desafios e Oportunidades**
  4. **Dicas práticas**
- Card de chamada: "Explorar outros aspectos"

**Tipos de Tópicos:**
- Posições planetárias (ex: "Sol em Áries")
- Aspectos (ex: "Sol Conjunção Mercúrio")
- Casas (ex: "Marte na Casa 10")

**Otimizações de Leitura:**
- Tipografia responsiva
- Line-height 1.8 (máxima legibilidade)
- Max-width 720px (50-75 chars/linha)
- Espaçamento generoso entre seções

---

### 6. Style Guide (Demo)

**Arquivo:** `App.tsx` (linha ~184)
**Rota:** `/style-guide` (view: 'style-guide')

**Propósito:** Demonstração do design system

**Seções:**

1. **Sistema de Temas**
   - Explicação Noturno vs Diurno
   - ThemeToggle interativo

2. **Paleta de Cores**
   - Cards com amostras de cor
   - Hex codes
   - Descrição de uso

3. **Tipografia**
   - Exemplos de H1, H2, H3, P
   - Demonstração Playfair + Inter

4. **Botões**
   - Variantes: Primary, Secondary
   - Tamanhos: lg, md, sm

5. **Form Inputs**
   - Inputs normais
   - Inputs com erro
   - Estados de foco

6. **Ícones do Zodíaco**
   - Grid 6x2 com os 12 signos
   - Hover effect

7. **Ícones dos Planetas**
   - Grid 5x2 com os 10 planetas
   - Hover effect

---

## 🎨 Sistema de Design

### Paleta de Cores

#### Tema Noturno (Dark - Padrão)

```css
--background: #0A0E2F;           /* Deep indigo cósmico */
--foreground: #F0F0F0;           /* Branco suave */
--accent: #E8B95A;               /* Dourado âmbar */
--secondary: #A0AEC0;            /* Cinza claro */
--card: rgba(28, 38, 77, 0.6);   /* Glassmorphic */
--border: rgba(232, 185, 90, 0.2); /* Borda dourada sutil */
```

#### Tema Diurno (Light)

```css
--background: #FDFBF7;           /* Quase branco cremoso */
--foreground: #1A1A1A;           /* Preto suave */
--accent: #D4A024;               /* Dourado vibrante */
--secondary: #6B7280;            /* Cinza médio */
--card: rgba(255, 255, 255, 0.8); /* Branco translúcido */
--border: rgba(212, 160, 36, 0.3); /* Borda dourada */
```

### Tipografia

#### Fontes

```css
--font-serif: 'Playfair Display', serif;  /* Títulos */
--font-sans: 'Inter', sans-serif;         /* Corpo */
```

#### Hierarquia

```css
--text-2xl: 2.5rem;    /* H1 - 40px */
--text-xl: 2rem;       /* H2 - 32px */
--text-lg: 1.5rem;     /* H3 - 24px */
--text-base: 1rem;     /* Body - 16px */
--text-sm: 0.875rem;   /* Small - 14px */
--text-xs: 0.75rem;    /* Extra small - 12px */
```

#### Aplicação

- **H1-H3:** Playfair Display (serifada elegante)
- **Body, Labels, UI:** Inter (sans-serif moderna)
- **Line-height:** 1.5 (padrão), 1.8 (leitura)
- **Font-weight:** 400 (normal), 500 (medium)

### Espaçamento

Sistema baseado em múltiplos de 4px:

```
1 = 0.25rem = 4px
2 = 0.5rem = 8px
3 = 0.75rem = 12px
4 = 1rem = 16px
6 = 1.5rem = 24px
8 = 2rem = 32px
12 = 3rem = 48px
```

### Border Radius

```css
--radius: 0.5rem;  /* 8px - padrão para cards e inputs */
```

### Sombras

```css
/* Card glassmorphic */
box-shadow: 0 8px 32px rgba(10, 14, 47, 0.3);

/* Card hover */
box-shadow: 0 12px 48px rgba(232, 185, 90, 0.2);

/* Button */
box-shadow: 0 4px 12px rgba(232, 185, 90, 0.3);
```

### Efeitos Glassmorphic

```css
background: rgba(28, 38, 77, 0.6);
backdrop-filter: blur(16px);
border: 1px solid rgba(232, 185, 90, 0.2);
```

---

## 🧩 Componentes Principais

### AstroButton

**Arquivo:** `/components/astro-button.tsx`

**Propósito:** Botão estilizado com tema dourado

**Variantes:**
- `primary`: Fundo dourado, texto escuro
- `secondary`: Fundo translúcido, borda dourada

**Tamanhos:**
- `sm`: py-2 px-4, text-sm
- `md`: py-3 px-6, text-base (padrão)
- `lg`: py-4 px-8, text-lg

**Props:**
```typescript
interface AstroButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}
```

**Estados:**
- Hover: brilho aumentado
- Disabled: opacity 50%, cursor not-allowed
- Active: scale(0.98)

---

### AstroCard

**Arquivo:** `/components/astro-card.tsx`

**Propósito:** Container glassmorphic para conteúdo

**Variantes:**
- `glass`: Translúcido com blur (padrão)
- `solid`: Opaco

**Props:**
```typescript
interface AstroCardProps {
  variant?: 'glass' | 'solid';
  children: ReactNode;
  className?: string;
}
```

**Estilo:**
```tsx
// Glass
bg-card backdrop-blur-md border border-border rounded-lg p-6

// Solid
bg-card/80 border border-border rounded-lg p-6
```

---

### AstroInput

**Arquivo:** `/components/astro-input.tsx`

**Propósito:** Input customizado com label e validação

**Props:**
```typescript
interface AstroInputProps extends InputHTMLAttributes {
  label?: string;
  error?: string;
}
```

**Features:**
- Label acima do input
- Borda dourada em foco
- Borda vermelha se erro
- Mensagem de erro abaixo
- Background translúcido

**Estados:**
- Default: borda cinza
- Focus: borda dourada + ring accent/20
- Error: borda vermelha + ring destructive/20

---

### BirthChartWheel

**Arquivo:** `/components/birth-chart-wheel.tsx`

**Propósito:** Visualização circular do mapa astral

**Estrutura:**
- Círculo externo: 12 signos do zodíaco
- Círculo médio: 12 casas astrológicas
- Círculo interno: 10 planetas posicionados

**Tecnologia:** SVG puro com cálculos trigonométricos

**Props:**
```typescript
interface BirthChartWheelProps {
  planets: PlanetPosition[];
  houses: HousePosition[];
  size?: number; // padrão: 400
}
```

**Animações:**
- Fade in ao montar
- Hover nos planetas: tooltip
- Clique: destaca planeta

---

### ElementChart

**Arquivo:** `/components/element-chart.tsx`

**Propósito:** Gráfico radar dos 4 elementos

**Estrutura:**
- Radar chart (Recharts)
- 4 eixos: Fogo, Terra, Ar, Água
- Área preenchida dourada

**Dados:**
```typescript
[
  { element: 'Fogo', value: 3 },
  { element: 'Terra', value: 2 },
  { element: 'Ar', value: 4 },
  { element: 'Água', value: 1 }
]
```

---

### ChartRulerSection

**Arquivo:** `/components/chart-ruler-section.tsx`

**Propósito:** Mostra o regente do mapa astral

**Estrutura:**
- Card de destaque
- Ícone grande do planeta regente (80px)
- Título: "Regente do seu Mapa"
- Descrição: "[Planeta] em [Signo]"
- Parágrafo: significado do regente
- Visualização: casa + signo

**Lógica:**
- Ascendente → determina signo → determina regente
- Ex: Asc Áries → regente = Marte

---

### DailyAdviceSection

**Arquivo:** `/components/daily-advice-section.tsx`

**Propósito:** Conselhos práticos do dia

**Seções:**

1. **Trânsitos da Lua:**
   - Signo atual da Lua
   - Conselho baseado no signo
   - Card com ícone da Lua

2. **Mercúrio Retrógrado:**
   - Alerta se ativo
   - Badge vermelho
   - Datas de início/fim
   - Orientações: evitar contratos, backup dados...

3. **Lua Fora de Curso (Void of Course):**
   - Alerta se ativo
   - Badge laranja
   - Horário de início/fim
   - Recomendações: evitar decisões importantes

**Dados:** Mockados mas realistas (calendário astronômico)

---

### FutureTransitsSection

**Arquivo:** `/components/future-transits-section.tsx`

**Propósito:** Timeline de trânsitos futuros

**Estrutura:**
- Timeline vertical
- Cards para cada trânsito
- Apenas planetas lentos (Saturno, Urano, Netuno, Plutão)
- Período: próximos 6 meses

**Informações por Trânsito:**
- Data
- Planeta transitante
- Aspecto (conjunção, quadratura, trígono...)
- Planeta natal afetado
- Tipo de impacto (desafio, crescimento, transformação...)
- Descrição breve

**Visual:**
- Linha vertical conectando trânsitos
- Ícone do planeta
- Badge colorido por tipo de aspecto

---

### ZodiacIcons

**Arquivo:** `/components/zodiac-icons.tsx`

**Propósito:** 12 ícones SVG dos signos do zodíaco

**Lista:**
1. Áries ♈
2. Touro ♉
3. Gêmeos ♊
4. Câncer ♋
5. Leão ♌
6. Virgem ♍
7. Libra ♎
8. Escorpião ♏
9. Sagitário ♐
10. Capricórnio ♑
11. Aquário ♒
12. Peixes ♓

**Exportação:**
```typescript
export const zodiacSigns = [
  { 
    name: 'Áries', 
    symbol: '♈', 
    icon: AriesIcon,
    element: 'Fogo',
    quality: 'Cardinal'
  },
  // ...
];
```

---

### PlanetIcons

**Arquivo:** `/components/planet-icons.tsx`

**Propósito:** 10 ícones SVG dos planetas

**Lista:**
1. Sol ☉
2. Lua ☽
3. Mercúrio ☿
4. Vênus ♀
5. Marte ♂
6. Júpiter ♃
7. Saturno ♄
8. Urano ♅
9. Netuno ♆
10. Plutão ♇

**Exportação:**
```typescript
export const planets = [
  { 
    name: 'Sol', 
    symbol: '☉', 
    icon: SunIcon,
    color: '#FDB813'
  },
  // ...
];
```

---

### AspectIcons

**Arquivo:** `/components/aspect-icons.tsx`

**Propósito:** Ícones dos aspectos astrológicos

**Tipos:**
- Conjunção (0°) ☌
- Oposição (180°) ☍
- Trígono (120°) △
- Quadratura (90°) □
- Sextil (60°) ⚹

---

### UIIcons

**Arquivo:** `/components/ui-icons.tsx`

**Propósito:** Wrapper para ícones Lucide React

**Lista Parcial:**
```typescript
export const UIIcons = {
  Star,
  Sun,
  Moon,
  Eye,
  EyeOff,
  Calendar,
  MapPin,
  Info,
  CheckCircle,
  Heart,
  // ... +30 ícones
};
```

**Uso:**
```tsx
<UIIcons.Star size={24} className="text-accent" />
```

---

### ThemeProvider

**Arquivo:** `/components/theme-provider.tsx`

**Propósito:** Context para gerenciar tema global

**API:**
```typescript
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const { theme, toggleTheme } = useTheme();
```

**Persistência:** localStorage ('astro-theme')

**Implementação:**
```tsx
<ThemeProvider>
  <App />
</ThemeProvider>
```

---

### ThemeToggle

**Arquivo:** `/components/theme-toggle.tsx`

**Propósito:** Botão para alternar tema

**Visual:**
- Noite → Dia: ícone Lua → Sol
- Transição suave
- Background: card glassmorphic
- Hover: brilho dourado

---

## 🎁 Componentes de UI (ShadCN)

### Lista Completa (47 componentes)

#### Forms & Inputs
- `input.tsx` - Input básico
- `textarea.tsx` - Área de texto
- `label.tsx` - Label de formulário
- `form.tsx` - Form com React Hook Form
- `checkbox.tsx` - Caixa de seleção
- `radio-group.tsx` - Grupo de rádios
- `switch.tsx` - Toggle switch
- `slider.tsx` - Slider de valor
- `select.tsx` - Dropdown select
- `input-otp.tsx` - Input de código OTP

#### Layout
- `card.tsx` - Container de card
- `separator.tsx` - Divisor horizontal/vertical
- `scroll-area.tsx` - Área scrollable customizada
- `resizable.tsx` - Painéis redimensionáveis
- `aspect-ratio.tsx` - Container com proporção
- `sidebar.tsx` - Sidebar navegacional

#### Navigation
- `tabs.tsx` - Abas
- `navigation-menu.tsx` - Menu de navegação
- `menubar.tsx` - Barra de menu
- `breadcrumb.tsx` - Migalhas de pão
- `pagination.tsx` - Paginação

#### Feedback
- `alert.tsx` - Alerta informativo
- `toast.tsx` / `sonner.tsx` - Notificações
- `progress.tsx` - Barra de progresso
- `skeleton.tsx` - Placeholder de loading
- `badge.tsx` - Badge/etiqueta
- `avatar.tsx` - Avatar de usuário

#### Overlay
- `dialog.tsx` - Modal dialog
- `alert-dialog.tsx` - Dialog de confirmação
- `sheet.tsx` - Painel lateral
- `drawer.tsx` - Drawer deslizante
- `popover.tsx` - Popover
- `tooltip.tsx` - Tooltip
- `hover-card.tsx` - Card ao hover
- `context-menu.tsx` - Menu de contexto
- `dropdown-menu.tsx` - Menu dropdown

#### Data Display
- `table.tsx` - Tabela responsiva
- `calendar.tsx` - Calendário
- `chart.tsx` - Gráficos (Recharts)
- `carousel.tsx` - Carrossel

#### Interactive
- `button.tsx` - Botão
- `toggle.tsx` - Botão toggle
- `toggle-group.tsx` - Grupo de toggles
- `collapsible.tsx` - Conteúdo colapsável
- `accordion.tsx` - Acordeão
- `command.tsx` - Command palette

#### Utilities
- `utils.ts` - cn() helper
- `use-mobile.ts` - Hook de detecção mobile

### Como Usar

```tsx
import { Button } from './components/ui/button';
import { Card } from './components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs';

<Card>
  <Tabs>
    <TabsList>
      <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    </TabsList>
    <TabsContent value="tab1">
      <Button>Click me</Button>
    </TabsContent>
  </Tabs>
</Card>
```

---

## 🗄️ Gerenciamento de Estado

### Arquitetura de Estado

**Padrão:** Lifting State Up (estado no componente pai mais próximo)

### Estado Global (App.tsx)

```typescript
const [currentView, setCurrentView] = useState<AppView>('landing');
const [userData, setUserData] = useState<OnboardingData | null>(null);
const [authData, setAuthData] = useState<AuthUserData | null>(null);
const [selectedTopic, setSelectedTopic] = useState<string>('');
```

### Estado Local (por componente)

**AuthPortal:**
```typescript
const [mode, setMode] = useState<'signup' | 'login'>('signup');
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');
const [errors, setErrors] = useState({});
```

**Onboarding:**
```typescript
const [step, setStep] = useState(1);
const [name, setName] = useState('');
const [birthDate, setBirthDate] = useState<Date>();
const [birthTime, setBirthTime] = useState('');
const [birthPlace, setBirthPlace] = useState('');
```

**AdvancedDashboard:**
```typescript
const [activeTab, setActiveTab] = useState('overview');
```

### Context API

**ThemeProvider:**
```typescript
const ThemeContext = createContext<ThemeContextType>();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  
  useEffect(() => {
    const stored = localStorage.getItem('astro-theme');
    if (stored) setTheme(stored);
  }, []);
  
  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('astro-theme', newTheme);
    document.documentElement.classList.toggle('light');
  };
  
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

### Props Drilling

Máximo 2-3 níveis:
```
App.tsx
  └─ AdvancedDashboard (recebe userData)
       └─ ChartRulerSection (recebe planetData)
```

Se precisar de mais níveis → considerar Context API

---

## 🌓 Sistema de Temas

### Implementação

**1. Variáveis CSS (`globals.css`):**
```css
:root, .dark {
  --background: #0A0E2F;
  --foreground: #F0F0F0;
  --accent: #E8B95A;
  /* ... */
}

.light {
  --background: #FDFBF7;
  --foreground: #1A1A1A;
  --accent: #D4A024;
  /* ... */
}
```

**2. ThemeProvider (Context):**
- Gerencia estado `theme`
- Persiste em localStorage
- Aplica classe `.light` no `<html>`

**3. ThemeToggle (UI):**
- Botão com ícone Sol/Lua
- Chama `toggleTheme()`

**4. Uso em Componentes:**
```tsx
// Automático via variáveis CSS
<div className="bg-background text-foreground">
  <p className="text-accent">Texto dourado</p>
</div>
```

### Cores que Adaptam

| Variável | Noturno | Diurno |
|----------|---------|--------|
| `--background` | #0A0E2F | #FDFBF7 |
| `--foreground` | #F0F0F0 | #1A1A1A |
| `--accent` | #E8B95A | #D4A024 |
| `--secondary` | #A0AEC0 | #6B7280 |
| `--card` | rgba(28,38,77,0.6) | rgba(255,255,255,0.8) |

### Gradientes que Adaptam

```css
/* Noturno */
bg-gradient-to-b from-background via-[#0F1535] to-background

/* Diurno */
bg-gradient-to-b from-background via-[#F5F1E8] to-background
```

---

## 📚 Bibliotecas e Dependências

### Core

| Biblioteca | Versão | Propósito |
|------------|--------|-----------|
| react | 18.x | Framework UI |
| react-dom | 18.x | Renderização DOM |
| typescript | 5.x | Tipagem estática |

### Styling

| Biblioteca | Versão | Propósito |
|------------|--------|-----------|
| tailwindcss | 4.0 | Utility-first CSS |
| @tailwindcss/typography | - | Tipografia responsiva |

### UI Components

| Biblioteca | Versão | Propósito |
|------------|--------|-----------|
| @radix-ui/* | - | Primitivos acessíveis |
| lucide-react | - | Ícones |
| sonner | 2.0.3 | Toast notifications |

### Data Visualization

| Biblioteca | Versão | Propósito |
|------------|--------|-----------|
| recharts | - | Gráficos (radar, linha...) |

### Forms

| Biblioteca | Versão | Propósito |
|------------|--------|-----------|
| react-hook-form | 7.55.0 | Gerenciamento de forms |
| zod | - | Validação de schema |

### Dates

| Biblioteca | Versão | Propósito |
|------------|--------|-----------|
| date-fns | - | Manipulação de datas |
| react-day-picker | 8.10.1 | Calendário |

### Utilities

| Biblioteca | Versão | Propósito |
|------------|--------|-----------|
| clsx | - | Merge de classes CSS |
| tailwind-merge | - | Merge inteligente Tailwind |

### Build Tools

| Biblioteca | Versão | Propósito |
|------------|--------|-----------|
| vite | 5.x | Build tool |
| @vitejs/plugin-react | - | Plugin React |

---

## 🎭 Dados Mockados

### Usuários (AuthPortal)

```typescript
const mockDatabase = [
  {
    email: 'joao@exemplo.com',
    password: '123456',
    hasCompletedOnboarding: true,
    name: 'João Silva'
  },
  {
    email: 'maria@exemplo.com',
    password: '123456',
    hasCompletedOnboarding: false,
    name: 'Maria Santos'
  }
];
```

### Mapa Astral (Dashboard)

```typescript
const mockUserData = {
  name: 'João Silva',
  birthDate: new Date(1990, 0, 15), // 15 jan 1990
  birthTime: '14:30',
  birthPlace: 'São Paulo, SP',
  
  sunSign: 'Capricórnio',
  moonSign: 'Câncer',
  ascendant: 'Touro',
  
  planets: [
    { name: 'Sol', sign: 'Capricórnio', degree: 25, house: 9 },
    { name: 'Lua', sign: 'Câncer', degree: 12, house: 3 },
    // ... 8 mais
  ],
  
  aspects: [
    { 
      planet1: 'Sol', 
      planet2: 'Mercúrio', 
      type: 'Conjunção', 
      orb: 3,
      description: 'Mente iluminada e criativa'
    },
    // ... mais aspectos
  ],
  
  houses: [
    { number: 1, sign: 'Touro', cusp: 15 },
    // ... 11 mais
  ],
  
  elements: {
    fire: 3,    // Planetas em signos de Fogo
    earth: 2,   // Terra
    air: 4,     // Ar
    water: 1    // Água
  }
};
```

### Trânsitos (DailyAdviceSection)

```typescript
const mockTransits = {
  moonSign: 'Leão',
  moonAdvice: 'Dia favorável para expressão criativa e liderança.',
  
  mercuryRetrograde: {
    active: true,
    start: '2024-12-13',
    end: '2025-01-02',
    sign: 'Sagitário'
  },
  
  moonVoidOfCourse: {
    active: true,
    start: '14:30',
    end: '18:45'
  },
  
  futureTransits: [
    {
      date: '2025-02-15',
      planet: 'Saturno',
      aspect: 'Quadratura',
      natalPlanet: 'Sol',
      type: 'Desafio',
      description: 'Período de reestruturação...'
    },
    // ... mais trânsitos
  ]
};
```

### Interpretações (InterpretationPage)

```typescript
const mockInterpretations = {
  'sun-capricorn': {
    title: 'Sol em Capricórnio',
    subtitle: 'A Força da Ambição',
    sections: [
      {
        title: 'O que significa?',
        content: 'Pessoas com Sol em Capricórnio...'
      },
      {
        title: 'Na sua vida',
        content: 'Esta posição te dá...'
      },
      // ...
    ]
  },
  // ... mais interpretações
};
```

---

## ✨ Animações e Efeitos

### Animações CSS (globals.css)

**fadeIn:**
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fadeIn { animation: fadeIn 0.3s ease-out; }
```

**twinkle (estrelas):**
```css
@keyframes twinkle {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}
.animate-twinkle { animation: twinkle 2s ease-in-out infinite; }
```

**spin-slow (mandala):**
```css
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.animate-spin-slow { animation: spin-slow 8s linear infinite; }
```

### Transições Tailwind

```tsx
// Hover suave
className="transition-all duration-200 hover:bg-accent/10"

// Fade in de componente
className="animate-fadeIn"

// Pulse de gradiente
className="animate-pulse"

// Bounce de pontinhos
className="animate-bounce"
```

### Efeitos de Glassmorphism

```css
background: rgba(28, 38, 77, 0.6);
backdrop-filter: blur(16px);
-webkit-backdrop-filter: blur(16px);
border: 1px solid rgba(232, 185, 90, 0.2);
```

### Hover States

```tsx
// Card
hover:shadow-2xl hover:shadow-accent/20 hover:scale-[1.02]

// Button
hover:bg-accent/90 hover:shadow-lg

// Icon
hover:text-accent hover:rotate-12
```

---

## 📱 Responsividade

### Breakpoints Tailwind

```css
sm: 640px   /* Mobile landscape, small tablets */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large desktops */
```

### Estratégias

#### Mobile First
```tsx
// Base: mobile
className="flex-col gap-4"

// Tablet+: horizontal
className="flex-col sm:flex-row gap-4"
```

#### Grid Responsivo
```tsx
// 1 col mobile, 2 tablet, 3 desktop
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
```

#### Texto Responsivo
```tsx
// Títulos que escalam
className="text-2xl sm:text-3xl lg:text-4xl"
```

#### Espaçamento Responsivo
```tsx
// Padding que aumenta
className="p-4 md:p-6 lg:p-8"
```

### Componentes Adaptativos

**AdvancedDashboard:**
- Mobile: Tabs empilhadas
- Desktop: Tabs horizontais

**BirthChartWheel:**
- Mobile: 300px
- Tablet: 400px
- Desktop: 500px

**InterpretationPage:**
- Mobile: 100% width
- Desktop: max-width 720px centralizado

---

## 🎯 Boas Práticas

### Código

1. **TypeScript em todo lugar:**
   ```typescript
   interface Props { ... }
   const Component = ({ prop }: Props) => { ... }
   ```

2. **Props explícitas:**
   ```typescript
   // ❌ Evitar
   const Component = (props) => { ... }
   
   // ✅ Preferir
   const Component = ({ name, age }: ComponentProps) => { ... }
   ```

3. **Nomes descritivos:**
   ```typescript
   // ❌ Evitar
   const h = () => { ... }
   
   // ✅ Preferir
   const handleAuthSuccess = () => { ... }
   ```

4. **Componentes pequenos:**
   - Máximo 300 linhas
   - Responsabilidade única
   - Fácil de testar

5. **Comentários quando necessário:**
   ```typescript
   // Calcula a posição do planeta baseado em graus
   const calculatePosition = (degrees: number) => { ... }
   ```

### Styling

1. **Tailwind classes ordenadas:**
   ```tsx
   // Layout → Spacing → Sizing → Colors → Effects
   className="flex items-center gap-4 p-6 bg-card text-foreground rounded-lg shadow-lg"
   ```

2. **Variáveis CSS para temas:**
   ```tsx
   // ❌ Evitar
   className="bg-[#0A0E2F]"
   
   // ✅ Preferir
   className="bg-background"
   ```

3. **Componentes reutilizáveis:**
   - AstroButton em vez de button genérico
   - AstroCard em vez de div genérico

### Acessibilidade

1. **Semântica HTML:**
   ```tsx
   <button> para ações
   <a> para navegação
   <nav> para menus
   <main> para conteúdo principal
   ```

2. **Labels em inputs:**
   ```tsx
   <AstroInput label="Nome" /> // sempre com label
   ```

3. **Alt em imagens:**
   ```tsx
   <img alt="Descrição clara" />
   ```

4. **Contraste adequado:**
   - Texto: 4.5:1 mínimo
   - Títulos: 3:1 mínimo

### Performance

1. **Lazy load de imagens:**
   ```tsx
   <img loading="lazy" />
   ```

2. **Memoização quando necessário:**
   ```tsx
   const expensiveCalculation = useMemo(() => {...}, [deps]);
   ```

3. **Evitar re-renders:**
   ```tsx
   const Component = memo(({ prop }) => {...});
   ```

### Organização

1. **Imports ordenados:**
   ```typescript
   // 1. React
   import { useState, useEffect } from 'react';
   
   // 2. Bibliotecas externas
   import { format } from 'date-fns';
   
   // 3. Componentes locais
   import { AstroButton } from './components/astro-button';
   
   // 4. Types
   import type { UserData } from './types';
   ```

2. **Um componente por arquivo:**
   - Exceção: sub-componentes muito pequenos

3. **Nomes de arquivo:**
   - kebab-case: `advanced-dashboard.tsx`
   - PascalCase para componente: `AdvancedDashboard`

---

## 🔍 Glossário de Conceitos

### Astrologia

- **Mapa Astral:** Fotografia do céu no momento do nascimento
- **Ascendente:** Signo que estava nascendo no horizonte leste
- **Sol/Lua/Ascendente:** Trio principal do mapa
- **Planetas:** 10 corpos celestiais (Sol a Plutão)
- **Signos:** 12 divisões do zodíaco (Áries a Peixes)
- **Casas:** 12 áreas da vida (relacionamentos, carreira...)
- **Aspectos:** Ângulos entre planetas (conjunção, oposição...)
- **Trânsitos:** Movimento atual dos planetas vs mapa natal
- **Regente:** Planeta que governa um signo

### Frontend

- **Component:** Bloco reutilizável de UI
- **Props:** Parâmetros passados para componentes
- **State:** Dados que mudam ao longo do tempo
- **Hook:** Função especial do React (useState, useEffect...)
- **Context:** Estado compartilhado globalmente
- **Glassmorphism:** Efeito de vidro fosco com blur
- **Responsive:** Adapta a diferentes tamanhos de tela
- **Tailwind:** Framework CSS utility-first
- **ShadCN:** Biblioteca de componentes prontos

---

## 📖 Documentação Adicional

### Documentos Relacionados

1. **AUTH_FLOWS_README.md** - Documentação técnica de autenticação
2. **QUICK_START_AUTH.md** - Guia rápido para testar auth
3. **GUIDE_COMPONENTS_README.md** - Documentação dos componentes de guia
4. **Attributions.md** - Créditos e licenças
5. **Guidelines.md** - Diretrizes de desenvolvimento

### Recursos Externos

- [React Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [ShadCN UI](https://ui.shadcn.com)
- [Lucide Icons](https://lucide.dev)
- [Recharts](https://recharts.org)

---

## 🚀 Como Começar

### 1. Explorar a Landing Page
- Observe o design e animações
- Teste o Theme Toggle
- Clique em "Calcular Meu Mapa Astral"

### 2. Testar Autenticação
- Siga o **QUICK_START_AUTH.md**
- Teste os 3 fluxos
- Observe as validações

### 3. Completar Onboarding
- Preencha dados de nascimento
- Observe o wizard de 5 steps
- Veja o loader místico

### 4. Explorar Dashboard
- Navegue pelas 5 abas
- Teste visualizações interativas
- Clique em "Ver Interpretação"

### 5. Ler Interpretações
- Explore conteúdo de leitura
- Observe tipografia otimizada
- Volte ao dashboard

### 6. Testar Temas
- Alterne Dia/Noite várias vezes
- Observe adaptações de cor
- Teste em diferentes páginas

---

## 🎓 Conclusão

Este sistema é um **exemplo completo de aplicação React moderna** que combina:

✅ Design system profissional e consistente
✅ UX fluida com feedback constante
✅ Código limpo e bem organizado
✅ TypeScript para segurança de tipos
✅ Responsividade em todos os dispositivos
✅ Acessibilidade (a11y)
✅ Performance otimizada
✅ Animações suaves e místicas
✅ Tema dia/noite completo
✅ Documentação abrangente

**Próximos passos sugeridos:**
1. Integrar com backend real (Supabase)
2. Implementar cálculos astrológicos reais
3. Adicionar mais interpretações
4. Sistema de notificações push
5. Exportar mapa em PDF
6. Compartilhar nas redes sociais

---

**Desenvolvido com ❤️ e ✨ por Figma Make AI**
**Última atualização: Novembro 2024**
