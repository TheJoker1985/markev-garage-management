Tâches de Développement pour l'Agent IA - Projet MarKev
Ce document détaille la feuille de route d'implémentation pour le projet MarKev. Chaque phase est décomposée en tâches spécifiques et actionnables, conçues pour être exécutées par un agent de codage IA.

Phase 1 : Configuration du Projet et Modèles de Base
Tâche 1.1 : Initialiser un nouveau projet Django nommé markev_project et une nouvelle application nommée garage_app. Configurer le fichier settings.py pour utiliser une base de données PostgreSQL.

Tâche 1.2 : Dans garage_app/models.py, définir les modèles Django suivants, conformément au blueprint architectural : CompanyProfile, Client, Vehicle, Service, InventoryItem, Invoice, InvoiceItem, Expense et Payment.

Tâche 1.3 : Générer et appliquer les migrations initiales de la base de données pour créer les tables correspondantes dans PostgreSQL.

Phase 2 : Interface d'Administration et Configuration Fondamentale
Tâche 2.1 : Enregistrer tous les modèles créés dans le site d'administration de Django (garage_app/admin.py) pour les rendre gérables via l'interface d'administration automatique.

Tâche 2.2 : Mettre en place le système d'authentification des utilisateurs intégré à Django. Créer une page d'accueil de base qui requiert une connexion pour y accéder.

Tâche 2.3 : Créer un formulaire et une vue pour le modèle CompanyProfile afin que l'utilisateur puisse saisir les informations de son entreprise (nom, adresse, logo, numéros de taxes, etc.).

Phase 3 : Gestion des Clients et des Services (CRUD)
Tâche 3.1 : Créer l'ensemble complet des vues, formulaires et templates pour les opérations CRUD (Créer, Lire, Mettre à jour, Supprimer) du modèle Client. La vue listant les clients doit inclure une fonction de recherche.

Tâche 3.2 : Créer l'ensemble complet des vues, formulaires et templates CRUD pour le modèle Service.

Phase 4 : Moteur de Facturation Principal et Génération de PDF
Tâche 4.1 : Développer l'interface pour la création d'une nouvelle Invoice. Le formulaire doit permettre de sélectionner un client, d'ajouter dynamiquement plusieurs InvoiceItem (services) et de définir une date d'échéance.

Tâche 4.2 : Implémenter la logique de calcul des taxes. Lors de la sauvegarde d'une facture, une fonction doit calculer la TPS (5 %) et la TVQ (9,975 %) sur le sous-total et enregistrer les montants dans le modèle Invoice. Cette logique ne doit s'activer que si l'indicateur is_tax_registered du CompanyProfile est activé.

Tâche 4.3 (Cruciale) : En utilisant la bibliothèque ReportLab, créer une vue Django generate_invoice_pdf(request, invoice_id). Cette vue devra récupérer l'objet Invoice et ses données associées pour générer un document PDF respectant scrupuleusement les exigences légales du Québec (logo, informations de l'entreprise, détails de la transaction, taxes, etc., comme défini dans le blueprint).

Tâche 4.4 : Sur la page de détail d'une facture, ajouter des boutons pour "Marquer comme Payée" (ce qui créera un enregistrement Payment associé) et "Générer le PDF".

Phase 5 : Suivi des Dépenses et Rapports Financiers
Tâche 5.1 : Créer les vues CRUD, le formulaire et les templates pour le modèle Expense, en incluant la fonctionnalité de téléversement de fichiers pour les reçus numérisés.

Tâche 5.2 : Développer la vue du tableau de bord principal. Cette vue effectuera des requêtes à la base de données pour calculer et afficher les indicateurs financiers clés : revenus totaux, dépenses totales et bénéfice net pour différentes périodes (mois, trimestre, année).

Tâche 5.3 : Créer les vues et les fonctions de génération de PDF (basées sur ReportLab) pour les rapports financiers essentiels :

État des Résultats (Revenus - Dépenses)

Rapport des Ventes (Liste des factures)

Rapport sur les Taxes de Vente (Total des taxes perçues vs. total des taxes payées sur les dépenses).