# Guide d'Utilisation - MarKev

## 🚀 Démarrage Rapide

### 1. Lancer l'application
```bash
python manage.py runserver
```
Accédez à: http://127.0.0.1:8000/

### 2. Connexion
- **Nom d'utilisateur**: admin
- **Mot de passe**: admin123

## 📋 Fonctionnalités Principales

### 🏢 Configuration Initiale
1. **Profil d'entreprise** (Menu → Profil entreprise)
   - Configurez le nom, adresse, téléphone
   - Ajoutez votre logo
   - Configurez les numéros TPS/TVQ si inscrit aux taxes

### 👥 Gestion des Clients
1. **Ajouter un client** (Menu → Clients → Nouveau client)
   - Nom, prénom, téléphone (obligatoires)
   - Email, adresse, notes (optionnels)

2. **Gérer les véhicules**
   - Depuis la fiche client, ajoutez les véhicules
   - Marque, modèle, année (obligatoires)
   - Couleur, plaque, VIN (optionnels)

### 🔧 Gestion des Services
1. **Créer des services** (Menu → Services → Nouveau service)
   - Nom et prix par défaut (obligatoires)
   - Catégories disponibles:
     - Vitres teintées
     - Protection pare-pierre (PPF)
     - Wrapping
     - Protection hydrophobe
     - Esthétique (compound, polissage)

### 💰 Facturation
1. **Créer une facture** (Menu → Factures → Nouvelle facture)
   - Sélectionnez le client et véhicule
   - Ajoutez les services avec quantités
   - Les taxes sont calculées automatiquement

2. **Gestion des paiements**
   - Marquez les factures comme payées
   - Suivez les statuts (brouillon, envoyée, payée, en retard)

3. **Génération PDF**
   - Cliquez "Générer PDF" sur une facture
   - PDF conforme aux exigences du Québec

### 📊 Suivi des Dépenses
1. **Enregistrer des dépenses** (Menu → Dépenses → Nouvelle dépense)
   - Description, montant, date (obligatoires)
   - Catégorie, taxes payées, reçu (optionnels)
   - Téléversez les reçus pour archivage

### 📈 Rapports Financiers
1. **Accéder aux rapports** (Menu → Rapports)
   - Revenus et dépenses par période
   - Calcul automatique des profits
   - Suivi des taxes TPS/TVQ
   - Répartition par catégories

## 🎯 Flux de Travail Recommandé

### Configuration initiale (une fois)
1. Configurez le profil d'entreprise
2. Créez vos services standards
3. Créez un premier client de test

### Utilisation quotidienne
1. **Nouveau client** → Ajoutez le client et ses véhicules
2. **Prestation de service** → Créez une facture avec les services
3. **Paiement reçu** → Marquez la facture comme payée
4. **Dépense** → Enregistrez vos achats et frais

### Suivi mensuel
1. Consultez les rapports financiers
2. Vérifiez les factures en retard
3. Préparez les déclarations de taxes

## 💡 Conseils d'Utilisation

### Facturation
- Utilisez des descriptions détaillées pour les services
- Vérifiez les dates d'échéance (30 jours par défaut)
- Générez les PDF pour envoi aux clients

### Dépenses
- Téléversez toujours les reçus
- Indiquez les taxes payées pour récupération
- Catégorisez correctement pour les rapports

### Taxes
- Si inscrit aux taxes, les calculs sont automatiques
- TPS: 5% sur tous les services
- TVQ: 9.975% sur tous les services
- Suivez les montants nets à remettre dans les rapports

## 🔧 Administration Avancée
Accédez à `/admin/` pour:
- Gestion avancée de tous les modèles
- Actions en lot sur les factures
- Configuration détaillée des données

## 📱 Interface Mobile
L'application est responsive et fonctionne sur:
- Ordinateurs de bureau
- Tablettes
- Téléphones mobiles

## 🆘 Support
Pour toute question ou problème:
1. Vérifiez ce guide d'utilisation
2. Consultez l'interface d'administration
3. Contactez le support technique
