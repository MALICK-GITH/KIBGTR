-- Migration initiale pour ORACXPRED MÉTAPHORE
-- PostgreSQL avec UUID et optimisations

-- Extension UUID pour PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    avatar_url VARCHAR(500),
    
    -- OAuth Provider
    provider VARCHAR(20) NOT NULL DEFAULT 'google',
    provider_id VARCHAR(100),
    
    -- Rôle et statut
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    plan VARCHAR(20) NOT NULL DEFAULT 'free',
    status VARCHAR(20) NOT NULL DEFAULT 'actif',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Index pour les utilisateurs
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_provider_id ON users(provider, provider_id);
CREATE INDEX IF NOT EXISTS idx_users_plan_status ON users(plan, status);

-- Table des abonnements
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    plan VARCHAR(20) NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Métadonnées paiement
    payment_method VARCHAR(50),
    payment_id VARCHAR(100),
    amount FLOAT
);

-- Index pour les abonnements
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(active);

-- Table d'audit
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    action VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    
    -- Métadonnées JSON
    meta JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index pour les logs d'audit
CREATE INDEX IF NOT EXISTS idx_audit_user_action ON audit_logs(user_id, action);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);

-- Table des prédictions
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    match_data JSONB NOT NULL,
    prediction JSONB NOT NULL,
    
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Index pour les prédictions
CREATE INDEX IF NOT EXISTS idx_predictions_user_status ON predictions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at);

-- Trigger pour mettre à jour last_login
CREATE OR REPLACE FUNCTION update_last_login()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND NEW.last_login IS DISTINCT FROM OLD.last_login) THEN
        UPDATE users 
        SET last_login = NEW.last_login 
        WHERE id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour les logs d'audit
CREATE TRIGGER trigger_update_last_login
    AFTER INSERT OR UPDATE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_last_login();

-- Insert admin user par défaut (adapter l'email)
INSERT INTO users (email, username, provider, role, plan, status)
VALUES (
    'admin@oracxpred.com',
    'admin',
    'local',
    'admin',
    'vip',
    'actif'
) ON CONFLICT (email) DO NOTHING;

-- Commentaires pour documentation
COMMENT ON TABLE users IS 'Utilisateurs avec auth OAuth et gestion des plans';
COMMENT ON TABLE subscriptions IS 'Abonnements et historique des plans payants';
COMMENT ON TABLE audit_logs IS 'Journal d''audit pour sécurité et conformité';
COMMENT ON TABLE predictions IS 'Historique des prédictions des utilisateurs';

COMMENT ON COLUMN users.provider IS 'OAuth provider: google, local';
COMMENT ON COLUMN users.provider_id IS 'ID unique du provider (sub pour Google)';
COMMENT ON COLUMN users.plan IS 'Plan: free, mensuel, 2mois, vip';
COMMENT ON COLUMN users.status IS 'Statut: actif, inactif';

COMMENT ON COLUMN audit_logs.action IS 'Action: login, logout, prediction_created, plan_changed';
COMMENT ON COLUMN audit_logs.meta IS 'Métadonnées JSON additionnelles';
