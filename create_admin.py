#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer le premier utilisateur administrateur
"""
import sys
import os

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from app import app, db
from models import User
from datetime import datetime

def create_admin():
    """Crée le premier utilisateur admin"""
    with app.app_context():
        # Importer les fonctions de sécurité
        try:
            from security import hash_password, check_password, create_admin_user
            SECURITY_ENABLED = True
        except ImportError:
            SECURITY_ENABLED = False
            print("ATTENTION: Module de sécurité non disponible - mot de passe en clair")
        
        # Vérifier si l'admin existe déjà
        admin = User.query.filter_by(username='ADMIN').first()
        if admin:
            print("OK - L'utilisateur ADMIN existe deja (ID: {})".format(admin.id))
            
            # Vérifier et corriger le statut admin
            if not admin.is_admin:
                admin.is_admin = True
                admin.is_approved = True
                db.session.commit()
                print("OK - Statut admin active")
            
            # Vérifier et corriger le mot de passe (hash si nécessaire)
            if SECURITY_ENABLED:
                # Si le mot de passe n'est pas hashé, le hasher
                if not admin.password.startswith(('$2a$', '$2b$', '$2y$')):
                    print("OK - Hashage du mot de passe existant...")
                    admin.password = hash_password('ADMIN123')
                    db.session.commit()
                    print("OK - Mot de passe hashé avec succès")
                # Si le mot de passe est hashé mais incorrect, le réinitialiser
                elif not check_password('ADMIN123', admin.password):
                    print("OK - Réinitialisation du mot de passe...")
                    admin.password = hash_password('ADMIN123')
                    db.session.commit()
                    print("OK - Mot de passe réinitialisé")
            
            return admin
        
        # Créer le nouvel admin avec hashage du mot de passe
        if SECURITY_ENABLED:
            # Utiliser la fonction sécurisée
            admin = create_admin_user('ADMIN', 'ADMIN123', 'admin@oracxpred.com')
            print("OK - Utilisateur ADMIN cree avec succes (mot de passe hashé) !")
        else:
            # Mode compatibilité sans sécurité
            admin = User(
                username='ADMIN',
                email='admin@oracxpred.com',
                password='ADMIN123',
                is_admin=True,
                is_approved=True,
                subscription_plan='vip',
                subscription_status='active',
                created_at=datetime.utcnow()
            )
            db.session.add(admin)
            db.session.commit()
            print("OK - Utilisateur ADMIN cree avec succes (mode compatibilité) !")
        
        print("   Username: ADMIN")
        print("   Password: ADMIN123")
        print("   Statut: Administrateur")
        
        return admin

if __name__ == '__main__':
    print("Creation de l'utilisateur administrateur...")
    print("=" * 50)
    try:
        create_admin()
        print("=" * 50)
        print("Termine ! Vous pouvez maintenant vous connecter avec ADMIN / ADMIN123")
    except Exception as e:
        print("ERREUR: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        sys.exit(1)
