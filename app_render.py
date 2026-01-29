# -*- coding: utf-8 -*-
"""
Application Flask principale pour ORACXPRED MÉTAPHORE - Adaptée pour Render
Intégre OAuth, PostgreSQL, et gestion des plans avec persistance complète
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
import atexit

# Configuration et services
from config_oauth import config
from models_oauth import init_db, db
from api_routes import api_bp

def create_app():
    """Fabrique d'application Flask pour Render"""
    app = Flask(__name__)
    
    # Configuration Render
    app.config['SECRET_KEY'] = config.APP_SECRET
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'max_overflow': 10
    }
    
    # CORS sécurisé pour Render
    CORS(app, 
         origins=config.CORS_ORIGINS,
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])
    
    # Initialisation base de données avec retry
    init_database_with_retry(app)
    
    # Enregistrement des routes API
    app.register_blueprint(api_bp)
    
    # Routes principales
    @app.route('/')
    def index():
        return jsonify({
            'message': 'ORACXPRED MÉTAPHORE API - Render',
            'status': 'running',
            'environment': 'Render',
            'service': 'oracxpred-metaphore',
            'endpoints': {
                'auth': '/api/auth/google/url',
                'callback': '/api/auth/google/callback',
                'me': '/api/me',
                'predictions': '/api/predictions',
                'plans': '/api/plans',
                'health': '/api/health',
                'backup_status': '/api/backup/status'
            },
            'signature': 'Signé SOLITAIRE HACK 🇨🇮'
        })
    
    @app.route('/api/backup/status')
    def backup_status():
        """Statut des backups sur Render"""
        try:
            import os
            backup_dir = '/tmp/render_backups'
            
            if os.path.exists(backup_dir):
                files = os.listdir(backup_dir)
                backup_files = [f for f in files if f.startswith('oracxpred_backup_')]
                
                return jsonify({
                    'backup_enabled': True,
                    'backup_count': len(backup_files),
                    'backup_location': backup_dir,
                    'last_backups': sorted(backup_files)[-5:] if backup_files else []
                })
            else:
                return jsonify({
                    'backup_enabled': False,
                    'message': 'Aucun backup trouvé'
                })
                
        except Exception as e:
            return jsonify({
                'backup_enabled': False,
                'error': str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint non trouvé'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Erreur serveur interne'}), 500
    
    # Cleanup au shutdown
    atexit.register(cleanup_on_exit)
    
    return app

def init_database_with_retry(app):
    """Initialise la base de données avec retry pour Render"""
    import time
    from sqlalchemy.exc import OperationalError
    
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"🗄️ Tentative connexion DB {attempt + 1}/{max_retries}")
            
            # Initialisation
            init_db(app)
            
            with app.app_context():
                # Test de connexion
                db.engine.execute('SELECT 1')
                
                # Crée les tables si besoin
                db.create_all()
                
                # Création admin si nécessaire
                from models_oauth import create_admin_user
                admin_email = os.getenv('ADMIN_EMAIL', 'admin@oracxpred.com')
                create_admin_user(admin_email)
                
                print("✅ Base de données initialisée avec succès")
                return
                
        except OperationalError as e:
            print(f"❌ Erreur connexion DB: {str(e)}")
            if attempt < max_retries - 1:
                print(f"🔄 Retry dans {retry_delay} secondes...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("❌ Échec connexion DB après toutes les tentatives")
                raise
        except Exception as e:
            print(f"❌ Erreur initialisation DB: {str(e)}")
            raise

def cleanup_on_exit():
    """Cleanup lors de l'arrêt de l'application"""
    print("🧹 Cleanup ORACXPRED MÉTAPHORE...")
    try:
        # Fermeture des connexions DB
        from models_oauth import db
        db.session.close()
        db.engine.dispose()
        print("✅ Connexions DB fermées")
    except Exception as e:
        print(f"❌ Erreur cleanup: {str(e)}")

def run_migrations():
    """Exécute les migrations SQL au démarrage"""
    try:
        print("🔄 Exécution migrations...")
        
        # Vérifie si les tables existent
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'users' not in tables:
            print("📋 Création tables depuis migration...")
            
            # Lecture et exécution du fichier de migration
            migration_file = 'migrations/001_initial_schema.sql'
            if os.path.exists(migration_file):
                with open(migration_file, 'r') as f:
                    migration_sql = f.read()
                
                # Exécution des commandes SQL
                db.session.execute(migration_sql)
                db.session.commit()
                print("✅ Migration terminée")
            else:
                print("⚠️ Fichier migration non trouvé, utilisation SQLAlchemy")
                db.create_all()
                db.session.commit()
        else:
            print("✅ Tables déjà existantes")
            
    except Exception as e:
        print(f"❌ Erreur migrations: {str(e)}")
        raise

# Point d'entrée pour Render
if __name__ == '__main__':
    print("🚀 Démarrage ORACXPRED MÉTAPHORE sur Render")
    
    app = create_app()
    
    # Port Render
    port = int(os.getenv('PORT', 10000))
    
    print(f"🌐 Service démarré sur port {port}")
    print(f"🔗 URL: https://oracxpred-metaphore.onrender.com")
    
    app.run(host='0.0.0.0', port=port, debug=config.FLASK_DEBUG)
