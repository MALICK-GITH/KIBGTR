# -*- coding: utf-8 -*-
"""
Application Flask principale pour ORACXPRED MÉTAPHORE
Intègre OAuth, PostgreSQL, et gestion des plans
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os

# Configuration et services
from config_oauth import config
from models_oauth import init_db, db
from api_routes import api_bp

def create_app():
    """Fabrique d'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = config.APP_SECRET
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CORS sécurisé
    CORS(app, 
         origins=config.CORS_ORIGINS,
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])
    
    # Initialisation base de données
    init_db(app)
    
    # Enregistrement des routes API
    app.register_blueprint(api_bp)
    
    # Routes principales
    @app.route('/')
    def index():
        return jsonify({
            'message': 'ORACXPRED MÉTAPHORE API',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth/google/url',
                'callback': '/api/auth/google/callback',
                'me': '/api/me',
                'predictions': '/api/predictions',
                'plans': '/api/plans',
                'health': '/api/health'
            },
            'signature': 'Signé SOLITAIRE HACK 🇨🇮'
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint non trouvé'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Erreur serveur interne'}), 500
    
    return app

# Point d'entrée pour développement
if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=config.FLASK_DEBUG)
