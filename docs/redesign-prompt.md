## Prompt de Implementação – Novo Design Astrologia

Use estas instruções como briefing completo para aplicar 100% do redesign inspirado no layout publicado em [`https://motto-aroma-20959676.figma.site/`](https://motto-aroma-20959676.figma.site/). O objetivo é substituir integralmente o visual atual pelo conceito “Faça seu mapa astral”, mantendo apenas a lógica de negócio existente.

---

### 1. Identidade visual (tokens)
- **Paleta base**
  - Fundo cósmico em gradiente diagonal `#F5E6D3 → #FAF8F5 → #E8DFD5` (135º). Aplicar no `body`.
  - Primário coral quente `#E07A5F` (hero, CTA e links de destaque) com gradiente linear (direção 90º) `rgba(237,152,120,0.8)` → `#E07A5F`.
  - Secundário verde sálvia `#81B29A` (subtítulos, CTAs secundárias).
  - Texto escuro `#1A1F2E` e apoio `#2D3548`.
  - Neutros claros: `#FAFAF9` (card), `#E7E5E4` (bordas inputs), `#F4F1ED` (divisor “ou”).
  - Acento Google: borda `#E7E5E4`, ícone colorido oficial (paths `#4285F4`, `#34A853`, `#FBBC05`, `#EA4335`).
- **Tipografia**
  - Títulos: `Crimson Pro`, 40px, peso 600, tracking normal.
  - Demais textos, inputs e CTAs: `Inter` 16px; usar pesos 400/500/600 conforme contraste.
  - Aplicar `font-smoothing: antialiased` para consistência.
- **Bordas e raios**
  - Cartão principal: raio 24px, sombra `0 25px 50px -12px rgba(0,0,0,0.25)`.
  - Inputs e botões: raio 16px (usar 16.4px para fidelidade), bordas de 1px (`#E7E5E4`) em campos e 2px em botões outline.
- **Spacing**
  - Card: padding interno 32px desktop, 24px mobile.
  - Pilha vertical dos elementos com 24px; inputs com margin-bottom 16px.

### 2. Estrutura de layout
1. **Body / Section**
   - `min-height: 100vh`, centralizar card via `flex` (`align-items: center; justify-content: center; padding: 16px`).
   - Aplicar gradiente de fundo e, opcionalmente, animação suave (10–15s) para reforçar tema etéreo.
2. **Card “Faça seu mapa astral”**
   - Largura fixa 448px desktop; 100% até 384px em mobile.
   - Conteúdo em coluna: título, subtítulo, formulário, divisor “ou”, CTA social e bloco “Ainda não tem uma conta?”.
3. **Tipografia dentro do card**
   - Título `h1`: `#E07A5F`, 40px, `Crimson Pro`.
   - Subtítulo “Entre na sua conta”: `#81B29A`, 16px, `Inter 400`.
4. **Imagem / Ornamentação**
   - Caso queira replicar a arte de fundo, use ilustração vetorial astral semi-transparente alinhada ao topo do card (SVG em `position: absolute; inset: 0; opacity: 0.15`), garantindo não interferir na leitura.

### 3. Componentes e estados
#### 3.1 Inputs
- Estrutura `label + input`.
- Labels: `Inter 400`, `#1A1F2E`, margin-bottom 8px.
- Inputs: altura 52px, padding `12px 16px`, placeholder `#1A1F2E` 70% opacidade.
- Estados:
  - `:focus` com borda 1px `#E07A5F` e sombra `0 0 0 4px rgba(224,122,95,0.15)`.
  - Erro: borda `#D25B5B`, helper text 14px.
- Campo senha: ícone “eye” (Lucide) alinhado à direita, 20px, cor `#2D3548` com hover `#E07A5F`.

#### 3.2 Ações principais
- **Botão “Entrar”**
  - Largura total, padding vertical 16px.
  - Gradiente coral, texto `#FAFAF9`, peso 600.
  - Hover: aumentar brilho + leve `transform: translateY(-1px)`.
  - Disabled: reduzir opacidade para 60%.
- **Link “Esqueceu a senha?”**
  - `Inter 400`, `#E07A5F`, underline on hover.

#### 3.3 Divisor social
- Linha com texto “ou”: usar `display: flex; align-items: center; gap: 16px`.
- Linhas laterais `height: 1px; background: #E7E5E4; flex: 1`.

#### 3.4 Botão “Entrar com Google”
- Outline 2px `#E7E5E4`, raio 16px, altura 56px.
- Conteúdo centralizado com gap 12px entre ícone SVG (24px) e texto.
- Hover: borda coral suave `#E07A5F`.

#### 3.5 CTA secundário
- Bloco final: texto `#2D3548` + botão fantasma “Criar Nova Conta”.
- Botão: borda e texto `#81B29A`, hover preenchido `#81B29A` com texto `#FAFAF9`.

### 4. Responsividade e comportamento
- Até 640px: reduzir título para 32px, padding do card 24px, espaçamento geral 16px.
- Ajustar grid para permitir altura total com `margin-top: 40px` para evitar colar no topo.
- Inputs devem ocupar 100% e manter toques amigáveis (min 48px).
- Mantém semântica acessível (`<label for>`, `aria-label` para ícones, botões com `type="submit"`).

### 5. Microinterações e feedback
- Validar formulários inline: mensagens 14px `#E07A5F`.
- Animar botão primário em sucesso (ex.: pseudo ripple ou brilho 250ms).
- Password toggle deve alternar `type=password/text` e anunciar via `aria-pressed`.
- Google CTA dispara fluxo OAuth; mostrar loading spinner 16px alinhado ao texto quando aguardando resposta.

### 6. Implementação prática
- Criar theme tokens em `src/styles/globals.css` ou provider (`theme-provider.tsx`) com as cores acima.
- Atualizar componentes compartilhados (`astro-button`, `astro-input`) para aceitarem variantes `primary`, `outline`, `ghost`.
- Refatorar telas de autenticação (`auth-portal.tsx`, `auth-loader.tsx`) para seguir a hierarquia descrita: card centralizado, seções na ordem título → subtítulo → formulário → divisor → CTA social → convite de cadastro.
- Substituir quaisquer backgrounds/imagens anteriores por gradiente indicado e remover estilos remanescentes do tema antigo.
- Garantir que dark mode atual seja desativado ou reflita cores equivalentes (usar interpolação com `mix-blend-mode` se necessário).

### 7. Checklist de entrega
1. Tokens globais criados (cores, tipografia, raios, sombras).
2. Componentes `Input`, `Button`, `Link`, `Divider`, `SocialButton` com variantes e estados.
3. Tela de login replicando ordem e espaçamentos (ver medidas acima).
4. Acessibilidade validada (tab order, contrast ratio ≥ 4.5).
5. Responsividade revisada em 320px, 768px e ≥1280px.
6. Testes de regressão para fluxos de autenticação (login, esqueci senha, cadastro, Google).

Siga estritamente este prompt para garantir que o novo layout reflita o design de referência e substitua completamente o visual anterior.

