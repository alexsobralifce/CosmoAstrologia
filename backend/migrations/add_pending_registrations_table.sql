-- Migração: Criar tabela pending_registrations
-- Execute este script no banco de dados PostgreSQL de produção

-- Criar tabela pending_registrations
CREATE TABLE IF NOT EXISTS pending_registrations (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR,
    name VARCHAR,
    verification_code VARCHAR NOT NULL,
    verification_code_expires TIMESTAMP NOT NULL,
    birth_chart_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Criar índice no email para busca rápida
CREATE INDEX IF NOT EXISTS idx_pending_registrations_email ON pending_registrations(email);

-- Criar índice na expiração para limpeza automática futura
CREATE INDEX IF NOT EXISTS idx_pending_registrations_expires ON pending_registrations(verification_code_expires);

-- Verificar se a tabela foi criada
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'pending_registrations'
ORDER BY ordinal_position;

