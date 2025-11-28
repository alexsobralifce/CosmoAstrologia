# 🎯 Guia de CSS Responsivo - Flexbox e CSS Grid

## 📱 Sistema Responsivo Priorizado

Este sistema CSS dá **prioridade máxima** ao uso de **Flexbox** e **CSS Grid** para criar layouts responsivos e modernos.

## 🎨 Filosofia

1. **Mobile First**: Estilos base para mobile, depois expandimos para telas maiores
2. **Flexbox**: Para layouts unidimensionais (linha ou coluna)
3. **CSS Grid**: Para layouts bidimensionais (linha E coluna)
4. **Sem Tailwind**: CSS puro, organizado e performático

## 📐 Breakpoints

```css
/* Mobile First */
Base: < 640px (mobile)

/* Breakpoints */
sm: 640px   - Mobile grande / Tablet pequeno
md: 768px   - Tablet
lg: 1024px  - Desktop pequeno
xl: 1280px  - Desktop
2xl: 1536px - Desktop grande
```

## 🔄 Flexbox - Uso Prioritário

### Quando usar Flexbox:
- Layouts unidimensionais (linha OU coluna)
- Alinhamento de itens
- Distribuição de espaço
- Navegação horizontal/vertical
- Cards em linha
- Formulários

### Exemplos:

```html
<!-- Container flexível -->
<div class="flex flex-col items-center gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Responsivo: coluna no mobile, linha no desktop -->
<div class="flex flex-col md:flex-row items-center justify-between gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Stack responsivo -->
<div class="responsive-stack">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

## 📊 CSS Grid - Uso Prioritário

### Quando usar CSS Grid:
- Layouts bidimensionais (linha E coluna)
- Cards em grid
- Formulários complexos
- Dashboards
- Galerias de imagens
- Layouts de página completos

### Exemplos:

```html
<!-- Grid básico -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
</div>

<!-- Grid responsivo automático -->
<div class="responsive-grid">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

<!-- Grid com spans responsivos -->
<div class="grid grid-cols-12 gap-4">
  <div class="col-span-12 md:col-span-6 lg:col-span-4">Sidebar</div>
  <div class="col-span-12 md:col-span-6 lg:col-span-8">Conteúdo</div>
</div>
```

## 🎯 Padrões de Layout Responsivo

### 1. Container Responsivo
```html
<div class="container">
  <!-- Conteúdo com largura máxima responsiva -->
</div>
```

### 2. Stack Responsivo (Vertical → Horizontal)
```html
<div class="responsive-stack">
  <!-- Coluna no mobile, linha no desktop -->
</div>
```

### 3. Grid Responsivo (1 → 2 → 3 colunas)
```html
<div class="responsive-grid">
  <!-- 1 coluna mobile, 2 tablet, 3+ desktop -->
</div>
```

### 4. Flex Wrap Responsivo
```html
<div class="flex-wrap-responsive">
  <!-- Wrap no mobile, nowrap no desktop -->
</div>
```

## 📱 Classes Responsivas Disponíveis

### Flexbox Responsivo
- `.sm:flex-row`, `.md:flex-row`, `.lg:flex-row`
- `.sm:flex-col`, `.md:flex-col`, `.lg:flex-col`
- `.sm:items-center`, `.md:items-center`, `.lg:items-center`
- `.sm:justify-between`, `.md:justify-between`, `.lg:justify-between`
- `.sm:gap-4`, `.md:gap-6`, `.lg:gap-8`

### CSS Grid Responsivo
- `.sm:grid-cols-2`, `.md:grid-cols-3`, `.lg:grid-cols-4`
- `.sm:col-span-6`, `.md:col-span-4`, `.lg:col-span-3`
- `.sm:col-span-full`, `.md:col-span-6`

### Dimensões Responsivas
- `.sm:w-full`, `.md:w-1/2`, `.lg:w-1/3`
- `.sm:w-auto`, `.md:w-1/2`

### Espaçamento Responsivo
- `.sm:p-4`, `.md:p-6`, `.lg:p-8`
- `.sm:px-4`, `.md:px-6`
- `.sm:py-4`, `.md:py-6`

### Display Responsivo
- `.sm:flex`, `.md:grid`, `.lg:block`
- `.sm:hidden`, `.md:block`

## 🎨 Exemplos Práticos

### Dashboard Responsivo
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="col-span-1">Card 1</div>
  <div class="col-span-1">Card 2</div>
  <div class="col-span-1 md:col-span-2 lg:col-span-1">Card 3</div>
</div>
```

### Navegação Responsiva
```html
<nav class="flex flex-col md:flex-row items-center justify-between gap-4">
  <div class="logo">Logo</div>
  <div class="flex flex-col md:flex-row gap-4">
    <a href="#">Link 1</a>
    <a href="#">Link 2</a>
  </div>
</nav>
```

### Formulário Responsivo
```html
<form class="grid grid-cols-1 md:grid-cols-2 gap-4">
  <div class="col-span-1 md:col-span-2">
    <input type="text" placeholder="Nome completo" />
  </div>
  <div>
    <input type="email" placeholder="Email" />
  </div>
  <div>
    <input type="tel" placeholder="Telefone" />
  </div>
</form>
```

### Cards em Grid Responsivo
```html
<div class="responsive-grid">
  <div class="card">Card 1</div>
  <div class="card">Card 2</div>
  <div class="card">Card 3</div>
  <div class="card">Card 4</div>
</div>
```

## 🚀 Boas Práticas

1. **Sempre comece com mobile**: Estilos base para mobile primeiro
2. **Use Flexbox para layouts simples**: Navegação, alinhamentos, espaçamentos
3. **Use CSS Grid para layouts complexos**: Dashboards, cards, formulários
4. **Combine quando necessário**: Grid para estrutura, Flexbox para itens internos
5. **Teste em diferentes tamanhos**: Use DevTools para testar breakpoints

## 📝 Checklist de Responsividade

- [ ] Layout funciona em mobile (< 640px)
- [ ] Layout funciona em tablet (768px)
- [ ] Layout funciona em desktop (1024px+)
- [ ] Textos são legíveis em todos os tamanhos
- [ ] Botões são clicáveis em mobile (min 44x44px)
- [ ] Imagens são responsivas
- [ ] Grid/Flex adapta-se aos breakpoints
- [ ] Não há overflow horizontal

## 🔗 Arquivos Relacionados

- `src/styles/main.css` - Classes base de Flexbox e Grid
- `src/styles/responsive.css` - Classes responsivas
- `src/styles/login-page.css` - Exemplo de página responsiva

