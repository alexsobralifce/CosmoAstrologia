# 📧 Configuração do Resend para Envio de Emails

## ✅ Mudanças Realizadas

O sistema foi atualizado para usar **Resend** em vez de SMTP do Gmail. O Resend é mais confiável e funciona perfeitamente no Railway.

---

## 🔧 Configuração no `.env` (Desenvolvimento Local)

Crie ou edite o arquivo `backend/.env`:

```env
# Resend API Key
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Email remetente (domínio verificado no Resend)
EMAIL_FROM=noreply@cosmoastral.com.br
# Para testes, pode usar:
# EMAIL_FROM=cosmoastral@resend.dev
```

---

## 🚀 Configuração no Railway (Produção)

No painel do Railway, adicione as seguintes variáveis de ambiente:

### Variáveis Obrigatórias:

```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@cosmoastral.com.br
```

### Como obter a API Key do Resend:

1. Acesse: https://resend.com/
2. Crie uma conta (grátis até 3.000 emails/mês)
3. Vá para **API Keys** no dashboard
4. Crie uma nova API Key
5. Copie a chave (começa com `re_`)

### ✅ Domínio Configurado:

O domínio `cosmoastral.com.br` já está verificado no Resend.
Use: `EMAIL_FROM=noreply@cosmoastral.com.br`

---

## 📋 Exemplo Completo de `.env`

```env
# Database
DATABASE_URL=sqlite:///./astrologia.db

# Security
SECRET_KEY=sua-chave-secreta-aqui
GROQ_API_KEY=sua-chave-groq-aqui

# Email (Resend)
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@cosmoastral.com.br

# Google OAuth (Opcional)
GOOGLE_CLIENT_ID=seu-client-id
GOOGLE_CLIENT_SECRET=seu-client-secret

# CORS (Opcional - para desenvolvimento)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## ✅ Verificação

Após configurar, teste o envio de email:

1. Faça um registro de novo usuário
2. Verifique os logs:
   ```
   [EMAIL] Enviando email de verificação para usuario@exemplo.com via Resend...
   [EMAIL] ✅ Código de verificação enviado para usuario@exemplo.com via Resend
   ```
3. Verifique a caixa de entrada do email

---

## 🆘 Troubleshooting

### Erro: "RESEND_API_KEY não configurado"
- **Solução**: Adicione `RESEND_API_KEY` no `.env` ou variáveis de ambiente do Railway

### Erro: "Invalid API key"
- **Solução**: Verifique se a API key está correta e começa com `re_`

### Erro: "Domain not verified"
- **Solução**: Use `cosmoastral@resend.dev` temporariamente ou verifique seu domínio no Resend

### Email não chega
- **Solução**: 
  1. Verifique a pasta de spam
  2. Verifique os logs do Resend no dashboard
  3. Confirme que o email está correto

---

## 📚 Referências

- [Resend Documentation](https://resend.com/docs)
- [Resend Python SDK](https://resend.com/docs/send-with-python)
- [Resend Dashboard](https://resend.com/api-keys)

---

**Status:** ✅ Resend configurado e pronto para uso!

