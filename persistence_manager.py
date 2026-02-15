"""
Module de persistance et backup pour ORACXPRED
Assure la sauvegarde automatique et la récupération des données
"""

import os
import shutil
import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time
from pathlib import Path

class DatabaseManager:
    """Gestionnaire de base de données avec backup automatique"""
    
    def __init__(self, db_path=None, backup_dir="backups"):
        # Utiliser le même chemin que l'application principale
        if db_path is None:
            import os
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            db_path = os.path.join(data_dir, 'oracxpred.db')
        
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.running = True
        
    def create_backup(self, backup_name=None):
        """Crée une sauvegarde de la base de données"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.db"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            # Vérifier si la base de données existe
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
                print(f"Backup cree: {backup_path}")
                
                # Créer un fichier de métadonnées
                metadata = {
                    "backup_time": datetime.now().isoformat(),
                    "original_db": self.db_path,
                    "backup_file": str(backup_path),
                    "size": os.path.getsize(backup_path)
                }
                
                metadata_path = self.backup_dir / f"{backup_name}.meta"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return True
            else:
                print(f"⚠️ Base de données {self.db_path} introuvable")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du backup: {e}")
            return False
    
    def restore_backup(self, backup_name):
        """Restaure une sauvegarde de la base de données"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"❌ Backup {backup_name} introuvable")
            return False
        
        try:
            # Créer un backup de la version actuelle avant restauration
            if os.path.exists(self.db_path):
                self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            
            shutil.copy2(backup_path, self.db_path)
            print(f"✅ Backup {backup_name} restauré avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la restauration: {e}")
            return False
    
    def list_backups(self):
        """Liste toutes les sauvegardes disponibles"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.db"):
            if backup_file.name.endswith(".meta"):
                continue
                
            metadata_file = self.backup_dir / f"{backup_file.name}.meta"
            metadata = {}
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            backups.append({
                "name": backup_file.name,
                "path": str(backup_file),
                "size": backup_file.stat().st_size,
                "created": datetime.fromtimestamp(backup_file.stat().st_ctime),
                "metadata": metadata
            })
        
        # Trier par date de création (plus récent en premier)
        backups.sort(key=lambda x: x["created"], reverse=True)
        return backups
    
    def cleanup_old_backups(self, keep_days=7):
        """Supprime les anciens backups (conserve les N derniers jours)"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0
        
        for backup_file in self.backup_dir.glob("*.db"):
            if backup_file.stat().st_ctime < cutoff_date.timestamp():
                try:
                    backup_file.unlink()
                    # Supprimer aussi le fichier de métadonnées
                    metadata_file = self.backup_dir / f"{backup_file.name}.meta"
                    if metadata_file.exists():
                        metadata_file.unlink()
                    deleted_count += 1
                    print(f"🗑️ Ancien backup supprimé: {backup_file.name}")
                except Exception as e:
                    print(f"❌ Erreur suppression {backup_file.name}: {e}")
        
        if deleted_count > 0:
            print(f"✅ Nettoyage terminé: {deleted_count} backups supprimés")
    
    def auto_backup_loop(self, interval_hours=6):
        """Boucle de backup automatique toutes les N heures"""
        print(f"🔄 Backup automatique toutes les {interval_hours} heures")
        
        while self.running:
            try:
                self.create_backup()
                self.cleanup_old_backups()
                
                # Attendre avant le prochain backup
                time.sleep(interval_hours * 3600)
                
            except KeyboardInterrupt:
                print("\n⏹️ Backup automatique arrêté")
                break
            except Exception as e:
                print(f"❌ Erreur backup automatique: {e}")
                time.sleep(300)  # Attendre 5 minutes en cas d'erreur
    
    def start_auto_backup(self, interval_hours=6):
        """Démarre le backup automatique dans un thread séparé"""
        backup_thread = threading.Thread(
            target=self.auto_backup_loop,
            args=(interval_hours,),
            daemon=True
        )
        backup_thread.start()
        return backup_thread
    
    def verify_database_integrity(self):
        """Vérifie l'intégrité de la base de données"""
        try:
            if not os.path.exists(self.db_path):
                return False, "Base de données introuvable"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vérification de base
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            conn.close()
            
            if result and result[0] == "ok":
                return True, "Base de données intacte"
            else:
                return False, f"Erreur d'intégrité: {result[0] if result else 'Inconnue'}"
                
        except Exception as e:
            return False, f"Erreur vérification: {e}"
    
    def get_database_stats(self):
        """Retourne des statistiques sur la base de données"""
        try:
            if not os.path.exists(self.db_path):
                return None
            
            size = os.path.getsize(self.db_path)
            modified = datetime.fromtimestamp(os.path.getmtime(self.db_path))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Compter les enregistrements dans chaque table
            tables = {}
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for table_name, in cursor.fetchall():
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                tables[table_name] = count
            
            conn.close()
            
            return {
                "path": self.db_path,
                "size_mb": round(size / (1024 * 1024), 2),
                "modified": modified,
                "tables": tables
            }
            
        except Exception as e:
            print(f"❌ Erreur statistiques: {e}")
            return None

# Instance globale du gestionnaire de base de données
db_manager = DatabaseManager()

def initialize_persistence():
    """Initialise le système de persistance"""
    print("Initialisation du systeme de persistance...")
    
    # Vérifier l'intégrité de la base de données
    is_valid, message = db_manager.verify_database_integrity()
    if is_valid:
        print(f"{message}")
    else:
        print(f"{message}")
        
        # Tenter de restaurer le dernier backup si disponible
        backups = db_manager.list_backups()
        if backups:
            print("Tentative de restauration depuis le dernier backup...")
            if db_manager.restore_backup(backups[0]["name"]):
                print("Base de données restauree")
            else:
                print("Echec de la restauration")
    
    # Créer un backup initial
    db_manager.create_backup("initial_backup.db")
    
    # Démarrer le backup automatique
    db_manager.start_auto_backup(interval_hours=6)
    
    # Afficher les statistiques
    stats = db_manager.get_database_stats()
    if stats:
        print(f"Base de données: {stats['size_mb']} MB, {len(stats['tables'])} tables")
        for table, count in stats['tables'].items():
            print(f"   {table}: {count} enregistrements")
    
    print("Systeme de persistance initialise avec succes")

def manual_backup():
    """Effectue un backup manuel"""
    return db_manager.create_backup()

def list_available_backups():
    """Liste les backups disponibles"""
    return db_manager.list_backups()

def restore_from_backup(backup_name):
    """Restaure depuis un backup spécifique"""
    return db_manager.restore_backup(backup_name)
