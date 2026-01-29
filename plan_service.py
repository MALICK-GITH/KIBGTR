# -*- coding: utf-8 -*-
"""
Service de gestion des plans et abonnements pour ORACXPRED MÉTAPHORE
Gère les limites, upgrades et vérifications d'accès
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from enum import Enum

from models_oauth import db, User, Subscription, AuditLog

class PlanType(Enum):
    FREE = 'free'
    MENSUEL = 'mensuel'
    DEUX_MOIS = '2mois'
    VIP = 'vip'

class PlanService:
    """Service de gestion des plans d'abonnement"""
    
    # Configuration des plans
    PLANS_CONFIG = {
        PlanType.FREE: {
            'name': 'Gratuit',
            'price': 0,
            'duration_days': None,  # illimité
            'daily_predictions': 3,
            'details_access': False,
            'analytics_access': False,
            'priority_support': False,
            'features': ['3 prédictions/jour', 'Prédictions de base']
        },
        PlanType.MENSUEL: {
            'name': 'Mensuel',
            'price': 19.99,
            'duration_days': 30,
            'daily_predictions': -1,  # illimité
            'details_access': True,
            'analytics_access': True,
            'priority_support': True,
            'features': ['Prédictions illimitées', 'Accès détails', 'Analytics', 'Support prioritaire']
        },
        PlanType.DEUX_MOIS: {
            'name': '2 Mois',
            'price': 34.99,  # -12.5% vs mensuel
            'duration_days': 60,
            'daily_predictions': -1,
            'details_access': True,
            'analytics_access': True,
            'priority_support': True,
            'features': ['Prédictions illimitées', 'Accès détails', 'Analytics', 'Support prioritaire', 'Meilleur prix']
        },
        PlanType.VIP: {
            'name': 'VIP',
            'price': 49.99,
            'duration_days': 30,
            'daily_predictions': -1,
            'details_access': True,
            'analytics_access': True,
            'priority_support': True,
            'features': ['Prédictions illimitées', 'Accès détails VIP', 'Analytics avancés', 'Support dédié', 'Méthodes exclusives']
        }
    }
    
    @classmethod
    def get_plan_config(cls, plan: PlanType) -> Dict:
        """Retourne la configuration d'un plan"""
        return cls.PLANS_CONFIG.get(plan, cls.PLANS_CONFIG[PlanType.FREE])
    
    @classmethod
    def get_available_plans(cls) -> List[Dict]:
        """Retourne tous les plans disponibles"""
        return [
            {
                'id': plan.value,
                'name': config['name'],
                'price': config['price'],
                'duration_days': config['duration_days'],
                'features': config['features']
            }
            for plan, config in cls.PLANS_CONFIG.items()
        ]
    
    def upgrade_user_plan(self, user_id: str, new_plan: PlanType, 
                         payment_method: str = None, payment_id: str = None) -> Subscription:
        """Effectue l'upgrade du plan d'un utilisateur"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Utilisateur non trouvé")
        
        old_plan = user.plan
        
        # Désactive les anciens abonnements
        Subscription.query.filter_by(user_id=user_id, active=True).update({'active': False})
        
        # Crée le nouvel abonnement
        plan_config = self.get_plan_config(new_plan)
        subscription = Subscription(
            user_id=user_id,
            plan=new_plan.value,
            start_date=datetime.now(timezone.utc),
            end_date=self._calculate_end_date(new_plan),
            active=True,
            payment_method=payment_method,
            payment_id=payment_id,
            amount=plan_config['price']
        )
        
        # Met à jour l'utilisateur
        user.plan = new_plan.value
        if new_plan != PlanType.FREE:
            user.status = 'actif'
        
        db.session.add(subscription)
        db.session.commit()
        
        # Log l'upgrade
        self._log_plan_change(user, old_plan, new_plan.value, 'upgrade')
        
        return subscription
    
    def downgrade_user_plan(self, user_id: str, new_plan: PlanType = PlanType.FREE) -> Subscription:
        """Effectue le downgrade du plan d'un utilisateur"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Utilisateur non trouvé")
        
        old_plan = user.plan
        
        # Désactive les abonnements actifs
        Subscription.query.filter_by(user_id=user_id, active=True).update({'active': False})
        
        # Crée le nouvel abonnement (gratuit)
        subscription = Subscription(
            user_id=user_id,
            plan=new_plan.value,
            start_date=datetime.now(timezone.utc),
            end_date=None,  # illimité pour free
            active=True,
            payment_method=None,
            payment_id=None,
            amount=0
        )
        
        # Met à jour l'utilisateur
        user.plan = new_plan.value
        
        db.session.add(subscription)
        db.session.commit()
        
        # Log le downgrade
        self._log_plan_change(user, old_plan, new_plan.value, 'downgrade')
        
        return subscription
    
    def check_user_limits(self, user_id: str) -> Dict:
        """Vérifie les limites actuelles de l'utilisateur"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Utilisateur non trouvé")
        
        plan_config = self.get_plan_config(PlanType(user.plan))
        
        # Compte les prédictions du jour
        from models_oauth import Prediction
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        
        daily_predictions = Prediction.query.filter(
            Prediction.user_id == user_id,
            Prediction.created_at >= today_start
        ).count()
        
        daily_limit = plan_config['daily_predictions']
        remaining = daily_limit - daily_predictions if daily_limit > 0 else float('inf')
        
        return {
            'plan': user.plan,
            'daily_limit': daily_limit,
            'daily_used': daily_predictions,
            'daily_remaining': remaining,
            'details_access': plan_config['details_access'],
            'analytics_access': plan_config['analytics_access'],
            'is_premium': user.plan != PlanType.FREE.value
        }
    
    def can_access_details(self, user_id: str) -> bool:
        """Vérifie si l'utilisateur peut accéder aux détails"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        plan_config = self.get_plan_config(PlanType(user.plan))
        return plan_config['details_access']
    
    def can_make_prediction(self, user_id: str) -> tuple[bool, str]:
        """Vérifie si l'utilisateur peut faire une prédiction"""
        limits = self.check_user_limits(user_id)
        
        if limits['daily_remaining'] <= 0:
            return False, f"Limite quotidienne atteinte ({limits['daily_used']}/{limits['daily_limit']})"
        
        return True, "Prédiction autorisée"
    
    def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Retourne l'abonnement actif de l'utilisateur"""
        return Subscription.query.filter_by(
            user_id=user_id, 
            active=True
        ).first()
    
    def _calculate_end_date(self, plan: PlanType) -> Optional[datetime]:
        """Calcule la date de fin d'abonnement"""
        duration_days = self.get_plan_config(plan)['duration_days']
        if duration_days is None:
            return None
        
        return datetime.now(timezone.utc) + timedelta(days=duration_days)
    
    def _log_plan_change(self, user: User, old_plan: str, new_plan: str, action: str):
        """Enregistre le changement de plan dans l'audit"""
        from flask import request
        
        log = AuditLog(
            user_id=user.id,
            action=f'plan_{action}',
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None,
            meta={
                'old_plan': old_plan,
                'new_plan': new_plan,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
        db.session.add(log)
        db.session.commit()
    
    def cleanup_expired_subscriptions(self):
        """Nettoie les abonnements expirés (task quotidienne)"""
        now = datetime.now(timezone.utc)
        
        expired = Subscription.query.filter(
            Subscription.active == True,
            Subscription.end_date.isnot(None),
            Subscription.end_date < now
        ).all()
        
        for sub in expired:
            sub.active = False
            # Downgrade vers free
            self.downgrade_user_plan(str(sub.user_id))
        
        db.session.commit()
        return len(expired)

# Instance globale
plan_service = PlanService()
