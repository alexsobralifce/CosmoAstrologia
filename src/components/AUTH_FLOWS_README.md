# Fluxos de Autenticação - Documentação Completa

## Visão Geral

Sistema de autenticação inteligente com três fluxos principais:
1. **Cadastro por E-mail** (Fluxo 1)
2. **Login Tradicional** (Fluxo 2)  
3. **Login Social com Google** (Fluxo 3 - com lógica condicional)

---

## 🎯 Componentes Principais

### 1. AuthPortal (`/components/auth-portal.tsx`)
Portal de autenticação com alternância entre Login e Cadastro.

**Features:**
- ✅ Validação em tempo real de e-mail e senha
- ✅ Indicador visual de senhas coincidentes
- ✅ Toggle de mostrar/ocultar senha
- ✅ Recuperação de senha
- ✅ Login com Google
- ✅ Toast notifications para feedback
- ✅ Fundo cósmico animado com estrelas

### 2. AuthLoader (`/components/auth-loader.tsx`)
Loader místico exibido durante autenticação.

**Features:**
- ✨ Mandala girando com animação
- ✨ Partículas orbitando
- ✨ Gradientes pulsantes
- ✨ Mensagens motivacionais

### 3. Onboarding Aprimorado
Aceita dados pré-preenchidos do Google/Auth.

---

## 📊 Fluxos Detalhados

### Fluxo 1: Cadastro por E-mail (Novo Usuário)

```
Landing Page
    ↓ [Clica "Calcular Meu Mapa Astral"]
Auth Portal (Aba "Criar Conta")
    ↓ [Preenche e-mail + senha + confirma senha]
    ↓ [Clica "Continuar"]
    ↓ [Validação: e-mail não existe no banco]
Onboarding (Coleta de Dados)
    ↓ [Preenche: Nome, Data, Hora, Local]
    ↓ [Clica "Gerar Mapa Astral"]
    ↓ [Loader místico]
Dashboard
```

**Estados de Erro:**
- E-mail já existe → Toast com link "Ir para Login"
- Senha < 6 caracteres → Erro inline
- Senhas não coincidem → Borda vermelha + erro

---

### Fluxo 2: Login Tradicional (Usuário Existente)

```
Landing Page
    ↓ [Clica "Calcular Meu Mapa Astral"]
Auth Portal (Aba "Entrar")
    ↓ [Preenche e-mail + senha]
    ↓ [Clica "Acessar meu Mapa"]
    ↓ [Validação: credenciais corretas]
    ↓
    ├─ Se hasCompletedOnboarding = true
    │      ↓ [Loader místico]
    │      Dashboard
    │
    └─ Se hasCompletedOnboarding = false
           ↓
           Onboarding (Completar dados)
               ↓
               Dashboard
```

**Estados de Erro:**
- Credenciais inválidas → Toast de erro
- E-mail não cadastrado → Toast de erro

---

### Fluxo 3: Login com Google (Lógica Condicional)

```
Landing Page
    ↓ [Clica "Calcular Meu Mapa Astral"]
Auth Portal
    ↓ [Clica botão "Google"]
    ↓ [Popup OAuth do Google]
    ↓ [Sistema verifica e-mail no banco]
    ↓
    ├─ CENÁRIO A: Usuário NOVO (e-mail não existe)
    │      ↓ [Toast: "Conta Google conectada!"]
    │      Onboarding (Nome e E-mail pré-preenchidos)
    │          ↓ [Preenche: Data, Hora, Local]
    │          Dashboard
    │
    └─ CENÁRIO B: Usuário EXISTENTE (e-mail já existe)
           ↓ [Toast: "Login realizado com sucesso!"]
           ↓ [Loader místico]
           Dashboard (Acesso direto)
```

---

## 🎨 Design e UX

### Visual
- **Fundo:** Gradiente cósmico com estrelas animadas (twinkle)
- **Card:** Glassmorphic com borda dourada
- **Cores:** Segue paleta do sistema (adapta ao tema dia/noite)
- **Ícones:** Estrela dourada no header

### Microinterações
- ✨ Estrelas piscando aleatoriamente
- 🌊 Gradientes pulsantes no fundo
- ✓ Ícone verde quando senhas coincidem
- 👁️ Toggle de mostrar/ocultar senha
- 🔄 Transições suaves entre Login/Cadastro

### Toast Notifications
- **Sucesso (Verde):** Login bem-sucedido
- **Erro (Vermelho):** Credenciais inválidas, e-mail duplicado
- **Info (Azul):** Google conectado
- **Ações:** Alguns toasts têm botões (ex: "Ir para Login")

---

## 💾 Banco de Dados Mockado

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

### Usuários de Teste

| E-mail | Senha | Status | Comportamento |
|--------|-------|--------|---------------|
| joao@exemplo.com | 123456 | Com mapa completo | Vai direto pro Dashboard |
| maria@exemplo.com | 123456 | Sem mapa | Vai para Onboarding |
| qualquer@novo.com | 123456 | Novo usuário | Vai para Onboarding |

---

## 🔧 Props e Interfaces

### AuthPortal Props
```typescript
interface AuthPortalProps {
  onAuthSuccess: (userData: AuthUserData) => void;
  onNeedsBirthData: (email: string, name?: string) => void;
}

interface AuthUserData {
  email: string;
  name?: string;
  hasCompletedOnboarding: boolean;
}
```

### Onboarding Props (Atualizado)
```typescript
interface OnboardingProps {
  onComplete: (data: OnboardingData) => void;
  initialEmail?: string;    // Novo: vem do auth
  initialName?: string;     // Novo: vem do Google
}
```

---

## 🚀 Como Usar

### 1. Landing Page → Auth
```tsx
<AstroButton onClick={() => setCurrentView('auth')}>
  Calcular Meu Mapa Astral
</AstroButton>
```

### 2. Auth Portal
```tsx
<AuthPortal 
  onAuthSuccess={handleAuthSuccess}
  onNeedsBirthData={handleNeedsBirthData}
/>
```

### 3. Handlers no App.tsx
```tsx
const handleAuthSuccess = (data: AuthUserData) => {
  setAuthData(data);
  if (data.hasCompletedOnboarding) {
    // Vai direto pro dashboard
    setCurrentView('dashboard');
  } else {
    // Precisa completar onboarding
    setCurrentView('onboarding');
  }
};

const handleNeedsBirthData = (email: string, name?: string) => {
  setAuthData({ email, name, hasCompletedOnboarding: false });
  setCurrentView('onboarding');
};
```

### 4. Onboarding com Dados Pré-preenchidos
```tsx
<Onboarding 
  onComplete={handleOnboardingComplete}
  initialEmail={authData?.email}
  initialName={authData?.name}
/>
```

---

## 🎭 Estados e Validações

### Validação de E-mail
```typescript
const validateEmail = (email: string) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};
```

### Validação de Senha
```typescript
const validatePassword = (password: string) => {
  return password.length >= 6;
};
```

### Validação Visual de Senhas Coincidentes
```tsx
{confirmPassword && (passwordsMatch ? 
  <UIIcons.CheckCircle className="text-green-500" /> :
  <border className="border-destructive" />
)}
```

---

## 🌟 Features Especiais

### 1. Esqueceu a Senha
- Usuário deve digitar e-mail primeiro
- Toast de confirmação de envio
- (Simulação - não envia e-mail real)

### 2. Login Social (Google)
- Simulação 50/50: novo vs existente
- Nome e e-mail importados automaticamente
- Detecção inteligente de cadastro existente

### 3. Card de Demo
Exibido abaixo do formulário para facilitar testes:
```
joao@exemplo.com / 123456 (com mapa)
maria@exemplo.com / 123456 (sem mapa)
```

### 4. Loader Místico
- Mandala girando em 3 camadas
- 6 partículas orbitando
- Mensagens: "Alinhando os Astros..."
- Gradientes pulsantes

---

## 📱 Responsividade

- **Mobile:** Cards em coluna, botões full-width
- **Tablet:** Layout mantido, espaçamentos ajustados
- **Desktop:** Centralizado com max-width 448px

---

## 🎨 Tema Dia/Noite

O AuthPortal adapta automaticamente ao tema:
- **Noturno:** Fundo #0A0E2F, estrelas douradas
- **Diurno:** Fundo #FDFBF7, estrelas âmbar

---

## 🔐 Segurança (Nota)

⚠️ **Este é um sistema de demonstração:**
- Senhas NÃO são hasheadas
- Dados em memória (não persistem)
- OAuth do Google é simulado
- Não use em produção sem implementar segurança real

---

## 🎯 Próximos Passos

### Backend Real
- [ ] Integrar com Supabase Auth
- [ ] Hash de senhas (bcrypt)
- [ ] Tokens JWT
- [ ] OAuth real do Google

### Features Adicionais
- [ ] Login com Facebook/Apple
- [ ] Verificação de e-mail
- [ ] Reset de senha funcional
- [ ] 2FA (autenticação de dois fatores)
- [ ] Rate limiting

### UX
- [ ] Lembrar senha (localStorage seguro)
- [ ] Auto-fill de formulários
- [ ] Validação enquanto digita
- [ ] Mensagens de erro contextuais

---

## 🐛 Troubleshooting

### Toast não aparece
- Certifique-se que `<Toaster />` está no App.tsx
- Importe: `import { Toaster } from './components/ui/sonner'`

### Loader não gira
- Verifique se animações CSS estão em globals.css
- Classes necessárias: `animate-spin`, `animate-spin-slow`

### Google login não funciona
- É uma simulação - não precisa de API keys
- 50% chance de ser novo usuário aleatoriamente

---

## 📚 Referências

- **Design:** Figma prompt fornecido
- **Paleta:** Místico-Profissional (Indigo + Dourado)
- **Tipografia:** Playfair Display + Inter
- **Framework:** React + TailwindCSS
- **Toast:** Sonner
- **Icons:** Lucide React
