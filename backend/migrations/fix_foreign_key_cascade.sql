-- Migração: Adicionar CASCADE na foreign key birth_charts_user_id_fkey
-- Execute este script no banco de dados PostgreSQL de produção

-- Remover constraint antiga
ALTER TABLE birth_charts 
DROP CONSTRAINT IF EXISTS birth_charts_user_id_fkey;

-- Recriar constraint com CASCADE
ALTER TABLE birth_charts 
ADD CONSTRAINT birth_charts_user_id_fkey 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE CASCADE;

-- Verificar se foi criada corretamente
SELECT 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
  ON rc.constraint_name = tc.constraint_name
WHERE tc.table_name = 'birth_charts' 
  AND tc.constraint_type = 'FOREIGN KEY'
  AND kcu.column_name = 'user_id';

-- Resultado esperado: delete_rule deve ser 'CASCADE'

