# Testes TDD - Todos os Tipos de Login do Sistema

## 📋 Resumo

**Arquivo:** `backend/tests/unit/test_auth_login.py`  
**Total de Testes:** 22 testes  
**Status:** ✅ Criados e Prontos para Execução

---

## 🎯 Tipos de Login Testados

### 1. **Registro com E-mail e Senha** (POST /api/auth/register)
- ✅ Registro de novo usuário
- ✅ E-mail duplicado retorna erro
- ✅ E-mail inválido retorna erro
- ✅ Criação automática de mapa astral

### 2. **Login Tradicional** (POST /api/auth/login)
- ✅ Login com credenciais corretas
- ✅ Usuário não encontrado (404)
- ✅ Senha incorreta (401)
- ✅ Conta sem senha (Google) retorna erro apropriado
- ✅ Login case-insensitive (maiúsculas/minúsculas)

### 3. **Verificação de Token Google** (POST /api/auth/google/verify)
- ✅ Verificação de token válido
- ✅ Formato inválido retorna erro
- ✅ Credential faltando retorna erro

### 4. **Login/Registro com Google OAuth** (POST /api/auth/google)
- ✅ Novo usuário via Google
- ✅ Usuário existente com mapa astral
- ✅ Usuário existente sem mapa astral
- ✅ Case-insensitive para e-mail

### 5. **Segurança**
- ✅ Token JWT contém e-mail correto
- ✅ Senha armazenada com hash (não texto plano)
- ✅ Token inválido não autentica
- ✅ Token expirado não funciona

### 6. **Fluxos Completos**
- ✅ Fluxo completo registro → login → acesso
- ✅ Usuário Google não pode fazer login com senha

---

## 📊 Estrutura dos Testes

### TestEmailPasswordRegistration (4 testes)
Testa o endpoint de registro:
- `test_register_new_user_success` - Registro bem-sucedido
- `test_register_duplicate_email_returns_400` - E-mail duplicado
- `test_register_invalid_email_format` - E-mail inválido
- `test_register_creates_birth_chart` - Criação de mapa astral

### TestEmailPasswordLogin (5 testes)
Testa o endpoint de login:
- `test_login_success_with_correct_credentials` - Login bem-sucedido
- `test_login_user_not_found_returns_404` - Usuário não encontrado
- `test_login_wrong_password_returns_401` - Senha incorreta
- `test_login_user_without_password_returns_401` - Conta sem senha
- `test_login_case_insensitive_email` - Case-insensitive

### TestGoogleTokenVerification (3 testes)
Testa verificação de token Google:
- `test_verify_google_token_success` - Token válido
- `test_verify_google_token_invalid_format` - Formato inválido
- `test_verify_google_token_missing_credential` - Credential faltando

### TestGoogleOAuthLogin (4 testes)
Testa login/registro com Google:
- `test_google_auth_new_user_success` - Novo usuário
- `test_google_auth_existing_user_with_birth_chart` - Usuário com mapa
- `test_google_auth_existing_user_without_birth_chart` - Usuário sem mapa
- `test_google_auth_case_insensitive_email` - Case-insensitive

### TestAuthenticationSecurity (4 testes)
Testa aspectos de segurança:
- `test_jwt_token_contains_correct_email` - Token contém e-mail
- `test_password_is_hashed_not_plain_text` - Senha com hash
- `test_invalid_token_returns_none_in_get_current_user` - Token inválido
- `test_expired_token_should_not_work` - Token expirado

### TestCompleteAuthFlow (2 testes)
Testa fluxos completos:
- `test_complete_register_and_login_flow` - Fluxo completo
- `test_google_auth_then_email_login_fails` - Google não pode login com senha

---

## 🔧 Fixtures Criadas

### `client`
Cliente de teste FastAPI para fazer requisições HTTP.

### `sample_user_data`
Dados de exemplo para criação de usuário com:
- E-mail
- Senha
- Nome
- Dados de nascimento completos

### `db_session`
Sessão de banco de dados para testes (se necessário).

---

## ✅ Casos de Teste Cobertos

### Casos de Sucesso
- ✅ Registro de novo usuário
- ✅ Login com credenciais corretas
- ✅ Verificação de token Google
- ✅ Autenticação Google (novo e existente)

### Casos de Erro
- ✅ E-mail duplicado
- ✅ E-mail inválido
- ✅ Usuário não encontrado
- ✅ Senha incorreta
- ✅ Conta sem senha
- ✅ Token inválido/expirado

### Validações de Segurança
- ✅ Senha armazenada com hash
- ✅ Token JWT válido
- ✅ Case-insensitive para e-mails
- ✅ Isolamento entre Google e senha

### Integrações
- ✅ Criação automática de mapa astral
- ✅ Fluxo completo de autenticação
- ✅ Verificação de onboarding necessário

---

## 🚀 Como Executar

```bash
cd backend
source venv/bin/activate

# Executar todos os testes de autenticação
pytest tests/unit/test_auth_login.py -v

# Executar apenas testes críticos
pytest tests/unit/test_auth_login.py -v -m critical

# Executar apenas testes de segurança
pytest tests/unit/test_auth_login.py -v -m security

# Executar apenas testes de autenticação
pytest tests/unit/test_auth_login.py -v -m auth

# Executar apenas testes de integração
pytest tests/unit/test_auth_login.py -v -m integration
```

---

## 📝 Observações Importantes

### Limpeza de Dados
Os testes fazem limpeza automática de usuários criados durante os testes para evitar conflitos.

### Mock de Token Google
O teste de verificação de token Google usa um token mockado (não valida com Google real), apenas testa a decodificação.

### Isolamento
Cada teste é independente e pode ser executado isoladamente.

---

## ✅ Checklist de Cobertura

- [x] Registro com e-mail e senha
- [x] Login tradicional
- [x] Verificação de token Google
- [x] Login/Registro com Google OAuth
- [x] Validações de segurança
- [x] Casos de erro
- [x] Fluxos completos
- [x] Case-insensitive
- [x] Hash de senhas
- [x] Tokens JWT

---

**Data de Criação:** 30/11/2025  
**Status:** ✅ Testes Criados e Prontos para Execução

