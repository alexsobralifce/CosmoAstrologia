# 📧 Configuração do Brevo (SendinBlue) - Guia Completo

Este guia explica como configurar o Brevo para envio de emails tanto localmente quanto em produção.

## 🎯 Visão Geral

O sistema usa **Brevo (SendinBlue)** como provedor de email para envio de códigos de verificação. O Brevo oferece:
- ✅ API simples e confiável
- ✅ 300 emails grátis por dia
- ✅ Dashboard completo para monitoramento
- ✅ Suporte a templates HTML

---

## 🏠 Configuração Local (Desenvolvimento)

### 1. Criar arquivo `.env`

No diretório `backend/`, crie um arquivo `.env` com o seguinte conteúdo:

```bash
# Email Configuration (Brevo)
BREVO_API_KEY=xkeysib-sua-api-key-aqui
EMAIL_FROM=noreply@cosmoastral.com.br
EMAIL_FROM_NAME=CosmoAstral

# Outras configurações
SECRET_KEY=sua-chave-secreta-aqui
GROQ_API_KEY=sua-chave-groq-aqui
```

### 2. Obter API Key do Brevo

1. Acesse: https://app.brevo.com/
2. Faça login na sua conta
3. Vá em **Settings** → **API Keys**
4. Clique em **Generate a new API key**
5. Copie a chave (formato: `xkeysib-...`)
6. Cole no arquivo `.env` como `BREVO_API_KEY`

### 3. Verificar Email no Brevo

Antes de enviar emails, você precisa verificar o email do remetente:

1. Acesse: https://app.brevo.com/settings/senders
2. Clique em **Add a sender**
3. Adicione o email que você usará (ex: `noreply@cosmoastral.com.br`)
4. Verifique o email através do link enviado ou configurando DNS

**Para testes locais:**
- Você pode usar qualquer email verificado na sua conta Brevo
- Não precisa verificar o domínio completo para testes

### 4. Instalar Dependências

```bash
cd backend
pip install sib-api-v3-sdk
```

Ou instale todas as dependências:

```bash
pip install -r requirements.txt
```

### 5. Testar Configuração

Execute o script de teste:

```bash
python3 test_brevo_local.py
```

O script irá:
- ✅ Verificar se a biblioteca está instalada
- ✅ Verificar se `BREVO_API_KEY` está configurado
- ✅ Enviar um email de teste
- ✅ Mostrar logs detalhados

---

## 🚀 Configuração em Produção (Railway)

### 1. Configurar Variáveis de Ambiente

No painel do Railway:

1. Acesse seu projeto no Railway
2. Vá em **Variables**
3. Adicione as seguintes variáveis:

```
BREVO_API_KEY=xkeysib-sua-api-key-aqui
EMAIL_FROM=noreply@cosmoastral.com.br
EMAIL_FROM_NAME=CosmoAstral
```

### 2. Verificar Domínio no Brevo

Para produção, você precisa verificar o domínio completo:

1. Acesse: https://app.brevo.com/settings/domains
2. Adicione seu domínio (ex: `cosmoastral.com.br`)
3. Configure os registros DNS conforme instruções do Brevo
4. Aguarde a verificação (pode levar algumas horas)

### 3. Fazer Redeploy

Após configurar as variáveis:

1. No Railway, vá em **Deployments**
2. Clique em **Redeploy** para aplicar as mudanças
3. Monitore os logs para verificar se há erros

---

## 🧪 Testar Envio de Email

### Teste Local

```bash
cd backend
python3 test_brevo_local.py
```

### Teste via API

1. Inicie o servidor:
   ```bash
   python run.py
   ```

2. Faça uma requisição de registro:
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "seu-email@exemplo.com",
       "password": "senha123",
       "name": "Seu Nome"
     }'
   ```

3. Verifique o email recebido (incluindo spam)

### Verificar Logs

Os logs do envio de email aparecem no console do servidor:

```
[EMAIL] 📧 INICIANDO ENVIO DE EMAIL DE VERIFICAÇÃO
[EMAIL] Destinatário: usuario@exemplo.com
[EMAIL] Código: 123456
[EMAIL] ✅✅✅ EMAIL ENVIADO COM SUCESSO! ✅✅✅
```

---

## 🐛 Troubleshooting

### Erro: "API key is invalid"

**Causa:** A `BREVO_API_KEY` está incorreta ou não foi configurada.

**Solução:**
1. Verifique se a chave começa com `xkeysib-`
2. Gere uma nova chave no Brevo se necessário
3. Certifique-se de que a variável está configurada no `.env` (local) ou Railway (produção)

### Erro: "Sender email not verified"

**Causa:** O email usado em `EMAIL_FROM` não está verificado no Brevo.

**Solução:**
1. Acesse: https://app.brevo.com/settings/senders
2. Verifique o email ou adicione um novo
3. Clique em "Verify" e siga as instruções

### Email não está sendo enviado

**Verificações:**
1. ✅ `BREVO_API_KEY` está configurado?
2. ✅ `EMAIL_FROM` está verificado no Brevo?
3. ✅ Biblioteca `sib-api-v3-sdk` está instalada?
4. ✅ Verifique os logs do servidor
5. ✅ Verifique os logs do Brevo: https://app.brevo.com/settings/logs

### Email vai para spam

**Soluções:**
1. Verifique o domínio no Brevo (SPF, DKIM, DMARC)
2. Use um email verificado e com boa reputação
3. Evite palavras suspeitas no assunto/corpo do email

---

## 📊 Monitoramento

### Dashboard do Brevo

Acesse: https://app.brevo.com/

Você pode monitorar:
- 📧 Emails enviados
- ✅ Taxa de entrega
- ❌ Bounces e erros
- 📈 Estatísticas de abertura

### Logs do Servidor

Os logs do servidor mostram informações detalhadas sobre cada envio:

```
[EMAIL] 📧 INICIANDO ENVIO DE EMAIL DE VERIFICAÇÃO
[EMAIL] Destinatário: usuario@exemplo.com
[EMAIL] Código: 123456
[EMAIL] ✅✅✅ EMAIL ENVIADO COM SUCESSO! ✅✅✅
[EMAIL] 🆔 Message ID: <message-id>
```

---

## 📚 Recursos

- **Documentação Brevo:** https://developers.brevo.com/
- **Python SDK:** https://github.com/getbrevo/brevo-python
- **Dashboard:** https://app.brevo.com/
- **API Keys:** https://app.brevo.com/settings/keys/api
- **Senders:** https://app.brevo.com/settings/senders
- **Logs:** https://app.brevo.com/settings/logs

---

## ✅ Checklist

### Local
- [ ] Conta Brevo criada
- [ ] API Key gerada e configurada no `.env`
- [ ] Email do remetente verificado no Brevo
- [ ] Biblioteca `sib-api-v3-sdk` instalada
- [ ] Script de teste executado com sucesso

### Produção
- [ ] Variáveis configuradas no Railway
- [ ] Domínio verificado no Brevo (se aplicável)
- [ ] Redeploy realizado
- [ ] Teste de envio em produção realizado
- [ ] Logs monitorados

---

✨ **Configuração concluída!** O sistema está pronto para enviar emails via Brevo.

