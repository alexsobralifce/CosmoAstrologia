# 🔧 Troubleshooting: Problemas com SMTP

## ❌ Erro: "Network is unreachable" ou "Connection refused"

Este erro indica que o servidor não consegue conectar ao servidor SMTP. Possíveis causas:

### 1. **Verificar Configuração no Railway**

Certifique-se de que as variáveis estão configuradas corretamente:

```env
SMTP_HOST=smtp.gmail.com          # ou seu provedor
SMTP_PORT=587                     # ou 465 para SSL
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app       # Senha de app, não senha normal
EMAIL_FROM=noreply@cosmoastral.com.br
```

### 2. **Provedores de Email Comuns**

#### **Gmail**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587                     # STARTTLS
# ou
SMTP_PORT=465                     # SSL direto
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=senha-de-app        # ⚠️ Use "Senha de App" do Google
```

**Como obter Senha de App do Google:**
1. Acesse: https://myaccount.google.com/apppasswords
2. Gere uma senha de app específica
3. Use essa senha (não a senha normal da conta)

#### **Outlook/Hotmail**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@outlook.com
SMTP_PASSWORD=sua-senha
```

#### **SendGrid**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=sua-api-key-sendgrid
```

#### **Mailgun**
```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@seu-dominio.mailgun.org
SMTP_PASSWORD=sua-senha-mailgun
```

#### **Amazon SES**
```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com  # Ajuste a região
SMTP_PORT=587
SMTP_USERNAME=sua-access-key
SMTP_PASSWORD=sua-secret-key
```

### 3. **Testar Conectividade**

O sistema agora tenta automaticamente:
- **STARTTLS** (porta 587) - método padrão
- **SSL direto** (porta 465) - fallback automático

Se ambos falharem, verifique:

#### **Verificar se o host está acessível:**
```bash
# No Railway, você pode executar via Railway CLI
railway run python -c "
import socket
try:
    socket.create_connection(('smtp.gmail.com', 587), timeout=5)
    print('✅ Conectado ao SMTP')
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

#### **Verificar DNS:**
```bash
railway run nslookup smtp.gmail.com
```

### 4. **Problemas Específicos do Railway**

#### **Firewall/Rede:**
- Railway pode ter restrições de saída
- Alguns provedores bloqueiam conexões de IPs desconhecidos
- **Solução**: Use um serviço de email confiável (SendGrid, Mailgun, SES)

#### **Timeout:**
- Timeout aumentado para 15 segundos
- Se ainda falhar, pode ser problema de rede

### 5. **Alternativas Recomendadas**

Para produção, recomenda-se usar serviços especializados:

#### **SendGrid (Recomendado)**
- ✅ Confiável e rápido
- ✅ API REST também disponível
- ✅ Grátis até 100 emails/dia
- 📝 https://sendgrid.com/

#### **Mailgun**
- ✅ Bom para transacionais
- ✅ API REST
- ✅ Grátis até 5.000 emails/mês
- 📝 https://www.mailgun.com/

#### **Amazon SES**
- ✅ Muito barato
- ✅ Escalável
- ✅ Integração com AWS
- 📝 https://aws.amazon.com/ses/

### 6. **Logs de Debug**

O sistema agora loga detalhes de cada tentativa:

```
[EMAIL] Tentando enviar para email@exemplo.com via STARTTLS na porta 587...
[ERROR] Erro de conexão ao SMTP smtp.gmail.com:587 - [Errno 101] Network is unreachable
[EMAIL] Tentando enviar para email@exemplo.com via SSL na porta 465...
[EMAIL] ✅ Código de verificação enviado para email@exemplo.com via SSL
```

### 7. **Solução Rápida: Usar SendGrid**

1. **Criar conta no SendGrid:**
   - Acesse: https://sendgrid.com/
   - Crie uma conta gratuita

2. **Obter API Key:**
   - Settings → API Keys
   - Crie uma chave com permissão "Mail Send"

3. **Configurar no Railway:**
   ```env
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USERNAME=apikey
   SMTP_PASSWORD=sua-api-key-aqui
   EMAIL_FROM=noreply@seu-dominio.com
   ```

4. **Verificar domínio (opcional):**
   - SendGrid permite enviar sem verificar domínio (com limitações)
   - Para produção, verifique seu domínio

### 8. **Fallback: Log do Código**

Se o SMTP não funcionar, o código ainda é salvo no banco e pode ser recuperado:

```sql
-- Ver código de verificação de um usuário
SELECT email, verification_code, verification_code_expires 
FROM users 
WHERE email = 'usuario@exemplo.com';
```

⚠️ **Atenção**: Isso é apenas para emergências. O ideal é resolver o SMTP.

---

## ✅ Checklist de Verificação

- [ ] Variáveis SMTP configuradas no Railway
- [ ] `SMTP_HOST` está correto (sem `http://` ou `https://`)
- [ ] `SMTP_PORT` está correto (587 ou 465)
- [ ] `SMTP_USERNAME` está correto
- [ ] `SMTP_PASSWORD` está correto (senha de app, não senha normal)
- [ ] `EMAIL_FROM` está configurado
- [ ] Testou conectividade (nslookup, telnet)
- [ ] Verificou logs do Railway para erros detalhados
- [ ] Considerou usar SendGrid/Mailgun para produção

---

## 📞 Suporte

Se o problema persistir:
1. Verifique os logs completos no Railway
2. Teste com outro provedor de email
3. Considere usar API REST (SendGrid, Mailgun) em vez de SMTP

