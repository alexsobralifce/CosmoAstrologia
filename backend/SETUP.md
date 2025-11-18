# Configuração do Backend

## Configurando a Chave da OpenAI para RAG

Para usar o sistema RAG (Retrieval-Augmented Generation) com interpretações avançadas, você precisa configurar sua chave da OpenAI.

### Passo 1: Criar arquivo .env

Na pasta `backend/`, crie um arquivo chamado `.env` (sem extensão). Você pode usar o arquivo de exemplo:

```bash
cd backend
cp .env.example .env
```

### Passo 2: Adicionar sua chave da OpenAI

Abra o arquivo `.env` e adicione sua chave da OpenAI:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

**Onde obter a chave:**
1. Acesse https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave gerada
5. Cole no arquivo `.env`

### Exemplo de arquivo .env completo:

```env
# OpenAI API Key para RAG
OPENAI_API_KEY=sk-proj-abc123xyz...

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# RAG Configuration (opcional - já tem valores padrão)
RAG_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# PDFs path
PDFS_PATH=../pdf
```

### ⚠️ Importante

- **NÃO** commite o arquivo `.env` no git (ele já está no `.gitignore`)
- Mantenha sua chave secreta e não a compartilhe
- Se não configurar a chave, o sistema usará interpretações fallback baseadas em regras

### Testando

Depois de configurar, reinicie o servidor backend:

```bash
python run.py
```

O sistema irá:
- Se tiver `OPENAI_API_KEY`: Usar GPT para interpretações avançadas
- Se não tiver: Usar interpretações fallback (ainda funcionará, mas menos detalhadas)

