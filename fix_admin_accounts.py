#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour diagnostiquer et corriger les comptes admin
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

def diagnose_admins():
    """Diagnostique les comptes admin"""
    with app.app_context():
        print("🔍 DIAGNOSTIC DES COMPTES ADMIN")
        print("=" * 50)
        
        # Trouver tous les admins
        admins = User.query.filter_by(is_admin=True).all()
        
        if not admins:
            print("❌ Aucun compte admin trouvé!")
            return False
        
        print(f"📊 {len(admins)} compte(s) admin trouvé(s)\n")
        
        all_ok = True
        for admin in admins:
            print(f"👤 Admin: {admin.username}")
            print(f"   ID: {admin.id}")
            print(f"   Email: {admin.email}")
            print(f"   is_admin: {admin.is_admin}")
            print(f"   is_approved: {admin.is_approved}")
            print(f"   Plan: {admin.subscription_plan}")
            print(f"   Statut: {admin.subscription_status}")
            
            # Vérifier le mot de passe
            try:
                from security import is_bcrypt_hash
                if is_bcrypt_hash(admin.password):
                    print(f"   🔐 Mot de passe: Hashé (bcrypt)")
                else:
                    print(f"   ⚠️  Mot de passe: NON hashé (en clair)")
                    all_ok = False
            except:
                print(f"   ⚠️  Impossible de vérifier le hash du mot de passe")
            
            # Vérifier les problèmes
            issues = []
            if not admin.is_approved:
                issues.append("❌ Compte non approuvé")
                all_ok = False
            if admin.subscription_plan != 'vip':
                issues.append(f"⚠️  Plan: {admin.subscription_plan} (devrait être 'vip')")
            if admin.subscription_status != 'active':
                issues.append(f"⚠️  Statut: {admin.subscription_status} (devrait être 'active')")
            
            if issues:
                print(f"   Problèmes détectés:")
                for issue in issues:
                    print(f"      {issue}")
            else:
                print(f"   ✅ Aucun problème détecté")
            
            print()
        
        return all_ok

def fix_admins():
    """Corrige tous les comptes admin"""
    with app.app_context():
        print("🔧 CORRECTION DES COMPTES ADMIN")
        print("=" * 50)
        
        try:
            from security import hash_password, check_password, create_admin_user
            SECURITY_ENABLED = True
        except ImportError:
            SECURITY_ENABLED = False
            print("⚠️  Module de sécurité non disponible")
        
        # Trouver tous les admins
        admins = User.query.filter_by(is_admin=True).all()
        
        if not admins:
            print("❌ Aucun compte admin trouvé!")
            print("📝 Création d'un nouveau compte admin...")
            if SECURITY_ENABLED:
                admin = create_admin_user('ADMIN', 'ADMIN123', 'admin@oracxpred.com')
                print(f"✅ Admin créé: {admin.username}")
            else:
                from datetime import datetime
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
                print(f"✅ Admin créé: {admin.username}")
            return True
        
        fixed = 0
        for admin in admins:
            print(f"\n🔧 Correction de {admin.username}...")
            needs_commit = False
            
            # Corriger is_approved
            if not admin.is_approved:
                admin.is_approved = True
                needs_commit = True
                print("   ✅ is_approved = True")
            
            # Corriger le plan
            if admin.subscription_plan != 'vip':
                admin.subscription_plan = 'vip'
                needs_commit = True
                print(f"   ✅ subscription_plan = 'vip'")
            
            # Corriger le statut
            if admin.subscription_status != 'active':
                admin.subscription_status = 'active'
                needs_commit = True
                print(f"   ✅ subscription_status = 'active'")
            
            # Corriger le mot de passe si nécessaire
            if SECURITY_ENABLED:
                # Vérifier si le mot de passe est hashé
                if not admin.password.startswith(('$2a$', '$2b$', '$2y$')):
                    print("   🔐 Hashage du mot de passe...")
                    admin.password = hash_password('ADMIN123')
                    needs_commit = True
                    print("   ✅ Mot de passe hashé")
                # Vérifier si le mot de passe hashé fonctionne
                elif not check_password('ADMIN123', admin.password):
                    print("   🔐 Réinitialisation du mot de passe...")
                    admin.password = hash_password('ADMIN123')
                    needs_commit = True
                    print("   ✅ Mot de passe réinitialisé")
            
            if needs_commit:
                db.session.commit()
                fixed += 1
                print(f"   ✅ {admin.username} corrigé avec succès")
            else:
                print(f"   ✅ {admin.username} était déjà correct")
        
        print(f"\n🎯 Correction terminée: {fixed} admin(s) corrigé(s)")
        return True

if __name__ == '__main__':
    print("🛡️  OUTIL DE DIAGNOSTIC ET CORRECTION ADMIN")
    print("=" * 50)
    print()
    
    try:
        # Diagnostic
        all_ok = diagnose_admins()
        
        if not all_ok:
            print("\n" + "=" * 50)
            response = input("\n❓ Voulez-vous corriger les problèmes détectés? (o/n): ")
            if response.lower() in ['o', 'oui', 'y', 'yes']:
                print()
                fix_admins()
            else:
                print("❌ Correction annulée")
        else:
            print("\n✅ Tous les comptes admin sont corrects!")
            print("\n💡 Pour tester la connexion:")
            print("   1. Démarrez l'application: python app.py")
            print("   2. Allez sur: http://localhost:5000/admin/login")
            print("   3. Connectez-vous avec: ADMIN / ADMIN123")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
