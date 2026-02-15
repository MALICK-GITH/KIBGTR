#!/usr/bin/env python3
"""
Script de migration pour sécuriser les mots de passe existants
Ce script hash les mots de passe en clair avec bcrypt
"""

from app import app, db
from models import User
from security import hash_password

def migrate_passwords():
    """Migration des mots de passe existants vers bcrypt"""
    with app.app_context():
        users = User.query.all()
        migrated = 0
        skipped = 0
        fixed_admins = 0
        
        for user in users:
            # Corriger les admins
            if user.is_admin:
                needs_fix = False
                if not user.is_approved:
                    user.is_approved = True
                    needs_fix = True
                if user.subscription_plan != 'vip':
                    user.subscription_plan = 'vip'
                    needs_fix = True
                if user.subscription_status != 'active':
                    user.subscription_status = 'active'
                    needs_fix = True
                
                if needs_fix:
                    fixed_admins += 1
                    print(f"🔧 {user.username}: statut admin corrigé")
            
            # Vérifier si le mot de passe est déjà hashé (bcrypt commence par $2a$, $2b$, ou $2y$)
            if user.password.startswith(('$2a$', '$2b$', '$2y$')):
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
        print(f"   ✅ Mots de passe migrés: {migrated}")
        print(f"   🔧 Admins corrigés: {fixed_admins}")
        print(f"   ⏭️  Ignorés: {skipped}")
        print(f"   📊 Total: {len(users)} utilisateurs")

def create_secure_admin():
    """Créer ou corriger un compte admin sécurisé"""
    with app.app_context():
        from security import create_admin_user, hash_password, check_password
        
        # Vérifier si l'admin existe
        admin = User.query.filter_by(username='ADMIN').first()
        
        if admin:
            print(f"📝 Admin existant trouvé: {admin.username}")
            
            # Corriger le statut admin
            if not admin.is_admin:
                admin.is_admin = True
                print("   ✅ Statut admin activé")
            
            # Corriger l'approbation
            if not admin.is_approved:
                admin.is_approved = True
                print("   ✅ Compte approuvé")
            
            # Corriger le mot de passe (hash si nécessaire)
            if not admin.password.startswith(('$2a$', '$2b$', '$2y$')):
                print("   🔐 Hashage du mot de passe...")
                admin.password = hash_password('ADMIN123')
                print("   ✅ Mot de passe hashé")
            elif not check_password('ADMIN123', admin.password):
                print("   🔐 Réinitialisation du mot de passe...")
                admin.password = hash_password('ADMIN123')
                print("   ✅ Mot de passe réinitialisé")
            
            # S'assurer que l'admin a les bons privilèges
            if admin.subscription_plan != 'vip':
                admin.subscription_plan = 'vip'
                print("   ✅ Plan VIP activé")
            
            if admin.subscription_status != 'active':
                admin.subscription_status = 'active'
                print("   ✅ Statut d'abonnement activé")
            
            db.session.commit()
            print(f"✅ Admin corrigé: {admin.username}")
        else:
            # Créer un nouvel admin
            admin = create_admin_user('ADMIN', 'ADMIN123', 'admin@oracxpred.com')
            print(f"✅ Admin sécurisé créé: {admin.username}")
        
        return admin

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
