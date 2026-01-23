#!/usr/bin/env python3
"""
Script de migration pour sécuriser les mots de passe existants
Ce script hash les mots de passe en clair avec bcrypt
"""

from fifa1 import app, db
from models import User
from security import hash_password

def migrate_passwords():
    """Migration des mots de passe existants vers bcrypt"""
    with app.app_context():
        users = User.query.all()
        migrated = 0
        skipped = 0
        
        for user in users:
            # Vérifier si le mot de passe est déjà hashé (bcrypt commence par $2b$)
            if user.password.startswith('$2b$'):
                print(f"⏭️  {user.username}: déjà hashé")
                skipped += 1
                continue
            
            # Hasher le mot de passe
            old_password = user.password
            user.password = hash_password(old_password)
            db.session.commit()
            
            print(f"✅ {user.username}: mot de passe hashé")
            migrated += 1
        
        print(f"\n🎯 Migration terminée:")
        print(f"   ✅ Migrés: {migrated}")
        print(f"   ⏭️  Ignorés: {skipped}")
        print(f"   📊 Total: {len(users)} utilisateurs")

def create_secure_admin():
    """Créer un compte admin sécurisé"""
    with app.app_context():
        from security import create_admin_user
        
        admin = create_admin_user('ADMIN', 'ADMIN123', 'admin@oracxpred.com')
        print(f"✅ Admin sécurisé créé: {admin.username}")

if __name__ == "__main__":
    print("🔐 Migration de sécurité ORACXPRED")
    print("=" * 40)
    
    try:
        # Créer l'admin sécurisé
        create_secure_admin()
        
        # Migrer les mots de passe existants
        migrate_passwords()
        
        print("\n🚀 Sécurité activée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
