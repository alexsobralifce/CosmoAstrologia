---
title: Configuração do Trail-code no projeto
author: Francisco
date: 2026-10-15
branch: main
cost: { minutes: 4, tokens: 34269 }
---

## Decided
- Rodamos `trail init --agents claude --no-global`: só o Claude Code foi ligado e nada foi escrito em ~/.claude, para não afetar outros projetos.
- O mapa fica em graft/ (ignorado pelo git); .claude/, .mcp.json, .trail/ e .ignore podem ser commitados.

## Tried and ruled out
- `npm install -g @trailhq/trail-code` falhou ao compilar tree-sitter-kotlin (node-gyp). O binário trail 0.22.0 já existia em /opt/homebrew/bin e funcionou, então a falha foi ignorada.

## Watch out
- Sem o parser de Kotlin, arquivos Kotlin podem não entrar no mapa; o projeto parece não usar Kotlin.
- Reiniciar o Claude Code para os hooks entrarem em vigor.
