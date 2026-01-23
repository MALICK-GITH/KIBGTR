# 🚀 ORACXPRED MÉTAPHORE - SYSTÈME DE PRÉDICTION RÉVOLUTIONNAIRE

## 📋 DESCRIPTION COMPLÈTE

ORACXPRED MÉTAPHORE est un système de prédiction sportif avancé utilisant :
- **IA Quantique** pour analyses prédictives
- **Systèmes Multi-Bots** spécialisés
- **Interface Admin** complète
- **Gestion des Abonnements** Premium/VIP
- **API Temps Réel** 1xBet

---

## 🔧 INSTALLATION RAPIDE

### 1. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 2. Initialisation de la base de données
```bash
python fifa1.py
```

### 3. Sécurisation des mots de passe (RECOMMANDÉ)
```bash
python migrate_security.py
```

### 4. Démarrage de l'application
```bash
python fifa1.py
```

L'application démarre sur : `http://localhost:10000`

---

## 🔐 ACCÈS ADMINISTRATEUR

### Compte Admin par défaut
- **URL** : `http://localhost:10000/admin/login`
- **Username** : `ADMIN`
- **Password** : `ADMIN123`

### Fonctionnalités Admin
- ✅ Validation des comptes utilisateurs
- ✅ Gestion des abonnements (Free/Premium/VIP)
- ✅ Statistiques complètes
- ✅ Logs système
- ✅ Interface ORACX-ADMIN avancée

---

## 👥 GESTION DES UTILISATEURS

### Inscription
- Les nouveaux utilisateurs doivent être **approuvés par un admin**
- Interface d'inscription : `http://localhost:10000/register`
- Mot de passe hashé avec **bcrypt** (sécurité maximale)

### Connexion
- Utilisateurs : `http://localhost:10000/login`
- Admin : `http://localhost:10000/admin/login`

---

## 🎯 FONCTIONNALITÉS PRINCIPALES

### 1. **Prédictions IA Avancées**
- Système quantique de prédiction
- Analyse multi-facteurs
- Value betting automatique
- Probabilités en temps réel

### 2. **Interface Temps Réel**
- Matchs live de 1xBet
- Cotes actualisées
- Scores en direct
- Statistiques détaillées

### 3. **Système d'Abonnement**
- **Free** : Accès limité
- **Premium** : Prédictions standards
- **VIP** : Toutes les fonctionnalités

### 4. **Dashboard Admin**
- Gestion des utilisateurs
- Validation des comptes
- Statistiques complètes
- Logs d'activité

---

## 📊 STRUCTURE TECHNIQUE

### Architecture
```
├── fifa1.py              # Application principale Flask
├── models.py             # Modèles de base de données
├── security.py           # Module de sécurité (bcrypt)
├── migrate_security.py   # Script de migration
├── prediction_manager.py # Gestion des prédictions
├── systeme_prediction_quantique.py  # IA Quantique
├── bots_alternatifs.py   # Bots spécialisés
└── requirements.txt      # Dépendances Python
```

### Technologies
- **Backend** : Flask + SQLAlchemy
- **Sécurité** : bcrypt + sessions
- **IA** : Algorithmes quantiques
- **API** : 1xBet temps réel
- **Frontend** : HTML5 + CSS3 + JavaScript

---

## 🔧 CONFIGURATION

### Variables d'environnement
```bash
PORT=10000
HOST=0.0.0.0
DATABASE_URL=sqlite:///oracxpred.db
SECRET_KEY=votre-clé-secrète
```

### Base de données
- SQLite par défaut (compatible tous environnements)
- Migration automatique au démarrage
- Backup intégré

---

## 🚀 DÉPLOIEMENT

### Local
```bash
python fifa1.py
```

### Production (Render/Heroku)
```bash
# Variables d'environnement configurées automatiquement
# Port dynamique géré par la plateforme
```

---

## 📈 PERFORMANCES

### Optimisations
- ✅ Cache des prédictions
- ✅ Requêtes SQL optimisées
- ✅ Compression des réponses
- ✅ Gestion mémoire efficace

### Sécurité
- ✅ Mots de passe hashés (bcrypt)
- ✅ Protection CSRF
- ✅ Validation des entrées
- ✅ Logs d'activité

---

## 🐛 DÉPANNAGE

### Problèmes courants
1. **Module bcrypt manquant** : `pip install bcrypt`
2. **Base de données vide** : Redémarrer l'application
3. **Admin non créé** : Exécuter `migrate_security.py`

### Logs
- Logs système dans `SystemLog`
- Logs d'accès dans `AccessLog`
- Console pour le debug

---

## 📞 SUPPORT

### Documentation complète
- `GUIDE_ACCES_ADMIN.md` : Guide admin détaillé
- `README_ORACXPRED.md` : Documentation technique
- `CHANGELOG_ORACXPRED.md` : Historique des mises à jour

### Contact
- Support technique intégré
- Logs d'erreur détaillés
- Interface admin pour diagnostic

---

## 🎉 MISES À JOUR

### Dernière version
- ✅ Sécurité bcrypt activée
- ✅ Interface admin améliorée
- ✅ Performance optimisée
- ✅ Bugs corrigés

### Prochaines fonctionnalités
- 🔄 API mobile
- 🔄 Notifications push
- 🔄 Analytics avancés
- 🔄 Multi-langues

---

**ORACXPRED MÉTAPHORE - Le futur de la prédiction sportive** 🚀
