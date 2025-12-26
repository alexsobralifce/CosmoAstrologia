# 🔑 Como Configurar GROQ_API_KEY em Produção (Railway)

## ⚠️ IMPORTANTE

**SIM, você PRECISA configurar a `GROQ_API_KEY` no Railway para que as interpretações astrológicas funcionem em produção.**

Sem essa chave, o sistema não conseguirá gerar interpretações usando IA.

---

## 🚀 Passo a Passo

### 1. Obter a Chave da API Groq

1. Acesse: **https://console.groq.com/**
2. Faça login ou crie uma conta
3. Vá em **API Keys** (ou **Keys**)
4. Clique em **Create API Key**
5. Copie a chave (ela começa com `gsk_`)

⚠️ **IMPORTANTE**: A chave só é mostrada uma vez! Copie e guarde em local seguro.

---

### 2. Configurar no Railway

#### Passo 1: Acessar o Projeto
1. Acesse o painel do Railway: **https://railway.app/**
2. Selecione seu projeto
3. Clique no serviço do **backend**

#### Passo 2: Adicionar Variável
1. Vá na aba **"Variables"** (ou **"Variáveis"**)
2. Clique em **"+ New Variable"** (ou **"+ Nova Variável"**)
3. Preencha:
   - **Name**: `GROQ_API_KEY`
   - **Value**: Cole a chave que você copiou (ex: `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
4. Clique em **"Add"** (ou **"Adicionar"**)

#### Passo 3: Verificar
- A variável deve aparecer na lista
- O nome deve ser exatamente `GROQ_API_KEY` (case-sensitive)
- O valor deve começar com `gsk_`

---

### 3. Reiniciar o Serviço

Após adicionar a variável:

1. O Railway **automaticamente** fará um novo deploy
2. Ou você pode forçar um redeploy:
   - Vá em **"Deployments"**
   - Clique em **"Redeploy"** no deploy mais recente

---

## ✅ Verificar se Está Funcionando

### Opção 1: Verificar Logs do Railway

Após o deploy, verifique os logs. Você deve ver:
```
[RAG] Groq client inicializado
```

Se houver erro, verá:
```
[ERROR] GROQ_API_KEY não configurada
```
ou
```
[ERROR] Invalid API Key
```

### Opção 2: Usar o Endpoint de Diagnóstico

Acesse no navegador:
```
https://seu-backend.railway.app/api/birth-chart/diagnostics
```

Procure por:
```json
{
  "services": {
    "groq": {
      "api_key_configured": true,
      "api_key_valid": true,
      "api_key_format_valid": true
    }
  }
}
```

Se `api_key_valid` for `false`, a chave está inválida ou expirada.

---

## 🔍 Troubleshooting

### Erro: "Invalid API Key" (401)

**Causas possíveis:**
1. Chave copiada incorretamente (espaços extras, caracteres faltando)
2. Chave expirada ou revogada
3. Chave de outro ambiente (teste vs produção)

**Solução:**
1. Verifique se copiou a chave completa (sem espaços)
2. Gere uma nova chave no console do Groq
3. Atualize a variável no Railway
4. Faça um novo deploy

### Erro: "GROQ_API_KEY não configurada"

**Causas possíveis:**
1. Variável não foi adicionada
2. Nome da variável está errado (case-sensitive)
3. Variável foi adicionada mas o deploy não foi feito

**Solução:**
1. Verifique se a variável existe no Railway
2. Verifique se o nome é exatamente `GROQ_API_KEY` (maiúsculas)
3. Force um novo deploy

### A chave funciona localmente mas não em produção

**Causa:** Pode ser que você tenha uma chave diferente configurada localmente

**Solução:**
1. Use a mesma chave em ambos os ambientes, OU
2. Configure chaves diferentes (uma para dev, outra para prod)
3. Certifique-se de que a chave de produção está ativa no console do Groq

---

## 📋 Checklist

Antes de considerar a configuração completa:

- [ ] Chave obtida no console do Groq (https://console.groq.com/)
- [ ] Variável `GROQ_API_KEY` adicionada no Railway
- [ ] Nome da variável está correto (case-sensitive)
- [ ] Valor da chave começa com `gsk_`
- [ ] Deploy realizado após adicionar a variável
- [ ] Logs do Railway mostram que o Groq foi inicializado
- [ ] Endpoint de diagnóstico confirma que a chave é válida

---

## 💡 Dicas

1. **Use a mesma chave em dev e prod?**
   - Pode usar a mesma chave, mas é recomendado ter chaves separadas
   - Facilita gerenciamento e segurança

2. **A chave tem limite de uso?**
   - O Groq tem limites de rate e quota
   - Verifique no console do Groq seu plano e limites

3. **Posso testar sem a chave?**
   - Sim, mas as interpretações não serão geradas
   - O sistema funcionará em modo degradado (sem IA)

---

## 📚 Referências

- [Railway Environment Variables](https://docs.railway.app/develop/variables)
- [Groq Console](https://console.groq.com/)
- [Documentação Groq API](https://console.groq.com/docs)

