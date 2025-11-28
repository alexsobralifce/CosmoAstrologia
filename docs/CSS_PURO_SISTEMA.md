# Sistema CSS Puro - Cosmos Astral

## 📋 Resumo

O Tailwind CSS foi completamente removido e substituído por um sistema CSS puro e organizado, incluindo classes utilitárias de **Flexbox** e **CSS Grid**.

## ✅ O que foi feito

### 1. Remoção do Tailwind
- ✅ Removidas dependências do `package.json`:
  - `tailwindcss`
  - `@tailwindcss/postcss`
  - `tailwind-merge`
  - `autoprefixer` e `postcss` (não mais necessários)
- ✅ Deletados arquivos de configuração:
  - `tailwind.config.js`
  - `postcss.config.js`
- ✅ Removidas diretivas `@tailwind` do `index.css`
- ✅ Substituído `twMerge` por `clsx` simples no `utils.ts`

### 2. Sistema CSS Puro Criado

#### Arquivo Principal: `src/styles/main.css`

**Estrutura:**
1. **Fontes** - Importação do Google Fonts (Tinos + Inter)
2. **Variáveis CSS** - Sistema de temas (dark/light)
3. **Reset e Estilos Base** - Normalização
4. **Classes Utilitárias de Cores** - Sistema de cores baseado em variáveis
5. **Flexbox** - Classes utilitárias completas
6. **CSS Grid** - Classes utilitárias completas
7. **Posicionamento e Dimensões** - Classes de layout
8. **Border Radius** - Classes de arredondamento
9. **Padding e Margin** - Sistema completo de espaçamento
10. **Cores Específicas** - Classes para cores do tema
11. **Animações** - Keyframes e classes de animação
12. **Estilos para Cards e Body**

## 🎨 Flexbox - Classes Disponíveis

### Display e Direção
- `.flex` - `display: flex`
- `.flex-col` - `flex-direction: column`
- `.flex-row` - `flex-direction: row`
- `.flex-wrap` - `flex-wrap: wrap`
- `.flex-nowrap` - `flex-wrap: nowrap`

### Alinhamento de Itens (Cross-axis)
- `.items-start` - `align-items: flex-start`
- `.items-center` - `align-items: center`
- `.items-end` - `align-items: flex-end`
- `.items-stretch` - `align-items: stretch`
- `.items-baseline` - `align-items: baseline`

### Justificação (Main-axis)
- `.justify-start` - `justify-content: flex-start`
- `.justify-center` - `justify-content: center`
- `.justify-end` - `justify-content: flex-end`
- `.justify-between` - `justify-content: space-between`
- `.justify-around` - `justify-content: space-around`
- `.justify-evenly` - `justify-content: space-evenly`

### Alinhamento de Conteúdo
- `.content-start` - `align-content: flex-start`
- `.content-center` - `align-content: center`
- `.content-end` - `align-content: flex-end`
- `.content-between` - `align-content: space-between`
- `.content-around` - `align-content: space-around`

### Alinhamento Próprio (Self)
- `.self-start` - `align-self: flex-start`
- `.self-center` - `align-self: center`
- `.self-end` - `align-self: flex-end`
- `.self-stretch` - `align-self: stretch`

### Flex Grow/Shrink
- `.flex-1` - `flex: 1 1 0%`
- `.flex-auto` - `flex: 1 1 auto`
- `.flex-initial` - `flex: 0 1 auto`
- `.flex-none` - `flex: none`
- `.flex-grow` - `flex-grow: 1`
- `.flex-shrink` - `flex-shrink: 1`
- `.flex-shrink-0` - `flex-shrink: 0`

## 📐 CSS Grid - Classes Disponíveis

### Display
- `.grid` - `display: grid`

### Grid Columns
- `.grid-cols-1` até `.grid-cols-12` - `grid-template-columns: repeat(N, minmax(0, 1fr))`

### Grid Rows
- `.grid-rows-1` até `.grid-rows-4` - `grid-template-rows: repeat(N, minmax(0, 1fr))`

### Grid Auto
- `.grid-auto-cols-auto` - `grid-auto-columns: auto`
- `.grid-auto-cols-min` - `grid-auto-columns: min-content`
- `.grid-auto-cols-max` - `grid-auto-columns: max-content`
- `.grid-auto-cols-fr` - `grid-auto-columns: minmax(0, 1fr)`
- `.grid-auto-rows-auto` - `grid-auto-rows: auto`
- `.grid-auto-rows-min` - `grid-auto-rows: min-content`
- `.grid-auto-rows-max` - `grid-auto-rows: max-content`
- `.grid-auto-rows-fr` - `grid-auto-rows: minmax(0, 1fr)`

### Gap
- `.gap-0` até `.gap-12` - Espaçamento geral
- `.gap-x-0` até `.gap-x-8` - Espaçamento entre colunas
- `.gap-y-0` até `.gap-y-8` - Espaçamento entre linhas

### Column Span
- `.col-span-1` até `.col-span-12` - `grid-column: span N / span N`
- `.col-span-full` - `grid-column: 1 / -1`

### Row Span
- `.row-span-1` até `.row-span-6` - `grid-row: span N / span N`
- `.row-span-full` - `grid-row: 1 / -1`

### Column Start/End
- `.col-start-1` até `.col-start-13` - `grid-column-start: N`
- `.col-start-auto` - `grid-column-start: auto`
- `.col-end-1` até `.col-end-13` - `grid-column-end: N`
- `.col-end-auto` - `grid-column-end: auto`

### Row Start/End
- `.row-start-1` até `.row-start-7` - `grid-row-start: N`
- `.row-start-auto` - `grid-row-start: auto`
- `.row-end-1` até `.row-end-7` - `grid-row-end: N`
- `.row-end-auto` - `grid-row-end: auto`

### Grid Auto Flow
- `.grid-flow-row` - `grid-auto-flow: row`
- `.grid-flow-col` - `grid-auto-flow: column`
- `.grid-flow-dense` - `grid-auto-flow: dense`
- `.grid-flow-row-dense` - `grid-auto-flow: row dense`
- `.grid-flow-col-dense` - `grid-auto-flow: column dense`

## 📏 Outras Classes Utilitárias

### Dimensões
- `.w-full`, `.w-auto`, `.w-1/2`, `.w-1/3`, `.w-2/3`, `.w-1/4`, `.w-3/4`, `.w-screen`
- `.h-full`, `.h-auto`, `.h-screen`
- `.min-h-screen`
- `.max-w-full`, `.max-h-full`

### Posicionamento
- `.relative`, `.absolute`, `.fixed`, `.sticky`
- `.inset-0`, `.top-*`, `.right-*`, `.bottom-*`, `.left-*`
- `.z-0` até `.z-50`

### Border Radius
- `.rounded-none`, `.rounded`, `.rounded-sm`, `.rounded-md`, `.rounded-lg`, `.rounded-xl`, `.rounded-2xl`, `.rounded-full`

### Padding
- `.p-0` até `.p-8`
- `.px-*`, `.py-*`, `.pt-*`, `.pr-*`, `.pb-*`, `.pl-*`

### Margin
- `.m-0` até `.m-8`, `.m-auto`
- `.mx-*`, `.my-*`, `.mt-*`, `.mr-*`, `.mb-*`, `.ml-*`

## 🎯 Exemplos de Uso

### Flexbox
```html
<div class="flex items-center justify-between gap-4">
  <div class="flex-1">Conteúdo 1</div>
  <div class="flex-shrink-0">Conteúdo 2</div>
</div>
```

### CSS Grid
```html
<div class="grid grid-cols-3 gap-4">
  <div class="col-span-2">Coluna 1-2</div>
  <div>Coluna 3</div>
</div>
```

### Layout Responsivo com Grid
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <!-- Itens do grid -->
</div>
```

## 📝 Próximos Passos

1. Converter componentes que ainda usam classes Tailwind para usar as novas classes CSS puro
2. Testar todos os componentes para garantir compatibilidade
3. Adicionar classes responsivas se necessário (usando media queries)
4. Documentar padrões de uso específicos do projeto

## 🔗 Arquivos Relacionados

- `src/styles/main.css` - Sistema CSS principal
- `src/styles/login-page.css` - CSS específico da página de login (já em CSS puro)
- `src/index.css` - Importa o main.css
- `src/components/ui/utils.ts` - Função `cn()` simplificada (sem tailwind-merge)

