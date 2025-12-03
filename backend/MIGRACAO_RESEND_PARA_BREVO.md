# 🔄 Migração: Resend → Brevo (SendinBlue)

## ✅ Migração Concluída

O sistema foi migrado do **Resend** para **Brevo (SendinBlue)** como provedor de email.

## 📋 Mudanças Implementadas

### 1. **Serviço de Email** (`app/services/email_service.py`)
- ✅ Removida integração com Resend
- ✅ Implementada integração com Brevo usando `sib-api-v3-sdk`
- ✅ Usa `TransactionalEmailsApi` para envio de emails transacionais
- ✅ Mantida mesma interface de função `send_verification_email()`

### 2. **Configurações** (`app/core/config.py`)
- ❌ Removido: `RESEND_API_KEY`
- ✅ Adicionado: `BREVO_API_KEY`
- ✅ Adicionado: `EMAIL_FROM_NAME` (nome do remetente)
- ✅ Mantido: `EMAIL_FROM` (email do remetente)

### 3. **Dependências**
- ❌ Removido: `resend>=2.0.0`
- ✅ Adicionado: `sib-api-v3-sdk>=8.2.0`
- Arquivos atualizados:
  - `requirements.txt`
  - `requirements-prod.txt`
  - `Dockerfile`

### 4. **Script de Teste**
- ✅ Criado: `test_brevo_local.py` para testar a integração localmente

## 🔧 Configuração Necessária

### Variáveis de Ambiente

**No arquivo `.env` (desenvolvimento local):**
```bash
# Email Configuration (Brevo)
BREVO_API_KEY=xkeysib-sua-api-key-aqui
EMAIL_FROM=noreply@cosmoastral.com.br
EMAIL_FROM_NAME=CosmoAstral
```

**No Railway (produção):**
1. Acesse o painel do Railway
2. Vá em **Variables**
3. Configure:
   - `BREVO_API_KEY`: Sua API key do Brevo (formato: `xkeysib-...`)
   - `EMAIL_FROM`: Email verificado no Brevo (ex: `noreply@cosmoastral.com.br`)
   - `EMAIL_FROM_NAME`: Nome do remetente (ex: `CosmoAstral`)

## 🔑 Como Obter a API Key do Brevo

1. Acesse: https://app.brevo.com/
2. Faça login na sua conta
3. Vá em **Settings** → **API Keys**
4. Clique em **Generate a new API key**
5. Copie a chave (formato: `xkeysib-...`)
6. Configure no `.env` ou Railway

## 📧 Verificar Email no Brevo

Antes de enviar emails em produção, você precisa verificar seu domínio no Brevo:

1. Acesse: https://app.brevo.com/settings/senders
2. Clique em **Add a sender**
3. Adicione o email que você usará (ex: `noreply@cosmoastral.com.br`)
4. Verifique o email através do link enviado ou configurando DNS

## 🧪 Testar Localmente

### 1. Instalar Dependências
```bash
cd backend
pip install sib-api-v3-sdk
```

### 2. Configurar `.env`
```bash
BREVO_API_KEY=xkeysib-sua-api-key-aqui
EMAIL_FROM=noreply@cosmoastral.com.br
EMAIL_FROM_NAME=CosmoAstral
```

### 3. Executar Script de Teste
```bash
python3 test_brevo_local.py
```

O script irá:
- ✅ Verificar se a biblioteca está instalada
- ✅ Verificar se `BREVO_API_KEY` está configurado
- ✅ Enviar um email de teste
- ✅ Mostrar logs detalhados

## 📊 Comparação: Resend vs Brevo

| Aspecto | Resend | Brevo |
|---------|--------|-------|
| **API Key** | `re_...` | `xkeysib-...` |
| **Biblioteca** | `resend` | `sib-api-v3-sdk` |
| **API** | REST simples | REST completa |
| **Domínio de Teste** | `resend.dev` | Não possui |
| **Verificação** | Necessária | Necessária |
| **Limite Grátis** | 3.000/mês | 300/dia |

## ⚠️ Importante

1. **Remova as variáveis antigas do Resend:**
   - ❌ `RESEND_API_KEY` (não é mais necessário)

2. **Certifique-se de que o email está verificado:**
   - O email usado em `EMAIL_FROM` deve estar verificado no Brevo
   - Caso contrário, os emails não serão enviados

3. **Após configurar no Railway:**
   - Faça um **redeploy** para aplicar as mudanças
   - Monitore os logs para verificar se há erros

## 🐛 Troubleshooting

### Erro: "API key is invalid"
- Verifique se a `BREVO_API_KEY` está correta
- Certifique-se de que a chave começa com `xkeysib-`
- Gere uma nova chave se necessário

### Erro: "Sender email not verified"
- Verifique o email em: https://app.brevo.com/settings/senders
- Clique em "Verify" ou configure os registros DNS

### Email não está sendo enviado
- Verifique os logs do servidor
- Verifique os logs do Brevo em: https://app.brevo.com/settings/logs
- Confirme que todas as variáveis de ambiente estão configuradas

## 📚 Documentação

- **Brevo API Docs:** https://developers.brevo.com/
- **Python SDK:** https://github.com/getbrevo/brevo-python
- **Dashboard:** https://app.brevo.com/

## ✅ Checklist de Migração

- [x] Atualizar `email_service.py`
- [x] Atualizar `config.py`
- [x] Atualizar `requirements.txt`
- [x] Atualizar `requirements-prod.txt`
- [x] Atualizar `Dockerfile`
- [x] Criar script de teste
- [ ] Configurar `BREVO_API_KEY` no `.env` local
- [ ] Configurar variáveis no Railway
- [ ] Testar envio localmente
- [ ] Fazer redeploy no Railway
- [ ] Verificar envio em produção

## 🎯 Próximos Passos

1. **Configurar variáveis de ambiente:**
   - Local: atualizar `backend/.env`
   - Produção: atualizar no Railway

2. **Testar localmente:**
   ```bash
   python3 backend/test_brevo_local.py
   ```

3. **Fazer redeploy:**
   - No Railway, faça um redeploy para aplicar as mudanças

4. **Monitorar:**
   - Verifique os logs do servidor
   - Verifique os logs do Brevo

---

✨ **Migração concluída com sucesso!**

