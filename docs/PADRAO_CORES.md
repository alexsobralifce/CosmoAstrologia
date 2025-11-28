# 🎨 PADRÃO DE CORES PERMANENTE - COSMOS ASTRAL

## 📋 Documento de Referência Oficial

Este documento define o padrão de cores permanente do sistema Cosmos Astral, baseado no design Figma. **TODAS as cores devem seguir este padrão daqui para frente.**

---

## 🎯 CORES PRINCIPAIS DO SISTEMA

### 🟠 Laranja Padrão (Accent/Primary)

**Cor principal de ação e destaque do sistema**

- **HSL**: `25 85% 60%` ou `25 100% 51%`
- **Hex**: `#FF8904`
- **Uso**: Botões principais, ações importantes, destaques
- **Texto sobre laranja**: `#160F24` (preto) - **SEMPRE**

**Exemplos de uso:**

- Botão "Gerar Análise Completa"
- Botão "Analisar Compatibilidade"
- Botões de ação primária
- Elementos de destaque

**Estados:**

- Normal: `hsl(25, 85%, 60%)`
- Hover: `hsl(25, 85%, 55%)`
- Active: `hsl(25, 85%, 50%)`
- Disabled: `hsl(25, 85%, 50%)` com `opacity: 0.6`

---

### 🟣 Roxo/Violeta (Primary Dark Mode)

**Cor primária no modo escuro**

- **HSL**: `265 80% 65%`
- **Hex**: `#C27AFF`
- **Uso**: Botões e elementos primários no modo escuro
- **Texto sobre roxo**: `#FFFFFF` (branco)

---

## 🌓 CORES POR TEMA

### 🌙 MODO ESCURO (Dark Mode)

#### Cores Base

- **Background**: `260 30% 8%` → `#120E1B` (Roxo Profundo)
- **Foreground**: `260 10% 95%` → `#F2F1F4` (Off-white)
- **Card**: `260 25% 12%` → `#1C1726` (Card background)
- **Border**: `260 20% 25%` → `#30293D` (Bordas)

#### Cores de Texto

- **Texto Principal**: `#F2F1F4` (branco/off-white)
- **Texto Secundário**: `260 10% 68%` → `#ADA3C2` (Cinza-roxo claro)
- **Texto Muted**: `260 10% 60%` (Cinza-roxo médio)

#### Cores de Ação

- **Primary**: `265 80% 65%` → `#C27AFF` (Violeta)
- **Accent**: `25 85% 60%` → `#FF8904` (Laranja)
- **Destructive**: `0 70% 60%` → `#FB2C36` (Vermelho)

---

### ☀️ MODO CLARO (Light Mode)

#### Cores Base

- **Background**: `36 20% 98%` → `#FBFAF9` (Creme Suave)
- **Foreground**: `260 45% 10%` → `#160F24` (Roxo Escuro)
- **Card**: `0 0% 100%` → `#FFFFFF` (Branco Puro)
- **Border**: `260 10% 81%` → `#CAC7D1` (Cinza suave)

#### Cores de Texto

- **Texto Principal**: `#160F24` (preto/roxo escuro)
- **Texto Secundário**: `260 8% 43%` → `#635C70` (Cinza-roxo)
- **Texto Muted**: `260 8% 43%` (Cinza-roxo médio)

#### Cores de Ação

- **Primary**: `25 100% 51%` → `#FF8904` (Laranja Vibrante)
- **Accent**: `25 100% 51%` → `#FF8904` (Laranja Vibrante)
- **Destructive**: `0 85% 58%` → `#FB2C36` (Vermelho)

---

## 📐 REGRAS DE CONTRASTE

### Texto sobre Fundo Escuro

- **Fundo escuro** (`#120E1B`, `#1C1726`) → **Texto claro** (`#F2F1F4`)
- **Fundo card escuro** (`#1C1726`) → **Texto branco** (`#F2F1F4`)

### Texto sobre Fundo Claro

- **Fundo claro** (`#FBFAF9`, `#FFFFFF`) → **Texto escuro** (`#160F24`)
- **Fundo card claro** (`#FFFFFF`) → **Texto preto** (`#160F24`)

### Texto sobre Laranja

- **Fundo laranja** (`#FF8904`) → **Texto preto** (`#160F24`) - **SEMPRE**

### Molduras de Ícones

- **Modo Escuro**: Moldura **branca** (`#F2F1F4`)
- **Modo Claro**: Moldura **preta** (`#160F24`)

---

## 🎨 CORES ESPECÍFICAS POR ELEMENTO

### Botões

#### Botão Primário (Laranja)

```css
background-color: hsl(25, 85%, 60%); /* #FF8904 */
color: #160f24; /* Preto - SEMPRE */
```

#### Botão Secundário

```css
background-color: hsl(var(--muted));
color: hsl(var(--foreground));
border: 1px solid hsl(var(--border));
```

### Cards

```css
/* Dark Mode */
background-color: hsl(260, 25%, 12%); /* #1C1726 */
color: hsl(260, 10%, 95%); /* #F2F1F4 */

/* Light Mode */
background-color: hsl(0, 0%, 100%); /* #FFFFFF */
color: hsl(260, 45%, 10%); /* #160F24 */
```

### Bordas

```css
/* Dark Mode */
border-color: hsl(260, 20%, 25%); /* #30293D */

/* Light Mode */
border-color: hsl(260, 10%, 81%); /* #CAC7D1 */
```

---

## 🔧 USO DE VARIÁVEIS CSS

### Sempre use variáveis CSS quando possível:

```css
/* ✅ CORRETO */
background-color: hsl(var(--background));
color: hsl(var(--foreground));
border: 1px solid hsl(var(--border));

/* ✅ CORRETO - Laranja padrão */
background-color: hsl(25, 85%, 60%);
color: #160f24; /* Preto sobre laranja */

/* ❌ EVITAR - Cores hardcoded sem necessidade */
background-color: #ff8904; /* Use hsl(25, 85%, 60%) */
color: #f2f1f4; /* Use hsl(var(--foreground)) */
```

---

## 📝 CHECKLIST DE APLICAÇÃO

Ao criar novos componentes, verifique:

- [ ] Cores seguem o padrão do tema (dark/light)
- [ ] Texto sobre laranja é sempre preto (`#160F24`)
- [ ] Contraste adequado entre texto e fundo
- [ ] Molduras de ícones: branca (dark) / preta (light)
- [ ] Uso de variáveis CSS quando possível
- [ ] Estados hover/active/disabled definidos
- [ ] Cores consistentes com o design Figma

---

## 🎯 CORES ESPECIAIS

### Laranja Sistema (Padrão)

- **Valor HSL**: `25 85% 60%` ou `25 100% 51%`
- **Hex**: `#FF8904`
- **Uso**: Botões de ação, destaques, elementos interativos principais

### Cores de Texto Fixas

- **Branco (Dark Mode)**: `#F2F1F4`
- **Preto (Light Mode)**: `#160F24`
- **Preto sobre Laranja**: `#160F24` (sempre)

### Cores de Moldura

- **Dark Mode**: `#F2F1F4` (branco)
- **Light Mode**: `#160F24` (preto)

---

## 📚 REFERÊNCIAS

- **Design Figma**: https://www.figma.com/design/fWJHUdy942lRVIOogbWrFj/modelo-astrologico
- **Arquivo de Tema**: `src/styles/theme.css`
- **Arquivo Principal**: `src/styles/main.css`

---

## ⚠️ IMPORTANTE

1. **NUNCA** use cores que não estejam neste documento
2. **SEMPRE** use texto preto (`#160F24`) sobre fundo laranja
3. **SEMPRE** verifique contraste em ambos os temas (dark/light)
4. **SEMPRE** use variáveis CSS quando disponíveis
5. **SEMPRE** teste em ambos os modos antes de finalizar

---

**Última atualização**: Baseado no design Figma oficial **Versão**: 1.0 **Status**: Padrão permanente - não alterar sem aprovação
