# 🚀 Variáveis de Ambiente para Railway

Este documento explica como configurar as variáveis de ambiente para fazer deploy do backend no Railway.

## 📋 Variáveis Necessárias

### ⚠️ Obrigatórias

#### `SECRET_KEY`
- **Descrição**: Chave secreta para assinar tokens JWT
- **Gerar uma chave segura**: 
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- **Exemplo**: `xK9mP2qR7vT4wY8zA1bC3dE5fG6hI0jK2lM4nO6pQ8rS0tU`

#### `GROQ_API_KEY`
- **Descrição**: Chave da API Groq para geração de interpretações astrológicas com IA
- **Onde obter**: https://console.groq.com/
- **Exemplo**: `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 🔧 Recomendadas para Produção

#### `DATABASE_URL`
- **Descrição**: URL de conexão com o banco de dados
- **Railway**: Se você adicionar um serviço PostgreSQL no Railway, ele define automaticamente esta variável
- **Formato PostgreSQL**: `postgresql://user:password@host:port/database`
- **Formato SQLite (dev)**: `sqlite:///./astrologia.db`

#### `CORS_ORIGINS`
- **Descrição**: URLs permitidas para fazer requisições ao backend (separadas por vírgula)
- **Formato**: URLs separadas por vírgula, sem espaços extras
- **Exemplo**: `https://seu-app.vercel.app,https://www.seu-dominio.com`
- **Padrão**: Se não definido, usa as URLs de desenvolvimento local

### 🔐 Opcionais (OAuth Google)

#### `GOOGLE_CLIENT_ID`
- **Descrição**: Client ID do Google OAuth
- **Onde obter**: https://console.cloud.google.com/

#### `GOOGLE_CLIENT_SECRET`
- **Descrição**: Client Secret do Google OAuth
- **Onde obter**: https://console.cloud.google.com/

### 📧 Email (Brevo/SendinBlue - Verificação de Email)

#### `BREVO_API_KEY` ⭐ **OBRIGATÓRIO para envio de emails**
- **Descrição**: API Key do Brevo (SendinBlue) para envio de emails de verificação
- **Onde obter**: https://app.brevo.com/settings/keys/api
- **Formato**: `xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Exemplo**: `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`
- **⚠️ IMPORTANTE**: Sem esta chave, os emails não serão enviados (código será apenas logado)

#### `EMAIL_FROM`
- **Descrição**: Email remetente (aparece como "De:")
- **Padrão**: `noreply@cosmoastral.com.br` (deve ser verificado no Brevo)
- **Como verificar email**: 
  1. Acesse https://app.brevo.com/settings/senders
  2. Adicione o email do remetente
  3. Verifique através do link enviado ou configure DNS

#### `EMAIL_FROM_NAME`
- **Descrição**: Nome do remetente (aparece como nome do remetente)
- **Padrão**: `CosmoAstral`
- **Exemplo**: `CosmoAstral`

**📖 Guia completo de configuração:** [CONFIGURACAO_BREVO.md](../backend/CONFIGURACAO_BREVO.md)

**✅ Vantagens do Brevo:**
- ✅ Funciona perfeitamente no Railway (sem problemas de rede)
- ✅ API simples e confiável
- ✅ Grátis até 300 emails/dia
- ✅ Dashboard completo para monitoramento
- ✅ Sem necessidade de configurar SMTP complexo

### 📝 Opcionais (com valores padrão)

#### `ALGORITHM`
- **Descrição**: Algoritmo para JWT
- **Padrão**: `HS256`
- **Não precisa configurar** a menos que queira mudar

#### `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Descrição**: Tempo de expiração do token JWT em minutos
- **Padrão**: `30`
- **Não precisa configurar** a menos que queira mudar

#### `PORT`
- **Descrição**: Porta em que o servidor vai rodar
- **Railway**: Definido automaticamente pelo Railway
- **Padrão**: `8000`
- **Não precisa configurar** - o Railway gerencia isso

---

## 🔧 Como Configurar no Railway

### Passo 1: Acesse as Configurações
1. No Railway, vá para o seu projeto
2. Clique no serviço do backend
3. Vá na aba **"Variables"** (Variáveis)

### Passo 2: Adicione as Variáveis

Adicione cada variável clicando em **"New Variable"**:

#### Variáveis Obrigatórias:
```
SECRET_KEY = [cole a chave gerada]
GROQ_API_KEY = [sua chave da Groq]
BREVO_API_KEY = [sua API key do Brevo - formato: xkeysib-...]
EMAIL_FROM = noreply@cosmoastral.com.br
EMAIL_FROM_NAME = CosmoAstral
```

#### Variável de CORS (ajuste com sua URL de produção):
```
CORS_ORIGINS = https://seu-frontend.vercel.app,https://www.seu-dominio.com
```

#### Se usar PostgreSQL no Railway:
- O Railway **define automaticamente** `DATABASE_URL` quando você adiciona um serviço PostgreSQL
- Não precisa configurar manualmente!

#### Se usar OAuth Google:
```
GOOGLE_CLIENT_ID = [seu client id]
GOOGLE_CLIENT_SECRET = [seu client secret]
```

### Passo 3: Deploy
Após configurar as variáveis, faça um novo deploy ou aguarde o deploy automático.

---

## 📝 Exemplo Completo de Configuração

### No Railway, você teria:

```
SECRET_KEY = xK9mP2qR7vT4wY8zA1bC3dE5fG6hI0jK2lM4nO6pQ8rS0tU
GROQ_API_KEY = gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BREVO_API_KEY = xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM = noreply@cosmoastral.com.br
EMAIL_FROM_NAME = CosmoAstral
CORS_ORIGINS = https://meu-app.vercel.app,https://www.meusite.com
DATABASE_URL = [definido automaticamente pelo Railway se usar Postgres]
GOOGLE_CLIENT_ID = [seu client id - se usar OAuth]
GOOGLE_CLIENT_SECRET = [seu client secret - se usar OAuth]
```

---

## 🔍 Verificando se Está Funcionando

Após o deploy, você pode verificar os logs do Railway para confirmar:

1. ✅ O servidor iniciou sem erros
2. ✅ O RAG service carregou o índice corretamente
3. ✅ O banco de dados está conectado

Se houver erros relacionados a variáveis de ambiente, verifique:
- Se o nome da variável está correto (case-sensitive)
- Se não há espaços extras no valor
- Se a variável foi salva corretamente no Railway

---

## 🆘 Troubleshooting

### Erro: "SECRET_KEY not set"
- **Solução**: Adicione a variável `SECRET_KEY` no Railway

### Erro: "RAG service not working"
- **Solução**: Verifique se `GROQ_API_KEY` está configurada corretamente

### Erro: "CORS error" no frontend
- **Solução**: Adicione a URL do seu frontend em `CORS_ORIGINS`

### Erro: "Database connection failed"
- **Solução**: Se usar PostgreSQL, certifique-se de que o serviço Postgres está rodando no Railway

---

## 📚 Referências

- [Railway Environment Variables](https://docs.railway.app/develop/variables)
- [Groq API Documentation](https://console.groq.com/docs)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)

