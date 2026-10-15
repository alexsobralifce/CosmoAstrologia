---
title: "Endpoints sumidos na merge, limpeza de histórico e estado da refatoração"
author: Francisco
date: 2026-10-15
branch: main
cost: { minutes: 20, tokens: 294426 }
touches:
  - src/services/api.ts
  - src/services/api/auth-api.ts
  - src/services/api/http-client.ts
  - src/services/api/index.ts
  - src/services/api/interpretation-api.ts
  - src/services/api/numerology-api.ts
  - src/services/api/solar-return-api.ts
  - src/services/api/transits-api.ts
  - src/services/api/types.ts
  - "__tests__/components/dashboard/overview-helpers.test.ts"
---

## Decided
- O front chama rotas que o backend atual NÃO tem: POST /api/interpretation (usado por houses, lunar-nodes, chart-ruler-section), /interpretation/aspect, /interpretation/daily-advice. Os componentes caem num texto fixo no catch, então a falha é silenciosa. As rotas existiam até o commit 7bd56d5 (interpretation.py de 3.458 linhas) e sumiram em a6a9736/c99b9a0 ("update_nextJS"). Decisão pendente: restaurar ou remover as chamadas.
- Handlers gordos viram serviços puros em app/services/*, sempre com teste de caracterização (saída antiga x nova idêntica) antes do commit: sinastria, numerologia, revolução solar, seção do mapa, descrições de trânsito.
- Front: api.ts virou src/services/api/ (HttpClient + módulos de domínio + fachada apiService); OverviewSection dividido; jest 224/224 e tsc 0 erros; build passa.
- Histórico limpo preparado em clone isolado com git filter-repo (285 MiB -> 19 MiB; a árvore do HEAD é idêntica). Falta o force-push, que depende do dono.

## Tried and ruled out
- Cookie httpOnly para o JWT: não feito. Com front (Vercel) e backend (Railway) em domínios diferentes seria SameSite=None e exigiria proteção CSRF; aceitar o cookie no servidor sem migrar o front só enfraquece a segurança. Caminho seguro: proxy do Next (rewrites de /api para o Railway) para o cookie ficar no mesmo site.
- Remover o rag-service/: não feito; start_services.*, testes de integração e docs ainda o citam, embora o backend use o RAG em processo (rag_service_fastembed).

## Watch out
- Repo público tinha livros em PDF (pdf/) e o banco com usuários no histórico; só o filter-repo + force-push remove isso do GitHub.
- A primeira consulta de numerology_interpretation/queries.py tem vírgula faltando (strings coladas); mantida de propósito para não mudar as buscas.
- Restam arquivos grandes: auth-portal (1.4k), numerology-section (1.3k), calculadoras (transits, best_timing, precomputed_chart_engine) e rag_service_fastembed.
