-- Migração: Adicionar colunas de verificação de email
-- Execute este script no banco de dados PostgreSQL de produção

-- Adicionar coluna email_verified
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;

-- Adicionar coluna verification_code
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS verification_code TEXT;

-- Adicionar coluna verification_code_expires
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS verification_code_expires TIMESTAMP;

-- Atualizar is_active para ter default FALSE (usuários não verificados não devem estar ativos)
ALTER TABLE users 
ALTER COLUMN is_active SET DEFAULT FALSE;

-- Atualizar usuários existentes para ter email_verified = true (se já estavam ativos)
UPDATE users 
SET email_verified = TRUE 
WHERE is_active = TRUE AND email_verified IS NULL;

-- Verificar se as colunas foram criadas
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('email_verified', 'verification_code', 'verification_code_expires')
ORDER BY column_name;

