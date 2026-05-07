CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(64) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(128) NOT NULL DEFAULT '',
    last_name VARCHAR(128) NOT NULL DEFAULT '',
    role VARCHAR(16) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT accounts_role_check CHECK (role IN ('user', 'admin'))
);

CREATE TABLE IF NOT EXISTS account_refresh_tokens (
    jti UUID PRIMARY KEY,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    token_hash CHAR(64) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_account_refresh_tokens_account_id
    ON account_refresh_tokens (account_id);

CREATE INDEX IF NOT EXISTS idx_account_refresh_tokens_expires_at
    ON account_refresh_tokens (expires_at);

INSERT INTO accounts (login, password_hash, first_name, last_name, role)
VALUES (
    'admin',
    '$argon2id$v=19$m=65536,t=3,p=4$Ifr1ZQ/5DxSzEi1Ij+JeRA$veqAn+AqkFYFqHg2R281uyBLB3PD96ixzt0d1xqMVmo',
    'System',
    'Admin',
    'admin'
)
ON CONFLICT (login) DO NOTHING;
