# Fluxo de Dados: Best Timing API

## 1. Frontend → Backend

### Componente: `src/components/best-timing-section.tsx`

**Função:** `fetchBestTiming()`

**Quando é chamada:**
- Quando o componente monta (`useEffect`)
- Quando `selectedAction` muda
- Quando a data muda (verificação a cada hora)
- Quando `userData.coordinates` está disponível

**Dados enviados:**
```typescript
{
  action_type: string,  // Ex: 'pedir_aumento'
  days_ahead: 30        // Padrão: 30 dias
}
```

**Chamada da API:**
```typescript
apiService.getBestTiming({
  action_type: selectedAction,
  days_ahead: 30
})
```

### Serviço: `src/services/api.ts`

**Método:** `getBestTiming()`

**Endpoint:** `POST /api/best-timing/calculate`

**Timeout:** 60 segundos

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer {token}` (se autenticado)

---

## 2. Backend → Processamento

### Endpoint: `backend/app/api/interpretation.py`

**Rota:** `@router.post("/best-timing/calculate")`

**Função:** `calculate_best_timing_endpoint()`

**Dados recebidos:**
```python
{
  "action_type": str,      # Ex: "pedir_aumento"
  "days_ahead": int        # Padrão: 30
}
```

**Dados do usuário obtidos:**
1. **Autenticação:** Token JWT do header `Authorization`
2. **Dados do mapa natal:** Busca no banco de dados usando `get_current_user()`
   - `birth_date` (datetime)
   - `birth_time` (string, formato "HH:MM")
   - `latitude` (float)
   - `longitude` (float)

**Validações:**
- Verifica se usuário está autenticado
- Verifica se usuário tem mapa astral primário no banco
- Verifica se `action_type` é válido

### Serviço: `backend/app/services/best_timing_calculator.py`

**Função:** `calculate_best_timing()`

**Parâmetros:**
```python
birth_date: datetime      # Do banco de dados
birth_time: str           # Do banco de dados
latitude: float           # Do banco de dados
longitude: float          # Do banco de dados
action_type: str          # Da requisição
days_ahead: int           # Da requisição (padrão: 30)
```

**Processamento:**
1. Busca configuração da ação em `ACTION_HOUSES[action_type]`
2. Calcula cúspides das casas relevantes (primárias + secundárias)
3. Itera por cada data/hora (a cada 6 horas) nos próximos `days_ahead` dias
4. Para cada momento:
   - Calcula posições planetárias usando Swiss Ephemeris
   - Verifica aspectos entre planetas benéficos e casas
   - Calcula score baseado nos aspectos
   - Adiciona penalizações (planetas desfavoráveis, Lua Fora de Curso)
   - Se score > 0, adiciona ao array de melhores momentos
5. Ordena por score (maior primeiro)
6. Retorna top 10 momentos

**Biblioteca usada:** Swiss Ephemeris (via kerykeion)

---

## 3. Backend → Frontend

### Resposta da API:

```typescript
{
  action_type: string,
  action_config: {
    primary_houses: number[],
    secondary_houses: number[],
    beneficial_planets: string[],
    avoid_planets: string[],
    preferred_aspects: string[]
  },
  best_moments: Array<{
    date: string,              // ISO format: "2025-12-06T00:00:00"
    score: number,             // Ex: 21
    aspects: Array<{
      planet: string,          // Ex: "Sol"
      house: number,           // Ex: 2
      aspect_type: string,     // Ex: "sextil"
      is_primary: boolean      // true se casa primária
    }>,
    reasons: string[],         // Descrições textuais
    is_moon_void: boolean      // Se Lua está Fora de Curso
  }>,
  total_checked: number,       // Total de momentos verificados
  analysis_date: string        // Data da análise
}
```

---

## 4. Frontend → Processamento e Exibição

### Validação Inicial (`fetchBestTiming()`)

1. **Validação da resposta:**
   - Verifica se `response` é objeto
   - Verifica se `response.best_moments` existe e é array

2. **Validação de cada momento:**
   - Verifica estrutura do objeto
   - Verifica `date` (string)
   - Verifica `score` (number > 0)
   - Verifica `aspects` (array não vazio)
   - Valida estrutura de cada aspecto

3. **Filtragem:**
   - Remove momentos inválidos
   - Atualiza `aspects` com apenas aspectos válidos

4. **Armazenamento:**
   - `setBestMoments(validMoments)` - armazena no estado React

### Processamento para Exibição (dentro do render)

1. **Filtragem adicional:**
   - Filtra momentos com `score > 0` e `aspects.length > 0`
   - Valida datas

2. **Agrupamento por data:**
   - Agrupa momentos por data (YYYY-MM-DD)
   - Usa regex para extrair data (evita problemas de timezone)

3. **Validação por grupo:**
   - Verifica se cada momento pertence à data do grupo
   - Filtra momentos inválidos

4. **Coleta de aspectos únicos:**
   - Itera sobre momentos válidos do grupo
   - Valida planeta (deve estar em `allowedPlanets[action]`)
   - Valida casa (deve estar em `allowedHouses[action]`)
   - Adiciona ao Set `validReasons`

5. **Cálculo de score máximo:**
   - Encontra maior score entre momentos do grupo

6. **Exibição:**
   - Renderiza card com data formatada
   - Mostra horários favoráveis
   - Mostra score máximo do dia
   - Lista aspectos únicos do dia

---

## Pontos Críticos

### 1. Dados do Usuário
- **Backend:** Obtém dados do banco de dados (mapa astral primário)
- **Frontend:** Usa `userData.coordinates` apenas para validação inicial
- **⚠️ IMPORTANTE:** O backend NÃO usa `userData.coordinates` do frontend!

### 2. Autenticação
- Backend requer token JWT válido
- Frontend envia token automaticamente via `apiService.request()`

### 3. Validações em Múltiplas Camadas
- **Backend:** Valida antes de retornar
- **Frontend (recebimento):** Valida estrutura da resposta
- **Frontend (processamento):** Valida novamente antes de exibir
- **Frontend (exibição):** Valida planeta e casa permitidos

### 4. Cache
- Frontend verifica `localStorage` para atualizar apenas quando necessário
- Backend calcula sempre do zero (sem cache)

---

## Possíveis Problemas

1. **Dados diferentes entre backend e frontend:**
   - Backend usa dados do banco de dados
   - Frontend pode ter dados desatualizados em `userData`

2. **Cache do navegador:**
   - Dados antigos podem estar sendo exibidos
   - Limpar cache pode resolver

3. **Timezone:**
   - Backend retorna datas em UTC
   - Frontend processa com cuidado para evitar problemas

4. **Aspectos duplicados:**
   - Set `validReasons` deve evitar duplicatas
   - Mas pode haver problemas se momentos de diferentes datas forem agrupados incorretamente

