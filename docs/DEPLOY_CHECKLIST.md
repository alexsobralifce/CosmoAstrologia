# ✅ Checklist de Deploy

Use este checklist antes de fazer push para produção.

## 🔐 Segurança

- [ ] `.env` e `.env.local` estão no `.gitignore`
- [ ] `backend/.env` está no `.gitignore`
- [ ] `SECRET_KEY` foi gerado e não é o padrão
- [ ] Nenhuma chave de API está hardcoded no código
- [ ] Variáveis sensíveis estão apenas em variáveis de ambiente

## 📝 Arquivos de Configuração

- [ ] `.env.example` criado na raiz
- [ ] `backend/.env.example` criado
- [ ] `vercel.json` configurado corretamente
- [ ] `package.json` tem scripts de build
- [ ] `.gitignore` atualizado

## 🌐 Variáveis de Ambiente - Produção

### Vercel (Frontend)
- [ ] `VITE_API_URL` configurado (URL do backend em produção)
- [ ] `VITE_GOOGLE_CLIENT_ID` configurado

### Railway (Backend)
- [ ] `DATABASE_URL` configurado (PostgreSQL do Railway)
- [ ] `SECRET_KEY` configurado (gerado aleatoriamente)
- [ ] `CORS_ORIGINS` configurado (URL do frontend Vercel)
- [ ] `GOOGLE_CLIENT_ID` configurado
- [ ] `GOOGLE_CLIENT_SECRET` configurado
- [ ] `GROQ_API_KEY` configurado (opcional mas recomendado)

## 🧪 Testes Locais

- [ ] Frontend roda localmente sem erros
- [ ] Backend roda localmente sem erros
- [ ] Autenticação funciona localmente
- [ ] API endpoints respondem corretamente
- [ ] Build do frontend funciona (`npm run build`)

## 📦 Deploy

- [ ] Código commitado e pushado para `main`
- [ ] Vercel conectado ao repositório GitHub
- [ ] Railway conectado ao repositório GitHub
- [ ] Deploy automático configurado
- [ ] Primeiro deploy bem-sucedido

## ✅ Pós-Deploy

- [ ] Frontend acessível e funcionando
- [ ] Backend respondendo em `/`
- [ ] Autenticação funcionando em produção
- [ ] CORS configurado corretamente
- [ ] Logs sem erros críticos
- [ ] Teste de registro de usuário
- [ ] Teste de login
- [ ] Teste de Google OAuth (se configurado)

## 🔄 Manutenção

- [ ] Documentação atualizada
- [ ] CHANGELOG.md atualizado
- [ ] README.md atualizado
- [ ] DEPLOY.md revisado

## 📚 Documentação

- [ ] DEPLOY.md criado e completo
- [ ] README.md atualizado
- [ ] Arquivos .env.example criados
- [ ] Comentários no código quando necessário

