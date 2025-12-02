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

### 📧 Email (Verificação de Email)

#### `SMTP_HOST`
- **Descrição**: Servidor SMTP para envio de emails de verificação
- **Exemplos**:
  - Gmail: `smtp.gmail.com`
  - SendGrid: `smtp.sendgrid.net`
  - Outlook: `smtp-mail.outlook.com`
- **Opcional**: Se não configurado, o sistema funcionará mas não enviará emails (código será logado)

#### `SMTP_PORT`
- **Descrição**: Porta do servidor SMTP
- **Padrão**: `587` (STARTTLS)
- **Alternativa**: `465` (SSL direto)
- **Opcional**: Usa 587 por padrão

#### `SMTP_USERNAME`
- **Descrição**: Usuário para autenticação SMTP
- **Exemplos**:
  - Gmail: seu email completo
  - SendGrid: `apikey`
  - Outlook: seu email completo
- **Opcional**: Necessário apenas se `SMTP_HOST` estiver configurado

#### `SMTP_PASSWORD`
- **Descrição**: Senha para autenticação SMTP
- **⚠️ IMPORTANTE**: 
  - Gmail: Use "Senha de App" (não a senha normal)
  - SendGrid: Use sua API Key
  - Outros: Use senha de app ou API key conforme o provedor
- **Opcional**: Necessário apenas se `SMTP_HOST` estiver configurado

#### `EMAIL_FROM`
- **Descrição**: Email remetente (aparece como "De:")
- **Padrão**: `noreply@cosmoastral.com.br`
- **Opcional**: Pode deixar o padrão ou personalizar

**📖 Guia completo de configuração SMTP:** [TROUBLESHOOTING_SMTP.md](../backend/TROUBLESHOOTING_SMTP.md)

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

