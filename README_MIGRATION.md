# Migração para Next.js - Guia de Implementação

## Resumo da Migração

Este projeto foi migrado de React + Vite + React Router para Next.js 14+ com App Router.

## Mudanças Principais

### Estrutura de Arquivos

- **Antes**: `src/main.tsx` → `src/App.tsx` → `src/router/AppRouter.tsx`
- **Depois**: `app/layout.tsx` → `app/page.tsx` e outras páginas

### Rotas

- **Antes**: React Router com `<Routes>` e `<Route>`
- **Depois**: App Router com estrutura de diretórios:
  - `app/page.tsx` → `/`
  - `app/login/page.tsx` → `/login`
  - `app/onboarding/page.tsx` → `/onboarding`
  - `app/dashboard/page.tsx` → `/dashboard`
  - `app/interpretation/[topicId]/page.tsx` → `/interpretation/:topicId`

### Variáveis de Ambiente

- **Antes**: `import.meta.env.VITE_API_URL`
- **Depois**: `process.env.NEXT_PUBLIC_API_URL`

### Componentes Client-Side

Todos os componentes que usam APIs do browser (localStorage, window, document) agora têm `'use client'` no topo.

### SEO

- **Antes**: Componente `SEOHead` que manipulava DOM
- **Depois**: Metadata API do Next.js em cada página/layout

## Como Executar

### Desenvolvimento

```bash
npm install
npm run dev
```

### Build

```bash
npm run build
npm start
```

### Testes

```bash
npm test
npm run test:watch
```

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Para produção, configure no Vercel ou seu provedor de hospedagem.

## Arquivos Importantes

- `next.config.js` - Configuração do Next.js
- `middleware.ts` - Middleware para proteção de rotas
- `app/layout.tsx` - Layout raiz com providers
- `src/hooks/useAuth.ts` - Hook de autenticação
- `src/hooks/useLocalStorage.ts` - Hook para localStorage seguro com SSR

## Testes

Os testes foram criados em `__tests__/`:

- `pages.test.tsx` - Testes de páginas
- `api.test.ts` - Testes do serviço de API
- `auth.test.tsx` - Testes de autenticação
- `navigation.test.tsx` - Testes de navegação
- `integration.test.tsx` - Testes de integração

## Próximos Passos

1. Executar testes manuais completos
2. Validar SEO (metadata, Open Graph, etc.)
3. Testar performance
4. Deploy em staging
5. Deploy em produção

## Notas

- O Google OAuth foi adaptado para usar `next/script`
- A autenticação ainda usa localStorage (considerar migrar para cookies HTTP-only em produção)
- Todos os componentes que precisam de browser APIs têm `'use client'`
