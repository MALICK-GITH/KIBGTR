# -*- coding: utf-8 -*-
"""
Configuration sécurisée pour ORACXPRED MÉTAPHORE
Gère les variables d'environnement et la validation
"""
import os
from typing import Optional
import sys

class ConfigError(Exception):
    """Erreur de configuration critique"""
    pass

class Config:
    """Configuration centralisée avec validation"""
    
    def __init__(self):
        self.validate_required_env()
        
    def validate_required_env(self):
        """Valide la présence des variables ENV obligatoires"""
        required_vars = {
            'GOOGLE_CLIENT_ID': 'Client ID Google OAuth requis',
            'GOOGLE_CLIENT_SECRET': 'Client Secret Google OAuth requis', 
            'GOOGLE_PROJECT_ID': 'Project ID Google requis',
            'APP_SECRET': 'Secret application requis pour JWT/sessions',
            'DATABASE_URL': 'URL de base de données PostgreSQL requis',
            'APP_BASE_URL': 'URL de base du backend requis',
            'FRONTEND_URL': 'URL du frontend requis'
        }
        
        missing_vars = []
        for var, message in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"❌ {var}: {message}")
        
        if missing_vars:
            error_msg = "\n".join(missing_vars)
            print(f"\n🚨 ERREUR CONFIGURATION CRITIQUE:\n{error_msg}\n")
            print("💡 Solution: Définissez ces variables dans .env ou dans votre dashboard d'hébergement")
            sys.exit(1)
    
    # --- Google OAuth ---
    @property
    def GOOGLE_CLIENT_ID(self) -> str:
        return os.getenv('GOOGLE_CLIENT_ID')
    
    @property
    def GOOGLE_CLIENT_SECRET(self) -> str:
        return os.getenv('GOOGLE_CLIENT_SECRET')
    
    @property
    def GOOGLE_PROJECT_ID(self) -> str:
        return os.getenv('GOOGLE_PROJECT_ID')
    
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
    
    @property
    def APP_BASE_URL(self) -> str:
        return os.getenv('APP_BASE_URL')
    
    @property
    def FRONTEND_URL(self) -> str:
        return os.getenv('FRONTEND_URL')
    
    @property
    def DATABASE_URL(self) -> str:
        return os.getenv('DATABASE_URL')
    
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
    
    # --- OAuth Scopes & Settings ---
    @property
    def GOOGLE_SCOPES(self) -> list:
        return [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
    
    @property
    def OAUTH_REDIRECT_URI(self) -> str:
        return f"{self.APP_BASE_URL}/api/auth/google/callback"
    
    def get_oauth_url(self, state: str) -> str:
        """Génère l'URL d'authentification Google OAuth"""
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

# Instance globale de configuration
config = Config()
