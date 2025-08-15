# 🚀 Déploiement MarKev sur Vercel

## 📋 Prérequis

1. **Compte Vercel** : [vercel.com](https://vercel.com)
2. **Repository GitHub** : Code poussé sur GitHub
3. **Base de données PostgreSQL** : Recommandé Supabase ou Neon

## 🔧 Configuration Vercel

### 1. Variables d'environnement à configurer dans Vercel :

```bash
SECRET_KEY=your-django-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:password@host:port/database
```

### 2. Commandes de déploiement :

```bash
# 1. Connecter le repository GitHub à Vercel
# 2. Configurer les variables d'environnement
# 3. Déployer automatiquement
```

## 🗄️ Configuration de la base de données

### Option 1: Supabase (Recommandé)
1. Créer un projet sur [supabase.com](https://supabase.com)
2. Récupérer l'URL de connexion PostgreSQL
3. Ajouter `DATABASE_URL` dans les variables Vercel

### Option 2: Neon
1. Créer un projet sur [neon.tech](https://neon.tech)
2. Récupérer l'URL de connexion
3. Ajouter `DATABASE_URL` dans les variables Vercel

## 📦 Après le déploiement

### 1. Migrations de base de données :
```bash
# Via Vercel CLI ou interface web
python manage.py migrate
```

### 2. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

### 3. Importer les services MarKev :
```bash
python manage.py import_markev_services
```

## 🔍 Vérification du déploiement

1. ✅ Application accessible via l'URL Vercel
2. ✅ Interface d'administration fonctionnelle
3. ✅ Services MarKev importés (36 services)
4. ✅ Création de clients/véhicules/rendez-vous
5. ✅ Génération de factures PDF

## 🛠️ Dépannage

### Erreur de base de données :
- Vérifier `DATABASE_URL` dans les variables Vercel
- S'assurer que les migrations sont appliquées

### Erreur de fichiers statiques :
- Vérifier que `build_files.sh` s'exécute correctement
- Contrôler la configuration `STATIC_URL` et `STATICFILES_DIRS`

### Erreur de timeout :
- Augmenter `maxLambdaSize` dans `vercel.json` si nécessaire

## 📞 Support

Pour toute question sur le déploiement, consulter :
- [Documentation Vercel Django](https://vercel.com/guides/deploying-django-with-vercel)
- [Documentation Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
