# 🧪 Guia Rápido: Testar Brevo Localmente e em Produção

Este guia fornece instruções rápidas para testar o envio de emails com Brevo tanto localmente quanto em produção.

---

## 🏠 Teste Local

### 1. Configurar Variáveis de Ambiente

Crie ou edite o arquivo `backend/.env`:

```bash
# Email Configuration (Brevo)
BREVO_API_KEY=xkeysib-sua-api-key-aqui
EMAIL_FROM=noreply@cosmoastral.com.br
EMAIL_FROM_NAME=CosmoAstral

# Outras configurações necessárias
SECRET_KEY=sua-chave-secreta-aqui
GROQ_API_KEY=sua-chave-groq-aqui
```

### 2. Instalar Dependências

```bash
cd backend
pip install sib-api-v3-sdk
```

Ou instale todas as dependências:

```bash
pip install -r requirements.txt
```

### 3. Executar Teste

```bash
python3 test_brevo_local.py
```

O script irá:
- ✅ Verificar se a biblioteca está instalada
- ✅ Verificar se `BREVO_API_KEY` está configurado
- ✅ Solicitar um email de teste
- ✅ Enviar um email de verificação
- ✅ Mostrar logs detalhados

### 4. Verificar Resultado

- ✅ Verifique a caixa de entrada do email
- ✅ Verifique a pasta de spam
- ✅ Confirme se recebeu o código de verificação

---

## 🚀 Teste em Produção (Railway)

### 1. Configurar Variáveis no Railway

No painel do Railway:

1. Acesse seu projeto
2. Vá em **Variables**
3. Adicione as seguintes variáveis:

```
BREVO_API_KEY=xkeysib-sua-api-key-aqui
EMAIL_FROM=noreply@cosmoastral.com.br
EMAIL_FROM_NAME=CosmoAstral
```

### 2. Fazer Redeploy

1. No Railway, vá em **Deployments**
2. Clique em **Redeploy**
3. Aguarde o deploy completar

### 3. Testar via API

Faça uma requisição de registro:

```bash
curl -X POST https://seu-backend.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu-email@exemplo.com",
    "password": "senha123",
    "name": "Seu Nome"
  }'
```

### 4. Verificar Logs

No Railway:
1. Vá em **Deployments**
2. Clique no deploy mais recente
3. Veja os logs para confirmar o envio

Você deve ver:
```
[EMAIL] ✅✅✅ EMAIL ENVIADO COM SUCESSO! ✅✅✅
```

### 5. Verificar Email

- ✅ Verifique a caixa de entrada
- ✅ Verifique a pasta de spam
- ✅ Confirme se recebeu o código

---

## 🔍 Verificar Configuração

### Verificar se Brevo está Configurado

Execute no terminal:

```bash
cd backend
python3 -c "from app.core.config import settings; print('BREVO_API_KEY:', '✅ Configurado' if settings.BREVO_API_KEY else '❌ Não configurado')"
```

### Verificar Biblioteca

```bash
python3 -c "import sib_api_v3_sdk; print('✅ Biblioteca instalada')"
```

---

## 🐛 Problemas Comuns

### Erro: "BREVO_API_KEY não configurado"

**Solução:**
1. Verifique se o arquivo `.env` existe em `backend/.env`
2. Verifique se a variável está escrita corretamente
3. Reinicie o servidor após adicionar a variável

### Erro: "API key is invalid"

**Solução:**
1. Verifique se a chave começa com `xkeysib-`
2. Gere uma nova chave no Brevo: https://app.brevo.com/settings/keys/api
3. Atualize a variável no `.env` ou Railway

### Erro: "Sender email not verified"

**Solução:**
1. Acesse: https://app.brevo.com/settings/senders
2. Verifique o email usado em `EMAIL_FROM`
3. Clique em "Verify" e siga as instruções

### Email não chega

**Verificações:**
1. ✅ Verifique a pasta de spam
2. ✅ Verifique os logs do servidor
3. ✅ Verifique os logs do Brevo: https://app.brevo.com/settings/logs
4. ✅ Confirme que o email está verificado no Brevo

---

## 📚 Recursos

- **Guia Completo:** [CONFIGURACAO_BREVO.md](./CONFIGURACAO_BREVO.md)
- **Script de Teste:** [test_brevo_local.py](./test_brevo_local.py)
- **Dashboard Brevo:** https://app.brevo.com/
- **API Keys:** https://app.brevo.com/settings/keys/api
- **Logs:** https://app.brevo.com/settings/logs

---

## ✅ Checklist Rápido

### Local
- [ ] `BREVO_API_KEY` configurado no `.env`
- [ ] `EMAIL_FROM` configurado no `.env`
- [ ] Biblioteca `sib-api-v3-sdk` instalada
- [ ] Script de teste executado com sucesso
- [ ] Email recebido e verificado

### Produção
- [ ] Variáveis configuradas no Railway
- [ ] Redeploy realizado
- [ ] Teste de registro realizado
- [ ] Logs verificados
- [ ] Email recebido e verificado

---

✨ **Pronto para testar!** Siga os passos acima para testar localmente e em produção.

