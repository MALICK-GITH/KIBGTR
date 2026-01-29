# -*- coding: utf-8 -*-
"""
Configuration Render pour ORACXPRED MÉTAPHORE
Adaptée spécifiquement pour l'environnement Render
"""
import os
from typing import Optional
import sys

class RenderConfigError(Exception):
    """Erreur de configuration Render"""
    pass

class RenderConfig:
    """Configuration spécifique Render avec validation"""
    
    def __init__(self):
        self.validate_render_environment()
        
    def validate_render_environment(self):
        """Valide l'environnement Render"""
        required_vars = {
            'DATABASE_URL': 'URL de base de données Render requis',
            'GOOGLE_CLIENT_ID': 'Client ID Google OAuth requis',
            'GOOGLE_CLIENT_SECRET': 'Client Secret Google OAuth requis',
            'APP_SECRET': 'Secret application requis',
            'RENDER_SERVICE_NAME': 'Nom du service Render requis',
            'RENDER_EXTERNAL_URL': 'URL externe Render requis'
        }
        
        missing_vars = []
        for var, message in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"❌ {var}: {message}")
        
        if missing_vars:
            error_msg = "\n".join(missing_vars)
            print(f"\n🚨 ERREUR CONFIGURATION RENDER:\n{error_msg}\n")
            print("💡 Solution: Définissez ces variables dans le dashboard Render → Environment")
            sys.exit(1)
    
    # --- URLs Render ---
    @property
    def APP_BASE_URL(self) -> str:
        """URL de base du service Render"""
        return os.getenv('RENDER_EXTERNAL_URL', 'https://oracxpred-metaphore.onrender.com')
    
    @property
    def FRONTEND_URL(self) -> str:
        """URL du frontend (à configurer)"""
        return os.getenv('FRONTEND_URL', self.APP_BASE_URL)
    
    @property
    def OAUTH_REDIRECT_URI(self) -> str:
        """URL de callback OAuth pour Render"""
        return f"{self.APP_BASE_URL}/api/auth/google/callback"
    
    # --- Database Render ---
    @property
    def DATABASE_URL(self) -> str:
        """URL de base de données Render PostgreSQL"""
        return os.getenv('DATABASE_URL')
    
    @property
    def DB_POOL_SIZE(self) -> int:
        """Taille du pool de connexions pour Render"""
        return int(os.getenv('DB_POOL_SIZE', '10'))
    
    @property
    def DB_MAX_OVERFLOW(self) -> int:
        """Overflow maximum pour le pool"""
        return int(os.getenv('DB_MAX_OVERFLOW', '20'))
    
    # --- Service Render ---
    @property
    def RENDER_SERVICE_NAME(self) -> str:
        """Nom du service Render"""
        return os.getenv('RENDER_SERVICE_NAME', 'oracxpred-metaphore')
    
    @property
    def RENDER_INSTANCE_ID(self) -> str:
        """ID de l'instance Render"""
        return os.getenv('RENDER_INSTANCE_ID', 'unknown')
    
    # --- Backup Configuration ---
    @property
    def BACKUP_ENABLED(self) -> bool:
        """Active ou non les backups automatiques"""
        return os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
    
    @property
    def BACKUP_SCHEDULE(self) -> str:
        """Schedule des backups (cron)"""
        return os.getenv('BACKUP_SCHEDULE', '0 3 * * *')  # 3h UTC quotidien
    
    @property
    def BACKUP_RETENTION_DAYS(self) -> int:
        """Rétention des backups en jours"""
        return int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
    
    # --- Google OAuth (hérité) ---
    @property
    def GOOGLE_CLIENT_ID(self) -> str:
        return os.getenv('GOOGLE_CLIENT_ID')
    
    @property
    def GOOGLE_CLIENT_SECRET(self) -> str:
        return os.getenv('GOOGLE_CLIENT_SECRET')
    
    @property
    def GOOGLE_PROJECT_ID(self) -> str:
        return os.getenv('GOOGLE_PROJECT_ID', 'black-resource-485505-v9')
    
    @property
    def GOOGLE_AUTH_URI(self) -> str:
        return os.getenv('GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth')
    
    @property
    def GOOGLE_TOKEN_URI(self) -> str:
        return os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token')
    
    @property
    def GOOGLE_CERTS_URL(self) -> str:
        return os.getenv('GOOGLE_CERTS_URL', 'https://www.googleapis.com/oauth2/v1/certs')
    
    # --- Application ---
    @property
    def APP_SECRET(self) -> str:
        return os.getenv('APP_SECRET')
    
    # --- Security ---
    @property
    def SESSION_COOKIE_SECURE(self) -> bool:
        return os.getenv('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
    
    @property
    def SESSION_COOKIE_HTTPONLY(self) -> bool:
        return os.getenv('SESSION_COOKIE_HTTPONLY', 'true').lower() == 'true'
    
    @property
    def SESSION_COOKIE_SAMESITE(self) -> str:
        return os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    
    @property
    def CORS_ORIGINS(self) -> list:
        origins = os.getenv('CORS_ORIGINS', self.FRONTEND_URL)
        return [origin.strip() for origin in origins.split(',')]
    
    # --- Environment ---
    @property
    def FLASK_ENV(self) -> str:
        return os.getenv('FLASK_ENV', 'production')
    
    @property
    def FLASK_DEBUG(self) -> bool:
        return os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    @property
    def PYTHON_VERSION(self) -> str:
        return os.getenv('PYTHON_VERSION', '3.12')
    
    @property
    def PORT(self) -> int:
        return int(os.getenv('PORT', '10000'))
    
    # --- OAuth Scopes & Settings ---
    @property
    def GOOGLE_SCOPES(self) -> list:
        return [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
    
    def get_oauth_url(self, state: str) -> str:
        """Génère l'URL d'authentification Google OAuth pour Render"""
        params = {
            'client_id': self.GOOGLE_CLIENT_ID,
            'redirect_uri': self.OAUTH_REDIRECT_URI,
            'scope': ' '.join(self.GOOGLE_SCOPES),
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.GOOGLE_AUTH_URI}?{param_string}"
    
    def get_render_info(self) -> dict:
        """Retourne les informations sur l'environnement Render"""
        return {
            'service_name': self.RENDER_SERVICE_NAME,
            'instance_id': self.RENDER_INSTANCE_ID,
            'base_url': self.APP_BASE_URL,
            'database_configured': bool(self.DATABASE_URL),
            'backup_enabled': self.BACKUP_ENABLED,
            'backup_schedule': self.BACKUP_SCHEDULE,
            'environment': 'Render',
            'signature': 'Signé SOLITAIRE HACK 🇨🇮'
        }

# Instance globale pour Render
render_config = RenderConfig()
