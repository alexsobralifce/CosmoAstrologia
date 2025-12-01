# 🚀 Iniciar Serviços

Scripts para iniciar todos os serviços (Backend, RAG Service, Frontend).

## 📋 Scripts Disponíveis

### 1. `start_services.sh` (Shell - Recomendado)
Script shell completo com suporte a Docker Compose e modo manual.

**Uso:**
```bash
# Iniciar serviços
./start_services.sh start

# Ou simplesmente
./start_services.sh

# Parar serviços
./start_services.sh stop

# Reiniciar serviços
./start_services.sh restart

# Ver status
./start_services.sh status

# Ver logs
./start_services.sh logs rag-service
./start_services.sh logs backend
./start_services.sh logs frontend
```

---

### 2. `start_services.py` (Python)
Script Python alternativo com mais funcionalidades.

**Uso:**
```bash
# Iniciar serviços
python3 start_services.py start

# Parar serviços
python3 start_services.py stop

# Reiniciar
python3 start_services.py restart

# Status
python3 start_services.py status

# Logs
python3 start_services.py logs --service rag-service

# Forçar modo manual (sem Docker)
python3 start_services.py start --no-docker
```

---

## 🎯 Funcionalidades

### ✅ Modo Docker Compose (Recomendado)
- Inicia todos os serviços com `docker-compose up -d`
- Mais fácil de gerenciar
- Isolamento completo
- Logs centralizados

### ✅ Modo Manual
- Inicia cada serviço individualmente
- Útil para desenvolvimento
- Permite debug mais fácil
- Logs em `logs/`

### ✅ Gerenciamento
- **start** - Inicia todos os serviços
- **stop** - Para todos os serviços
- **restart** - Reinicia todos os serviços
- **status** - Mostra status dos serviços
- **logs** - Mostra logs de um serviço

---

## 📊 Serviços

### 1. RAG Service
- **Porta:** 8001
- **URL:** http://localhost:8001
- **Health:** http://localhost:8001/health

### 2. Backend
- **Porta:** 8000
- **URL:** http://localhost:8000
- **Health:** http://localhost:8000/

### 3. Frontend
- **Porta:** 5173 (Vite)
- **URL:** http://localhost:5173

---

## 🚀 Início Rápido

### Opção 1: Docker Compose (Recomendado)
```bash
# Iniciar tudo
./start_services.sh start

# Verificar status
./start_services.sh status

# Ver logs
./start_services.sh logs rag-service
```

### Opção 2: Manual
```bash
# Iniciar manualmente
./start_services.sh start
# Escolher 'n' quando perguntar sobre Docker Compose

# Ou forçar modo manual
python3 start_services.py start --no-docker
```

---

## 📝 Pré-requisitos

### Para Docker Compose:
- Docker instalado
- Docker Compose instalado
- Arquivo `docker-compose.yml` na raiz

### Para Modo Manual:
- Python 3.11+ (para Backend e RAG Service)
- Node.js e npm (para Frontend)
- Dependências instaladas:
  ```bash
  # Backend
  cd backend && pip install -r requirements.txt
  
  # RAG Service
  cd rag-service && pip install -r requirements.txt
  
  # Frontend
  npm install
  ```

---

## 🔍 Verificação

Após iniciar, verifique se os serviços estão rodando:

```bash
# Verificar status
./start_services.sh status

# Ou testar manualmente
curl http://localhost:8001/health  # RAG Service
curl http://localhost:8000/        # Backend
curl http://localhost:5173         # Frontend
```

---

## 🐛 Troubleshooting

### Porta já em uso
```bash
# Verificar qual processo está usando a porta
lsof -i :8001  # RAG Service
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# Parar processo
kill -9 <PID>
```

### Serviço não inicia
```bash
# Ver logs
./start_services.sh logs rag-service
./start_services.sh logs backend
./start_services.sh logs frontend

# Ou com Docker
docker-compose logs rag-service
docker-compose logs backend
```

### Docker Compose não funciona
```bash
# Verificar se está instalado
docker compose version
# ou
docker-compose --version

# Usar modo manual
./start_services.sh start
# Escolher 'n' quando perguntar
```

---

## 📚 Logs

### Docker Compose
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f rag-service
docker-compose logs -f backend
```

### Modo Manual
```bash
# Ver logs
tail -f logs/rag-service.log
tail -f logs/backend.log
tail -f logs/frontend.log

# Ou usar o script
./start_services.sh logs rag-service
```

---

## 🔗 Links Relacionados

- [Testar Serviços](./README_TESTES.md)
- [Docker Compose](./docker-compose.yml)
- [Documentação do Microsserviço RAG](./README_MICROSERVICO_RAG.md)

