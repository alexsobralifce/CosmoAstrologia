# 🔧 Setup - Swiss Ephemeris Integration

## 📦 Instalação

Para completar a instalação do Swiss Ephemeris, execute:

```bash
cd backend
source venv/bin/activate
pip install kerykeion pytz
pip install -r requirements.txt  # Garantir que tudo está instalado
```

## ✅ O Que Foi Implementado

### 1. Novo Serviço com Swiss Ephemeris
- **Arquivo**: `backend/app/services/swiss_ephemeris_calculator.py`
- **Função principal**: `calculate_birth_chart()`
- **Fonte única**: Todas as posições calculadas uma única vez

### 2. Integração no Código Existente
- **Arquivo**: `backend/app/services/astrology_calculator.py`
- **Modificado**: Função `calculate_birth_chart()` agora usa Swiss Ephemeris por padrão
- **Fallback**: Se houver erro, usa PyEphem automaticamente (não quebra nada)

### 3. Dependências Atualizadas
- **Arquivo**: `backend/requirements.txt`
- Adicionado: `kerykeion>=5.3.0` e `pytz>=2024.1`

## 🎯 Como Funciona

1. **Por padrão**, `calculate_birth_chart()` tenta usar Swiss Ephemeris
2. Se kerykeion não estiver instalado ou houver erro, **automaticamente** usa PyEphem
3. **Zero breaking changes** - código existente continua funcionando

## 🔍 Verificação

Para verificar se está funcionando:

```python
# Teste simples
from app.services.astrology_calculator import calculate_birth_chart
from datetime import datetime

result = calculate_birth_chart(
    birth_date=datetime(1990, 5, 15),
    birth_time="10:30:00",
    latitude=-23.5505,
    longitude=-46.6333
)

print(result["venus_sign"])  # Deve ser consistente!
```

## 📊 Benefícios Imediatos

- ✅ **Precisão**: Cálculos precisos (não mais aproximações)
- ✅ **Consistência**: Mesmas coordenadas = mesmos resultados
- ✅ **Fonte Única**: Todas as posições calculadas uma vez
- ✅ **Zero Inconsistências**: Não mais "Vênus em Sagitário" depois "Stellium em Libra"

## ⚠️ Nota Importante

O sistema tem **fallback automático**. Mesmo que kerykeion não esteja instalado, o sistema continua funcionando com PyEphem. Isso permite:

1. Deploy gradual
2. Testes sem risco
3. Migração suave

---

**Próximo passo**: Instalar kerykeion e testar em produção!

