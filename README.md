# MarKev - Système de Gestion de Garage

## Description
MarKev est un système de facturation et de comptabilité complet développé spécifiquement pour un garage spécialisé dans les services d'esthétique automobile au Québec.

## Fonctionnalités

### ✅ Phase 1 - Terminée
- ✅ Configuration du projet Django avec PostgreSQL
- ✅ Modèles de données complets (Client, Vehicle, Service, Invoice, etc.)
- ✅ Migrations de base de données

### ✅ Phase 2 - Terminée
- ✅ Interface d'administration Django personnalisée
- ✅ Système d'authentification
- ✅ Tableau de bord principal avec statistiques
- ✅ Gestion du profil d'entreprise

### ✅ Phase 3 - Terminée
- ✅ Gestion complète des clients (CRUD avec recherche)
- ✅ Gestion des véhicules associés aux clients
- ✅ Gestion complète des services (CRUD avec filtres)
- ✅ Interfaces utilisateur intuitives et responsives

### ✅ Phase 4 - Terminée
- ✅ Interface de création de factures avec éléments dynamiques
- ✅ Calcul automatique des taxes TPS (5%) et TVQ (9.975%)
- ✅ Génération de PDF conformes aux exigences du Québec
- ✅ Gestion des paiements et statuts de factures

### ✅ Phase 5 - Terminée
- ✅ Gestion complète des dépenses avec téléversement de reçus
- ✅ Rapports financiers détaillés avec calculs de profits
- ✅ Suivi des taxes TPS/TVQ (perçues vs payées)
- ✅ Répartition des revenus et dépenses par catégories

## 🎉 **PROJET COMPLET** - Toutes les phases terminées !

## Services supportés
- Pose de vitres teintées
- Protection pare-pierre (PPF)
- Wrapping de véhicules
- Protection hydrophobe pour vitres
- Compound, polissage et autres services d'esthétique

## Installation et Configuration

### Prérequis
- Python 3.8+
- PostgreSQL (optionnel, SQLite configuré pour le développement)

### Installation
```bash
# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Démarrer le serveur de développement
python manage.py runserver
```

### Accès
- Application principale: http://127.0.0.1:8000/
- Administration: http://127.0.0.1:8000/admin/

### Compte administrateur par défaut
- Nom d'utilisateur: admin
- Mot de passe: admin123

## Structure du projet
```
markev_project/
├── garage_app/           # Application principale
│   ├── models.py        # Modèles de données
│   ├── views.py         # Vues et logique métier
│   ├── forms.py         # Formulaires Django
│   ├── admin.py         # Configuration administration
│   └── templates/       # Templates HTML
├── markev_project/      # Configuration Django
│   └── settings.py      # Paramètres du projet
└── requirements.txt     # Dépendances Python
```

## Conformité fiscale
Le système est conçu pour respecter les exigences fiscales du Québec :
- Calcul automatique TPS (5%) et TVQ (9.975%)
- Génération de factures conformes
- Suivi des taxes payées et perçues

## Technologies utilisées
- **Backend**: Django 5.2.5
- **Base de données**: PostgreSQL / SQLite
- **Frontend**: Bootstrap 5.1.3
- **Génération PDF**: ReportLab
- **Images**: Pillow

## Prochaines étapes
1. Finaliser les interfaces CRUD pour clients et services
2. Implémenter le moteur de facturation complet
3. Ajouter la génération de PDF conformes aux exigences du Québec
4. Créer le système de suivi des dépenses
5. Développer les rapports financiers automatisés
