# -*- coding: utf-8 -*-
"""
Service de backup automatique pour Render ORACXPRED MÉTAPHORE
Sauvegarde complète de la base de données et des fichiers critiques
"""
import os
import sys
import subprocess
import datetime
import json
import boto3
from botocore.exceptions import ClientError

# Configuration
BACKUP_TYPE = os.getenv('BACKUP_TYPE', 'daily_full')
RETENTION_DAYS = int(os.getenv('RETENTION_DAYS', 30))
BACKUP_LOCATION = os.getenv('BACKUP_LOCATION', 'render_internal')

# Configuration Render
RENDER_DB_URL = os.getenv('DATABASE_URL')
RENDER_SERVICE_NAME = os.getenv('RENDER_SERVICE_NAME', 'oracxpred-metaphore')

class RenderBackupService:
    """Service de backup complet pour Render"""
    
    def __init__(self):
        self.backup_date = datetime.datetime.now(datetime.timezone.utc)
        self.backup_filename = f"oracxpred_backup_{self.backup_date.strftime('%Y%m%d_%H%M%S')}"
        
    def log(self, message):
        """Log avec timestamp"""
        timestamp = self.backup_date.strftime('%Y-%m-%d %H:%M:%S UTC')
        print(f"[{timestamp}] 📦 {message}")
    
    def backup_postgresql(self):
        """Sauvegarde de la base de données PostgreSQL"""
        self.log("🗄️ Début backup PostgreSQL...")
        
        try:
            # Extraction des infos de connexion depuis DATABASE_URL
            import urllib.parse
            db_url = urllib.parse.urlparse(RENDER_DB_URL)
            
            # Commande pg_dump
            backup_file = f"/tmp/{self.backup_filename}_db.sql"
            
            cmd = [
                'pg_dump',
                '--host', db_url.hostname,
                '--port', str(db_url.port or 5432),
                '--username', db_url.username,
                '--dbname', db_url.path[1:],  # Enlève le /
                '--verbose',
                '--clean',
                '--no-acl',
                '--no-owner',
                '--format=custom',
                '--file', backup_file
            ]
            
            # Définit le password dans l'environnement
            env = os.environ.copy()
            env['PGPASSWORD'] = db_url.password
            
            # Exécution du backup
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                file_size = os.path.getsize(backup_file)
                self.log(f"✅ Backup PostgreSQL réussi: {file_size} bytes")
                return backup_file
            else:
                self.log(f"❌ Erreur backup PostgreSQL: {result.stderr}")
                return None
                
        except Exception as e:
            self.log(f"❌ Exception backup PostgreSQL: {str(e)}")
            return None
    
    def backup_application_data(self):
        """Sauvegarde des données de l'application (fichiers critiques)"""
        self.log("📁 Début backup données application...")
        
        try:
            # Création archive des données critiques
            import zipfile
            backup_file = f"/tmp/{self.backup_filename}_app.zip"
            
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Ajouter les fichiers de configuration (sans secrets)
                critical_files = [
                    'render.yaml',
                    'requirements.txt',
                    'migrations/001_initial_schema.sql',
                    '.env.example'
                ]
                
                for file_path in critical_files:
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
                
                # Ajouter un manifeste du backup
                manifest = {
                    'backup_date': self.backup_date.isoformat(),
                    'backup_type': BACKUP_TYPE,
                    'service_name': RENDER_SERVICE_NAME,
                    'files_included': critical_files,
                    'version': '1.0.0',
                    'signature': 'Signé SOLITAIRE HACK 🇨🇮'
                }
                
                zipf.writestr('backup_manifest.json', json.dumps(manifest, indent=2))
            
            file_size = os.path.getsize(backup_file)
            self.log(f"✅ Backup application réussi: {file_size} bytes")
            return backup_file
            
        except Exception as e:
            self.log(f"❌ Erreur backup application: {str(e)}")
            return None
    
    def store_backup_render_internal(self, db_file, app_file):
        """Stockage des backups dans le stockage Render interne"""
        self.log("💾 Stockage backups Render interne...")
        
        try:
            # Render fournit un stockage persistant dans /tmp
            # Les fichiers survivent aux redéploiements
            
            stored_files = []
            
            if db_file and os.path.exists(db_file):
                stored_db = f"/tmp/render_backups/{os.path.basename(db_file)}"
                os.makedirs('/tmp/render_backups', exist_ok=True)
                os.rename(db_file, stored_db)
                stored_files.append(stored_db)
                self.log(f"✅ DB backup stocké: {stored_db}")
            
            if app_file and os.path.exists(app_file):
                stored_app = f"/tmp/render_backups/{os.path.basename(app_file)}"
                os.makedirs('/tmp/render_backups', exist_ok=True)
                os.rename(app_file, stored_app)
                stored_files.append(stored_app)
                self.log(f"✅ App backup stocké: {stored_app}")
            
            return stored_files
            
        except Exception as e:
            self.log(f"❌ Erreur stockage: {str(e)}")
            return []
    
    def cleanup_old_backups(self):
        """Nettoyage des anciens backups"""
        self.log(f"🧹 Nettoyage backups > {RETENTION_DAYS} jours...")
        
        try:
            backup_dir = '/tmp/render_backups'
            if not os.path.exists(backup_dir):
                return
            
            cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=RETENTION_DAYS)
            deleted_count = 0
            
            for filename in os.listdir(backup_dir):
                filepath = os.path.join(backup_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath), datetime.timezone.utc)
                    
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        deleted_count += 1
            
            self.log(f"✅ {deleted_count} anciens backups supprimés")
            
        except Exception as e:
            self.log(f"❌ Erreur nettoyage: {str(e)}")
    
    def create_backup_report(self, success, files):
        """Crée un rapport de backup"""
        report = {
            'backup_date': self.backup_date.isoformat(),
            'backup_type': BACKUP_TYPE,
            'service_name': RENDER_SERVICE_NAME,
            'success': success,
            'files_backed_up': files,
            'retention_days': RETENTION_DAYS,
            'backup_location': BACKUP_LOCATION,
            'signature': 'Signé SOLITAIRE HACK 🇨🇮'
        }
        
        # Sauvegarde du rapport
        report_file = f"/tmp/render_backups/{self.backup_filename}_report.json"
        os.makedirs('/tmp/render_backups', exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"📋 Rapport backup créé: {report_file}")
        return report
    
    def run_full_backup(self):
        """Exécution complète du backup"""
        self.log(f"🚀 Début backup {BACKUP_TYPE} pour {RENDER_SERVICE_NAME}")
        
        try:
            # Backup PostgreSQL
            db_file = self.backup_postgresql()
            
            # Backup application
            app_file = self.backup_application_data()
            
            # Stockage
            stored_files = self.store_backup_render_internal(db_file, app_file)
            
            # Nettoyage anciens backups
            self.cleanup_old_backups()
            
            # Rapport
            success = len(stored_files) > 0
            report = self.create_backup_report(success, stored_files)
            
            if success:
                self.log(f"✅ Backup terminé avec succès - {len(stored_files)} fichiers")
            else:
                self.log("❌ Backup échoué")
            
            return report
            
        except Exception as e:
            self.log(f"❌ Erreur critique backup: {str(e)}")
            return None

def main():
    """Point d'entrée pour le service Render"""
    print("🚀 Démarrage service backup ORACXPRED MÉTAPHORE")
    
    if not RENDER_DB_URL:
        print("❌ DATABASE_URL non configuré")
        sys.exit(1)
    
    backup_service = RenderBackupService()
    result = backup_service.run_full_backup()
    
    if result:
        print(f"✅ Backup complété: {result['success']}")
        sys.exit(0)
    else:
        print("❌ Backup échoué")
        sys.exit(1)

if __name__ == '__main__':
    main()
