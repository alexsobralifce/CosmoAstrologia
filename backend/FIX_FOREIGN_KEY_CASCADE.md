# 🔧 Correção: Foreign Key Constraint com CASCADE

## ❌ Problema

Ao tentar deletar usuários no PostgreSQL, ocorria o erro:

```
ERROR: update or delete on table "users" violates foreign key constraint "birth_charts_user_id_fkey" on table "birth_charts"
DETAIL: Key (id)=(X) is still referenced from table "birth_charts".
```

## ✅ Solução

A foreign key constraint `birth_charts_user_id_fkey` não tinha `ON DELETE CASCADE`, então o PostgreSQL impedia a deleção de usuários que tinham birth_charts associados.

### Correção Aplicada

1. **Modelo atualizado** (`backend/app/models/database.py`):
   ```python
   user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
   ```

2. **Migração automática** (`backend/app/main.py`):
   - O sistema detecta e corrige automaticamente na inicialização
   - Remove a constraint antiga e recria com `ON DELETE CASCADE`

3. **Script SQL manual** (`backend/migrations/fix_foreign_key_cascade.sql`):
   - Para executar manualmente se necessário

## 🔄 Como Aplicar

### Opção 1: Automático (Recomendado)

O sistema corrige automaticamente na próxima inicialização. Verifique os logs:

```
[MIGRATION] Corrigindo foreign key constraint para CASCADE...
[MIGRATION] ✅ Foreign key constraint corrigida com CASCADE!
```

### Opção 2: SQL Manual

Execute no PostgreSQL de produção:

```sql
-- Remover constraint antiga
ALTER TABLE birth_charts 
DROP CONSTRAINT IF EXISTS birth_charts_user_id_fkey;

-- Recriar constraint com CASCADE
ALTER TABLE birth_charts 
ADD CONSTRAINT birth_charts_user_id_fkey 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE CASCADE;
```

### Opção 3: Via Script

Execute o script de migração:

```bash
cd backend
railway connect  # ou use psql diretamente
psql $DATABASE_URL -f migrations/fix_foreign_key_cascade.sql
```

## ✅ Verificação

Para verificar se a constraint está correta:

```sql
SELECT 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.referential_constraints AS rc
  ON rc.constraint_name = tc.constraint_name
WHERE tc.table_name = 'birth_charts' 
  AND tc.constraint_type = 'FOREIGN KEY'
  AND kcu.column_name = 'user_id';
```

**Resultado esperado:** `delete_rule` deve ser `'CASCADE'`

## 📋 Resultado

Após a correção:
- ✅ Usuários podem ser deletados sem erro
- ✅ Birth charts são deletados automaticamente quando o usuário é deletado
- ✅ Não há mais violação de foreign key constraint

---

**Status:** ✅ Corrigido automaticamente na próxima inicialização do servidor

