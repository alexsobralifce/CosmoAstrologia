# 🔄 Migração: Colunas de Verificação de Email

## ⚠️ **PROBLEMA:**
O banco de dados PostgreSQL em produção não tem as colunas novas:
- `email_verified`
- `verification_code`
- `verification_code_expires`

## ✅ **SOLUÇÃO:**

### **Opção 1: Migração Automática (Recomendado)**

A migração será executada **automaticamente** na próxima inicialização do servidor.

**O que fazer:**
1. Faça um novo deploy no Railway
2. O servidor detectará as colunas faltantes e as criará automaticamente
3. Verifique os logs para confirmar: `[MIGRATION] Colunas de verificação adicionadas com sucesso!`

### **Opção 2: Migração Manual via SQL**

Se preferir executar manualmente:

1. **Acesse o PostgreSQL no Railway:**
   - Vá para o serviço PostgreSQL no Railway
   - Clique em "Query" ou use um cliente SQL

2. **Execute o SQL:**
   ```sql
   ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
   ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code TEXT;
   ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code_expires TIMESTAMP;
   ALTER TABLE users ALTER COLUMN is_active SET DEFAULT FALSE;
   UPDATE users SET email_verified = TRUE WHERE is_active = TRUE AND email_verified IS NULL;
   ```

3. **Verificar:**
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'users' 
   AND column_name IN ('email_verified', 'verification_code', 'verification_code_expires');
   ```

### **Opção 3: Script Python (Local ou Railway CLI)**

Se tiver acesso ao Railway CLI:

```bash
# Conectar ao serviço
railway connect

# Executar script de migração
cd backend
python scripts/migrate_email_verification.py
```

---

## 📋 **Verificação Pós-Migração:**

Após a migração, teste:

1. **Registro de novo usuário:**
   - Deve enviar email de verificação
   - Modal deve aparecer
   - Código deve funcionar

2. **Verificar logs:**
   - Não deve aparecer erro `column users.email_verified does not exist`
   - Deve aparecer `[MIGRATION] Colunas de verificação adicionadas com sucesso!`

---

## 🔍 **Troubleshooting:**

### Erro: "column already exists"
✅ **Normal** - A coluna já existe, pode ignorar.

### Erro: "permission denied"
⚠️ **Problema de permissão** - Verifique se o usuário do banco tem permissão ALTER TABLE.

### Erro: "relation users does not exist"
❌ **Problema crítico** - A tabela users não existe. Execute primeiro:
```sql
-- O SQLAlchemy deve criar automaticamente, mas se não criar:
-- Verifique se o modelo User está sendo importado corretamente
```

---

## ✅ **Status Esperado Após Migração:**

```sql
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('email_verified', 'verification_code', 'verification_code_expires');
```

**Resultado esperado:**
```
email_verified          | boolean | false
verification_code       | text    | null
verification_code_expires | timestamp without time zone | null
```

---

## 🚀 **Próximos Passos:**

1. ✅ Executar migração (automática ou manual)
2. ✅ Verificar se colunas foram criadas
3. ✅ Testar registro de novo usuário
4. ✅ Verificar se email de verificação é enviado
5. ✅ Testar fluxo completo de verificação

