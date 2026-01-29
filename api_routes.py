# -*- coding: utf-8 -*-
"""
API Routes pour ORACXPRED MÉTAPHORE
Endpoints sécurisés avec OAuth et gestion des plans
"""
from flask import Blueprint, request, jsonify, redirect, make_response
from functools import wraps
import uuid

from config_oauth import config
from oauth_service import oauth_service
from session_manager import session_manager
from plan_service import plan_service, PlanType
from models_oauth import db, User, Prediction, AuditLog

# Blueprint API
api_bp = Blueprint('api', __name__, url_prefix='/api')

def require_auth(f):
    """Décorateur pour exiger l'authentification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_payload = session_manager.get_current_user(request)
        if not user_payload:
            return jsonify({'error': 'Authentification requise'}), 401
        return f(user_payload, *args, **kwargs)
    return decorated

def require_premium(f):
    """Décorateur pour exiger un plan premium"""
    @wraps(f)
    def decorated(user_payload, *args, **kwargs):
        if not session_manager.is_premium_user(user_payload):
            return jsonify({'error': 'Plan premium requis'}), 403
        return f(user_payload, *args, **kwargs)
    return decorated

def require_details_access(f):
    """Décorateur pour exiger l'accès aux détails"""
    @wraps(f)
    def decorated(user_payload, *args, **kwargs):
        if not session_manager.can_access_details(user_payload):
            return jsonify({'error': 'Accès détails non autorisé'}), 403
        return f(user_payload, *args, **kwargs)
    return decorated

# --- OAuth Endpoints ---

@api_bp.route('/auth/google/url')
def get_google_auth_url():
    """Retourne l'URL d'authentification Google"""
    state = str(uuid.uuid4())
    auth_url = oauth_service.get_auth_url(state)
    
    return jsonify({
        'auth_url': auth_url,
        'state': state
    })

@api_bp.route('/auth/google/callback')
def google_callback():
    """Callback OAuth Google"""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        return redirect(f"{config.FRONTEND_URL}?error=oauth_error&message={error}")
    
    if not code:
        return redirect(f"{config.FRONTEND_URL}?error=missing_code")
    
    try:
        # Authentification complète
        auth_result = oauth_service.authenticate_user(code, state)
        user_data = auth_result['user']
        
        # Crée les tokens
        tokens = session_manager.create_tokens(user_data)
        
        # Crée la réponse avec cookies httpOnly
        response = make_response(redirect(f"{config.FRONTEND_URL}?auth=success"))
        
        # Cookies sécurisés
        response.set_cookie(
            'access_token', 
            tokens['access_token'],
            httponly=True,
            secure=config.SESSION_COOKIE_SECURE,
            samesite=config.SESSION_COOKIE_SAMESITE,
            max_age=tokens['expires_in']
        )
        
        response.set_cookie(
            'refresh_token',
            tokens['refresh_token'],
            httponly=True,
            secure=config.SESSION_COOKIE_SECURE,
            samesite=config.SESSION_COOKIE_SAMESITE,
            max_age=7*24*3600  # 7 jours
        )
        
        return response
        
    except Exception as e:
        return redirect(f"{config.FRONTEND_URL}?error=auth_failed&message={str(e)}")

@api_bp.route('/auth/refresh', methods=['POST'])
def refresh_token():
    """Rafraîchit le token d'accès"""
    refresh_token = request.cookies.get('refresh_token') or request.json.get('refresh_token')
    
    if not refresh_token:
        return jsonify({'error': 'Refresh token requis'}), 401
    
    new_tokens = session_manager.refresh_access_token(refresh_token)
    
    if not new_tokens:
        return jsonify({'error': 'Refresh token invalide'}), 401
    
    return jsonify(new_tokens)

@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Déconnexion"""
    response = make_response(jsonify({'message': 'Déconnecté'}))
    
    # Supprime les cookies
    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)
    
    return response

# --- User Endpoints ---

@api_bp.route('/me')
@require_auth
def get_current_user(user_payload):
    """Retourne les infos de l'utilisateur connecté"""
    user = User.query.get(user_payload['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Ajoute les infos de limites
    limits = plan_service.check_user_limits(user_payload['user_id'])
    
    user_data = user.to_dict()
    user_data.update(limits)
    
    return jsonify(user_data)

@api_bp.route('/plans')
def get_available_plans():
    """Retourne les plans disponibles"""
    return jsonify(plan_service.get_available_plans())

@api_bp.route('/upgrade-plan', methods=['POST'])
@require_auth
def upgrade_plan(user_payload):
    """Upgrade du plan utilisateur"""
    data = request.get_json()
    plan_id = data.get('plan_id')
    
    if not plan_id:
        return jsonify({'error': 'Plan requis'}), 400
    
    try:
        new_plan = PlanType(plan_id)
        subscription = plan_service.upgrade_user_plan(
            user_payload['user_id'], 
            new_plan,
            payment_method=data.get('payment_method'),
            payment_id=data.get('payment_id')
        )
        
        return jsonify({
            'message': 'Plan mis à jour',
            'subscription': subscription.to_dict()
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erreur upgrade plan'}), 500

# --- Predictions Endpoints ---

@api_bp.route('/predictions', methods=['GET'])
@require_auth
def get_predictions(user_payload):
    """Retourne les prédictions de l'utilisateur"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    predictions = Prediction.query.filter_by(
        user_id=user_payload['user_id']
    ).order_by(
        Prediction.created_at.desc()
    ).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'predictions': [pred.to_dict() for pred in predictions.items],
        'total': predictions.total,
        'pages': predictions.pages,
        'current_page': page
    })

@api_bp.route('/predictions', methods=['POST'])
@require_auth
def create_prediction(user_payload):
    """Crée une nouvelle prédiction"""
    # Vérifie les limites
    can_predict, message = plan_service.can_make_prediction(user_payload['user_id'])
    if not can_predict:
        return jsonify({'error': message}), 429
    
    data = request.get_json()
    match_data = data.get('match_data')
    prediction_data = data.get('prediction')
    
    if not match_data or not prediction_data:
        return jsonify({'error': 'Données incomplètes'}), 400
    
    try:
        prediction = Prediction(
            user_id=user_payload['user_id'],
            match_data=match_data,
            prediction=prediction_data,
            status='pending'
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        # Log l'action
        audit_log = AuditLog(
            user_id=user_payload['user_id'],
            action='prediction_created',
            meta={'prediction_id': str(prediction.id)}
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Prédiction créée',
            'prediction': prediction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur création prédiction'}), 500

@api_bp.route('/predictions/<prediction_id>/details')
@require_auth
@require_details_access
def get_prediction_details(user_payload, prediction_id):
    """Retourne les détails d'une prédiction (premium)"""
    prediction = Prediction.query.filter_by(
        id=prediction_id,
        user_id=user_payload['user_id']
    ).first()
    
    if not prediction:
        return jsonify({'error': 'Prédiction non trouvée'}), 404
    
    # Ajoute les détails premium (analytics, etc.)
    details = prediction.to_dict()
    details.update({
        'premium_analysis': True,
        'confidence_score': 0.85,  # Exemple
        'risk_factors': ['low', 'medium'],
        'recommendation': 'strong_buy'
    })
    
    return jsonify(details)

# --- Admin Endpoints ---

@api_bp.route('/admin/users')
@require_auth
def admin_get_users(user_payload):
    """Liste tous les utilisateurs (admin seulement)"""
    user = User.query.get(user_payload['user_id'])
    if user.role != 'admin':
        return jsonify({'error': 'Accès admin requis'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages
    })

@api_bp.route('/admin/users/<user_id>', methods=['PATCH'])
@require_auth
def admin_update_user(user_payload, user_id):
    """Met à jour un utilisateur (admin seulement)"""
    current_user = User.query.get(user_payload['user_id'])
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès admin requis'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    data = request.get_json()
    
    # Mise à jour des champs autorisés
    if 'plan' in data:
        try:
            new_plan = PlanType(data['plan'])
            plan_service.upgrade_user_plan(user_id, new_plan)
        except ValueError:
            return jsonify({'error': 'Plan invalide'}), 400
    
    if 'status' in data:
        user.status = data['status']
    
    if 'role' in data:
        user.role = data['role']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Utilisateur mis à jour',
        'user': user.to_dict()
    })

@api_bp.route('/admin/users/<user_id>', methods=['DELETE'])
@require_auth
def admin_delete_user(user_payload, user_id):
    """Supprime un utilisateur (admin seulement)"""
    current_user = User.query.get(user_payload['user_id'])
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès admin requis'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'Utilisateur supprimé'})

# --- Health Check ---

@api_bp.route('/health')
def health_check():
    """Vérification de santé de l'API"""
    return jsonify({
        'status': 'healthy',
        'service': 'ORACXPRED MÉTAPHORE',
        'version': '1.0.0',
        'signature': 'Signé SOLITAIRE HACK 🇨🇮'
    })
