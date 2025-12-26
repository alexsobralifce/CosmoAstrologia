# 🏠 Configuração Local do Sistema

Este guia explica como configurar o sistema para rodar localmente em desenvolvimento.

## 📋 Pré-requisitos

- Python 3.11 ou superior
- Node.js 18 ou superior
- npm ou yarn

---

## 🚀 Configuração Rápida

### 1. Backend

#### 1.1. Configurar Variáveis de Ambiente

1. **Copie o arquivo de exemplo:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edite o arquivo `.env` e configure:**
   ```env
   SECRET_KEY=sua-chave-secreta-aqui
   GROQ_API_KEY=sua-chave-groq-aqui
   BREVO_API_KEY=xkeysib-sua-api-key-aqui
   EMAIL_FROM=noreply@cosmoastral.com.br
   EMAIL_FROM_NAME=CosmoAstral
   ```

   **Gerar SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   **Obter GROQ_API_KEY:**
   - Acesse: https://console.groq.com/
   - Crie uma conta e obtenha sua chave de API
   
   **Obter BREVO_API_KEY:**
   - Acesse: https://app.brevo.com/settings/keys/api
   - Gere uma nova API key (formato: `xkeysib-...`)
   - Configure no `.env` como `BREVO_API_KEY`
   
   **📧 Guia completo de configuração do Brevo:** [../backend/CONFIGURACAO_BREVO.md](../backend/CONFIGURACAO_BREVO.md)

3. **Banco de dados:**
   - Por padrão, usa SQLite (`sqlite:///./astrologia.db`)
   - O banco será criado automaticamente na primeira execução
   - Não precisa configurar `DATABASE_URL` para desenvolvimento local

4. **CORS:**
   - Por padrão, já inclui `http://localhost:5173` e outras portas comuns
   - Não precisa configurar para desenvolvimento local

#### 1.2. Instalar Dependências e Rodar

**Opção A - Usando o script:**
```bash
./scripts/start-backend.sh
```

**Opção B - Manual:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

O backend estará rodando em: `http://localhost:8000`

---

### 2. Frontend

#### 2.1. Configurar Variáveis de Ambiente

1. **Copie o arquivo de exemplo:**
   ```bash
   cp .env.local.example .env.local
   ```

2. **Edite o arquivo `.env.local`:**
   ```env
   VITE_API_URL=http://localhost:8000
   ```

   ⚠️ **Importante:**
   - O nome da variável DEVE começar com `VITE_`
   - Não inclua barra final (`/`) na URL
   - Use `http://` para desenvolvimento local

#### 2.2. Instalar Dependências e Rodar

```bash
npm install
npm run dev
```

O frontend estará rodando em: `http://localhost:3000` (ou a porta configurada no `vite.config.ts`)

---

## ✅ Verificação

### Backend
1. Acesse: http://localhost:8000
   - Deve retornar: `{"message": "Astrologia API"}`

2. Acesse: http://localhost:8000/docs
   - Deve abrir a documentação interativa da API (Swagger)

### Frontend
1. Acesse: http://localhost:3000
   - Deve abrir a aplicação
   - Verifique o console do navegador (F12) para ver se está conectando ao backend correto

### Teste de Conexão
1. Abra o console do navegador (F12)
2. Tente fazer login ou cadastro
3. Verifique se as requisições estão indo para `http://localhost:8000`

---

## 🔧 Solução de Problemas

### Backend não inicia

**Erro: "SECRET_KEY not set"**
- Verifique se o arquivo `.env` existe em `backend/.env`
- Verifique se `SECRET_KEY` está definida no arquivo

**Erro: "Module not found"**
- Ative o ambiente virtual: `source venv/bin/activate`
- Instale as dependências: `pip install -r requirements.txt`

**Erro: "Port 8000 already in use"**
- Pare o processo na porta 8000:
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```
- Ou mude a porta no `run.py` e no `.env.local` do frontend

### Frontend não conecta ao backend

**Erro: "Failed to fetch"**
- Verifique se o backend está rodando
- Verifique se `VITE_API_URL` está configurada corretamente no `.env.local`
- Verifique se não há barra final na URL (`http://localhost:8000` ✅, `http://localhost:8000/` ❌)

**Erro: "CORS error"**
- Verifique se `http://localhost:3000` (ou a porta do frontend) está em `CORS_ORIGINS` no backend
- Por padrão, já está incluído, mas verifique se não sobrescreveu no `.env`

**Variável de ambiente não funciona**
- ⚠️ Variáveis do Vite só funcionam se começarem com `VITE_`
- ⚠️ Reinicie o servidor de desenvolvimento após mudar variáveis
- ⚠️ Variáveis são lidas apenas no build, não em runtime

---

## 📁 Estrutura de Arquivos

```
CosmoAstrologia/
├── backend/
│   ├── .env              # ← Crie este arquivo (copie de .env.example)
│   ├── .env.example       # ← Arquivo de exemplo
│   └── ...
├── .env.local             # ← Crie este arquivo (copie de .env.local.example)
├── .env.local.example     # ← Arquivo de exemplo
└── ...
```

---

## 🔄 Diferenças: Local vs Produção

### Local (Desenvolvimento)
- **Backend:** `http://localhost:8000`
- **Frontend:** `http://localhost:3000` ou `http://localhost:5173`
- **Banco:** SQLite (`astrologia.db`)
- **Variáveis:** Arquivo `.env` / `.env.local`

### Produção
- **Backend:** `https://seu-backend.railway.app`
- **Frontend:** `https://seu-app.vercel.app`
- **Banco:** PostgreSQL (Railway)
- **Variáveis:** Configuradas no painel (Railway/Vercel)

---

## 📚 Referências

- [Backend - Variáveis de Ambiente](./RAILWAY_VARIAVEIS_AMBIENTE.md)
- [Conectar Frontend e Backend](./CONECTAR_FRONTEND_BACKEND.md)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/)

---

## ✅ Checklist

- [ ] Arquivo `backend/.env` criado e configurado
- [ ] `SECRET_KEY` gerada e configurada
- [ ] `GROQ_API_KEY` configurada (se usar interpretações com IA)
- [ ] Arquivo `.env.local` criado na raiz do projeto
- [ ] `VITE_API_URL=http://localhost:8000` configurado
- [ ] Backend rodando em `http://localhost:8000`
- [ ] Frontend rodando e conectando ao backend
- [ ] Teste de login/cadastro funcionando

---

## 💡 Dicas

1. **Use valores diferentes para desenvolvimento e produção**
   - Nunca use a mesma `SECRET_KEY` em desenvolvimento e produção
   - Gere uma chave diferente para cada ambiente

2. **Mantenha os arquivos `.env` no `.gitignore`**
   - Já estão configurados para serem ignorados
   - Nunca commite credenciais

3. **Use scripts de inicialização**
   - `./scripts/start-backend.sh` para iniciar o backend
   - Facilita o desenvolvimento

4. **Verifique os logs**
   - Backend: logs aparecem no terminal
   - Frontend: console do navegador (F12)

