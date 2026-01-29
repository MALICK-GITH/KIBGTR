# -*- coding: utf-8 -*-
"""
Modèle de données PostgreSQL pour ORACXPRED MÉTAPHORE
Utilise SQLAlchemy avec UUID et relations optimisées
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text, Index, DateTime
from datetime import datetime, timezone
import uuid

db = SQLAlchemy()

class User(db.Model):
    """Utilisateurs avec auth Google et gestion des plans"""
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # OAuth Provider
    provider = db.Column(db.String(20), nullable=False, default='google')  # google, local
    provider_id = db.Column(db.String(100), nullable=True)  # Google 'sub' claim
    
    # Rôle et statut
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, user
    plan = db.Column(db.String(20), nullable=False, default='free')  # free, mensuel, 2mois, vip
    status = db.Column(db.String(20), nullable=False, default='actif')  # actif, inactif
    
    # Timestamps
    created_at = db.Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    subscriptions = db.relationship('Subscription', backref='user', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Index
    __table_args__ = (
        Index('idx_users_provider_id', 'provider', 'provider_id'),
        Index('idx_users_plan_status', 'plan', 'status'),
    )
    
    def to_dict(self):
        """Sérialisation pour API"""
        return {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'avatar_url': self.avatar_url,
            'provider': self.provider,
            'role': self.role,
            'plan': self.plan,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @property
    def is_premium(self) -> bool:
        """Vérifie si l'utilisateur a un plan payant actif"""
        return self.plan in ['mensuel', '2mois', 'vip'] and self.status == 'actif'
    
    @property
    def daily_prediction_limit(self) -> int:
        """Limite de prédictions quotidiennes selon le plan"""
        limits = {
            'free': 3,
            'mensuel': -1,  # illimité
            '2mois': -1,
            'vip': -1
        }
        return limits.get(self.plan, 3)

class Subscription(db.Model):
    """Abonnements et historique des plans"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    plan = db.Column(db.String(20), nullable=False)  # mensuel, 2mois, vip
    start_date = db.Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    end_date = db.Column(DateTime(timezone=True), nullable=True)  # null pour illimité
    
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Métadonnées
    payment_method = db.Column(db.String(50), nullable=True)  # stripe, paypal, etc.
    payment_id = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=True)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'plan': self.plan,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'amount': self.amount
        }

class AuditLog(db.Model):
    """Journal d'audit pour la sécurité"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    
    action = db.Column(db.String(100), nullable=False)  # login, logout, prediction_created, plan_changed
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Métadonnées JSON
    meta = db.Column(db.JSON, nullable=True)  # {old_plan: 'free', new_plan: 'mensuel'}
    
    created_at = db.Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Index
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_created', 'created_at'),
    )

class Prediction(db.Model):
    """Historique des prédictions"""
    __tablename__ = 'predictions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    match_data = db.Column(db.JSON, nullable=False)  # {teams, odds, date, etc.}
    prediction = db.Column(db.JSON, nullable=False)  # {result, confidence, system}
    
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, won, lost, void
    
    created_at = db.Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(DateTime(timezone=True), nullable=True)
    
    # Index
    __table_args__ = (
        Index('idx_predictions_user_status', 'user_id', 'status'),
        Index('idx_predictions_created', 'created_at'),
    )

# Fonctions utilitaires
def init_db(app):
    """Initialise la base de données avec l'application Flask"""
    db.init_app(app)
    
    with app.app_context():
        # Crée les tables si elles n'existent pas
        db.create_all()
        print("✅ Base de données PostgreSQL initialisée")

def create_admin_user(email: str, username: str = None):
    """Crée un utilisateur admin (pour le setup initial)"""
    from config_oauth import config
    
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            username=username or email.split('@')[0],
            provider='local',
            role='admin',
            plan='vip',
            status='actif'
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ Admin user créé: {email}")
        return user
    else:
        print(f"ℹ️  Admin user existe déjà: {email}")
        return user
