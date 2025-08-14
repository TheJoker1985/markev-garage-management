Contexte du Projet : MarKev
1. Objectif du Projet
Le projet MarKev vise à développer un système de facturation et de comptabilité complet et sur mesure pour un garage spécialisé dans les services d'esthétique automobile. L'application doit être robuste, conforme aux réglementations fiscales du Québec et intuitive pour l'utilisateur final.

2. Public Cible
L'application est destinée au propriétaire ou gestionnaire d'un garage offrant des services spécialisés tels que :

Pose de vitres teintées

Protection pare-pierre (PPF)

Wrapping de véhicules

Protection hydrophobe pour vitres

Compound, polissage et autres services d'esthétique

3. Fonctionnalités Clés Requises
Le système sera organisé en plusieurs modules interconnectés pour couvrir tous les aspects de la gestion de l'entreprise :

a. Gestion des Clients (CRM)
Créer et gérer des fiches clients (nom, téléphone, etc.).

Associer un ou plusieurs véhicules à chaque client.

Consulter l'historique complet des services et factures pour chaque client.

b. Gestion des Services et Facturation
Définir une liste de services offerts avec des prix par défaut.

Créer des soumissions, des estimations et des factures professionnelles.

Calculer automatiquement les taxes (TPS/TVQ) applicables au Québec.

Personnaliser les factures avec une date d'échéance sélectionnable.

c. Comptabilité et Finances
Suivi des Dépenses : Enregistrer toutes les dépenses de l'entreprise (matériaux, outils, loyer, etc.) et joindre les reçus.

Comptabilité Complète : Le système doit permettre de tenir les comptes complets en suivant les entrées d'argent (revenus) et les sorties (dépenses).

Rapports Financiers :

Un tableau de bord affichant en temps réel les revenus, les dépenses et les profits.

Générer des rapports financiers clés (état des résultats, rapport de ventes, rapport de dépenses).

d. Personnalisation et Conformité
Génération de PDF : Créer des factures et des rapports en format PDF, prêts à être imprimés ou envoyés par courriel.

Personnalisation : Prévoir un espace dans l'en-tête des documents pour le logo et les informations de l'entreprise.

Conformité Fiscale : S'assurer que toutes les factures et tous les calculs respectent les exigences de Revenu Québec et de l'Agence du revenu du Canada.

4. Pile Technologique Recommandée
Backend : Python avec le framework Django (pour sa robustesse, sa sécurité et son développement rapide).

Base de données : PostgreSQL (pour sa fiabilité et son intégrité des données, cruciales pour une application financière).

Génération de PDF : Bibliothèque ReportLab (pour un contrôle total sur la mise en page des documents).