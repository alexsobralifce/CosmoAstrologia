# Plano de Restauração Segura dos Endpoints

## 🛡️ Garantias

1. ✅ **NÃO vai alterar endpoints existentes** - apenas ADICIONAR novos
2. ✅ **NÃO vai quebrar configurações atuais** - manter tudo que está funcionando
3. ✅ **NÃO vai usar código antigo** - atualizar para usar `get_ai_provider()`
4. ✅ **Fazer incrementalmente** - adicionar um endpoint por vez para testar

## 📋 Estratégia

### Fase 1: Endpoints Críticos (Prioridade ALTA)
Adicionar primeiro os endpoints mais usados pelo frontend:

1. `/api/full-birth-chart/section` - **CRÍTICO** (usado pelo mapa completo)
2. `/api/interpretation/chart-ruler` - **CRÍTICO** (usado pelo regente do mapa)
3. `/api/interpretation/daily-advice` - **CRÍTICO** (usado por conselhos diários)

### Fase 2: Endpoints Importantes (Prioridade MÉDIA)
4. `/api/interpretation` - Interpretação geral
5. `/api/interpretation/aspect` - Aspectos
6. `/api/interpretation/planet-house` - Planeta na casa

### Fase 3: Endpoints Secundários (Prioridade BAIXA)
7. `/api/interpretation/search` - Busca
8. `/api/interpretation/status` - Status
9. `/api/full-birth-chart/all` - Mapa completo completo
10. `/api/solar-return/calculate` - Cálculo revolução solar
11. `/api/solar-return/interpretation` - Interpretação revolução solar
12. `/api/numerology/map` - Mapa numerológico
13. `/api/numerology/interpretation` - Interpretação numerológica
14. `/api/numerology/birth-grid-quantities` - Grid numerológico

## 🔧 Padrão de Atualização

### ❌ NÃO USAR (código antigo do .bak):
```python
groq_client = _get_groq_client()
```

### ✅ USAR (padrão atual):
```python
from app.services.ai_provider_service import get_ai_provider
provider = get_ai_provider()
if provider:
    interpretation = provider.generate_text(...)
```

## ✅ Checklist de Segurança

Antes de adicionar cada endpoint:
- [ ] Verificar que não existe no arquivo atual
- [ ] Extrair do .bak apenas o necessário
- [ ] Atualizar para usar `get_ai_provider()`
- [ ] Remover dependências de `_get_groq_client()`
- [ ] Testar endpoint isoladamente
- [ ] Verificar que não quebrou nada existente

## 🎯 Resultado Esperado

Após restauração:
- ✅ Todos os endpoints atuais continuam funcionando
- ✅ Novos endpoints adicionados funcionando
- ✅ Todos usando `get_ai_provider()` (padrão moderno)
- ✅ Nenhuma configuração alterada
- ✅ Nada quebrado

