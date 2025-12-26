# Status da Integracao com a Swiss Ephemeris (kerykeion)

## Realizado
- Criado **novo ambiente virtual** `backend/venv` baseado em **Python 3.11.14** (via `pyenv`) para garantir compatibilidade com `kerykeion` / `pyswisseph`.
- Instalado `kerykeion 5.3.2`, `pyswisseph` e novas dependencias (`timezonefinder`, `h3`, `cffi`, etc.).
- Atualizado `swiss_ephemeris_calculator.py` para usar a API v5 do kerykeion (`AstrologicalSubject`) e incluir:
  - Inferencia automatica do timezone via `TimezoneFinder` (fallback para `Etc/GMT+/-X`).
  - Exportacao de **todas as longitudes brutas** (`planet_longitudes`) para `_source_longitudes`.
  - Conserto do mapeamento do Meio do Ceu (`medium_coeli`) e nodos.
- `astrology_calculator.calculate_birth_chart()` agora retorna `_source_longitudes` mesmo no caminho Swiss.
- Rodados testes unitarios (`pytest tests/unit/test_astrology_calculator.py`) demonstrando funcionamento pos-migracao.

## Como reproduzir (macOS / Linux)
```bash
cd /Users/alexandrerocha/CosmoAstrologia/backend
~/.pyenv/versions/3.11.14/bin/python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pytest tests/unit/test_astrology_calculator.py \
  --cov=app/services/astrology_calculator.py \
  --cov-report=term --cov-fail-under=0
```

## Observacoes importantes
- `TimezoneFinder` nem sempre retorna o timezone municipal correto (ex.: Sobral -> `America/Sao_Paulo`).
  - Sempre que possivel, informe `timezone_name` explicitamente (ex.: `America/Fortaleza`).
- Mesmo com o novo motor, **a Lua do nascimento fornecido continua em Leao**.
  - Resultado verificado diretamente com `pyswisseph`: longitude ~123.9 (Leao a 3).
  - Se o usuario possuir dados oficiais que apontam outra posicao, precisamos confirmar data/hora/timezone.
- O pipeline inteiro continua passando pelas travas de seguranca (`chart_data_cache`, `precomputed_chart_engine`, PDF etc.).

## Proximos passos sugeridos
1. Expor `timezone_name` no frontend/onboarding para eliminar heuristicas.
2. Atualizar scripts/docs que ainda fazem referencia ao antigo `KrInstance`.
3. Regerar mapas/PDFs para usuarios ja cadastrados utilizando os novos dados.

