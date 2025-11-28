# 🎨 Plano de Correção de Cores - Cosmos Astral

## 📋 Objetivo

Garantir que todos os componentes sigam fielmente o padrão de cores do Figma, com suporte completo para Light Mode (dia) e Dark Mode (noite).

---

## 🎯 Padrão de Cores do Figma

### ☀️ **LIGHT MODE (Dia) - Padrão Principal**

#### Cores Base
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--background` | `36 20% 98%` | `#FBFAF9` | Fundo principal da aplicação |
| `--foreground` | `260 45% 10%` | `#160F24` | Texto principal (títulos, headings) |
| `--card` | `0 0% 100%` | `#FFFFFF` | Fundo de cards e containers |
| `--card-foreground` | `260 45% 10%` | `#160F24` | Texto dentro de cards |

#### Cores Primárias e Ações
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--primary` | `25 100% 51%` | `#FF8904` | Botões primários, logo, elementos de destaque |
| `--primary-foreground` | `0 0% 100%` | `#FFFFFF` | Texto sobre botões primários |
| `--accent` | `25 100% 51%` | `#FF8904` | Elementos de destaque, hover states |
| `--accent-foreground` | `0 0% 100%` | `#FFFFFF` | Texto sobre elementos accent |

#### Cores Secundárias
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--secondary` | `260 15% 88%` | - | Botões secundários, backgrounds sutis |
| `--secondary-foreground` | `260 45% 10%` | `#160F24` | Texto sobre secundários |
| `--muted` | `260 15% 95%` | - | Backgrounds muito sutis |
| `--muted-foreground` | `260 8% 43%` | `#635C70` | Texto secundário, labels, placeholders |

#### Bordas e Inputs
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--border` | `260 10% 81%` | `#CAC7D1` | Bordas de cards, inputs, separadores |
| `--input` | `260 15% 92%` | `rgba(202, 199, 209, 0.3)` | Fundo de inputs |
| `--input-border` | `260 10% 81%` | `#CAC7D1` | Borda de inputs (estado normal) |
| `--input-border-active` | `25 100% 51%` | `#FF8904` | Borda de inputs (foco) |
| `--ring` | `25 100% 51%` | `#FF8904` | Indicador de foco (outline) |

#### Sidebar
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--sidebar` | `0 0% 100%` | `#FFFFFF` | Fundo da sidebar |
| `--sidebar-foreground` | `260 45% 10%` | `#160F24` | Texto da sidebar |
| `--sidebar-accent` | `25 100% 96%` | - | Fundo hover/ativo na sidebar |
| `--sidebar-accent-foreground` | `25 100% 35%` | - | Texto hover/ativo na sidebar |
| `--sidebar-border` | `260 10% 81%` | `#CAC7D1` | Borda da sidebar |

#### Estados Especiais
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--destructive` | `0 85% 58%` | `#FB2C36` | Erros, ações destrutivas |
| `--destructive-foreground` | `0 0% 100%` | `#FFFFFF` | Texto sobre elementos destrutivos |

---

### 🌙 **DARK MODE (Noite)**

#### Cores Base
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--background` | `260 30% 8%` | `#120E1B` | Fundo principal da aplicação |
| `--foreground` | `260 10% 95%` | `#F2F1F4` | Texto principal (títulos, headings) |
| `--card` | `260 25% 12%` | `#1C1726` | Fundo de cards e containers |
| `--card-foreground` | `260 10% 95%` | `#F2F1F4` | Texto dentro de cards |

#### Cores Primárias e Ações
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--primary` | `265 80% 65%` | `#C27AFF` | Botões primários, logo, elementos de destaque |
| `--primary-foreground` | `0 0% 100%` | `#FFFFFF` | Texto sobre botões primários |
| `--accent` | `25 85% 60%` | `#FF8904` | Elementos de destaque, hover states |
| `--accent-foreground` | `0 0% 100%` | `#FFFFFF` | Texto sobre elementos accent |

#### Cores Secundárias
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--secondary` | `260 20% 25%` | - | Botões secundários, backgrounds sutis |
| `--secondary-foreground` | `260 10% 95%` | `#F2F1F4` | Texto sobre secundários |
| `--muted` | `260 20% 20%` | - | Backgrounds muito sutis |
| `--muted-foreground` | `260 10% 68%` | `#ADA3C2` | Texto secundário, labels, placeholders |

#### Bordas e Inputs
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--border` | `260 20% 25%` | `#30293D` | Bordas de cards, inputs, separadores |
| `--input` | `260 25% 12%` | - | Fundo de inputs |
| `--input-border` | `260 20% 30%` | - | Borda de inputs (estado normal) |
| `--input-border-active` | `265 80% 65%` | `#C27AFF` | Borda de inputs (foco) |
| `--ring` | `265 80% 65%` | `#C27AFF` | Indicador de foco (outline) |

#### Sidebar
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--sidebar` | `260 30% 10%` | `#1C1726` | Fundo da sidebar |
| `--sidebar-foreground` | `260 10% 95%` | `#F2F1F4` | Texto da sidebar |
| `--sidebar-accent` | `25 85% 60%` | `#FF8904` | Fundo hover/ativo na sidebar |
| `--sidebar-accent-foreground` | `260 30% 8%` | `#120E1B` | Texto hover/ativo na sidebar |
| `--sidebar-border` | `260 20% 20%` | - | Borda da sidebar |

#### Estados Especiais
| Variável CSS | Valor HSL | Hex | Uso |
|-------------|-----------|-----|-----|
| `--destructive` | `0 70% 60%` | `#FB2C36` | Erros, ações destrutivas |
| `--destructive-foreground` | `0 0% 100%` | `#FFFFFF` | Texto sobre elementos destrutivos |

---

## 🔍 Análise de Componentes

### ✅ Componentes que JÁ seguem o padrão

1. **Dashboard Principal** (`cosmos-dashboard.tsx`)
   - ✅ Usa variáveis CSS corretas
   - ✅ Suporta light/dark mode
   - ⚠️ Alguns cards ainda usam cores hardcoded

2. **Modais** (`inactivity-warning-modal.tsx`, `edit-user-modal.tsx`)
   - ✅ Refatorados para CSS puro
   - ✅ Usam variáveis CSS

3. **Sistema de Tema** (`theme.css`)
   - ✅ Variáveis definidas corretamente
   - ✅ Light e Dark mode implementados

---

### ❌ Componentes que PRECISAM de correção

#### 1. **Cards de Insights** (`cosmos-dashboard.tsx`)
**Problema**: Cores hardcoded nos cards de insights
```tsx
// ❌ ERRADO - Cores hardcoded
style={{ backgroundColor: theme === 'dark' ? '#000000' : '#ffffff' }}
```

**Correção**:
```tsx
// ✅ CORRETO - Usar variáveis CSS
className="dashboard-insight-card"
```

**CSS a adicionar**:
```css
.dashboard-insight-card {
  background-color: hsl(var(--card));
  color: hsl(var(--card-foreground));
  border-color: hsl(var(--border));
}
```

---

#### 2. **Cards de Áreas** (`cosmos-dashboard.tsx`)
**Problema**: Cores hardcoded nos cards de previsões por área
```tsx
// ❌ ERRADO
style={{ backgroundColor: theme === 'dark' ? '#000000' : '#ffffff' }}
```

**Correção**:
```css
.dashboard-area-card {
  background-color: hsl(var(--card));
  color: hsl(var(--card-foreground));
  border-color: hsl(var(--border));
}

.dashboard-area-title {
  color: hsl(var(--foreground));
}

.dashboard-area-description {
  color: hsl(var(--muted-foreground));
}
```

---

#### 3. **Hero Section** (`cosmos-dashboard.tsx`)
**Status**: ✅ Já está correto (usa gradiente fixo conforme Figma)

---

#### 4. **Sidebar** (`cosmos-dashboard.tsx`)
**Problema**: Verificar se todas as cores estão usando variáveis CSS

**Correção**:
```css
.dashboard-sidebar {
  background-color: hsl(var(--sidebar));
  border-color: hsl(var(--sidebar-border));
}

.dashboard-sidebar-name {
  color: hsl(var(--sidebar-foreground));
}

.dashboard-sidebar-menu-item.active {
  background-color: hsl(var(--sidebar-accent));
  color: hsl(var(--sidebar-accent-foreground));
}
```

---

#### 5. **Header** (`cosmos-dashboard.tsx`)
**Correção**:
```css
.dashboard-header {
  background-color: hsl(var(--background) / 0.8);
  border-color: hsl(var(--border));
}

.dashboard-header-logo-text {
  color: hsl(var(--foreground));
}

.dashboard-header-logo-subtitle {
  color: hsl(var(--muted-foreground));
}
```

---

#### 6. **Botões** (`astro-button.tsx`)
**Verificar**: Se está usando variáveis CSS corretas

**Correção**:
```css
.astro-button-primary {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}

.astro-button-secondary {
  background-color: hsl(var(--secondary));
  color: hsl(var(--secondary-foreground));
  border-color: hsl(var(--border));
}
```

---

#### 7. **Inputs** (`astro-input.tsx`)
**Correção**:
```css
.astro-input {
  background-color: hsl(var(--input-background));
  border-color: hsl(var(--input-border));
  color: hsl(var(--foreground));
}

.astro-input:focus {
  border-color: hsl(var(--input-border-active));
  outline-color: hsl(var(--ring));
}
```

---

#### 8. **Cards** (`astro-card.tsx`)
**Correção**:
```css
.astro-card {
  background-color: hsl(var(--card));
  color: hsl(var(--card-foreground));
  border-color: hsl(var(--border));
}
```

---

## 📝 Checklist de Correção

### Fase 1: Verificação de Variáveis CSS
- [ ] Verificar se todas as variáveis estão definidas em `theme.css`
- [ ] Confirmar valores HSL corretos para Light Mode
- [ ] Confirmar valores HSL corretos para Dark Mode
- [ ] Testar transição entre temas

### Fase 2: Componentes Principais
- [ ] **Dashboard** (`cosmos-dashboard.tsx`)
  - [ ] Remover cores hardcoded dos cards de insights
  - [ ] Remover cores hardcoded dos cards de áreas
  - [ ] Verificar sidebar usa variáveis CSS
  - [ ] Verificar header usa variáveis CSS
  - [ ] Verificar footer usa variáveis CSS

- [ ] **Botões** (`astro-button.tsx`)
  - [ ] Verificar primary button
  - [ ] Verificar secondary button
  - [ ] Verificar estados hover/active/disabled

- [ ] **Inputs** (`astro-input.tsx`)
  - [ ] Verificar background
  - [ ] Verificar border (normal e focus)
  - [ ] Verificar texto e placeholder

- [ ] **Cards** (`astro-card.tsx`)
  - [ ] Verificar background
  - [ ] Verificar border
  - [ ] Verificar texto

### Fase 3: Componentes Secundários
- [ ] **Modais** (`inactivity-warning-modal.tsx`, `edit-user-modal.tsx`)
  - [ ] Verificar overlay
  - [ ] Verificar content
  - [ ] Verificar botões

- [ ] **Formulários** (`auth-portal.tsx`, `onboarding.tsx`)
  - [ ] Verificar inputs
  - [ ] Verificar labels
  - [ ] Verificar mensagens de erro/sucesso

- [ ] **Navegação** (Sidebar, Header)
  - [ ] Verificar itens de menu
  - [ ] Verificar estados hover/active
  - [ ] Verificar badges

### Fase 4: Estados e Interações
- [ ] **Hover States**
  - [ ] Botões
  - [ ] Cards
  - [ ] Links
  - [ ] Itens de menu

- [ ] **Focus States**
  - [ ] Inputs
  - [ ] Botões
  - [ ] Links

- [ ] **Disabled States**
  - [ ] Botões
  - [ ] Inputs

- [ ] **Active States**
  - [ ] Itens de menu ativos
  - [ ] Botões pressionados

### Fase 5: Validação Final
- [ ] Testar Light Mode completo
- [ ] Testar Dark Mode completo
- [ ] Testar transição entre temas
- [ ] Verificar contraste (acessibilidade)
- [ ] Comparar com design Figma

---

## 🛠️ Guia de Implementação

### Passo 1: Remover Cores Hardcoded

**Antes**:
```tsx
<div style={{ backgroundColor: theme === 'dark' ? '#000000' : '#ffffff' }}>
```

**Depois**:
```tsx
<div className="component-class">
```

```css
.component-class {
  background-color: hsl(var(--card));
  color: hsl(var(--card-foreground));
}
```

---

### Passo 2: Usar Variáveis CSS Sempre

**Regra de Ouro**: Nunca usar cores hardcoded. Sempre usar variáveis CSS.

**Exceções**:
- Hero section com gradiente fixo (conforme Figma)
- Elementos com cores específicas do Figma que não mudam com tema

---

### Passo 3: Testar Ambos os Temas

Para cada componente:
1. Abrir em Light Mode
2. Verificar cores conforme Figma
3. Trocar para Dark Mode
4. Verificar cores conforme Figma
5. Comparar com design original

---

### Passo 4: Verificar Contraste

Usar ferramenta de contraste (WCAG):
- Texto normal: mínimo 4.5:1
- Texto grande: mínimo 3:1
- Elementos interativos: mínimo 3:1

---

## 📊 Mapeamento de Cores do Figma

### Cores Específicas do Figma (Light Mode)

| Elemento | Cor Hex | Variável CSS | Uso |
|----------|---------|--------------|-----|
| Logo Background | `#6E1AE6` | `--logo-bg` | Logo no header |
| Search Input Background | `rgba(202, 199, 209, 0.3)` | `--input` | Fundo do input de busca |
| Card Border | `#CAC7D1` | `--border` | Bordas de cards |
| Texto Secundário | `#635C70` | `--muted-foreground` | Labels, descrições |
| Primary Button | `#FF8904` | `--primary` | Botões principais |
| Badge "New" | `rgba(255, 105, 0, 0.9)` | - | Badge laranja |

### Cores Específicas do Figma (Dark Mode)

| Elemento | Cor Hex | Variável CSS | Uso |
|----------|---------|--------------|-----|
| Logo Background | `#9A5EED` | `--logo-bg` | Logo no header |
| Card Background | `#1C1726` | `--card` | Fundo de cards |
| Texto Secundário | `#ADA3C2` | `--muted-foreground` | Labels, descrições |
| Primary Button | `#C27AFF` | `--primary` | Botões principais |

---

## 🎯 Prioridades de Correção

### 🔴 **Alta Prioridade** (Crítico)
1. Cards de Insights - remover cores hardcoded
2. Cards de Áreas - remover cores hardcoded
3. Sidebar - garantir uso de variáveis CSS
4. Header - garantir uso de variáveis CSS

### 🟡 **Média Prioridade** (Importante)
5. Botões - verificar todos os estados
6. Inputs - verificar focus states
7. Modais - verificar overlay e content

### 🟢 **Baixa Prioridade** (Melhorias)
8. Animações e transições
9. Estados hover mais refinados
10. Micro-interações

---

## ✅ Critérios de Aceitação

Um componente está correto quando:

1. ✅ **Não usa cores hardcoded** (exceto casos especiais documentados)
2. ✅ **Usa variáveis CSS** para todas as cores
3. ✅ **Funciona em Light Mode** conforme Figma
4. ✅ **Funciona em Dark Mode** conforme Figma
5. ✅ **Transição suave** entre temas
6. ✅ **Contraste adequado** (WCAG AA mínimo)
7. ✅ **Estados visuais claros** (hover, focus, active, disabled)

---

## 📚 Referências

- **Figma Design**: https://www.figma.com/design/fWJHUdy942lRVIOogbWrFj/modelo-astrologico
- **Arquivo de Tema**: `src/styles/theme.css`
- **Documentação UI/UX**: `docs/UI_UX_VERIFICACAO.md`

---

## 🔄 Processo de Revisão

1. **Desenvolvedor**: Implementa correções seguindo este plano
2. **Revisão Visual**: Compara com Figma (Light e Dark Mode)
3. **Teste Funcional**: Verifica transição entre temas
4. **Teste de Acessibilidade**: Verifica contraste
5. **Aprovação**: Marca como concluído no checklist

---

**Última atualização**: 2025-01-XX
**Versão**: 1.0.0
**Status**: 🟡 Em Andamento

