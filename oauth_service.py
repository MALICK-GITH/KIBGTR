# -*- coding: utf-8 -*-
"""
Service Google OAuth pour ORACXPRED MÉTAPHORE
Gère l'authentification sécurisée avec validation JWT
"""
import requests
import json
import jwt
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import uuid

from config_oauth import config
from models_oauth import db, User, AuditLog

class GoogleOAuthService:
    """Service OAuth 2.0 pour Google"""
    
    def __init__(self):
        self.client_id = config.GOOGLE_CLIENT_ID
        self.client_secret = config.GOOGLE_CLIENT_SECRET
        self.token_uri = config.GOOGLE_TOKEN_URI
        self.certs_url = config.GOOGLE_CERTS_URL
        self.redirect_uri = config.OAUTH_REDIRECT_URI
    
    def get_auth_url(self, state: str = None) -> str:
        """Génère l'URL d'authentification Google"""
        if not state:
            state = str(uuid.uuid4())
        
        return config.get_oauth_url(state)
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Échange le code d'autorisation contre des tokens"""
        data = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.post(self.token_uri, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Erreur échange token: {str(e)}")
    
    def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Vérifie et décode le ID token Google"""
        try:
            # Récupère les certificats Google
            certs_response = requests.get(self.certs_url)
            certs_response.raise_for_status()
            certs = certs_response.json()
            
            # Décode sans vérification d'abord pour obtenir le kid
            unverified_header = jwt.get_unverified_header(id_token)
            kid = unverified_header.get('kid')
            
            if not kid:
                raise Exception("Token sans kid (key ID)")
            
            # Trouve la clé publique correspondante
            key = None
            for cert_key in certs['keys']:
                if cert_key['kid'] == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(cert_key)
                    break
            
            if not key:
                raise Exception("Clé publique non trouvée")
            
            # Vérifie le token
            payload = jwt.decode(
                id_token,
                key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer='https://accounts.google.com'
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise Exception("Token expiré")
        except jwt.InvalidTokenError as e:
            raise Exception(f"Token invalide: {str(e)}")
        except Exception as e:
            raise Exception(f"Erreur vérification token: {str(e)}")
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Récupère les informations utilisateur depuis Google"""
        url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Erreur récupération infos utilisateur: {str(e)}")
    
    def authenticate_user(self, code: str, state: str = None) -> Dict[str, Any]:
        """Flux complet d'authentification OAuth"""
        try:
            # 1. Échanger le code contre des tokens
            tokens = self.exchange_code_for_tokens(code)
            id_token = tokens.get('id_token')
            access_token = tokens.get('access_token')
            
            if not id_token:
                raise Exception("ID token manquant")
            
            # 2. Vérifier le ID token
            token_payload = self.verify_id_token(id_token)
            
            # 3. Récupérer les infos utilisateur
            user_info = self.get_user_info(access_token)
            
            # 4. Créer/mettre à jour l'utilisateur
            user = self.create_or_update_user(token_payload, user_info)
            
            # 5. Logger l'authentification
            self.log_auth_event(user, 'login', {
                'provider': 'google',
                'state': state,
                'token_payload': token_payload
            })
            
            return {
                'user': user.to_dict(),
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': tokens.get('refresh_token'),
                    'expires_in': tokens.get('expires_in')
                }
            }
            
        except Exception as e:
            raise Exception(f"Échec authentification: {str(e)}")
    
    def create_or_update_user(self, token_payload: Dict, user_info: Dict) -> User:
        """Crée ou met à jour l'utilisateur en base"""
        email = user_info.get('email')
        google_sub = token_payload.get('sub')
        
        if not email:
            raise Exception("Email requis")
        
        # Recherche utilisateur existant
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Mise à jour utilisateur existant
            user.last_login = datetime.now(timezone.utc)
            if not user.username:
                user.username = user_info.get('name', email.split('@')[0])
            if not user.avatar_url:
                user.avatar_url = user_info.get('picture')
            if not user.provider_id:
                user.provider_id = google_sub
        else:
            # Création nouvel utilisateur
            user = User(
                email=email,
                username=user_info.get('name', email.split('@')[0]),
                avatar_url=user_info.get('picture'),
                provider='google',
                provider_id=google_sub,
                role='user',
                plan='free',
                status='actif'
            )
            db.session.add(user)
        
        db.session.commit()
        return user
    
    def log_auth_event(self, user: User, action: str, meta: Dict = None):
        """Enregistre un événement d'authentification"""
        from flask import request
        
        log = AuditLog(
            user_id=user.id,
            action=action,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None,
            meta=meta or {}
        )
        db.session.add(log)
        db.session.commit()

# Instance globale
oauth_service = GoogleOAuthService()
