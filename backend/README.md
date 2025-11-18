# Astrologia Backend API

Backend Python com FastAPI para cálculo e interpretação de mapas astrológicos usando RAG (Retrieval-Augmented Generation).

## Funcionalidades

- ✅ Cálculo de mapas astrológicos completos (Swiss Ephemeris)
- ✅ Interpretações baseadas em RAG com documentos PDF
- ✅ Cálculo de trânsitos diários e futuros
- ✅ Interpretações de planetas, casas e aspectos
- ✅ Sistema de regente do mapa

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o .env e adicione sua OPENAI_API_KEY (opcional)
```

3. Execute o servidor:
```bash
python run.py
```

A API estará disponível em `http://localhost:8000`

## Documentação da API

Acesse `http://localhost:8000/docs` para ver a documentação interativa do Swagger.

## Endpoints Principais

### Charts
- `POST /api/charts/calculate` - Calcula mapa astral completo

### Interpretations
- `POST /api/interpretations/planet/{planet_name}` - Interpretação de planeta
- `POST /api/interpretations/house/{house_number}` - Interpretação de casa
- `POST /api/interpretations/aspect` - Interpretação de aspecto
- `POST /api/interpretations/chart-ruler` - Interpretação do regente do mapa
- `POST /api/interpretations/custom` - Interpretação customizada

### Transits
- `POST /api/transits/daily` - Trânsitos diários
- `POST /api/transits/future` - Trânsitos futuros

## Estrutura

```
backend/
├── app/
│   ├── api/          # Endpoints da API
│   ├── core/         # Configurações
│   ├── models/       # Schemas Pydantic
│   ├── services/     # Lógica de negócio
│   └── main.py       # Aplicação FastAPI
├── requirements.txt
└── run.py
```

## Notas

- O sistema RAG usa OpenAI por padrão. Se não configurar a API key, usará interpretações fallback baseadas em regras.
- Os documentos PDF devem estar na pasta `../pdf` (relativa ao backend) ou configurada via `PDFS_PATH`.
- Swiss Ephemeris é usado para cálculos astronômicos precisos.

