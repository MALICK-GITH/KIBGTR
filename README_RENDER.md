# ORACXPRED MÉTAPHORE - Guide de Déploiement Render Complet

## 🎯 Objectif
Déploiement sur Render avec persistance PostgreSQL complète et sauvegardes automatiques.

## 🚀 Déploiement Rapide

### 1. Prérequis GitHub
```bash
# Votre repo doit contenir tous les fichiers OAuth
git status
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Création Services Render

#### A. Base de données PostgreSQL
1. **Dashboard Render** → **New** → **PostgreSQL**
2. **Nom**: `oracxpred-db`
3. **Plan**: Free (starter)
4. **Region**: Plus proche de vos utilisateurs
5. **Database Name**: `oracxpred`
6. **User**: `oracxpred_user`

#### B. Service Web
1. **Dashboard Render** → **New** → **Web Service**
2. **Connect GitHub repo**: `MALICK-GITH/KIBGTR`
3. **Nom**: `oracxpred-metaphore`
4. **Runtime**: Python 3
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `python app_render.py`
7. **Health Check Path**: `/api/health`

#### C. Service Backup (Optionnel)
1. **Dashboard Render** → **New** → **Cron Job**
2. **Nom**: `oracxpred-backup-service`
3. **Schedule**: `0 3 * * *` (3h UTC quotidien)
4. **Start Command**: `python render_backup_service.py`

## 🔧 Configuration Variables d'Environnement

### Dans le dashboard Render → Environment Variables:

#### Variables obligatoires:
```bash
# Google OAuth
GOOGLE_CLIENT_ID=623094418745-0hk5n0otigl86rk81r2a384tam665jfl.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=votre_secret_google_ic
GOOGLE_PROJECT_ID=black-resource-485505-v9

# Application
APP_SECRET=votre_secret_jwt_32_caracteres_minimum
FRONTEND_URL=https://votre-frontend.onrender.com

# Base de données (fourni automatiquement par Render)
DATABASE_URL=postgresql://... (Render génère automatiquement)

# Service (fourni automatiquement par Render)
RENDER_SERVICE_NAME=oracxpred-metaphore
RENDER_EXTERNAL_URL=https://oracxpred-metaphore.onrender.com
```

#### Variables recommandées:
```bash
# Sécurité
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
CORS_ORIGINS=https://oracxpred-metaphore.onrender.com

# Backup
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=30

# Database optimisation
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Admin
ADMIN_EMAIL=admin@oracxpred.com
```

## 🗄️ Setup Base de Données

### 1. Connection PostgreSQL
Render fournit automatiquement `DATABASE_URL`. Pour vérifier:
```bash
# Dans le shell Render
psql $DATABASE_URL
```

### 2. Migration automatique
L'application `app_render.py` exécute automatiquement les migrations au démarrage:
- Vérifie si les tables existent
- Exécute `migrations/001_initial_schema.sql` si nécessaire
- Crée l'utilisateur admin par défaut

### 3. Vérification manuelle (optionnelle)
```sql
-- Connectez-vous à la base Render
\dt  -- Liste des tables
SELECT email, role, plan FROM users WHERE role = 'admin';  -- Vérification admin
```

## 🔄 Configuration OAuth Google

### 1. Google Console
1. Allez dans [Google Console](https://console.cloud.google.com/)
2. Projet: `black-resource-485505-v9`
3. **APIs & Services** → **Credentials**
4. **OAuth 2.0 Client IDs**
5. **Authorized redirect URIs**:
   ```
   https://oracxpred-metaphore.onrender.com/api/auth/google/callback
   ```

### 2. Test du flow OAuth
```bash
# 1. Récupérer l'URL OAuth
curl https://oracxpred-metaphore.onrender.com/api/auth/google/url

# 2. Suivre l'URL Google
# 3. Vérifier la redirection et création session
```

## 💾 Sauvegardes Automatiques

### 1. Configuration Render
Render sauvegarde automatiquement PostgreSQL:
- **Backup quotidien**: 2h UTC
- **Rétention**: 30 jours
- **Restauration**: 1-click dans dashboard

### 2. Backup service additionnel
Le service `render_backup_service.py` ajoute:
- **Backup complet**: DB + fichiers critiques
- **Stockage interne**: `/tmp/render_backups/`
- **Nettoyage automatique**: 30 jours
- **Rapports détaillés**: JSON avec métadonnées

### 3. Vérification backups
```bash
# API endpoint de statut
curl https://oracxpred-metaphore.onrender.com/api/backup/status

# Réponse attendue:
{
  "backup_enabled": true,
  "backup_count": 5,
  "last_backups": ["oracxpred_backup_20240129_030000_db.sql", ...]
}
```

## 🔍 Monitoring et Logs

### 1. Logs Render
- **Dashboard** → **Logs** → Sélectionner le service
- **Filtres utiles**: `ERROR`, `WARNING`, `backup`
- **Real-time**: Logs en temps réel

### 2. Health Checks
```bash
# Health check principal
curl https://oracxpred-metaphore.onrender.com/api/health

# Réponse attendue:
{
  "status": "healthy",
  "service": "ORACXPRED MÉTAPHORE",
  "environment": "Render",
  "signature": "Signé SOLITAIRE HACK 🇨🇮"
}
```

### 3. Métriques
- **Dashboard Render** → **Metrics**
- **CPU**, **Memory**, **Database connections**
- **Response times** et **Error rates**

## 🚨 Dépannage

### Problèmes communs:

#### 1. Erreur connexion DB
```bash
# Vérifier DATABASE_URL
echo $DATABASE_URL

# Tester connexion manuelle
psql $DATABASE_URL -c "SELECT 1;"
```

#### 2. OAuth redirect error
- Vérifier l'URL dans Google Console
- Doit correspondre exactement: `https://oracxpred-metaphore.onrender.com/api/auth/google/callback`

#### 3. Backup échoue
```bash
# Vérifier logs du service backup
# Dashboard → Cron Jobs → oracxpred-backup-service → Logs
```

#### 4. Variables ENV manquantes
```bash
# Redémarrer le service après ajout de variables
# Dashboard → Web Service → Manual Deploy
```

## 📊 Architecture Complète

```
┌─────────────────────────────────────────────────────────────┐
│                    RENDER CLOUD                              │
├─────────────────────────────────────────────────────────────┤
│  Web Service (oracxpred-metaphore)                         │
│  ├── Python 3.12                                            │
│  ├── Flask + OAuth + PostgreSQL                             │
│  └── https://oracxpred-metaphore.onrender.com              │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL (oracxpred-db)                                  │
│  ├── Automatic backups (2h UTC)                            │
│  ├── 30-day retention                                       │
│  └── Connection pooling                                     │
├─────────────────────────────────────────────────────────────┤
│  Cron Job (oracxpred-backup-service)                       │
│  ├── Daily at 3h UTC                                       │
│  ├── Full backup + cleanup                                 │
│  └── Internal storage (/tmp/render_backups/)                │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 URLs Finales

- **API principale**: https://oracxpred-metaphore.onrender.com
- **OAuth callback**: https://oracxpred-metaphore.onrender.com/api/auth/google/callback
- **Health check**: https://oracxpred-metaphore.onrender.com/api/health
- **Backup status**: https://oracxpred-metaphore.onrender.com/api/backup/status

## ✅ Checklist Post-Déploiement

- [ ] Service web démarré et health check OK
- [ ] Base de données connectée et tables créées
- [ ] Variables ENV configurées
- [ ] OAuth Google fonctionnel
- [ ] Backup service actif
- [ ] Logs sans erreurs critiques
- [ ] Premier utilisateur test créé
- [ ] Plans et limites fonctionnels

---
**Signé SOLITAIRE HACK 🇨🇮**

Votre système ORACXPRED MÉTAPHORE est maintenant déployé sur Render avec persistance complète et sauvegardes automatiques!
