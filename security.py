"""
Module de sécurité pour ORACXPRED - Hashage des mots de passe avec bcrypt
"""

import bcrypt
from flask import current_app

def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        Mot de passe hashé
    """
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    # Générer un sel et hasher le mot de passe
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    
    return hashed.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe correspond au hash
    
    Args:
        password: Mot de passe en clair à vérifier
        hashed_password: Mot de passe hashé stocké en base
        
    Returns:
        True si le mot de passe est correct, False sinon
    """
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password, hashed_password)

def create_admin_user(username: str, password: str, email: str = None):
    """
    Crée un utilisateur admin avec mot de passe hashé
    
    Args:
        username: Nom d'utilisateur admin
        password: Mot de passe
        email: Email optionnel
        
    Returns:
        User object créé
    """
    from models import User, db
    
    # Vérifier si l'admin existe déjà
    existing_admin = User.query.filter_by(username=username).first()
    if existing_admin:
        return existing_admin
    
    # Hasher le mot de passe
    hashed_password = hash_password(password)
    
    # Créer l'admin
    admin = User(
        username=username,
        email=email or f"{username}@oracxpred.com",
        password=hashed_password,
        is_admin=True,
        is_approved=True,
        subscription_plan='vip',
        subscription_status='active'
    )
    
    db.session.add(admin)
    db.session.commit()
    
    return admin
