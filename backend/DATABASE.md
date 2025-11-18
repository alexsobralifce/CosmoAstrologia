# Database - SQLite

O sistema usa SQLite para armazenar dados de usuários e mapas astrológicos.

## Estrutura do Banco de Dados

### Tabela `users`
Armazena informações dos usuários autenticados via Google OAuth:
- `id`: ID único do usuário (primary key)
- `google_id`: ID do Google (único)
- `email`: Email do usuário (único)
- `name`: Nome do usuário
- `picture`: URL da foto de perfil
- `created_at`: Data de criação
- `updated_at`: Data de atualização

### Tabela `birth_charts`
Armazena os mapas astrológicos calculados pelos usuários:
- `id`: ID único do mapa (primary key)
- `user_id`: ID do usuário proprietário (foreign key)
- `name`: Nome da pessoa no mapa
- `birth_date`: Data de nascimento (YYYY-MM-DD)
- `birth_time`: Hora de nascimento (HH:MM)
- `birth_place`: Local de nascimento
- `sun_sign`: Signo solar
- `moon_sign`: Signo lunar
- `ascendant_sign`: Signo ascendente
- `chart_data`: Dados completos do mapa em JSON
- `is_primary`: Se é o mapa principal do usuário
- `created_at`: Data de criação
- `updated_at`: Data de atualização

## Localização do Banco

O banco de dados SQLite é criado em:
```
backend/astrologia.db
```

Este arquivo é criado automaticamente na primeira inicialização do backend.

## Endpoints da API

### Autenticação (`/api/auth`)
- `GET /api/auth/login` - Inicia login Google
- `GET /api/auth/callback` - Callback OAuth
- `GET /api/auth/me` - Informações do usuário atual
- `POST /api/auth/logout` - Logout

### Mapas Astrológicos (`/api/charts`)
- `POST /api/charts/calculate` - Calcula mapa astral (não salva)
- `POST /api/charts/save` - Salva mapa calculado
- `GET /api/charts/` - Lista todos os mapas do usuário
- `GET /api/charts/{chart_id}` - Obtém mapa específico
- `GET /api/charts/primary/current` - Obtém mapa principal do usuário
- `PUT /api/charts/{chart_id}/primary` - Define mapa como principal
- `DELETE /api/charts/{chart_id}` - Deleta mapa

## Uso

### Salvar um mapa após calcular:
```python
# 1. Calcular mapa
POST /api/charts/calculate
{
  "name": "João Silva",
  "birth_date": "1990-01-15",
  "birth_time": "14:30",
  "birth_place": "São Paulo, SP"
}

# 2. Salvar o resultado
POST /api/charts/save
{
  "chart": { /* resultado do cálculo */ },
  "is_primary": true
}
```

### Obter mapas salvos:
```python
# Listar todos os mapas
GET /api/charts/

# Obter mapa específico
GET /api/charts/1

# Obter mapa principal
GET /api/charts/primary/current
```

## Notas

- O banco de dados é criado automaticamente na primeira execução
- Usuários são criados automaticamente no primeiro login via Google OAuth
- Cada usuário pode ter múltiplos mapas, mas apenas um pode ser marcado como `primary`
- Ao deletar um usuário, todos os seus mapas são deletados automaticamente (CASCADE)
- O arquivo `astrologia.db` está no `.gitignore` e não será commitado

