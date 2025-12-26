# 📋 Arquivos que Podem Ser Removidos da Raiz do Projeto

## 🗑️ Categoria 1: Arquivos de Teste Temporários (Python)

Estes arquivos são scripts de teste/validação que podem ser movidos para `tests/` ou removidos:

- `analyze_francisco_report.py` - Script de análise temporária
- `recalculate_francisco_chart.py` - Script de recálculo temporário
- `validate_francisco_chart.py` - Script de validação temporária
- `validate_pdf_data.py` - Script de validação temporária
- `validate_pedro_lucas_map.py` - Script de validação temporária
- `verificar_endpoints_api.py` - Script de verificação temporária
- `test_complete_chart_format.py` - Teste temporário
- `test_mapa_astral_completo.py` - Teste temporário
- `test_mapa_astral.py` - Teste temporário
- `test_numerologia_melhorias.py` - Teste temporário
- `test_prompt.py` - Teste temporário
- `test_transits_endpoint.py` - Teste temporário

**Ação recomendada:** Mover para `tests/` ou remover se não forem mais necessários.

---

## 🗑️ Categoria 2: Arquivos JSON de Teste/Resposta

Arquivos JSON gerados durante testes que podem ser removidos:

- `test_data_random.json` - Dados de teste temporários
- `test_francisco.json` - Dados de teste temporários
- `test_response_20251203_214009.json` - Resposta de teste
- `test_response_20251203_214018.json` - Resposta de teste
- `test_response_20251203_214115.json` - Resposta de teste
- `test_response_20251203_214323.json` - Resposta de teste
- `test_response_20251203_214445.json` - Resposta de teste
- `test_response_20251203_214556.json` - Resposta de teste
- `test_response_20251203_214839.json` - Resposta de teste
- `test_response_francisco_20251203_215054.json` - Resposta de teste
- `test_response_random_20251203_214723.json` - Resposta de teste
- `test_response_triad_20251203_215441.json` - Resposta de teste
- `test_response_triad_refeito_20251203_215733.json` - Resposta de teste
- `test_response_triad_v2_20251203_215506.json` - Resposta de teste
- `test_output_20251203_214438.log` - Log de teste

**Ação recomendada:** Remover (são arquivos temporários de teste).

---

## 🗑️ Categoria 3: Arquivos de Log

Arquivos de log que já estão no `.gitignore` mas ainda estão na raiz:

- `backend.log` - Log do backend (já no .gitignore)
- `frontend.log` - Log do frontend (já no .gitignore)

**Ação recomendada:** Remover (já estão no .gitignore, podem ser regenerados).

---

## 🗑️ Categoria 4: Arquivos de Documentação Temporária/Antiga

Documentação de desenvolvimento que pode ser consolidada ou removida:

- `ANALISE_TESTE_MAPA_ASTRAL.md` - Análise temporária
- `CHANGELOG_TESTES.md` - Changelog de testes (pode ser consolidado no CHANGELOG.md)
- `COMO_TESTAR_NUMEROLOGIA.md` - Pode ser movido para `docs/` ou `tests/`
- `INTEGRACAO_TAROT_NUMEROLOGIA.md` - Pode ser movido para `docs/`
- `MELHORIAS_NUMEROLOGIA.md` - Pode ser movido para `docs/`
- `MELHORIAS_TRANSITOS.md` - Pode ser movido para `docs/`
- `RELATORIO_VERIFICACAO_API.md` - Relatório temporário
- `SOLUCAO_ATUALIZACAO_NUMEROLOGIA.md` - Pode ser movido para `docs/`
- `VALIDACAO_FINAL_MAPA_ASTRAL.md` - Validação temporária
- `VALIDACAO_FORMATO_MAPA_ASTRAL.md` - Validação temporária
- `VERIFICACAO_PRODUCAO.md` - Pode ser movido para `docs/`

**Ação recomendada:** Mover para `docs/` ou consolidar em documentação principal.

---

## 🗑️ Categoria 5: Arquivos de Imagem de Teste/Verificação

Imagens de teste/verificação de UI que podem ser removidas:

- `controls-final.png`
- `controls-fixed.png`
- `dark-mode-final.png`
- `dark-mode-fixed.png`
- `dark-mode-verification.png`
- `google-modal-fixed.png`
- `google-onboarding-full.png`
- `google-onboarding-screen.png`
- `language-toggle-final.png`
- `language-toggle-fixed.png`
- `light-mode-check.png`
- `light-mode-final.png`
- `login-button-fixed.png`
- `login-buttons-final.png`
- `login-buttons-fixed.png`
- `login-controls-final.png`
- `login-controls-fixed.png`
- `login-screenshot-comparison.png`
- `login-screenshot.png`
- `modal-size-check.png`
- `theme-toggle-test.png`

**Ação recomendada:** Remover (são screenshots de teste/verificação temporários).

---

## 🗑️ Categoria 6: Arquivos de Build Temporários

- `build/` - Diretório de build (já no .gitignore)
- `index.html` - Pode ser um arquivo de build temporário (verificar se é necessário)

**Ação recomendada:** Verificar se `index.html` na raiz é necessário ou se é apenas build temporário.

---

## 🗑️ Categoria 7: Arquivos de Banco de Dados Local

- `astrologia.db` - Banco de dados SQLite local (já no .gitignore)

**Ação recomendada:** Remover (já está no .gitignore, é gerado automaticamente).

---

## ✅ Arquivos que DEVEM PERMANECER na Raiz

### Essenciais do Projeto:
- `README.md` - Documentação principal
- `CHANGELOG.md` - Histórico de mudanças
- `DEPLOY.md` - Instruções de deploy
- `package.json` - Dependências do frontend
- `package-lock.json` - Lock de dependências
- `tsconfig.json` - Configuração TypeScript
- `tsconfig.node.json` - Configuração TypeScript Node
- `vite.config.ts` - Configuração Vite
- `vercel.json` - Configuração Vercel
- `docker-compose.yml` - Configuração Docker

### Scripts de Inicialização:
- `start_services.py` - Script de inicialização
- `start_services.sh` - Script de inicialização
- `start-all.sh` - Script de inicialização
- `start-all.ps1` - Script de inicialização (PowerShell)

### Diretórios Principais:
- `backend/` - Código do backend
- `src/` - Código do frontend
- `public/` - Arquivos públicos
- `docs/` - Documentação
- `scripts/` - Scripts auxiliares
- `tests/` - Testes

---

## 📊 Resumo

### Total de Arquivos para Remover:
- **Scripts Python de teste:** ~12 arquivos
- **Arquivos JSON de teste:** ~14 arquivos
- **Arquivos de log:** 2 arquivos
- **Documentação temporária:** ~12 arquivos
- **Imagens de teste:** ~20 arquivos
- **Banco de dados local:** 1 arquivo

**Total aproximado:** ~61 arquivos podem ser removidos ou movidos

---

## 🚀 Comandos Sugeridos para Limpeza

### 1. Remover arquivos JSON de teste:
```bash
rm test_response_*.json test_data_*.json test_francisco.json test_output_*.log
```

### 2. Remover imagens de teste:
```bash
rm *.png
```

### 3. Remover scripts Python de teste (ou mover para tests/):
```bash
# Opção 1: Remover
rm analyze_*.py recalculate_*.py validate_*.py test_*.py verificar_*.py

# Opção 2: Mover para tests/
mkdir -p tests/temp_scripts
mv analyze_*.py recalculate_*.py validate_*.py test_*.py verificar_*.py tests/temp_scripts/
```

### 4. Mover documentação temporária para docs/:
```bash
mv ANALISE_*.md CHANGELOG_TESTES.md COMO_TESTAR_*.md INTEGRACAO_*.md MELHORIAS_*.md RELATORIO_*.md SOLUCAO_*.md VALIDACAO_*.md VERIFICACAO_*.md docs/temp/
```

### 5. Remover logs e banco de dados local:
```bash
rm *.log astrologia.db
```

---

## ⚠️ Atenção

Antes de remover, certifique-se de:
1. Fazer backup se necessário
2. Verificar se algum arquivo contém informações importantes
3. Confirmar que os arquivos não são referenciados em outros lugares
4. Considerar mover para uma pasta `archive/` ao invés de deletar completamente

