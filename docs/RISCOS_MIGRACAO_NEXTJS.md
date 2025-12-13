# ⚠️ Análise de Riscos: Migração para Next.js

## 🔴 Riscos Identificados

### **1. APIs do Browser (ALTO RISCO)**

#### Problemas:

- **localStorage**: Usado extensivamente para:

  - `auth_token` (autenticação)
  - `best_timing_last_update`
  - `daily_info_last_update`
  - `astro-theme` (tema)
  - `astro-language` (idioma)
  - Dados de onboarding temporários

- **window/document**: Usado em:
  - Google OAuth (`window.google`)
  - Manipulação de DOM (`document.title`, `document.head`)
  - Event listeners (`window.addEventListener`)
  - Media queries (`window.matchMedia`)

**Impacto**: ❌ **CRÍTICO** - Essas APIs não existem no servidor (SSR)

**Solução**:

- Usar `'use client'` em componentes que dependem de browser APIs
- Usar `useEffect` para acesso a `localStorage`/`window`
- Usar `typeof window !== 'undefined'` para verificações
- Criar hooks customizados (`useLocalStorage`, `useWindowSize`)

---

### **2. Estrutura de Rotas (ALTO RISCO)**

#### Problema Atual:

```typescript
// App.tsx - Estado interno
type AppView = "auth" | "onboarding" | "dashboard" | "landing";
const [currentView, setCurrentView] = useState<AppView>("landing");
```

**Sem rotas reais** - tudo é controlado por estado interno.

**Impacto**: ❌ **CRÍTICO** - Next.js precisa de rotas baseadas em arquivos

**Solução**:

- Refatorar para usar Next.js App Router:
  ```
  app/
    page.tsx              → /
    login/
      page.tsx            → /login
    dashboard/
      page.tsx            → /dashboard
    onboarding/
      page.tsx            → /onboarding
  ```
- Migrar lógica de navegação para `useRouter()` do Next.js
- Atualizar links e navegação

**Tempo estimado**: 2-3 dias

---

### **3. Variáveis de Ambiente (MÉDIO RISCO)**

#### Problema:

```typescript
// src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

**Impacto**: ⚠️ **MÉDIO** - `import.meta.env` é específico do Vite

**Solução**:

- Next.js usa `process.env.NEXT_PUBLIC_*`
- Renomear variáveis:
  ```typescript
  // Next.js
  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  ```
- Atualizar arquivo `.env`

**Tempo estimado**: 1-2 horas

---

### **4. Google OAuth (MÉDIO RISCO)**

#### Problema:

```typescript
// auth-portal.tsx
window.google?.accounts?.id.initialize({...})
window.google.accounts.id.renderButton(...)
```

**Impacto**: ⚠️ **MÉDIO** - Precisa ser executado apenas no cliente

**Solução**:

- Usar `'use client'` no componente
- Verificar `typeof window !== 'undefined'` antes de usar
- Usar `useEffect` para inicializar após mount
- Script do Google deve ser carregado via `next/script`

**Tempo estimado**: 2-3 horas

---

### **5. Componentes que Manipulam DOM (BAIXO RISCO)**

#### Problemas:

- `seo-head.tsx`: Manipula `document.title`, `document.head`
- `theme-provider.tsx`: Manipula `document.documentElement`
- Vários componentes usam `document.addEventListener`

**Impacto**: ⚠️ **BAIXO** - Fácil de corrigir com `'use client'`

**Solução**:

- Adicionar `'use client'` no topo dos arquivos
- Usar `useEffect` para manipulações de DOM

**Tempo estimado**: 1-2 horas

---

### **6. Estado Global e Context (BAIXO RISCO)**

#### Estrutura Atual:

- `ThemeProvider` (Context)
- `LanguageProvider` (Context)
- Estado compartilhado via props drilling

**Impacto**: ✅ **BAIXO** - Next.js suporta Context API normalmente

**Solução**:

- Funciona igual, apenas adicionar `'use client'` nos providers
- Considerar usar Zustand/Redux se necessário

**Tempo estimado**: 1 hora

---

### **7. Build e Deploy (MÉDIO RISCO)**

#### Problema:

- Vite usa `build/` como output
- Next.js usa `.next/` e `out/` (para static export)
- Vercel configurado para Vite

**Impacto**: ⚠️ **MÉDIO** - Precisa atualizar configurações

**Solução**:

- Atualizar `vercel.json` para Next.js
- Ou usar configuração automática do Vercel (recomendado)
- Atualizar scripts de build

**Tempo estimado**: 1 hora

---

### **8. Dependências (BAIXO RISCO)**

#### Verificação:

✅ Todas as dependências são compatíveis com Next.js:

- React 18.3.1 ✅
- Radix UI ✅
- Tailwind CSS ✅
- Sonner ✅
- Recharts ✅

**Impacto**: ✅ **BAIXO** - Compatibilidade total

---

## 📊 Resumo de Riscos

| Risco | Severidade | Complexidade | Tempo Estimado |
| --- | --- | --- | --- |
| Browser APIs (localStorage/window) | 🔴 Alta | ⚠️ Média | 1-2 dias |
| Estrutura de Rotas | 🔴 Alta | ⚠️ Alta | 2-3 dias |
| Variáveis de Ambiente | 🟡 Média | ✅ Baixa | 1-2 horas |
| Google OAuth | 🟡 Média | ⚠️ Média | 2-3 horas |
| Manipulação DOM | 🟢 Baixa | ✅ Baixa | 1-2 horas |
| Estado Global | 🟢 Baixa | ✅ Baixa | 1 hora |
| Build/Deploy | 🟡 Média | ✅ Baixa | 1 hora |
| Dependências | 🟢 Baixa | ✅ Baixa | 0 horas |

**Tempo Total Estimado**: 4-7 dias de desenvolvimento

---

## ✅ O que NÃO vai quebrar

1. **Componentes React**: Todos os componentes continuarão funcionando
2. **Lógica de Negócio**: Toda a lógica permanece igual
3. **Estilos CSS**: Todos os estilos continuam funcionando
4. **API Calls**: Estrutura de chamadas à API não muda
5. **Autenticação**: Lógica de auth permanece (apenas precisa adaptar localStorage)

---

## 🛡️ Estratégia de Migração Segura

### **Fase 1: Preparação (1 dia)**

- ✅ Criar branch separado (`feature/nextjs-migration`)
- ✅ Configurar Next.js em paralelo (não substituir ainda)
- ✅ Testar build básico

### **Fase 2: Migração Incremental (3-4 dias)**

1. **Dia 1**: Setup Next.js + Páginas básicas
   - Landing page
   - Login page
2. **Dia 2**: Migrar rotas principais

   - Dashboard
   - Onboarding
   - Adicionar `'use client'` onde necessário

3. **Dia 3**: Adaptar Browser APIs

   - Criar hooks para localStorage
   - Adaptar Google OAuth
   - Corrigir manipulação de DOM

4. **Dia 4**: Testes e ajustes finais
   - Testar fluxo completo
   - Corrigir bugs
   - Otimizar performance

### **Fase 3: Deploy e Monitoramento (1 dia)**

- Deploy em staging
- Testes completos
- Deploy em produção
- Monitorar erros

---

## 🎯 Recomendações

### **Opção 1: Migração Completa (Recomendado se SEO é crítico)**

- ✅ Melhor SEO a longo prazo
- ✅ Performance superior
- ⚠️ Requer 4-7 dias de trabalho
- ⚠️ Risco médio (mas gerenciável)

### **Opção 2: Migração Híbrida**

- ✅ Migrar apenas páginas públicas para Next.js
- ✅ Manter dashboard como SPA React
- ⚠️ Mais complexo de manter
- ✅ Menos risco

### **Opção 3: Melhorias Sem Migrar (Menor risco)**

- ✅ Adicionar React Router + Prerendering
- ✅ Corrigir robots.txt (já feito)
- ✅ Melhorar SEO sem migração completa
- ⚠️ SEO ainda limitado (mas melhor que antes)

---

## ⚠️ Pontos de Atenção

### **1. Autenticação**

- `localStorage` não funciona no SSR
- **Solução**: Usar cookies HTTP-only para tokens (mais seguro) OU verificar apenas no cliente

### **2. Roteamento**

- Lógica de navegação precisa ser completamente refatorada
- **Solução**: Usar `useRouter()` e `Link` do Next.js

### **3. Estado Inicial**

- Estado derivado de `localStorage` precisa ser hidratado no cliente
- **Solução**: Usar `useEffect` para sincronizar após mount

### **4. Google OAuth**

- Script precisa carregar apenas no cliente
- **Solução**: Usar `next/script` com `strategy="afterInteractive"`

---

## 📝 Checklist de Migração

- [ ] Setup Next.js
- [ ] Migrar estrutura de rotas
- [ ] Adicionar `'use client'` onde necessário
- [ ] Criar hooks para localStorage
- [ ] Adaptar Google OAuth
- [ ] Corrigir variáveis de ambiente
- [ ] Atualizar configuração de build
- [ ] Testar autenticação
- [ ] Testar todas as rotas
- [ ] Testar em produção

---

## 🔒 Conclusão

**Risco Geral**: ⚠️ **MÉDIO** - Gerenciável com planejamento adequado

**Pode quebrar?**:

- ❌ **Sim**, se não seguir as adaptações necessárias
- ✅ **Não**, se seguir estratégia incremental e testar adequadamente

**Recomendação Final**:

- Se SEO é **crítico** → Migrar para Next.js (vale o risco)
- Se SEO é **importante mas não urgente** → Fazer melhorias incrementais primeiro (React Router + Prerendering)
- Se SEO não é prioridade → Manter como está e focar em outras melhorias
