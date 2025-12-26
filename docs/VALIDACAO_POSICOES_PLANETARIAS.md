# Validação de Posições Planetárias

## Dados do Usuário

- **Nome:** Francisco Alexandre Araujo Rocha
- **Data:** 20/10/1981
- **Hora:** 13:30
- **Local:** Sobral, Ceará, Brasil
- **Coordenadas:** Latitude: -3.6883, Longitude: -40.3497

## Posições Exibidas no Sistema (da imagem)

### Planetas
1. **Sol:** Libra, Casa 1
2. **Lua:** Leão, Casa 4
3. **Mercúrio:** Libra, Casa 3
4. **Vênus:** Sagitário, Casa 2
5. **Marte:** Leão, Casa 1
6. **Júpiter:** Libra, Casa 9
7. **Saturno:** Libra, Casa 10
8. **Urano:** Escorpião, Casa 11
9. **Netuno:** Sagitário, Casa 12
10. **Plutão:** Libra, Casa 8

## Análise e Validação

### ✅ Signos - Validação Lógica

Para 20 de outubro de 1981, as posições em signos parecem corretas:

- **Sol em Libra:** ✅ CORRETO - Entre 23/09 e 22/10
- **Lua em Leão:** ✅ PROVÁVEL - Lua muda de signo rapidamente (2-3 dias), mas Leão é plausível
- **Mercúrio em Libra:** ✅ CORRETO - Mercúrio geralmente está próximo ao Sol (±30°), Libra faz sentido
- **Vênus em Sagitário:** ✅ PROVÁVEL - Vênus pode estar em diferentes signos
- **Marte em Leão:** ⚠️ VERIFICAR - Marte em Leão é possível, mas precisa confirmação
- **Júpiter em Libra:** ✅ CORRETO - Júpiter muda lentamente (~1 ano/signo)
- **Saturno em Libra:** ✅ CORRETO - Saturno muda muito lentamente (~2.5 anos/signo)
- **Urano em Escorpião:** ✅ CORRETO - Urano estava em Escorpião entre 1975-1981
- **Netuno em Sagitário:** ✅ CORRETO - Netuno estava em Sagitário entre 1970-1984
- **Plutão em Libra:** ✅ CORRETO - Plutão estava em Libra entre 1971-1983

### ⚠️ Casas - Verificação Necessária

As **casas** dependem fortemente da:
- Hora exata de nascimento (13:30)
- Local exato (coordenadas de Sobral)
- Sistema de casas usado (Placidus, Equal, etc.)

**Observação importante:** Para validar as casas com precisão, é necessário:
1. Verificar se o sistema está usando o sistema de casas correto (geralmente Placidus)
2. Confirmar as coordenadas exatas de Sobral, CE
3. Validar se a hora está no fuso horário correto (GMT-3 para Brasil em 1981)

## Como Validar os Cálculos

### Opção 1: Usar o Endpoint da API

Execute uma requisição para o backend com os dados exatos:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@validacao.com",
    "name": "Francisco Alexandre Araujo Rocha",
    "birth_data": {
      "birth_date": "1981-10-20",
      "birth_time": "13:30",
      "latitude": -3.6883,
      "longitude": -40.3497,
      "birth_place": "Sobral, Ceará, Brasil"
    }
  }'
```

### Opção 2: Comparar com Calculadoras Online Confiáveis

Use ferramentas reconhecidas para validar:

1. **Astro.com (Astrodienst)** - https://www.astro.com
   - Cadastre-se gratuitamente
   - Use a calculadora de mapa natal
   - Compare as posições

2. **Time and Date Astrology** - https://www.timeanddate.com
   - Calculadora de mapa astral
   - Validação de fuso horário histórico

3. **Cafe Astrology** - https://cafeastrology.com
   - Birth Chart Calculator
   - Mostra posições planetárias

### Opção 3: Verificar Manualmente

#### Para Sol em Libra:
- Período: 23/09 a 22/10 aproximadamente
- 20/10/1981 está dentro deste período ✅

#### Para Júpiter e Saturno em Libra:
- Júpiter estava em Libra entre 1980-1981 ✅
- Saturno estava em Libra entre 1980-1983 ✅

#### Para Urano, Netuno e Plutão:
- Urano em Escorpião: 1975-1981 ✅
- Netuno em Sagitário: 1970-1984 ✅
- Plutão em Libra: 1971-1983 ✅

## Possíveis Problemas

### 1. Sistema de Casas
Se as **casas** estiverem incorretas, pode ser devido a:
- Sistema de casas diferente do esperado
- Fuso horário incorreto
- Coordenadas imprecisas

### 2. Fuso Horário
Em 1981, o Brasil estava em GMT-3. Verifique se:
- O sistema está convertendo corretamente para UTC
- Está considerando horário de verão (se aplicável em 1981)

### 3. Coordenadas de Sobral
Coordenadas aproximadas de Sobral, CE:
- Latitude: -3.6883
- Longitude: -40.3497

Verifique se essas são as coordenadas exatas usadas no cálculo.

## Recomendações

1. **Validar com Astro.com** - Fonte mais confiável para comparação
2. **Verificar fuso horário** - Confirmar UTC correto para 20/10/1981 13:30 em Sobral
3. **Confirmar coordenadas** - Usar coordenadas GPS exatas de Sobral
4. **Sistema de casas** - Confirmar qual sistema está sendo usado (deve ser Placidus)

## Próximos Passos

1. Criar script de teste específico para validar essas posições
2. Comparar resultado com Astro.com
3. Documentar qualquer discrepância encontrada
4. Corrigir se necessário

