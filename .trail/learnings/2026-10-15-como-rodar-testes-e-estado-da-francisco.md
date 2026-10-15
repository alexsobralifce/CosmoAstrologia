---
title: Como rodar testes e estado da refatoração (backend/front)
author: Francisco
date: 2026-10-15
branch: main
cost: { minutes: 23, tokens: 231469 }
touches:
  - middleware.ts
  - backend/app/api/interpretation/synastry.py
  - backend/app/services/synastry/__init__.py
  - backend/app/services/synastry/context.py
  - backend/app/services/synastry/prompts.py
  - backend/tests/unit/test_synastry_service.py
  - backend/app/core/config.py
  - backend/app/models/database.py
  - backend/app/services/ai_cache.py
  - backend/app/services/ai_provider_service.py
---

## Decided
- Backend: `python -m pytest tests/unit -o addopts="" -q` (o pytest.ini exige pytest-cov e 70% de cobertura). Os testes usam SQLite temporário (tests/conftest.py); antes apagavam usuários do astrologia.db local.
- interpretation.py virou pacote app/api/interpretation/ (um módulo por tema). Política de acesso fica em __init__.py: require_user em tudo menos daily; llm_rate_limit (30/min/usuário) nas rotas de LLM.
- Cache de LLM: CachedAIProvider (Decorator) aplicado dentro de get_ai_provider; tabela llm_cache.
- Sinastria é o modelo para refatorar rotas gordas: serviço puro (app/services/synastry/) + teste de caracterização comparando saída antiga x nova.
- Front: src/components/dashboard-sections/ (uma seção por arquivo, index.ts mantém a API).

## Tried and ruled out
- requirements.txt pedia sib-api-v3-sdk>=8.2.0 (não existe; última 7.6.0): corrigido para >=7.6.0.
- Abortar o boot com SECRET_KEY padrão: não feito, pode derrubar produção se o Railway ainda usa a chave padrão. Precisa confirmar com o dono.

## Watch out
- `npm run build` já falhava antes (noUnusedLocals + ~99 erros de tsc); tsc e jest no CI são não bloqueantes. Linha de base jest: 161 ok / 58 falhas.
- O banco astrologia.db e JSONs de teste continuam no histórico do git (repo público); limpar exige git filter-repo + force-push.
- Rate limit é em memória por processo (vários workers multiplicam o limite).
