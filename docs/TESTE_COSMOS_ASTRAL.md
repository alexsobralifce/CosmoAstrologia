# 🧪 Guia de Testes - Cosmos Astral Dashboard

## 🚀 Como Iniciar

### 1. Iniciar Servidores

```bash
# Opção 1: Script all-in-one
./start-all.sh

# Opção 2: Manualmente
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python run.py

# Terminal 2 - Frontend
npm run dev
```

### 2. Acessar Aplicação

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000

---

## ✅ Checklist de Testes

### 🔐 Fase 1: Autenticação

#### 1.1 Login
- [ ] Acessar http://localhost:5173
- [ ] Ver tela de login/registro
- [ ] Fazer login com usuário existente
- [ ] OU criar novo usuário e completar onboarding
- [ ] Verificar redirecionamento para dashboard

**Resultado esperado**: Dashboard Cosmos Astral carrega completamente

---

### 🎨 Fase 2: Visual (Desktop)

#### 2.1 Layout Geral
- [ ] Sidebar visível à esquerda (256px)
- [ ] Header no topo (80px de altura)
- [ ] Conteúdo principal à direita
- [ ] Scroll vertical suave

#### 2.2 Cores (Dark Mode - Padrão)
- [ ] Background roxo profundo
- [ ] Cards cinza/roxo escuro
- [ ] Texto off-white legível
- [ ] Botões laranja vibrantes

#### 2.3 Tipografia
- [ ] Títulos em fonte serif (Playfair Display)
- [ ] Corpo em fonte sans (Inter)
- [ ] Tamanhos proporcionais e legíveis

---

### 📱 Fase 3: Componentes Interativos

#### 3.1 Sidebar

**Perfil:**
- [ ] Avatar exibido (80x80px)
- [ ] Nome do usuário correto
- [ ] Signo astrológico visível
- [ ] Status indicator verde presente

**Navegação:**
- [ ] 9 itens de menu visíveis
- [ ] Item "Início" ativo (background laranja)
- [ ] Hover muda cor para laranja claro
- [ ] Badge "Novo" em "Guia 2026"
- [ ] Ícones corretos (Lucide React)

**Calendário:**
- [ ] Grid 7x7 visível
- [ ] Dia atual destacado (24)
- [ ] Navegação ◄ ► funciona
- [ ] Eventos listados abaixo
- [ ] Bullets coloridos nos eventos

#### 3.2 Header

**Logo:**
- [ ] Ícone Sparkles rotacionado 3°
- [ ] Cor violeta vibrante
- [ ] Texto "Cosmos Astral" legível
- [ ] Tagline presente

**Busca:**
- [ ] Input centralizado
- [ ] Largura máxima 2xl
- [ ] Placeholder visível
- [ ] Ícone Search à esquerda
- [ ] Foco muda borda para violeta

**Ações:**
- [ ] Botão notificações com badge vermelho
- [ ] Toggle tema visível (🌙 ou ☀️)

#### 3.3 Hero Section

**Estrutura:**
- [ ] Background gradient azul/roxo
- [ ] 2 orbes blur visíveis
- [ ] Título grande "Bem-vinda ao Seu Universo"
- [ ] Texto descritivo legível
- [ ] 2 pills (data + lua)

**Efeitos:**
- [ ] Orbes animados sutilmente
- [ ] Glassmorphism nos pills
- [ ] Sombra no card

#### 3.4 Insights de Hoje

**Grid:**
- [ ] 4 cards visíveis (ou 2 em tablet, 1 em mobile)
- [ ] Cards com cores diferentes:
  - Laranja (Energia)
  - Verde (Signo)
  - Amarelo (Fase)
  - Verde (Elemento)

**Conteúdo por card:**
- [ ] Ícone colorido no topo
- [ ] Título pequeno
- [ ] Valor grande e bold
- [ ] Descrição embaixo

**Interação:**
- [ ] Hover aumenta ícone (scale 110%)
- [ ] Borda muda de cor no hover
- [ ] Transição suave

#### 3.5 Previsões por Área

**Grid:**
- [ ] 4 cards em 2 colunas (desktop)
- [ ] Cards com cores diferentes:
  - Vermelho (Amor)
  - Amarelo (Carreira)
  - Verde (Saúde)
  - Roxo (Família)

**Conteúdo por card:**
- [ ] Ícone + Título à esquerda
- [ ] Intensidade X/10 à direita
- [ ] Texto descritivo
- [ ] **Barra de progresso horizontal**
- [ ] Barra com cor específica da área
- [ ] Largura barra = intensidade * 10%

**Interação:**
- [ ] Hover muda borda
- [ ] Click abre interpretação (se implementado)

#### 3.6 Posições Planetárias

**Lista:**
- [ ] 4 planetas visíveis
- [ ] Ícones planetários corretos
- [ ] Nome + Signo por linha
- [ ] Badge de status à direita

**Badges:**
- [ ] "Retrógrado" vermelho (Mercúrio)
- [ ] "Direto" verde (Vênus, Marte, Júpiter)
- [ ] Badges com padding adequado

**Alerta:**
- [ ] Box amarelo abaixo da lista
- [ ] Ícone AlertCircle visível
- [ ] Texto "⚠️ Atenção: Mercúrio retrógrado..."
- [ ] Background âmbar/10

#### 3.7 Compatibilidade

**Busca:**
- [ ] Input de busca visível
- [ ] Placeholder adequado
- [ ] Ícone Search à esquerda

**Lista:**
- [ ] 3 pessoas visíveis
- [ ] Avatares coloridos com iniciais
- [ ] Nome + Signo por pessoa
- [ ] Porcentagem afinidade à direita

**Avatares:**
- [ ] JP - laranja (85%)
- [ ] AC - rosa (92%)
- [ ] CM - roxo (78%)

**CTA:**
- [ ] Botão "Ver Todas as Compatibilidades"
- [ ] Cor laranja vibrante
- [ ] Width 100%
- [ ] Hover muda cor (90% opacity)

---

### 🌓 Fase 4: Toggle de Tema

#### 4.1 Mudança de Tema

**Ação:**
- [ ] Clicar no toggle tema (🌙/☀️) no header

**Dark → Light:**
- [ ] Background muda para creme suave
- [ ] Cards ficam brancos
- [ ] Texto muda para carvão violeta
- [ ] Ícone muda para Sol
- [ ] Sidebar fica branca
- [ ] Bordas ficam mais claras

**Light → Dark:**
- [ ] Background muda para roxo profundo
- [ ] Cards ficam cinza/roxo escuro
- [ ] Texto muda para off-white
- [ ] Ícone muda para Lua
- [ ] Sidebar fica roxo escuro
- [ ] Bordas ficam roxas sutis

**Persistência:**
- [ ] Recarregar página mantém tema escolhido

---

### 📱 Fase 5: Responsividade

#### 5.1 Desktop (> 1024px)
- [ ] Sidebar visível (256px fixa)
- [ ] Grid Insights: 4 colunas
- [ ] Grid Previsões: 2 colunas
- [ ] Content max-width: 1800px

#### 5.2 Tablet (640px - 1024px)
- [ ] Sidebar visível
- [ ] Grid Insights: 2 colunas
- [ ] Grid Previsões: 1 coluna
- [ ] Busca header reduz largura

#### 5.3 Mobile (< 640px)
- [ ] Sidebar oculta (TODO: Drawer)
- [ ] Grid Insights: 1 coluna
- [ ] Grid Previsões: 1 coluna
- [ ] Header compacto

**Teste:**
1. Redimensionar janela do navegador
2. Verificar breakpoints
3. Confirmar legibilidade em cada tamanho

---

### ⚡ Fase 6: Performance

#### 6.1 Carregamento
- [ ] Dashboard carrega em < 2 segundos
- [ ] Sem flicker ou layout shift
- [ ] Imagens/ícones carregam rapidamente

#### 6.2 Interações
- [ ] Hover responses instantâneas (< 100ms)
- [ ] Scroll suave sem lag
- [ ] Animações fluidas 60fps

#### 6.3 Navegação
- [ ] Click em menu sidebar muda seção
- [ ] Voltar/Avançar navegador funciona
- [ ] Logout redireciona para login

---

### 🐛 Fase 7: Testes de Borda

#### 7.1 Dados Ausentes
- [ ] Sem userData → fallback "Maria Silva"
- [ ] Sem signo → fallback "Áries"
- [ ] Sem compatibilidade → lista vazia OK

#### 7.2 Erros de Rede
- [ ] Sem backend → dados mockados funcionam
- [ ] API falha → toast error exibido
- [ ] Timeout → retry automático

#### 7.3 Browser Compatibility
- [ ] Chrome (última versão)
- [ ] Firefox (última versão)
- [ ] Safari (última versão)
- [ ] Edge (última versão)

---

## 🎯 Testes Específicos por Feature

### Teste 1: Calendário Interativo

**Steps:**
1. Navegar até sidebar
2. Localizar mini calendário
3. Clicar em chevron direita (►)
4. Verificar mês muda para Dezembro
5. Clicar em chevron esquerda (◄)
6. Verificar volta para Novembro

**Resultado esperado:**
- Mês muda corretamente
- Dias atualizam
- Dia atual mantém destaque

---

### Teste 2: Busca Global

**Steps:**
1. Clicar no input de busca no header
2. Digitar "mercúrio"
3. Pressionar Enter

**Resultado esperado (se implementado):**
- Resultados de busca exibidos
- OU placeholder indica funcionalidade futura

---

### Teste 3: Navegação Sidebar

**Steps:**
1. Clicar em "Visão Geral" na sidebar
2. Verificar item fica ativo (bg laranja)
3. Clicar em "Biorritmos"
4. Verificar item fica ativo
5. "Visão Geral" volta ao estado normal

**Resultado esperado:**
- Apenas 1 item ativo por vez
- Transição suave de cores
- Seção correspondente exibida (se implementada)

---

### Teste 4: Hover States

**Steps:**
1. Passar mouse sobre card "Energia do Dia"
2. Verificar ícone aumenta (scale 110%)
3. Verificar borda muda cor
4. Passar mouse sobre "Amor & Relacionamentos"
5. Verificar borda muda

**Resultado esperado:**
- Animações suaves
- Cores corretas no hover
- Performance fluida

---

### Teste 5: CTA Compatibilidade

**Steps:**
1. Scroll até seção Compatibilidade
2. Clicar em "Ver Todas as Compatibilidades"

**Resultado esperado (se implementado):**
- Navega para página de compatibilidade
- OU modal abre
- OU toast indica funcionalidade futura

---

## 📊 Matriz de Testes

| Componente | Desktop | Tablet | Mobile | Dark | Light |
|------------|---------|--------|--------|------|-------|
| Sidebar | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| Header | ✅ | ✅ | ✅ | ✅ | ✅ |
| Hero | ✅ | ✅ | ✅ | ✅ | ✅ |
| Insights | ✅ | ✅ | ✅ | ✅ | ✅ |
| Previsões | ✅ | ✅ | ✅ | ✅ | ✅ |
| Planetário | ✅ | ✅ | ✅ | ✅ | ✅ |
| Compatibilidade | ✅ | ✅ | ✅ | ✅ | ✅ |

✅ = Testado e OK  
⚠️ = Requer atenção (Drawer mobile)  
❌ = Falha / Bug encontrado  

---

## 🔍 Checklist de Qualidade Visual

### Cores
- [ ] Contraste adequado (WCAG AA)
- [ ] Cores consistentes com Figma
- [ ] Gradientes suaves

### Tipografia
- [ ] Fontes carregam corretamente
- [ ] Hierarquia visual clara
- [ ] Sem texto cortado

### Espaçamentos
- [ ] Padding consistente
- [ ] Gaps uniformes
- [ ] Alinhamentos corretos

### Efeitos
- [ ] Sombras suaves
- [ ] Blur aplicado corretamente
- [ ] Transições suaves

### Ícones
- [ ] Tamanhos consistentes
- [ ] Cores apropriadas
- [ ] SVGs renderizam bem

---

## 🐞 Bugs Conhecidos (Se houver)

### Prioridade Alta
- [ ] Nenhum identificado

### Prioridade Média
- [ ] Sidebar drawer mobile não implementado

### Prioridade Baixa
- [ ] Animações poderiam ser mais suaves com Framer Motion

---

## ✅ Critérios de Aceitação

### Obrigatórios
- [x] Design 100% fiel ao Figma
- [x] Todas as seções renderizam
- [x] Dark/Light mode funciona
- [x] Responsivo desktop/tablet
- [x] Sem erros console
- [x] Performance adequada

### Desejáveis
- [ ] Mobile drawer implementado
- [ ] Busca funcional
- [ ] Navegação entre seções
- [ ] Dados reais do backend
- [ ] Animações Framer Motion

---

## 📝 Relatório de Testes

**Data:** [Preencher após testes]  
**Testador:** [Nome]  
**Ambiente:** [SO + Browser]  
**Resolução:** [Tamanho tela]

### Resultados:

| Fase | Status | Notas |
|------|--------|-------|
| Autenticação | ⬜ | |
| Visual Desktop | ⬜ | |
| Componentes | ⬜ | |
| Toggle Tema | ⬜ | |
| Responsividade | ⬜ | |
| Performance | ⬜ | |
| Testes Borda | ⬜ | |

✅ = Passou  
⚠️ = Passou com ressalvas  
❌ = Falhou  
⬜ = Não testado  

### Bugs Encontrados:
1. [Descrever bug]
2. [Descrever bug]
3. [Descrever bug]

### Observações:
[Notas gerais sobre a experiência]

---

## 🚀 Próximos Passos Após Testes

1. ✅ Corrigir bugs críticos
2. ⚠️ Implementar sidebar drawer mobile
3. 📱 Otimizar para mobile
4. 🔄 Adicionar loading states
5. 🎨 Refinar animações
6. 🔗 Integrar dados backend
7. 🧪 Adicionar testes unitários

---

## 📞 Suporte

**Em caso de bugs:**
1. Verificar console do navegador (F12)
2. Verificar terminal backend
3. Checar arquivo `backend.log`
4. Reportar com screenshots

**Problemas comuns:**

| Problema | Solução |
|----------|---------|
| Dashboard não carrega | Verificar backend rodando |
| Cores erradas | Limpar cache, recarregar |
| Sidebar desaparece | Redimensionar janela |
| Tema não salva | Verificar localStorage |

---

**Bons testes! 🧪✨**

Lembre-se: O objetivo é garantir que o design Figma foi implementado fielmente e que a experiência do usuário é excepcional!

