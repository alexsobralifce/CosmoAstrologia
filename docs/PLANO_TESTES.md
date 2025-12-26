# Plano de Testes - CosmoAstrologia

Este documento descreve o plano completo de testes para os componentes do frontend e a integração com o backend.

## 📋 Índice

1. [Testes de Componentes](#testes-de-componentes)
2. [Testes de Integração com Backend](#testes-de-integração-com-backend)
3. [Estrutura de Testes](#estrutura-de-testes)
4. [Cobertura Esperada](#cobertura-esperada)
5. [Ordem de Implementação](#ordem-de-implementação)

---

## 🧩 Testes de Componentes

### 1. Componentes de Autenticação

#### 1.1 `AuthPortal` (`src/components/auth-portal.tsx`)

**Prioridade: ALTA**

**Cenários de Teste:**

- [ ] Renderização inicial no modo login
- [ ] Alternância entre modo login e signup
- [ ] Validação de email (formato inválido, campo vazio)
- [ ] Validação de senha (mínimo de caracteres, campo vazio)
- [ ] Validação de confirmação de senha (senhas não coincidem)
- [ ] Validação de nome completo (campo obrigatório no signup)
- [ ] Validação de dados de nascimento (data, hora, local)
- [ ] Submissão de formulário de login com credenciais válidas
- [ ] Submissão de formulário de login com credenciais inválidas
- [ ] Submissão de formulário de signup com dados válidos
- [ ] Submissão de formulário de signup com dados inválidos
- [ ] Exibição de erros de API (401, 400, 500)
- [ ] Integração com Google OAuth (botão e callback)
- [ ] Exibição de modal de verificação de email
- [ ] Reenvio de código de verificação
- [ ] Verificação de código de email
- [ ] Loading states durante requisições
- [ ] Integração com `LocationAutocomplete`
- [ ] Tradução de textos (i18n)
- [ ] Acessibilidade (navegação por teclado, ARIA labels)

#### 1.2 `Onboarding` (`src/components/onboarding.tsx`)

**Prioridade: ALTA**

**Cenários de Teste:**

- [ ] Renderização inicial com dados pré-preenchidos (email, nome)
- [ ] Validação de todos os campos obrigatórios
- [ ] Validação de formato de data de nascimento
- [ ] Validação de formato de hora de nascimento
- [ ] Integração com `LocationAutocomplete`
- [ ] Cálculo automático de coordenadas ao selecionar local
- [ ] Submissão de dados completos
- [ ] Tratamento de erros de API
- [ ] Loading states
- [ ] Navegação de volta para login
- [ ] Tradução de textos
- [ ] Acessibilidade

#### 1.3 `GoogleOnboarding` (`src/components/google-onboarding.tsx`)

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] Renderização com dados do Google pré-preenchidos
- [ ] Validação de dados de nascimento
- [ ] Submissão de dados
- [ ] Tratamento de erros
- [ ] Loading states

#### 1.4 `EmailVerificationModal` (`src/components/email-verification-modal.tsx`)

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] Renderização do modal
- [ ] Entrada de código de verificação
- [ ] Validação de código (formato, tamanho)
- [ ] Submissão de código válido
- [ ] Submissão de código inválido
- [ ] Reenvio de código
- [ ] Fechamento do modal
- [ ] Loading states

### 2. Componentes de Dashboard

#### 2.1 `CosmosDashboard` (`src/components/cosmos-dashboard.tsx`)

**Prioridade: ALTA**

**Cenários de Teste:**

- [ ] Renderização com dados de usuário válidos
- [ ] Renderização sem dados de usuário (redirect)
- [ ] Exibição de todas as seções do dashboard
- [ ] Navegação entre seções
- [ ] Menu de configurações (abrir/fechar)
- [ ] Toggle de tema
- [ ] Toggle de idioma
- [ ] Logout
- [ ] Modal de inatividade
- [ ] Loading states durante carregamento de dados
- [ ] Tratamento de erros de API
- [ ] Responsividade (mobile/desktop)
- [ ] Acessibilidade

#### 2.2 `CompleteBirthChartSection` (`src/components/complete-birth-chart-section.tsx`)

**Prioridade: ALTA**

**Cenários de Teste:**

- [ ] Renderização com dados de mapa astral válidos
- [ ] Exibição de todos os planetas e seus signos
- [ ] Exibição de casas astrológicas
- [ ] Exibição de aspectos
- [ ] Visualização de roda astrológica
- [ ] Exportação para PDF
- [ ] Loading states
- [ ] Tratamento de dados ausentes
- [ ] Responsividade

#### 2.3 `BirthChartWheel` (`src/components/birth-chart-wheel.tsx`)

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] Renderização da roda astrológica
- [ ] Posicionamento correto dos planetas
- [ ] Exibição de signos e casas
- [ ] Exibição de aspectos (linhas)
- [ ] Interatividade (hover, zoom)
- [ ] Responsividade

#### 2.4 `DashboardSections` (vários componentes)

**Prioridade: MÉDIA**

**Componentes a testar:**

- `OverviewSection`
- `PlanetsSection`
- `HousesSection`
- `AspectsSection`
- `LunarNodesSection`
- `BiorhythmsSection`
- `SynastrySection`
- `SolarReturnSection`
- `NumerologySection`

**Cenários de Teste (para cada seção):**

- [ ] Renderização com dados válidos
- [ ] Renderização sem dados (estado vazio)
- [ ] Loading states
- [ ] Tratamento de erros
- [ ] Interatividade (expansão/colapso, filtros)
- [ ] Responsividade

#### 2.5 `BestTimingSection` (`src/components/best-timing-section.tsx`)

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] Renderização inicial
- [ ] Seleção de tipo de ação
- [ ] Cálculo de melhores momentos
- [ ] Exibição de resultados (datas, scores, aspectos)
- [ ] Filtros e ordenação
- [ ] Loading states
- [ ] Tratamento de erros
- [ ] Validação de parâmetros

#### 2.6 `DailyAdviceSection` (`src/components/daily-advice-section.tsx`)

**Prioridade: BAIXA**

**Cenários de Teste:**

- [ ] Renderização com dados do dia
- [ ] Atualização automática de dados
- [ ] Exibição de fase lunar
- [ ] Exibição de signo lunar
- [ ] Tratamento de erros

#### 2.7 `FutureTransitsSection` (`src/components/future-transits-section.tsx`)

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] Renderização de trânsitos futuros
- [ ] Filtros por tipo de trânsito
- [ ] Ordenação por data
- [ ] Exibição de detalhes de cada trânsito
- [ ] Loading states
- [ ] Tratamento de erros

#### 2.8 `SolarReturnSection` (`src/components/solar-return-section.tsx`)

**Prioridade: BAIXA**

**Cenários de Teste:**

- [ ] Renderização de retorno solar
- [ ] Cálculo de data de retorno solar
- [ ] Exibição de interpretação
- [ ] Loading states

#### 2.9 `NumerologySection` (`src/components/numerology-section.tsx`)

**Prioridade: BAIXA**

**Cenários de Teste:**

- [ ] Renderização de mapa numerológico
- [ ] Cálculo de números (caminho de vida, expressão, etc.)
- [ ] Exibição de interpretações
- [ ] Loading states

#### 2.10 `ChartRulerSection` (`src/components/chart-ruler-section.tsx`)

**Prioridade: BAIXA**

**Cenários de Teste:**

- [ ] Identificação do regente do mapa
- [ ] Exibição de interpretação do regente
- [ ] Loading states

### 3. Componentes de Interpretação

#### 3.1 `InterpretationPage` (`src/components/interpretation-page.tsx`)

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] Renderização com topicId válido
- [ ] Navegação entre seções de conteúdo
- [ ] Exibição de conteúdo correto para cada tópico
- [ ] Botão de voltar para dashboard
- [ ] Loading states
- [ ] Tratamento de topicId inválido
- [ ] Responsividade

### 4. Componentes de UI/Utilitários

#### 4.1 Componentes Astro Customizados

**Prioridade: BAIXA**

**Componentes:**

- `AstroButton`
- `AstroInput`
- `AstroCard`

**Cenários de Teste:**

- [ ] Renderização básica
- [ ] Props customizadas (variants, sizes)
- [ ] Estados (disabled, loading)
- [ ] Event handlers (onClick, onChange)
- [ ] Acessibilidade

#### 4.2 Componentes de Navegação/UI

**Prioridade: BAIXA**

**Componentes:**

- `ThemeToggle`
- `LanguageToggle`
- `ScrollToTop`
- `GlossaryTooltip`
- `LocationAutocomplete`

**Cenários de Teste:**

- [ ] Funcionalidade básica
- [ ] Integração com providers (Theme, Language)
- [ ] Interatividade
- [ ] Acessibilidade

#### 4.3 Modais

**Prioridade: MÉDIA**

**Componentes:**

- `EditUserModal`
- `ThemeCustomizationModal`
- `InactivityWarningModal`

**Cenários de Teste:**

- [ ] Abertura/fechamento
- [ ] Validação de formulários
- [ ] Submissão de dados
- [ ] Tratamento de erros
- [ ] Acessibilidade (foco, escape key)

### 5. Hooks Customizados

#### 5.1 `useAuth` (`src/hooks/useAuth.ts`)

**Prioridade: ALTA**

**Cenários de Teste:**

- [ ] Verificação de autenticação ao montar
- [ ] Retorno de dados de usuário quando autenticado
- [ ] Retorno de null quando não autenticado
- [ ] `handleAuthSuccess` - redirecionamento correto
- [ ] `handleNeedsBirthData` - redirecionamento para onboarding
- [ ] `handleGoogleNeedsOnboarding` - redirecionamento para Google onboarding
- [ ] `handleOnboardingComplete` - registro e redirecionamento
- [ ] `handleGoogleOnboardingComplete` - registro Google e redirecionamento
- [ ] `handleViewInterpretation` - navegação para interpretação
- [ ] `handleBackToDashboard` - navegação para dashboard
- [ ] `handleLogout` - limpeza de estado e redirecionamento
- [ ] Estado `isCheckingAuth` durante verificação
- [ ] Tratamento de erros de API

#### 5.2 `useLocalStorage` (`src/hooks/useLocalStorage.ts`)

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] Leitura de valor do localStorage
- [ ] Escrita de valor no localStorage
- [ ] Atualização de valor
- [ ] Valor padrão quando chave não existe
- [ ] SSR safety (não acessa localStorage no servidor)
- [ ] Sincronização entre múltiplos componentes

#### 5.3 `useClientOnly` (`src/hooks/useClientOnly.ts`)

**Prioridade: BAIXA**

**Cenários de Teste:**

- [ ] Retorna false durante SSR
- [ ] Retorna true após montagem no cliente

#### 5.4 `useInactivityTimeout` (`src/hooks/useInactivityTimeout.ts`)

**Prioridade: BAIXA**

**Cenários de Teste:**

- [ ] Dispara callback após período de inatividade
- [ ] Reseta timer ao detectar atividade
- [ ] Limpeza de event listeners

---

## 🔌 Testes de Integração com Backend

### 1. Serviço de API (`src/services/api.ts`)

#### 1.1 Autenticação

**Prioridade: ALTA**

**Métodos a testar:**

- `registerUser`
- `loginUser`
- `verifyEmail`
- `resendVerificationCode`
- `getCurrentUser`
- `getUserBirthChart`
- `updateUser`
- `logout`
- `verifyGoogleToken`

**Cenários de Teste:**

- [ ] Registro de usuário com dados válidos
- [ ] Registro de usuário com dados inválidos (validação)
- [ ] Login com credenciais válidas
- [ ] Login com credenciais inválidas
- [ ] Verificação de email com código válido
- [ ] Verificação de email com código inválido
- [ ] Reenvio de código de verificação
- [ ] Obtenção de usuário atual (com token válido)
- [ ] Obtenção de usuário atual (sem token)
- [ ] Obtenção de usuário atual (token inválido)
- [ ] Obtenção de mapa astral (com token válido)
- [ ] Obtenção de mapa astral (sem token)
- [ ] Atualização de dados de usuário
- [ ] Logout (remoção de token)
- [ ] Verificação de token Google
- [ ] Tratamento de erros HTTP (400, 401, 403, 404, 500)
- [ ] Timeout de requisições
- [ ] Headers de autenticação corretos
- [ ] Formatação de dados de requisição
- [ ] Parsing de respostas JSON
- [ ] Tratamento de respostas vazias

#### 1.2 Interpretações Astrológicas

**Prioridade: ALTA**

**Métodos a testar:**

- `getPlanetInterpretation`
- `getChartRulerInterpretation`
- `getPlanetHouseInterpretation`
- `getAspectInterpretation`
- `getInterpretationStatus`

**Cenários de Teste:**

- [ ] Interpretação de planeta com parâmetros válidos
- [ ] Interpretação de regente do mapa
- [ ] Interpretação de planeta em casa
- [ ] Interpretação de aspecto
- [ ] Verificação de status de interpretação
- [ ] Timeout de requisições (120s para interpretações)
- [ ] Tratamento de erros
- [ ] Formatação de parâmetros
- [ ] Parsing de respostas (interpretação, fontes, query)

#### 1.3 Trânsitos e Timing

**Prioridade: MÉDIA**

**Métodos a testar:**

- `getBestTiming`
- `getCurrentPersonalTransits`
- `getFutureTransits`
- `getDailyInfo`

**Cenários de Teste:**

- [ ] Cálculo de melhores momentos com parâmetros válidos
- [ ] Cálculo de melhores momentos com diferentes tipos de ação
- [ ] Obtenção de trânsitos pessoais atuais
- [ ] Obtenção de trânsitos futuros
- [ ] Obtenção de informações diárias
- [ ] Obtenção de informações diárias com coordenadas
- [ ] Timeout de requisições (60s para cálculos)
- [ ] Tratamento de erros
- [ ] Formatação de parâmetros de query
- [ ] Parsing de respostas complexas

#### 1.4 Dados Astrológicos

**Prioridade: MÉDIA**

**Métodos a testar:**

- `getSolarReturn`
- `getNumerologyMap`
- `getBiorhythms`
- `getSynastry`

**Cenários de Teste:**

- [ ] Obtenção de retorno solar
- [ ] Obtenção de mapa numerológico
- [ ] Obtenção de biorritmos
- [ ] Obtenção de sinastria
- [ ] Tratamento de erros
- [ ] Parsing de respostas

#### 1.5 Utilitários do Serviço

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] `getAuthToken` - retorna token do localStorage
- [ ] `getAuthToken` - retorna null quando não há token
- [ ] `getAuthToken` - retorna null no servidor (SSR)
- [ ] `request` - adiciona headers de autenticação
- [ ] `request` - adiciona Content-Type correto
- [ ] `request` - timeout de requisições
- [ ] `request` - tratamento de erros de rede
- [ ] `request` - tratamento de erros HTTP
- [ ] `request` - parsing de JSON
- [ ] `request` - tratamento de respostas vazias
- [ ] URL base da API (variável de ambiente vs. padrão)

### 2. Fluxos de Integração End-to-End

#### 2.1 Fluxo de Registro e Onboarding

**Prioridade: ALTA**

**Cenários de Teste:**

- [ ] Usuário preenche formulário de registro
- [ ] Sistema valida dados
- [ ] Sistema envia requisição de registro
- [ ] Sistema exibe modal de verificação de email
- [ ] Usuário insere código de verificação
- [ ] Sistema verifica código
- [ ] Sistema redireciona para onboarding
- [ ] Usuário preenche dados de nascimento
- [ ] Sistema calcula coordenadas do local
- [ ] Sistema envia dados de onboarding
- [ ] Sistema redireciona para dashboard
- [ ] Dashboard carrega dados do usuário e mapa astral

#### 2.2 Fluxo de Login

**Prioridade: ALTA**

**Cenários de Teste:**

- [ ] Usuário insere email e senha
- [ ] Sistema valida credenciais
- [ ] Sistema envia requisição de login
- [ ] Sistema salva token no localStorage
- [ ] Sistema busca dados do usuário
- [ ] Sistema busca mapa astral
- [ ] Sistema redireciona para dashboard (se onboarding completo)
- [ ] Sistema redireciona para onboarding (se incompleto)
- [ ] Dashboard exibe dados corretos

#### 2.3 Fluxo de Google OAuth

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] Usuário clica em "Entrar com Google"
- [ ] Sistema carrega Google Identity Services
- [ ] Usuário seleciona conta Google
- [ ] Sistema recebe credential
- [ ] Sistema verifica token com backend
- [ ] Sistema salva token de autenticação
- [ ] Sistema redireciona para onboarding Google (se novo usuário)
- [ ] Sistema redireciona para dashboard (se usuário existente)
- [ ] Dashboard exibe dados corretos

#### 2.4 Fluxo de Visualização de Interpretação

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] Usuário clica em tópico de interpretação no dashboard
- [ ] Sistema navega para página de interpretação
- [ ] Sistema carrega dados do tópico
- [ ] Sistema faz requisição de interpretação ao backend
- [ ] Sistema exibe interpretação formatada
- [ ] Sistema exibe fontes utilizadas
- [ ] Usuário navega entre seções
- [ ] Usuário volta para dashboard

#### 2.5 Fluxo de Cálculo de Melhores Momentos

**Prioridade: BAIXA**

**Cenários de Teste:**

- [ ] Usuário seleciona tipo de ação
- [ ] Sistema envia requisição de cálculo
- [ ] Sistema exibe loading state
- [ ] Sistema recebe e exibe resultados
- [ ] Sistema formata datas e scores
- [ ] Sistema exibe aspectos e razões
- [ ] Tratamento de erros

#### 2.6 Fluxo de Atualização de Dados do Usuário

**Prioridade: BAIXA**

**Cenários de Teste:**

- [ ] Usuário abre modal de edição
- [ ] Sistema carrega dados atuais
- [ ] Usuário modifica dados
- [ ] Sistema valida dados
- [ ] Sistema envia atualização
- [ ] Sistema atualiza estado local
- [ ] Sistema fecha modal
- [ ] Dashboard reflete mudanças

### 3. Tratamento de Erros e Edge Cases

#### 3.1 Erros de Rede

**Prioridade: ALTA**

**Cenários de Teste:**

- [ ] Timeout de requisição
- [ ] Falha de conexão (offline)
- [ ] Erro de DNS
- [ ] Erro de CORS
- [ ] Mensagens de erro amigáveis ao usuário
- [ ] Retry automático (se aplicável)

#### 3.2 Erros HTTP

**Prioridade: ALTA**

**Cenários de Teste:**

- [ ] 400 Bad Request (dados inválidos)
- [ ] 401 Unauthorized (token inválido/expirado)
- [ ] 403 Forbidden (sem permissão)
- [ ] 404 Not Found (recurso não existe)
- [ ] 500 Internal Server Error
- [ ] 502 Bad Gateway
- [ ] 503 Service Unavailable
- [ ] Mensagens de erro específicas por código
- [ ] Redirecionamento apropriado (401 → login)

#### 3.3 Edge Cases

**Prioridade: MÉDIA**

**Cenários de Teste:**

- [ ] Token expirado durante sessão
- [ ] Dados ausentes/null do backend
- [ ] Respostas malformadas do backend
- [ ] Múltiplas requisições simultâneas
- [ ] Cancelamento de requisições
- [ ] localStorage indisponível (modo privado)
- [ ] Navegação rápida entre páginas
- [ ] Componente desmontado durante requisição

---

## 📁 Estrutura de Testes

```
__tests__/
├── components/
│   ├── auth/
│   │   ├── auth-portal.test.tsx
│   │   ├── onboarding.test.tsx
│   │   ├── google-onboarding.test.tsx
│   │   └── email-verification-modal.test.tsx
│   ├── dashboard/
│   │   ├── cosmos-dashboard.test.tsx
│   │   ├── complete-birth-chart-section.test.tsx
│   │   ├── birth-chart-wheel.test.tsx
│   │   ├── best-timing-section.test.tsx
│   │   ├── daily-advice-section.test.tsx
│   │   ├── future-transits-section.test.tsx
│   │   └── dashboard-sections.test.tsx
│   ├── interpretation/
│   │   └── interpretation-page.test.tsx
│   ├── ui/
│   │   ├── astro-button.test.tsx
│   │   ├── astro-input.test.tsx
│   │   ├── astro-card.test.tsx
│   │   ├── theme-toggle.test.tsx
│   │   └── language-toggle.test.tsx
│   └── modals/
│       ├── edit-user-modal.test.tsx
│       └── inactivity-warning-modal.test.tsx
├── hooks/
│   ├── useAuth.test.tsx
│   ├── useLocalStorage.test.ts
│   ├── useClientOnly.test.ts
│   └── useInactivityTimeout.test.ts
├── services/
│   ├── api.test.ts
│   ├── api-auth.test.ts
│   ├── api-interpretations.test.ts
│   └── api-transits.test.ts
├── integration/
│   ├── auth-flow.test.tsx
│   ├── onboarding-flow.test.tsx
│   ├── google-oauth-flow.test.tsx
│   ├── interpretation-flow.test.tsx
│   └── dashboard-flow.test.tsx
├── utils/
│   └── test-utils.tsx
└── __mocks__/
    ├── next-navigation.ts
    ├── api-service.ts
    └── localStorage.ts
```

---

## 📊 Cobertura Esperada

### Cobertura Mínima por Categoria

- **Componentes de Autenticação**: 90%+
- **Componentes de Dashboard**: 80%+
- **Hooks Customizados**: 90%+
- **Serviço de API**: 85%+
- **Fluxos de Integração**: 75%+
- **Cobertura Geral**: 80%+

### Métricas de Qualidade

- Todos os testes devem passar
- Zero testes flaky (intermitentes)
- Tempo de execução < 2 minutos
- Testes isolados (não dependem de ordem de execução)

---

## 🚀 Ordem de Implementação

### Fase 1: Fundação (Prioridade ALTA)

1. Configuração de ambiente de testes
2. Mocks e utilitários de teste
3. Testes do serviço de API (métodos básicos)
4. Testes do hook `useAuth`
5. Testes do componente `AuthPortal`

### Fase 2: Autenticação e Onboarding (Prioridade ALTA)

6. Testes do componente `Onboarding`
7. Testes do componente `GoogleOnboarding`
8. Testes do componente `EmailVerificationModal`
9. Fluxos de integração de autenticação

### Fase 3: Dashboard Core (Prioridade ALTA)

10. Testes do componente `CosmosDashboard`
11. Testes do componente `CompleteBirthChartSection`
12. Testes de hooks utilitários (`useLocalStorage`, `useClientOnly`)

### Fase 4: Dashboard Sections (Prioridade MÉDIA)

13. Testes das seções do dashboard
14. Testes do componente `InterpretationPage`
15. Testes de integração de interpretações

### Fase 5: Componentes Auxiliares (Prioridade BAIXA)

16. Testes de componentes UI customizados
17. Testes de modais
18. Testes de componentes de navegação

### Fase 6: Integração Completa (Prioridade MÉDIA)

19. Fluxos end-to-end completos
20. Testes de tratamento de erros
21. Testes de edge cases

### Fase 7: Otimização e Refinamento

22. Revisão de cobertura
23. Otimização de testes lentos
24. Documentação de testes

---

## 🛠️ Ferramentas e Configurações

### Ferramentas Utilizadas

- **Jest**: Framework de testes
- **@testing-library/react**: Testes de componentes React
- **@testing-library/jest-dom**: Matchers adicionais
- **@testing-library/user-event**: Simulação de interações do usuário
- **jest-environment-jsdom**: Ambiente de testes

### Mocks Necessários

- `next/navigation` (useRouter, useParams)
- `next/script` (Google Identity Services)
- `localStorage` (SSR safety)
- `window.matchMedia` (responsive)
- `IntersectionObserver` (lazy loading)
- `fetch` (requisições HTTP)

### Utilitários de Teste

- `renderWithProviders`: Wrapper com ThemeProvider e LanguageProvider
- `mockApiResponse`: Helper para mockar respostas de API
- `waitForApiCall`: Helper para aguardar chamadas de API
- `createMockUser`: Factory para criar dados de usuário mockados
- `createMockBirthChart`: Factory para criar mapa astral mockado

---

## 📝 Notas de Implementação

### Boas Práticas

1. **Isolamento**: Cada teste deve ser independente
2. **Arrange-Act-Assert**: Estrutura clara dos testes
3. **Nomes Descritivos**: Nomes de testes devem descrever o comportamento
4. **Mocks Apropriados**: Mockar apenas o necessário
5. **Cleanup**: Limpar estado entre testes
6. **Async Handling**: Usar `waitFor` e `findBy` para operações assíncronas

### Padrões de Teste

```typescript
describe("ComponentName", () => {
  beforeEach(() => {
    // Setup
  });

  afterEach(() => {
    // Cleanup
  });

  it("should render correctly", () => {
    // Test
  });

  it("should handle user interaction", async () => {
    // Test with user-event
  });

  it("should handle API errors", async () => {
    // Test error handling
  });
});
```

### Exemplo de Teste de Integração

```typescript
describe("Login Flow", () => {
  it("should complete full login flow", async () => {
    // 1. Render AuthPortal
    // 2. Fill login form
    // 3. Submit form
    // 4. Mock API response
    // 5. Verify navigation
    // 6. Verify user data loaded
  });
});
```

---

## ✅ Checklist de Validação

Antes de considerar os testes completos, verificar:

- [ ] Todos os testes passam
- [ ] Cobertura mínima atingida
- [ ] Testes não são flaky
- [ ] Mocks estão corretos
- [ ] Cleanup adequado entre testes
- [ ] Documentação de testes complexos
- [ ] Testes de acessibilidade incluídos
- [ ] Testes de responsividade incluídos
- [ ] Testes de tratamento de erros incluídos
- [ ] CI/CD configurado para rodar testes

---

## 📚 Referências

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/react)
- [Next.js Testing](https://nextjs.org/docs/app/building-your-application/testing)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

**Última atualização**: 2024 **Versão**: 1.0.0
