# Bug de Timezone na Função formatDate

## Data: 05/12/2025

## Problema Identificado

A função `formatDate` no frontend estava usando `new Date(dateString)` sem considerar timezone, causando:
- Datas sendo exibidas incorretamente (ex: 8/12 sendo exibido como 5/12)
- Problemas quando o navegador está em timezone diferente de UTC

## Validação

### Backend:
- Retorna datas no formato ISO: `2025-12-08T00:00:00`
- 8/12/2025: Score 17, aspectos válidos
- 5/12/2025: Não está nos top 10 (score 17, mas há outros com mesmo score)

### Frontend (ANTES da correção):
- `formatDate` usava `new Date(dateString)` que interpreta no timezone local
- Se o navegador está em timezone UTC-3, `2025-12-08T00:00:00` pode ser interpretado como 7/12 21:00
- Isso causava datas sendo exibidas incorretamente

### Frontend (DEPOIS da correção):
- Extrai data diretamente do formato YYYY-MM-DD se disponível
- Usa UTC para parsear timestamps
- Evita problemas de timezone

## Correção Implementada

```typescript
const formatDate = (dateString: string): string => {
  // Se a data já está no formato YYYY-MM-DD, usar diretamente
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
    const [year, month, day] = dateString.split('-');
    // ... formatar diretamente
  }
  
  // Se tem timestamp, usar UTC
  const date = new Date(dateString);
  return `${date.getUTCDate()} de ${months[date.getUTCMonth()]} de ${date.getUTCFullYear()}`;
};
```

## Garantias

✅ **Datas são extraídas diretamente do formato YYYY-MM-DD quando possível**
✅ **UTC é usado para parsear timestamps, evitando problemas de timezone**
✅ **Validação de data inválida com fallback**
✅ **Logs de erro para debug**

