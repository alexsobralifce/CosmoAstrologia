# ✅ Verificar Variável Compartilhada no Railway

## 📋 Situação

Você está usando `${{shared.GROQ_API_KEY}}` no Railway, que é a **sintaxe correta** para variáveis compartilhadas.

---

## 🔍 Como Verificar se Está Funcionando

### 1. Verificar se a Variável Compartilhada Existe

No Railway Dashboard:

1. Vá para o **projeto** (não o serviço específico)
2. Vá na aba **"Variables"** (no nível do projeto)
3. Procure por `GROQ_API_KEY` na seção **"Shared Variables"**
4. Verifique se:
   - ✅ A variável existe
   - ✅ O valor começa com `gsk_`
   - ✅ Não há espaços extras

### 2. Verificar se o Serviço Está Referenciando Corretamente

No serviço do backend:

1. Vá para o serviço **backend**
2. Aba **"Variables"**
3. Procure por `GROQ_API_KEY`
4. Deve aparecer como: `${{shared.GROQ_API_KEY}}`

⚠️ **IMPORTANTE**: O valor deve ser exatamente `${{shared.GROQ_API_KEY}}` (com as chaves duplas)

### 3. Verificar se o Railway Está Resolvendo

O Railway resolve a referência automaticamente. Para verificar:

1. Após fazer deploy, veja os **logs do Railway**
2. Procure por mensagens relacionadas ao Groq
3. Se a chave estiver sendo lida, você verá:
   ```
   [RAG] Groq client inicializado
   ```
4. Se não estiver, verá:
   ```
   [WARNING] GROQ_API_KEY não configurada
   ```

---

## 🧪 Testar via Endpoint de Diagnóstico

Após o deploy, acesse:

```
https://seu-backend.railway.app/api/birth-chart/diagnostics
```

Procure por:

```json
{
  "services": {
    "groq": {
      "api_key_configured": true,
      "api_key_length": 51,
      "api_key_format_valid": true,
      "api_key_valid": true,
      "source": "env"
    }
  }
}
```

**Se `api_key_valid` for `false`**, a chave está sendo lida mas é inválida.

---

## 🔧 Troubleshooting

### Problema: Variável compartilhada não está sendo resolvida

**Sintomas:**
- `api_key_configured: false` no diagnóstico
- Erro "GROQ_API_KEY não configurada" nos logs

**Soluções:**

1. **Verificar se a variável compartilhada existe:**
   - Vá no nível do **projeto** (não serviço)
   - Aba **"Variables"** → **"Shared Variables"**
   - Certifique-se de que `GROQ_API_KEY` existe lá

2. **Verificar a sintaxe no serviço:**
   - No serviço backend, aba **"Variables"**
   - O valor deve ser exatamente: `${{shared.GROQ_API_KEY}}`
   - Não deve ser: `{{shared.GROQ_API_KEY}}` (sem o `$`)
   - Não deve ser: `${{ shared.GROQ_API_KEY }}` (com espaços)

3. **Fazer um novo deploy:**
   - Após configurar, force um redeploy
   - Vá em **"Deployments"** → **"Redeploy"**

### Problema: Chave inválida (401)

**Sintomas:**
- `api_key_configured: true` mas `api_key_valid: false`
- Erro "Invalid API Key" nos logs

**Soluções:**

1. **Verificar o valor da variável compartilhada:**
   - Vá no nível do **projeto**
   - Aba **"Variables"** → **"Shared Variables"**
   - Clique em `GROQ_API_KEY` para ver/editar
   - Verifique se:
     - Começa com `gsk_`
     - Não tem espaços antes/depois
     - Está completa (não cortada)

2. **Atualizar a chave:**
   - Obtenha uma nova chave em: https://console.groq.com/
   - Atualize a variável compartilhada
   - Force um novo deploy

---

## 📝 Checklist de Verificação

- [ ] Variável compartilhada `GROQ_API_KEY` existe no nível do projeto
- [ ] Valor da variável compartilhada começa com `gsk_`
- [ ] Serviço backend referencia como `${{shared.GROQ_API_KEY}}`
- [ ] Deploy realizado após configurar
- [ ] Logs mostram que o Groq foi inicializado
- [ ] Endpoint de diagnóstico mostra `api_key_valid: true`

---

## 💡 Dica: Variáveis Compartilhadas vs Variáveis de Serviço

**Variáveis Compartilhadas** (`${{shared.VAR}}`):
- ✅ Definidas no nível do projeto
- ✅ Podem ser usadas em múltiplos serviços
- ✅ Úteis para valores que são os mesmos em todos os serviços
- ✅ Fácil de gerenciar (uma única fonte)

**Variáveis de Serviço** (valor direto):
- ✅ Definidas no nível do serviço
- ✅ Específicas para cada serviço
- ✅ Úteis quando cada serviço precisa de valores diferentes

Para `GROQ_API_KEY`, usar variável compartilhada é uma **excelente escolha**! 👍

---

## 🚀 Próximos Passos

1. Verifique se a variável compartilhada está configurada corretamente
2. Force um novo deploy
3. Teste o endpoint de diagnóstico
4. Se ainda houver erro, verifique os logs do Railway

