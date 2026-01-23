#!/usr/bin/env python3
"""
Script de gestion complète de la persistance pour ORACXPRED
Permet de gérer les backups, migrations et récupérations
"""

import os
import sys
import argparse
from pathlib import Path

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from persistence_manager import DatabaseManager, db_manager
from models import db, User, SystemLog

def show_status():
    """Affiche le statut actuel du système de persistance"""
    print("📊 STATUT DU SYSTÈME DE PERSISTANCE")
    print("=" * 50)
    
    # Vérifier l'intégrité
    is_valid, message = db_manager.verify_database_integrity()
    status = "✅" if is_valid else "❌"
    print(f"{status} Intégrité: {message}")
    
    # Statistiques
    stats = db_manager.get_database_stats()
    if stats:
        print(f"📁 Base de données: {stats['path']}")
        print(f"💾 Taille: {stats['size_mb']} MB")
        print(f"📅 Dernière modification: {stats['modified']}")
        print(f"📋 Tables: {len(stats['tables'])}")
        
        for table, count in stats['tables'].items():
            print(f"   📊 {table}: {count} enregistrements")
    
    # Backups disponibles
    backups = db_manager.list_backups()
    print(f"💾 Backups disponibles: {len(backups)}")
    
    if backups:
        print("   📋 Derniers backups:")
        for i, backup in enumerate(backups[:3]):
            print(f"   {i+1}. {backup['name']} ({backup['created'].strftime('%d/%m/%Y %H:%M')})")

def create_backup():
    """Crée un backup manuel"""
    print("💾 CRÉATION D'UN BACKUP MANUEL")
    print("=" * 30)
    
    success = db_manager.create_backup()
    if success:
        print("✅ Backup créé avec succès!")
        
        # Afficher les backups récents
        backups = db_manager.list_backups()
        if backups:
            print(f"📋 Dernier backup: {backups[0]['name']}")
    else:
        print("❌ Échec de la création du backup")

def list_backups():
    """Liste tous les backups disponibles"""
    print("📋 LISTE DES BACKUPS DISPONIBLES")
    print("=" * 40)
    
    backups = db_manager.list_backups()
    
    if not backups:
        print("❌ Aucun backup disponible")
        return
    
    for i, backup in enumerate(backups, 1):
        size_mb = backup['size'] / (1024 * 1024)
        print(f"{i:2d}. 📁 {backup['name']}")
        print(f"     📅 Créé: {backup['created'].strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"     💾 Taille: {size_mb:.2f} MB")
        
        if backup.get('metadata', {}).get('backup_time'):
            print(f"     ℹ️  Backup: {backup['metadata']['backup_time']}")
        
        print()

def restore_backup():
    """Restaure un backup"""
    print("🔄 RESTAURATION D'UN BACKUP")
    print("=" * 30)
    
    backups = db_manager.list_backups()
    
    if not backups:
        print("❌ Aucun backup disponible pour la restauration")
        return
    
    print("Backups disponibles:")
    for i, backup in enumerate(backups, 1):
        print(f"{i:2d}. {backup['name']} ({backup['created'].strftime('%d/%m/%Y %H:%M')})")
    
    try:
        choice = int(input("\nChoisissez le backup à restaurer (numéro): ")) - 1
        if 0 <= choice < len(backups):
            backup_name = backups[choice]['name']
            
            confirm = input(f"Confirmer la restauration de '{backup_name}' ? (o/N): ")
            if confirm.lower() in ['o', 'oui', 'yes']:
                success = db_manager.restore_backup(backup_name)
                if success:
                    print("✅ Backup restauré avec succès!")
                else:
                    print("❌ Échec de la restauration")
            else:
                print("❌ Restauration annulée")
        else:
            print("❌ Choix invalide")
    except ValueError:
        print("❌ Entrée invalide")

def cleanup_backups():
    """Nettoie les anciens backups"""
    print("🗑️ NETTOYAGE DES ANCIENS BACKUPS")
    print("=" * 35)
    
    try:
        days = int(input("Nombre de jours de backups à conserver (défaut: 7): ") or "7")
        db_manager.cleanup_old_backups(days)
    except ValueError:
        print("❌ Nombre de jours invalide")

def export_data():
    """Exporte les données au format JSON"""
    print("📤 EXPORT DES DONNÉES")
    print("=" * 25)
    
    try:
        from fifa1 import app
        
        with app.app_context():
            # Exporter les utilisateurs
            users_data = []
            users = User.query.all()
            for user in users:
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin,
                    'is_approved': user.is_approved,
                    'subscription_plan': user.subscription_plan,
                    'subscription_status': user.subscription_status,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
                })
            
            # Exporter les logs système
            logs_data = []
            logs = SystemLog.query.all()
            for log in logs:
                logs_data.append({
                    'id': log.id,
                    'action': log.action,
                    'details': log.details,
                    'severity': log.severity,
                    'created_at': log.created_at.isoformat() if log.created_at else None,
                    'user_id': log.user_id,
                    'admin_id': log.admin_id
                })
            
            export_data = {
                'export_time': db_manager.verify_database_integrity()[1],
                'users': users_data,
                'system_logs': logs_data,
                'total_users': len(users_data),
                'total_logs': len(logs_data)
            }
            
            # Sauvegarder dans un fichier
            from datetime import datetime
            filename = f"oracxpred_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Export réussi: {filename}")
            print(f"📊 {len(users_data)} utilisateurs exportés")
            print(f"📋 {len(logs_data)} logs exportés")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Gestion de la persistance ORACXPRED')
    parser.add_argument('action', choices=['status', 'backup', 'list', 'restore', 'cleanup', 'export'],
                       help='Action à effectuer')
    
    args = parser.parse_args()
    
    if args.action == 'status':
        show_status()
    elif args.action == 'backup':
        create_backup()
    elif args.action == 'list':
        list_backups()
    elif args.action == 'restore':
        restore_backup()
    elif args.action == 'cleanup':
        cleanup_backups()
    elif args.action == 'export':
        export_data()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Mode interactif si aucun argument
        print("🔧 GESTION DE LA PERSISTANCE ORACXPRED")
        print("=" * 40)
        print("1. 📊 Afficher le statut")
        print("2. 💾 Créer un backup")
        print("3. 📋 Lister les backups")
        print("4. 🔄 Restaurer un backup")
        print("5. 🗑️ Nettoyer les anciens backups")
        print("6. 📤 Exporter les données")
        print("0. Quitter")
        
        while True:
            try:
                choice = input("\nChoisissez une option (0-6): ")
                
                if choice == '0':
                    print("👋 Au revoir!")
                    break
                elif choice == '1':
                    show_status()
                elif choice == '2':
                    create_backup()
                elif choice == '3':
                    list_backups()
                elif choice == '4':
                    restore_backup()
                elif choice == '5':
                    cleanup_backups()
                elif choice == '6':
                    export_data()
                else:
                    print("❌ Choix invalide")
            except KeyboardInterrupt:
                print("\n👋 Au revoir!")
                break
    else:
        main()
