# ✅ Verificação: Google OAuth Configurado

## Status Atual

✅ **Backend configurado:**
- `GOOGLE_CLIENT_ID`: Configurado em `backend/.env`
- `GOOGLE_CLIENT_SECRET`: Configurado em `backend/.env`

✅ **Frontend configurado:**
- `VITE_GOOGLE_CLIENT_ID`: Adicionado ao `.env.local`

---

## 🔍 Como Verificar se Está Funcionando

### 1. Reiniciar Servidores

⚠️ **IMPORTANTE:** Variáveis de ambiente só são carregadas quando o servidor inicia!

**Frontend:**
```bash
# Parar o servidor (Ctrl+C)
# Reiniciar
npm run dev
```

**Backend:**
```bash
cd backend
# Parar o servidor (Ctrl+C)
# Reiniciar
python3 run.py
```

### 2. Verificar no Console do Navegador

1. Abra o DevTools (F12)
2. Vá na aba **Console**
3. Procure por mensagens:
   - ✅ `[AUTH] Google Identity Services inicializado e botão renderizado` = Funcionando!
   - ❌ `[AUTH] Google Identity Services não disponível` = Verificar configuração

### 3. Verificar o Botão do Google

**Com OAuth configurado:**
- O botão será renderizado automaticamente pelo Google Identity Services
- Terá o estilo oficial do Google
- Ao clicar, abre popup do Google (não modal simulado)

**Sem OAuth configurado:**
- Usa botão customizado (com ícone Chrome)
- Ao clicar, abre modal simulado para digitar email manualmente

### 4. Testar o Fluxo

1. Clique no botão **"Google"**
2. Deve abrir popup do Google (não modal simulado)
3. Faça login com sua conta Google
4. O sistema deve capturar seu email automaticamente
5. Verificar se redireciona corretamente (dashboard ou onboarding)

---

## 🔧 Troubleshooting

### Problema: "Modal simulado ainda aparece"

**Causa:** `VITE_GOOGLE_CLIENT_ID` não está sendo lido

**Solução:**
1. Verificar se `.env.local` tem `VITE_GOOGLE_CLIENT_ID`
2. **Reiniciar o servidor de desenvolvimento** (muito importante!)
3. Verificar se não há erros no console

### Problema: "Erro 400: redirect_uri_mismatch"

**Causa:** URL do frontend não está autorizada no Google Cloud Console

**Solução:**
1. Acesse: https://console.cloud.google.com/apis/credentials
2. Clique no seu OAuth Client ID
3. Adicione a URL do frontend em:
   - **Origens JavaScript autorizadas:** `http://localhost:3000`, `http://localhost:5173`
   - **URIs de redirecionamento autorizados:** Mesmas URLs
4. Salve e teste novamente

### Problema: "Erro ao verificar token"

**Causa:** Backend não está encontrando `GOOGLE_CLIENT_ID`

**Solução:**
1. Verificar se `backend/.env` tem `GOOGLE_CLIENT_ID`
2. Reiniciar o backend
3. Verificar logs do backend para mais detalhes

### Problema: "Google Identity Services não disponível"

**Causa:** Script do Google não está carregando

**Solução:**
1. Verificar se `index.html` tem o script:
   ```html
   <script src="https://accounts.google.com/gsi/client" async defer></script>
   ```
2. Verificar Network tab no DevTools se o script está carregando
3. Verificar se não há bloqueadores de popup/script

---

## 📋 Checklist de Verificação

- [ ] `backend/.env` tem `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET`
- [ ] `.env.local` tem `VITE_GOOGLE_CLIENT_ID`
- [ ] Frontend reiniciado após adicionar variável
- [ ] Backend reiniciado
- [ ] Console do navegador mostra "Google Identity Services inicializado"
- [ ] Botão do Google é renderizado pelo Google (não customizado)
- [ ] Popup do Google abre ao clicar (não modal simulado)
- [ ] Email é capturado automaticamente após login
- [ ] Sistema redireciona corretamente (dashboard ou onboarding)

---

## 🎉 Próximos Passos

Se tudo estiver funcionando:

1. **Testar em produção:**
   - Adicionar `VITE_GOOGLE_CLIENT_ID` no Vercel
   - Adicionar URLs de produção no Google Cloud Console
   - Fazer redeploy

2. **Monitorar logs:**
   - Console do navegador (frontend)
   - Terminal do backend
   - Google Cloud Console → Logs

3. **Testar com diferentes contas:**
   - Testar com contas diferentes
   - Verificar se onboarding funciona corretamente
   - Verificar se usuários existentes vão direto para dashboard

