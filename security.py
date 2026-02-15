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

def is_bcrypt_hash(password_hash: str) -> bool:
    """
    Vérifie si un mot de passe est déjà hashé avec bcrypt
    
    Args:
        password_hash: Hash à vérifier
        
    Returns:
        True si c'est un hash bcrypt, False sinon
    """
    if not isinstance(password_hash, str):
        return False
    
    # Les hashes bcrypt commencent par $2a$, $2b$, ou $2y$ et font 60 caractères
    return (password_hash.startswith(('$2a$', '$2b$', '$2y$')) and 
            len(password_hash) == 60)

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
        hashed_password_bytes = hashed_password.encode('utf-8')
    else:
        hashed_password_bytes = hashed_password
    
    # Si c'est un hash bcrypt, utiliser bcrypt
    if is_bcrypt_hash(hashed_password):
        try:
            return bcrypt.checkpw(password, hashed_password_bytes)
        except (ValueError, TypeError):
            return False
    else:
        # Sinon, comparaison directe (mot de passe en clair)
        try:
            return password.decode('utf-8') == hashed_password
        except:
            return password == hashed_password_bytes

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
