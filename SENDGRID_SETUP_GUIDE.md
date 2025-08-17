# 📧 Guide de Configuration SendGrid - Garage MarKev

## 🚨 Problème Identifié

L'envoi d'emails échoue avec l'erreur **403 Forbidden** car aucune adresse d'expédition n'est vérifiée dans SendGrid.

```
The from address does not match a verified Sender Identity. 
Mail cannot be sent until this error is resolved.
```

## ✅ Solution : Vérifier une Sender Identity

### Étape 1 : Accéder au Dashboard SendGrid

1. Connectez-vous à [SendGrid Dashboard](https://app.sendgrid.com/)
2. Utilisez vos identifiants SendGrid

### Étape 2 : Configurer une Sender Identity

#### Option A : Vérification d'une adresse email unique (Recommandé pour débuter)

1. Dans le menu de gauche, allez dans **Settings** > **Sender Authentication**
2. Cliquez sur **Single Sender Verification**
3. Cliquez sur **Create New Sender**
4. Remplissez le formulaire :
   - **From Name** : `Garage MarKev`
   - **From Email Address** : `Garage.MarKev@outlook.com` (ou une adresse que vous contrôlez)
   - **Reply To** : `Garage.MarKev@outlook.com`
   - **Company Address** : Votre adresse d'entreprise
   - **City, State, Zip** : Vos informations
   - **Country** : Canada

5. Cliquez sur **Create**
6. **IMPORTANT** : Vérifiez votre boîte email et cliquez sur le lien de vérification

#### Option B : Authentification de domaine (Pour la production)

1. Dans **Settings** > **Sender Authentication**
2. Cliquez sur **Domain Authentication**
3. Suivez les instructions pour configurer les enregistrements DNS

### Étape 3 : Mettre à jour la configuration

Une fois l'adresse vérifiée, mettez à jour le fichier `.env` :

```bash
# Configuration SendGrid
SENDGRID_API_KEY=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
DEFAULT_FROM_EMAIL=Garage.MarKev@outlook.com  # Utilisez l'adresse vérifiée
```

## 🧪 Test de la Configuration

### Test via Script

```bash
python test_sendgrid_real.py
```

### Test via Interface d'Administration

1. Allez dans l'interface d'administration Django
2. Section **Vehicles** > **Vehicles**
3. Sélectionnez des véhicules
4. Dans le menu **Actions**, choisissez **Tester la configuration SendGrid**

## 🔧 Configuration Alternative (Temporaire)

Si vous ne pouvez pas vérifier `Garage.MarKev@outlook.com` immédiatement, utilisez une adresse que vous contrôlez :

### 1. Vérifiez votre adresse personnelle dans SendGrid

Exemple : `votre.email@gmail.com`

### 2. Mettez à jour le .env

```bash
DEFAULT_FROM_EMAIL=votre.email@gmail.com
```

### 3. Testez l'envoi

Les emails seront envoyés depuis votre adresse personnelle temporairement.

## 📋 Vérification du Statut

### Dashboard SendGrid

1. **Activity** > **Email Activity** : Voir les emails envoyés
2. **Stats** > **Overview** : Statistiques d'envoi
3. **Suppressions** : Vérifier les bounces/spam

### Logs Django

Les logs d'envoi sont visibles dans la console Django :

```bash
python manage.py runserver
# Les tentatives d'envoi apparaîtront dans les logs
```

## 🚀 Test Complet

Une fois la configuration terminée :

### 1. Créer une facture de test

1. Interface d'administration > **Invoices**
2. Créer une nouvelle facture avec un client ayant un email
3. Finaliser la facture

### 2. Tester l'envoi

1. Aller sur la page de détail de la facture
2. Cliquer sur **Envoyer par courriel**
3. Vérifier le message de succès
4. Vérifier la réception de l'email

## ⚠️ Points Importants

### Limites SendGrid

- **Plan gratuit** : 100 emails/jour
- **Vérification requise** : Toutes les adresses d'expédition doivent être vérifiées
- **Réputation** : Évitez les bounces et spam complaints

### Sécurité

- **Ne jamais exposer** la clé API SendGrid
- **Utiliser HTTPS** en production
- **Surveiller** les logs d'envoi

### Production

Pour la production sur Vercel :

1. Configurer les variables d'environnement :
   ```
   SENDGRID_API_KEY=votre_clé_api
   DEFAULT_FROM_EMAIL=adresse_vérifiée
   ```

2. Vérifier le domaine complet pour une meilleure délivrabilité

## 🆘 Dépannage

### Erreur 403 Forbidden
- ✅ Vérifier que l'adresse d'expédition est vérifiée dans SendGrid
- ✅ Vérifier la clé API SendGrid

### Emails non reçus
- ✅ Vérifier les spams
- ✅ Vérifier l'activité dans le dashboard SendGrid
- ✅ Vérifier que l'adresse destinataire est valide

### Erreur de clé API
- ✅ Vérifier que la clé API est correcte
- ✅ Vérifier les permissions de la clé API

## 📞 Support

- **Documentation SendGrid** : https://docs.sendgrid.com/
- **Support SendGrid** : Via le dashboard SendGrid
- **Logs système** : Vérifier les logs Django pour plus de détails

---

**Une fois la Sender Identity vérifiée, l'envoi d'emails fonctionnera parfaitement !** 📧✅
