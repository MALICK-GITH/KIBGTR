#!/usr/bin/env python3
"""
Script de gestion du stockage cloud pour ORACXPRED
Permet de configurer et tester les providers cloud
"""

import os
import sys
import argparse
from pathlib import Path

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage import cloud_manager, initialize_cloud_storage, sync_now, get_cloud_status

def show_cloud_status():
    """Affiche le statut du stockage cloud"""
    print("STATUT DU STOCKAGE CLOUD")
    print("=" * 40)
    
    status = get_cloud_status()
    
    # Afficher les providers
    print("Providers configures:")
    for provider, config in status["providers"].items():
        provider_name = provider.replace("_", " ").title()
        status_text = "Actif" if config["enabled"] else "Inactif"
        print(f"   {provider_name}: {status_text}")
    
    # Afficher l'auto-sync
    auto_sync = status["auto_sync"]
    sync_status = "Actif" if auto_sync["enabled"] else "Inactif"
    print(f"\nSynchronisation automatique: {sync_status}")
    if auto_sync["enabled"]:
        print(f"   Intervalle: {auto_sync['interval_hours']} heures")
    
    # Afficher les backups cloud
    backups = status["backups"]
    print(f"\nBackups dans le cloud: {len(backups)}")
    for backup in backups:
        print(f"   {backup['filename']} ({backup['provider']})")

def setup_google_drive():
    """Configure Google Drive"""
    print("CONFIGURATION GOOGLE DRIVE")
    print("=" * 35)
    
    print("Pour configurer Google Drive, vous avez besoin de:")
    print("1. Un projet Google Cloud Platform")
    print("2. Activer l'API Google Drive")
    print("3. Créer des credentials OAuth 2.0")
    print("4. Télécharger le fichier JSON des credentials")
    print()
    
    credentials_path = input("Chemin du fichier credentials JSON (laisser vide pour tester): ").strip()
    
    if not credentials_path:
        # Mode test avec credentials factices
        test_credentials = '{"client_id": "test", "client_secret": "test", "redirect_uris": ["http://localhost"]}'
        success = cloud_manager.setup_google_drive(test_credentials)
    else:
        try:
            with open(credentials_path, 'r') as f:
                credentials = f.read()
            success = cloud_manager.setup_google_drive(credentials)
        except Exception as e:
            print(f"❌ Erreur lecture fichier: {e}")
            return
    
    if success:
        print("Google Drive configure avec succes!")
    else:
        print("Erreur configuration Google Drive")

def setup_dropbox():
    """Configure Dropbox"""
    print("CONFIGURATION DROPBOX")
    print("=" * 30)
    
    print("Pour configurer Dropbox, vous avez besoin de:")
    print("1. Une app Dropbox")
    print("2. Activer les permissions 'files.content.write' et 'files.content.read'")
    print("3. Générer un access token")
    print()
    
    token = input("Access token Dropbox (laisser vide pour tester): ").strip()
    
    if not token:
        # Mode test avec token factice
        token = "sl.test_token_123456789"
    
    success = cloud_manager.setup_dropbox(token)
    
    if success:
        print("Dropbox configure avec succes!")
    else:
        print("Erreur configuration Dropbox")

def setup_ftp():
    """Configure FTP"""
    print("CONFIGURATION FTP")
    print("=" * 25)
    
    host = input("Hôte FTP: ").strip()
    username = input("Utilisateur: ").strip()
    password = input("Mot de passe: ").strip()
    folder = input("Dossier (défaut: /oracxpred): ").strip() or "/oracxpred"
    
    if not all([host, username, password]):
        print("❌ Tous les champs sont requis")
        return
    
    success = cloud_manager.setup_ftp(host, username, password, folder)
    
    if success:
        print("✅ FTP configuré avec succès!")
    else:
        print("❌ Erreur configuration FTP")

def test_sync():
    """Test la synchronisation cloud"""
    print("TEST DE SYNCHRONISATION")
    print("=" * 30)
    
    # Vérifier qu'au moins un provider est configuré
    active_providers = []
    for provider, config in cloud_manager.config["providers"].items():
        if config["enabled"]:
            active_providers.append(provider)
    
    if not active_providers:
        print("❌ Aucun provider cloud configuré")
        print("Configurez d'abord un provider avec les options 1, 2 ou 3")
        return
    
    print(f"Providers actifs: {', '.join(active_providers)}")
    
    # Chemin de la base de données
    db_path = os.path.join("data", "oracxpred.db")
    if not os.path.exists(db_path):
        print(f"❌ Base de données introuvable: {db_path}")
        return
    
    confirm = input("Lancer la synchronisation ? (o/N): ")
    if confirm.lower() in ['o', 'oui', 'yes']:
        success, results = sync_now(db_path)
        
        if success:
            print("Synchronisation reussie!")
        else:
            print("Synchronisation partielle ou echouee")
        
        print("\nResultats detailles:")
        for provider, success, message in results:
            status = "OK" if success else "ERREUR"
            print(f"  {status} {provider}: {message}")
    else:
        print("Test annule")

def toggle_auto_sync():
    """Active/désactive la synchronisation automatique"""
    print("🔄 SYNCHRONISATION AUTOMATIQUE")
    print("=" * 35)
    
    current_status = cloud_manager.config["auto_sync"]["enabled"]
    interval = cloud_manager.config["auto_sync"]["interval_hours"]
    
    print(f"Statut actuel: {'✅ Actif' if current_status else '❌ Inactif'}")
    print(f"Intervalle actuel: {interval} heures")
    
    choice = input("1. Activer\n2. Désactiver\n3. Modifier l'intervalle\nChoix (1-3): ").strip()
    
    if choice == "1":
        cloud_manager.config["auto_sync"]["enabled"] = True
        cloud_manager.save_config()
        print("✅ Synchronisation automatique activée")
    elif choice == "2":
        cloud_manager.config["auto_sync"]["enabled"] = False
        cloud_manager.save_config()
        print("❌ Synchronisation automatique désactivée")
    elif choice == "3":
        try:
            new_interval = int(input("Nouvel intervalle (heures): "))
            cloud_manager.config["auto_sync"]["interval_hours"] = new_interval
            cloud_manager.save_config()
            print(f"✅ Intervalle modifié à {new_interval} heures")
        except ValueError:
            print("❌ Intervalle invalide")
    else:
        print("❌ Choix invalide")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Gestion du stockage cloud ORACXPRED')
    parser.add_argument('action', choices=['status', 'google-drive', 'dropbox', 'ftp', 'sync', 'auto-sync'],
                       help='Action à effectuer')
    
    args = parser.parse_args()
    
    if args.action == 'status':
        show_cloud_status()
    elif args.action == 'google-drive':
        setup_google_drive()
    elif args.action == 'dropbox':
        setup_dropbox()
    elif args.action == 'ftp':
        setup_ftp()
    elif args.action == 'sync':
        test_sync()
    elif args.action == 'auto-sync':
        toggle_auto_sync()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Mode interactif si aucun argument
        print("☁️ GESTION DU STOCKAGE CLOUD ORACXPRED")
        print("=" * 45)
        print("1. 📊 Afficher le statut")
        print("2. 📁 Configurer Google Drive")
        print("3. 📦 Configurer Dropbox")
        print("4. 🌐 Configurer FTP")
        print("5. 🚀 Tester la synchronisation")
        print("6. 🔄 Gérer la synchronisation automatique")
        print("0. Quitter")
        
        while True:
            try:
                choice = input("\nChoisissez une option (0-6): ")
                
                if choice == '0':
                    print("👋 Au revoir!")
                    break
                elif choice == '1':
                    show_cloud_status()
                elif choice == '2':
                    setup_google_drive()
                elif choice == '3':
                    setup_dropbox()
                elif choice == '4':
                    setup_ftp()
                elif choice == '5':
                    test_sync()
                elif choice == '6':
                    toggle_auto_sync()
                else:
                    print("❌ Choix invalide")
            except KeyboardInterrupt:
                print("\n👋 Au revoir!")
                break
    else:
        main()
