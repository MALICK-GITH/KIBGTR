# -*- coding: utf-8 -*-
"""
Gestion des sessions et JWT pour ORACXPRED MÉTAPHORE
Sessions sécurisées avec httpOnly cookies
"""
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from flask import current_app

from config_oauth import config

class SessionManager:
    """Gestionnaire de sessions JWT sécurisées"""
    
    def __init__(self):
        self.secret = config.APP_SECRET
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(hours=24)
        self.refresh_expiry = timedelta(days=7)
    
    def create_tokens(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Crée les tokens d'accès et de rafraîchissement"""
        now = datetime.now(timezone.utc)
        
        # Token d'accès (court)
        access_payload = {
            'user_id': str(user_data['id']),
            'email': user_data['email'],
            'role': user_data['role'],
            'plan': user_data['plan'],
            'type': 'access',
            'iat': now,
            'exp': now + self.token_expiry
        }
        
        # Token de rafraîchissement (long)
        refresh_payload = {
            'user_id': str(user_data['id']),
            'type': 'refresh',
            'iat': now,
            'exp': now + self.refresh_expiry
        }
        
        access_token = jwt.encode(access_payload, self.secret, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret, algorithm=self.algorithm)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(self.token_expiry.total_seconds()),
            'token_type': 'Bearer'
        }
    
    def verify_token(self, token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            
            # Vérifie le type de token
            if payload.get('type') != token_type:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Génère un nouveau token d'accès depuis le refresh token"""
        payload = self.verify_token(refresh_token, 'refresh')
        
        if not payload:
            return None
        
        # Récupère les infos utilisateur fraîches
        from models_oauth import User
        
        user = User.query.get(payload['user_id'])
        if not user or user.status != 'actif':
            return None
        
        # Crée nouveaux tokens
        return self.create_tokens(user.to_dict())
    
    def get_current_user(self, request) -> Optional[Dict[str, Any]]:
        """Extrait et vérifie l'utilisateur depuis la requête"""
        # Tente depuis l'en-tête Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = self.verify_token(token)
            if payload:
                return payload
        
        # Tente depuis les cookies
        token = request.cookies.get('access_token')
        if token:
            payload = self.verify_token(token)
            if payload:
                return payload
        
        return None
    
    def is_premium_user(self, user_payload: Dict[str, Any]) -> bool:
        """Vérifie si l'utilisateur a un plan premium"""
        plan = user_payload.get('plan', 'free')
        return plan in ['mensuel', '2mois', 'vip']
    
    def can_access_details(self, user_payload: Dict[str, Any]) -> bool:
        """Vérifie si l'utilisateur peut accéder aux détails"""
        return self.is_premium_user(user_payload)
    
    def get_daily_limit(self, user_payload: Dict[str, Any]) -> int:
        """Retourne la limite quotidienne de prédictions"""
        plan = user_payload.get('plan', 'free')
        limits = {
            'free': 3,
            'mensuel': -1,  # illimité
            '2mois': -1,
            'vip': -1
        }
        return limits.get(plan, 3)

# Instance globale
session_manager = SessionManager()
