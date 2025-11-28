# 🎨 Mapeamento Completo do Sistema CSS - Cosmos Astral

## 📋 Estrutura de Arquivos

### Arquivos Principais

1. **`src/styles/theme.css`** ⭐ **ARQUIVO PRINCIPAL**
   - Contém TODAS as variáveis CSS do sistema
   - Define temas Dark e Light
   - Formato HSL para compatibilidade com Tailwind
   - Única fonte de verdade para cores e variáveis

2. **`src/index.css`** - Entry Point
   - Importa `theme.css` e `globals.css`
   - Configura Tailwind (@tailwind directives)
   - Classes utilitárias customizadas (cores semânticas)

3. **`src/styles/globals.css`** - Base Styles
   - Estilos base do Tailwind (@layer base)
   - Tipografia base
   - Aplicação de fontes

4. **`src/styles/figma-theme.css`** - ⚠️ DEPRECADO
   - Mantido apenas para referência
   - Não deve ser importado

### Arquivos de Configuração

- **`tailwind.config.js`**
  - Configuração do Tailwind CSS
  - Mapeia variáveis CSS para classes Tailwind
  - Formato: `hsl(var(--variable-name))`

---

## 🎨 Sistema de Variáveis CSS

### Formato das Variáveis

Todas as variáveis estão no formato **HSL sem a função `hsl()`** para compatibilidade com Tailwind:

```css
/* ✅ CORRETO (para Tailwind) */
--primary: 265 80% 65%;

/* ❌ ERRADO */
--primary: hsl(265, 80%, 65%);
```

O Tailwind usa assim: `hsl(var(--primary))` → `hsl(265 80% 65%)`

---

## 🌓 Temas (Dark/Light)

### Tema Escuro (Dark Mode) - Padrão

**Aplicado em:** `:root, .dark`

| Variável | Valor HSL | Hex | Descrição |
|----------|-----------|-----|-----------|
| `--background` | `260 30% 8%` | `#120E1B` | Fundo principal roxo profundo |
| `--foreground` | `260 10% 95%` | `#F2F1F4` | Texto principal off-white |
| `--card` | `260 25% 12%` | `#1C1726` | Fundo de cards |
| `--primary` | `265 80% 65%` | `#C27AFF` | Violeta vibrante (botões primários) |
| `--accent` | `25 85% 60%` | `#FF8904` | Laranja accent (CTAs) |
| `--muted` | `260 20% 20%` | - | Backgrounds sutis |
| `--border` | `260 20% 25%` | `#30293D` | Bordas |
| `--destructive` | `0 70% 60%` | `#FB2C36` | Vermelho (erros) |

### Tema Claro (Light Mode)

**Aplicado em:** `.light`

| Variável | Valor HSL | Hex | Descrição |
|----------|-----------|-----|-----------|
| `--background` | `40 20% 98%` | `#FBFAF9` | Fundo creme suave |
| `--foreground` | `260 40% 10%` | `#160F24` | Texto carvão violeta |
| `--card` | `0 0% 100%` | `#FFFFFF` | Fundo branco puro |
| `--primary` | `265 80% 50%` | `#7C3AED` | Violeta vibrante |
| `--accent` | `25 85% 60%` | `#FF8904` | Laranja vibrante |
| `--muted` | `260 15% 95%` | - | Backgrounds sutis claros |
| `--border` | `260 15% 90%` | `#E5E7EB` | Bordas sutis |
| `--destructive` | `0 70% 50%` | `#DC2626` | Vermelho |

---

## 📦 Categorias de Variáveis

### 1. Cores Base
- `--background` - Fundo principal
- `--foreground` - Texto principal

### 2. Cards & Containers
- `--card` - Fundo de cards
- `--card-foreground` - Texto em cards
- `--popover` - Fundo de popovers
- `--popover-foreground` - Texto em popovers

### 3. Botões & Ações
- `--primary` - Cor primária (botões principais)
- `--primary-foreground` - Texto em botões primários
- `--secondary` - Cor secundária
- `--secondary-foreground` - Texto em botões secundários
- `--accent` - Cor de destaque (CTAs)
- `--accent-foreground` - Texto em acentos

### 4. Estados
- `--muted` - Backgrounds sutis
- `--muted-foreground` - Texto muted
- `--destructive` - Cor destrutiva (erros)
- `--destructive-foreground` - Texto em erros

### 5. Bordas & Inputs
- `--border` - Cor de bordas
- `--input` - Fundo de inputs
- `--input-background` - Fundo alternativo de inputs
- `--input-border` - Borda de inputs
- `--input-border-active` - Borda de inputs em foco
- `--ring` - Indicador de foco (outline)
- `--switch-background` - Fundo de switches

### 6. Sidebar/Navegação
- `--sidebar` - Fundo da sidebar
- `--sidebar-foreground` - Texto da sidebar
- `--sidebar-primary` - Elementos primários da sidebar
- `--sidebar-primary-foreground` - Texto primário
- `--sidebar-accent` - Cor de hover na sidebar
- `--sidebar-accent-foreground` - Texto em hover
- `--sidebar-border` - Bordas da sidebar
- `--sidebar-ring` - Foco na sidebar

### 7. Charts
- `--chart-1` a `--chart-5` - Cores para gráficos

---

## 🎯 Uso no Tailwind

### Classes Padrão

```tsx
// Backgrounds
<div className="bg-background">...</div>
<div className="bg-card">...</div>
<div className="bg-primary">...</div>
<div className="bg-accent">...</div>

// Texto
<p className="text-foreground">...</p>
<p className="text-muted-foreground">...</p>
<p className="text-primary">...</p>

// Bordas
<div className="border border-border">...</div>
<div className="border-primary">...</div>

// Inputs
<input className="bg-input-background border-input-border" />
```

### Com Opacidade

```tsx
// 10% de opacidade
<div className="bg-primary/10">...</div>

// 50% de opacidade
<div className="bg-muted/50">...</div>
```

---

## 🔧 Classes Utilitárias Customizadas

### Cores Semânticas (em `index.css`)

```css
.bg-orange        /* Laranja vibrante */
.text-orange      /* Texto laranja */
.bg-emerald-50    /* Verde esmeralda claro */
.bg-amber-500     /* Amarelo âmbar */
.bg-purple-500    /* Roxo */
```

### Search Bars

```css
.search-bar-header  /* Barra de busca grande (48px) */
.search-bar-small   /* Barra de busca pequena (40px) */
```

### Animações

```css
.animate-fadeIn     /* Fade in suave */
.animate-twinkle    /* Efeito twinkle */
.animate-spin-slow  /* Rotação lenta (8s) */
```

---

## 📐 Tipografia

### Fontes

- **Serifada:** `Playfair Display` (títulos)
- **Sans-serif:** `Inter` (corpo de texto)

### Variáveis

```css
--font-serif: 'Playfair Display', serif;
--font-sans: 'Inter', sans-serif;
--font-size: 16px;
--font-weight-normal: 400;
--font-weight-medium: 500;
```

### Uso

```tsx
<h1 className="font-serif">Título</h1>
<p className="font-sans">Texto</p>
```

---

## 🔄 Migração de Código Antigo

### ❌ Antes (Conflitante)

```css
/* Múltiplos arquivos com definições diferentes */
:root {
  --primary: hsl(265, 80%, 65%);  /* index.css */
}
:root {
  --primary: #C27AFF;  /* globals.css */
}
:root {
  --figma-primary-dark: #C27AFF;  /* figma-theme.css */
}
```

### ✅ Agora (Consolidado)

```css
/* Apenas theme.css */
:root, .dark {
  --primary: 265 80% 65%;  /* Formato HSL para Tailwind */
}
```

---

## ✅ Checklist de Estabilidade

- [x] Todas as variáveis consolidadas em `theme.css`
- [x] Formato HSL consistente (sem função `hsl()`)
- [x] Temas Dark e Light definidos
- [x] Tailwind config atualizado
- [x] Duplicações removidas
- [x] Imports organizados
- [x] Documentação criada

---

## 🚨 Problemas Comuns e Soluções

### Problema: Cores não aparecem

**Solução:** Verifique se está usando `hsl(var(--variable))` no Tailwind config.

### Problema: Tema não muda

**Solução:** Verifique se a classe `.light` ou `.dark` está no elemento `<html>`.

### Problema: Conflitos de cores

**Solução:** Certifique-se de que apenas `theme.css` define variáveis de tema.

---

## 📚 Referências

- [Tailwind CSS - Using CSS Variables](https://tailwindcss.com/docs/customizing-colors#using-css-variables)
- [Figma Design](https://www.figma.com/design/aI95Nh89jEv6YtxGq1ksnj)

---

**Última atualização:** 2025-01-27
**Versão do sistema:** 2.0 (Consolidado)

