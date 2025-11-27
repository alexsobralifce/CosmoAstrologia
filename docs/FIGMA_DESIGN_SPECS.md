# Especificações do Design Figma

## 🎨 Design System - Login Screen and Dashboard

**Link do Figma:** https://www.figma.com/make/cPJ7DSdIcFXl6wmgQQOzvP/Login-Screen-and-Dashboard

---

## 📋 Como usar este documento

1. Abra o link do Figma acima
2. Preencha as especificações abaixo baseado no design
3. Salve o arquivo
4. O sistema será atualizado automaticamente para refletir o design

---

## 🎨 Cores

### Tema Principal (Extraído do Figma)
```css
/* Modo Claro (Dia) */
--background: #E8E4F3  /* Fundo lavanda/lilás suave */
--foreground: #1F1F1F  /* Texto preto escuro */
--card: #FFFFFF        /* Cards brancos */
--card-foreground: #1F1F1F
--primary: #7C3AED     /* Roxo/violeta do logo */
--primary-foreground: #FFFFFF
--secondary: #F97316   /* Laranja dos botões */
--secondary-foreground: #FFFFFF
--accent: #FF6B35      /* Laranja vibrante */
--accent-foreground: #FFFFFF
--muted: #E5E7EB       /* Cinza claro para inputs */
--muted-foreground: #6B7280  /* Texto secundário */
--border: #E5E7EB
--input: #E5E7EB       /* Fundo dos inputs */
--ring: #7C3AED

/* Modo Escuro (Noite) - conforme documentação */
--background: #0F0720  /* Roxo profundo/escuro */
--foreground: #F5F5F5  /* Off-white */
--card: #1A1A2E        /* Cards escuros */
--card-foreground: #F5F5F5
```

### Gradientes
```css
--gradient-bg: radial-gradient(circle at 20% 50%, rgba(124, 58, 237, 0.15), transparent 50%),
               radial-gradient(circle at 80% 80%, rgba(249, 115, 22, 0.1), transparent 50%)
```

---

## 📝 Tipografia

### Fontes (Extraído do Figma)
- **Logo/Títulos H1:** Serif (Playfair Display ou similar), Bold, 48-56px
  - Exemplo: "Cosmic Insight"
- **Títulos H2:** Serif, Bold, 32-36px
  - Exemplo: "Welcome Back"
- **Subtítulos:** Sans-serif (Inter), Regular, 16-18px
  - Exemplo: "Unlock the mysteries of your stars"
- **Corpo de texto:** Sans-serif (Inter), Regular, 14-16px
- **Labels de input:** Sans-serif (Inter), Medium, 14px
  - Cor: #6B7280 (texto secundário)
- **Botões:** Sans-serif (Inter), Semibold, 16px

### Line Heights
- **Títulos:** 1.2
- **Corpo:** 1.5
- **Labels:** 1.4

---

## 📐 Espaçamentos

### Padding/Margin System
```css
--spacing-xs: _____px
--spacing-sm: _____px
--spacing-md: _____px
--spacing-lg: _____px
--spacing-xl: _____px
--spacing-2xl: _____px
```

### Border Radius
```css
--radius-sm: _____px
--radius-md: _____px
--radius-lg: _____px
--radius-xl: _____px
--radius-full: 9999px
```

---

## 🔘 Componentes - Login Screen (Extraído do Figma)

### Layout Geral
- **Largura máxima do card:** 480px
- **Padding do card:** 48px (vertical) 40px (horizontal)
- **Espaçamento entre elementos:** 24px
- **Posição do logo:** centro (ícone roxo com estrela)
- **Tamanho do logo:** 80px × 80px
- **Background geral:** #E8E4F3 com gradientes radiais sutis

### Logo
- **Icon:** Estrela branca em círculo roxo (#7C3AED)
- **Tamanho do ícone:** 48px dentro do círculo
- **Border radius do círculo:** 24px (arredondado mas não totalmente redondo)

### Input Fields
- **Altura:** 56px
- **Padding horizontal:** 20px
- **Border width:** 0px (sem borda visível)
- **Border radius:** 12px
- **Background:** #E5E7EB (cinza claro)
- **Background (focus):** #E5E7EB (mantém mesmo)
- **Background (dark mode):** #1F2937
- **Cor do texto:** #1F1F1F
- **Cor do placeholder:** #9CA3AF
- **Label dentro do input:** Sim (placeholder interno)

### Botões
#### Botão Primário (Sign In)
- **Altura:** 56px
- **Padding horizontal:** 24px
- **Background:** #F97316 (laranja vibrante)
- **Background (hover):** #EA580C (laranja mais escuro)
- **Cor do texto:** #FFFFFF
- **Border radius:** 12px
- **Box shadow:** 0 4px 12px rgba(249, 115, 22, 0.25)
- **Ícone:** Seta para direita (→) no lado direito

#### Botão Secundário (Google)
- **Background:** #FFFFFF
- **Border:** 1px solid #E5E7EB
- **Cor do texto:** #1F1F1F
- **Ícone:** Logo Google colorido no lado esquerdo
- **Border radius:** 12px
- **Altura:** 48px

### Headers e Textos
- **Título principal:** "Cosmic Insight" - 48px, Serif, Bold, Preto
- **Subtítulo:** "Unlock the mysteries of your stars" - 16px, Sans-serif, #6B7280
- **Título do card:** "Welcome Back" - 32px, Serif, Bold, Preto
- **Descrição:** "Sign in to access your personalized dashboard" - 14px, #6B7280

### Controles de Tema/Idioma (Canto superior direito)
- **Botão EN:** Ícone de globo + texto
- **Botão tema:** Ícone de lua/sol
- **Tamanho:** 40px × 40px
- **Border radius:** 8px
- **Background:** Transparente, hover: rgba(255,255,255,0.1)

---

## 📊 Componentes - Dashboard

### Header
- **Altura:** _____px
- **Background:** #______
- **Border bottom:** _____px solid #______
- **Padding:** _____px

### Layout do Dashboard
- **Grid columns:** [número de colunas]
- **Gap entre colunas:** _____px
- **Largura máxima:** _____px

### Cards
- **Background:** #______
- **Border:** _____px solid #______
- **Border radius:** _____px
- **Padding:** _____px
- **Box shadow:** _____________________

### Sidebar (se houver)
- **Largura:** _____px
- **Background:** #______
- **Padding:** _____px

### Mapa Astral (Chart Wheel)
- **Diâmetro:** _____px
- **Cor de fundo:** #______
- **Espessura das linhas:** _____px
- **Cores dos planetas:** [lista]
- **Cores dos signos:** [lista]

---

## 🎭 Efeitos e Animações

### Sombras
```css
--shadow-sm: _____________________
--shadow-md: _____________________
--shadow-lg: _____________________
--shadow-xl: _____________________
```

### Transições
- **Duração padrão:** _____ms
- **Timing function:** [ease/linear/ease-in-out/etc]

### Hover Effects
- **Botões:** [descrever]
- **Cards:** [descrever]
- **Links:** [descrever]

---

## 📱 Responsividade

### Breakpoints
- **Mobile:** até _____px
- **Tablet:** _____px até _____px
- **Desktop:** acima de _____px

### Ajustes por Tela
- **Mobile:** [descrever mudanças]
- **Tablet:** [descrever mudanças]
- **Desktop:** [configuração completa]

---

## 🖼️ Ícones e Imagens

### Ícones
- **Biblioteca:** [Lucide/Heroicons/Custom/etc]
- **Tamanho padrão:** _____px
- **Cor padrão:** #______

### Imagens
- **Border radius:** _____px
- **Aspect ratio:** [valor]

---

## 📝 Observações Adicionais

[Adicione aqui quaisquer detalhes específicos do design que não se encaixam nas categorias acima]

---

## ✅ Checklist de Implementação

- [ ] Cores definidas
- [ ] Tipografia configurada
- [ ] Espaçamentos padronizados
- [ ] Componentes de login implementados
- [ ] Dashboard implementado
- [ ] Responsividade testada
- [ ] Animações aplicadas
- [ ] Testes de usabilidade realizados

---

**Última atualização:** [Data]
**Responsável:** [Nome]

