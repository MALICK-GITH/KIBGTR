# ORACXPRED MÉTAPHORE - Guide de Déploiement Sécurisé

## 🎯 Objectif
Intégration Google OAuth avec PostgreSQL persistant et gestion des plans premium.

## 📋 Prérequis

### 1. Google Console OAuth
- Créer un projet dans [Google Console](https://console.cloud.google.com/)
- Activer l'API Google+ et Google OAuth2
- Créer des identifiants OAuth2 (Application web)
- **Redirect URI**: `https://votre-app.vercel.app/api/auth/google/callback`

### 2. Base de données PostgreSQL
- Render PostgreSQL (recommandé)
- Railway PostgreSQL
- Supabase PostgreSQL
- AWS RDS PostgreSQL

## 🔧 Configuration Variables d'Environnement

### Variables Obligatoires
```bash
# Google OAuth
GOOGLE_CLIENT_ID=623094418745-0hk5n0otigl86rk81r2a384tam665jfl.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=votre_secret_google
GOOGLE_PROJECT_ID=black-resource-485505-v9

# Application
APP_SECRET=votre_secret_jwt_32_caracteres_minimum
APP_BASE_URL=https://votre-app.vercel.app
FRONTEND_URL=https://votre-frontend.vercel.app

# Base de données
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Variables Optionnelles
```bash
# Sécurité
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
CORS_ORIGINS=https://votre-frontend.vercel.app

# Environment
FLASK_ENV=production
FLASK_DEBUG=false
```

## 🚀 Déploiement Vercel

### 1. Préparation du repo
```bash
# Copier la configuration
cp .env.example .env
# Remplir .env avec les vraies valeurs (NE PAS COMMITTER)

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration Vercel
```bash
# Renommer la config Vercel
cp vercel_oauth.json vercel.json

# Déployer
vercel --prod
```

### 3. Variables d'environnement Vercel
Dans le dashboard Vercel → Settings → Environment Variables:
- Ajouter toutes les variables listées ci-dessus
- **NE JAMAIS** mettre de secrets dans le code

## 🗄️ Setup Base de Données

### 1. Création des tables
```bash
# Se connecter à PostgreSQL
psql $DATABASE_URL

# Exécuter la migration
\i migrations/001_initial_schema.sql
```

### 2. Vérification
```sql
-- Vérifier les tables
\dt

-- Vérifier l'utilisateur admin
SELECT email, role, plan FROM users WHERE role = 'admin';
```

## 🔒 Checklist Sécurité

### ✅ Configuration
- [ ] Variables d'environnement configurées
- [ ] `.env` dans `.gitignore`
- [ ] HTTPS activé
- [ ] CORS configuré correctement
- [ ] Cookies httpOnly et secure

### ✅ OAuth
- [ ] Redirect URI identique dans Google Console et Vercel
- [ ] Client secret jamais exposé côté client
- [ ] State token pour protection CSRF
- [ ] Validation JWT signature

### ✅ Base de données
- [ ] Connexion SSL/TLS
- [ ] Utilisateurs avec permissions minimales
- [ ] Backups automatiques
- [ ] Migrations versionnées

## 📊 Structure des Dossiers

```
project/
├── api/
│   └── index_oauth.py          # Entry point Vercel
├── migrations/
│   └── 001_initial_schema.sql # Schema PostgreSQL
├── config_oauth.py            # Configuration sécurisée
├── models_oauth.py            # Models SQLAlchemy
├── oauth_service.py           # Service Google OAuth
├── session_manager.py         # Gestion JWT
├── plan_service.py            # Gestion des plans
├── api_routes.py              # Endpoints API
├── app_oauth.py               # Application Flask
├── requirements.txt           # Dépendances
├── .env.example              # Template configuration
└── vercel.json               # Config Vercel
```

## 🎯 Plans et Limites

| Plan | Prix | Prédictions/jour | Détails | Analytics |
|------|------|------------------|---------|-----------|
| Free | 0€   | 3                | ❌      | ❌        |
| Mensuel | 19.99€ | ∞            | ✅      | ✅        |
| 2 Mois | 34.99€ | ∞             | ✅      | ✅        |
| VIP | 49.99€ | ∞               | ✅      | ✅        |

## 🔄 Flow OAuth Complet

1. **Frontend** → `GET /api/auth/google/url`
   - Retourne URL Google OAuth avec state

2. **Utilisateur** → Redirection Google
   - Authentification Google

3. **Google** → `GET /api/auth/google/callback?code=...`
   - Échange code contre tokens
   - Vérification JWT
   - Création/mise à jour utilisateur
   - Création session JWT
   - Redirection vers frontend avec cookies

4. **Frontend** → `GET /api/me`
   - Retourne infos utilisateur + limites

## 🛠️ Endpoints API

### Authentification
- `GET /api/auth/google/url` - URL OAuth
- `GET /api/auth/google/callback` - Callback OAuth
- `POST /api/auth/refresh` - Rafraîchir token
- `POST /api/auth/logout` - Déconnexion

### Utilisateur
- `GET /api/me` - Infos utilisateur
- `GET /api/plans` - Plans disponibles
- `POST /api/upgrade-plan` - Upgrade plan

### Prédictions
- `GET /api/predictions` - Historique
- `POST /api/predictions` - Créer prédiction
- `GET /api/predictions/:id/details` - Détails (premium)

### Admin
- `GET /api/admin/users` - Liste utilisateurs
- `PATCH /api/admin/users/:id` - Modifier utilisateur
- `DELETE /api/admin/users/:id` - Supprimer utilisateur

## 🚨 Tests Post-Déploiement

### 1. Health Check
```bash
curl https://votre-app.vercel.app/api/health
```

### 2. OAuth Flow
- Visiter `https://votre-app.vercel.app/api/auth/google/url`
- Suivre le flow Google
- Vérifier redirection et cookies

### 3. API Authentifiée
```bash
# Récupérer token depuis les cookies du navigateur
curl -H "Authorization: Bearer TOKEN" \
     https://votre-app.vercel.app/api/me
```

## 📞 Support

En cas de problème:
1. Vérifier les logs Vercel
2. Valider les variables ENV
3. Tester la connexion DB
4. Vérifier la configuration Google Console

---
**Signé SOLITAIRE HACK 🇨🇮**
