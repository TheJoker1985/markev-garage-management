from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import date, datetime, timedelta
import json
from dateutil.relativedelta import relativedelta


class CompanyProfile(models.Model):
    """Profil de l'entreprise - informations de base pour les factures"""
    name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    address = models.TextField(verbose_name="Adresse complète")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    website = models.URLField(blank=True, null=True, verbose_name="Site web")
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, verbose_name="Logo")

    # Numéros d'enregistrement fiscal
    gst_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Numéro TPS")
    qst_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Numéro TVQ")
    is_tax_registered = models.BooleanField(default=False, verbose_name="Inscrit aux taxes")

    # Configuration de l'année fiscale
    fiscal_year_end_month = models.IntegerField(
        default=12,
        choices=[(i, date(2000, i, 1).strftime('%B')) for i in range(1, 13)],
        verbose_name="Mois de fin d'année fiscale",
        help_text="Mois où se termine votre année fiscale (défaut: décembre)"
    )
    fiscal_year_end_day = models.IntegerField(
        default=31,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name="Jour de fin d'année fiscale",
        help_text="Jour où se termine votre année fiscale (défaut: 31)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil d'entreprise"
        verbose_name_plural = "Profils d'entreprise"

    def __str__(self):
        return self.name

    def get_fiscal_year_end(self, year=None):
        """Retourne la date de fin d'année fiscale pour une année donnée"""
        if year is None:
            year = date.today().year

        try:
            # Gérer le cas du 29 février pour les années non bissextiles
            if self.fiscal_year_end_month == 2 and self.fiscal_year_end_day == 29:
                # Si l'année n'est pas bissextile, utiliser le 28 février
                if not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
                    return date(year, self.fiscal_year_end_month, 28)

            return date(year, self.fiscal_year_end_month, self.fiscal_year_end_day)
        except ValueError:
            # Si la date n'est pas valide (ex: 31 avril), utiliser le dernier jour du mois
            import calendar
            last_day = calendar.monthrange(year, self.fiscal_year_end_month)[1]
            return date(year, self.fiscal_year_end_month, min(self.fiscal_year_end_day, last_day))

    def get_current_fiscal_year_period(self):
        """Retourne la période de l'année fiscale actuelle (début, fin)"""
        today = date.today()
        fiscal_year_end = self.get_fiscal_year_end(today.year)

        if today <= fiscal_year_end:
            # Nous sommes dans l'année fiscale qui se termine cette année
            fiscal_year_start = self.get_fiscal_year_end(today.year - 1) + timedelta(days=1)
            return fiscal_year_start, fiscal_year_end
        else:
            # Nous sommes dans l'année fiscale qui se terminera l'année prochaine
            fiscal_year_start = fiscal_year_end + timedelta(days=1)
            fiscal_year_end = self.get_fiscal_year_end(today.year + 1)
            return fiscal_year_start, fiscal_year_end

    def get_fiscal_year_period(self, fiscal_year):
        """Retourne la période pour une année fiscale spécifique"""
        fiscal_year_end = self.get_fiscal_year_end(fiscal_year)
        fiscal_year_start = self.get_fiscal_year_end(fiscal_year - 1) + timedelta(days=1)
        return fiscal_year_start, fiscal_year_end

    def get_fiscal_year_for_date(self, target_date):
        """Retourne l'année fiscale pour une date donnée"""
        if isinstance(target_date, datetime):
            target_date = target_date.date()

        fiscal_year_end = self.get_fiscal_year_end(target_date.year)

        if target_date <= fiscal_year_end:
            return target_date.year
        else:
            return target_date.year + 1


# Modèle Discount supprimé - système simplifié avec pourcentages directs


class Client(models.Model):
    """Modèle pour les clients du garage"""
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom de famille")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    address = models.TextField(blank=True, null=True, verbose_name="Adresse")

    # Informations supplémentaires
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    # Rabais par défaut pour ce client (pourcentage simple)
    default_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Pourcentage de rabais par défaut (%)",
        help_text="Rabais automatiquement appliqué aux factures de ce client (0-100%)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class VehicleType(models.Model):
    """Modèle pour les types de véhicules (VUS, Berline, Pickup, etc.)"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom du type")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    # Correspondances avec l'API NHTSA pour le mapping automatique
    nhtsa_body_classes = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste des 'Body Class' de l'API NHTSA correspondant à ce type",
        verbose_name="Classes de carrosserie NHTSA"
    )

    is_active = models.BooleanField(default=True, verbose_name="Type actif")

    # Champ pour le calculateur de lettrage
    complexity_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        verbose_name="Multiplicateur de complexité",
        help_text="Multiplicateur de complexité pour le lettrage (ex: Berline=1.0, Sprinter=1.6)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Type de véhicule"
        verbose_name_plural = "Types de véhicules"
        ordering = ['name']

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    """Modèle pour les véhicules des clients"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='vehicles', verbose_name="Client")
    make = models.CharField(max_length=50, verbose_name="Marque")
    model = models.CharField(max_length=50, verbose_name="Modèle")
    year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2030)],
        verbose_name="Année"
    )
    color = models.CharField(max_length=30, blank=True, null=True, verbose_name="Couleur")
    license_plate = models.CharField(max_length=20, blank=True, null=True, verbose_name="Plaque d'immatriculation")

    # Nouveau champ pour le type de véhicule
    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles',
        verbose_name="Type de véhicule"
    )

    # Champ pour indiquer si le type a été identifié automatiquement
    auto_identified_type = models.BooleanField(
        default=False,
        verbose_name="Type identifié automatiquement"
    )

    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        ordering = ['client__last_name', 'make', 'model']

    def __str__(self):
        return f"{self.year} {self.make} {self.model} - {self.client.full_name}"


class Supplier(models.Model):
    """Modèle pour les fournisseurs"""
    name = models.CharField(max_length=200, verbose_name="Nom du fournisseur")
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="Personne contact")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, null=True, verbose_name="Adresse")
    website = models.URLField(blank=True, null=True, verbose_name="Site web")

    # Informations commerciales
    account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Numéro de compte")
    payment_terms = models.CharField(max_length=100, blank=True, null=True, verbose_name="Conditions de paiement")

    # Catégorie de fournisseur
    SUPPLIER_CATEGORY_CHOICES = [
        ('materials', 'Matériaux'),
        ('tools', 'Outils'),
        ('services', 'Services'),
        ('utilities', 'Services publics'),
        ('professional', 'Services professionnels'),
        ('other', 'Autre'),
    ]
    category = models.CharField(
        max_length=20,
        choices=SUPPLIER_CATEGORY_CHOICES,
        default='other',
        verbose_name="Catégorie"
    )

    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Fournisseur actif")

    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_expenses(self):
        """Calculer le total des dépenses pour ce fournisseur"""
        return self.expenses.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')


class Service(models.Model):
    """Modèle pour les services offerts par le garage"""
    name = models.CharField(max_length=200, verbose_name="Nom du service")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    default_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix par défaut"
    )

    # Catégories de services
    CATEGORY_CHOICES = [
        ('package', 'Forfaits Signature'),
        ('tinting', 'Vitres teintées'),
        ('ppf', 'Protection pare-pierre (PPF)'),
        ('wrapping', 'Wrapping / Personnalisation'),
        ('ceramic', 'Protection céramique'),
        ('hydrophobic', 'Protection hydrophobe'),
        ('detailing', 'Esthétique & Correction de peinture'),
        ('other', 'Autre'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Catégorie")

    is_active = models.BooleanField(default=True, verbose_name="Service actif")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class ServiceConsumption(models.Model):
    """Modèle pour définir la consommation de matériaux par service et type de véhicule"""
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='consumption_rules',
        verbose_name="Service"
    )
    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.CASCADE,
        related_name='consumption_rules',
        verbose_name="Type de véhicule"
    )
    inventory_item = models.ForeignKey(
        'InventoryItem',  # Forward reference car InventoryItem est défini après
        on_delete=models.CASCADE,
        related_name='consumption_rules',
        verbose_name="Article d'inventaire"
    )

    # Taux de consommation (ex: 0.20 pour 20% d'un rouleau)
    consumption_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001')), MaxValueValidator(Decimal('10.0000'))],
        verbose_name="Taux de consommation",
        help_text="Quantité consommée par service (ex: 0.20 pour 20% d'un rouleau)"
    )

    # Unité de mesure pour clarifier le taux
    UNIT_CHOICES = [
        ('percentage', 'Pourcentage du rouleau'),
        ('meters', 'Mètres'),
        ('pieces', 'Pièces'),
        ('liters', 'Litres'),
        ('other', 'Autre'),
    ]
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default='percentage',
        verbose_name="Unité de mesure"
    )

    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    is_active = models.BooleanField(default=True, verbose_name="Règle active")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Règle de consommation"
        verbose_name_plural = "Règles de consommation"
        ordering = ['service__name', 'vehicle_type__name']
        # Contrainte d'unicité : une seule règle par combinaison service/type/article
        unique_together = ['service', 'vehicle_type', 'inventory_item']

    def __str__(self):
        return f"{self.service.name} - {self.vehicle_type.name} - {self.inventory_item.name} ({self.consumption_rate})"


class InventoryItem(models.Model):
    """Modèle pour la gestion de l'inventaire"""
    name = models.CharField(max_length=200, verbose_name="Nom de l'article")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    sku = models.CharField(max_length=50, unique=True, verbose_name="Code SKU")

    # Relation avec le fournisseur
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_items',
        verbose_name="Fournisseur"
    )

    # Quantités et prix (utilisation de DecimalField pour supporter les fractions)
    quantity_in_stock = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name="Quantité en stock"
    )
    minimum_stock_level = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name="Niveau de stock minimum"
    )
    reorder_level = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name="Niveau de réapprovisionnement"
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Coût unitaire"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix de vente unitaire"
    )

    # Catégories d'inventaire
    INVENTORY_CATEGORY_CHOICES = [
        ('materials', 'Matériaux'),
        ('tools', 'Outils'),
        ('supplies', 'Fournitures'),
        ('chemicals', 'Produits chimiques'),
        ('other', 'Autre'),
    ]
    category = models.CharField(max_length=20, choices=INVENTORY_CATEGORY_CHOICES, default='other', verbose_name="Catégorie")

    # Niveau de qualité pour la tarification dynamique
    QUALITY_TIER_CHOICES = [
        ('standard', 'Standard'),
        ('ceramic', 'Céramique'),
        ('premium', 'Premium'),
        ('ultra', 'Ultra Premium'),
    ]
    quality_tier = models.CharField(
        max_length=20,
        choices=QUALITY_TIER_CHOICES,
        blank=True,
        null=True,
        verbose_name="Niveau de qualité",
        help_text="Niveau de qualité du matériau pour la tarification dynamique"
    )

    is_active = models.BooleanField(default=True, verbose_name="Article actif")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Article d'inventaire"
        verbose_name_plural = "Articles d'inventaire"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} (SKU: {self.sku})"

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.minimum_stock_level

    @property
    def needs_reorder(self):
        """Vérifie si l'article a besoin d'être réapprovisionné"""
        return self.quantity_in_stock <= self.reorder_level

    @property
    def total_value(self):
        if self.unit_cost is not None:
            return self.quantity_in_stock * self.unit_cost
        return 0

    def check_stock_alerts(self):
        """Vérifier et créer les alertes de stock nécessaires"""
        alerts_created = []

        # Vérifier si une alerte de réapprovisionnement est nécessaire
        if self.needs_reorder:
            alert, created = self.create_or_update_alert('reorder', self.reorder_level)
            if created:
                alerts_created.append(alert)

        # Vérifier si une alerte de stock faible est nécessaire
        if self.is_low_stock:
            alert, created = self.create_or_update_alert('low_stock', self.minimum_stock_level)
            if created:
                alerts_created.append(alert)

        # Vérifier si une alerte de rupture de stock est nécessaire
        if self.quantity_in_stock == 0:
            alert, created = self.create_or_update_alert('out_of_stock', 0)
            if created:
                alerts_created.append(alert)

        return alerts_created

    def create_or_update_alert(self, alert_type, threshold_level):
        """Créer ou mettre à jour une alerte de stock"""
        # Vérifier s'il existe déjà une alerte active de ce type
        existing_alert = self.stock_alerts.filter(
            alert_type=alert_type,
            status='active'
        ).first()

        if existing_alert:
            # Mettre à jour l'alerte existante
            existing_alert.quantity_at_alert = self.quantity_in_stock
            existing_alert.threshold_level = threshold_level
            existing_alert.save()
            return existing_alert, False
        else:
            # Créer une nouvelle alerte
            # StockAlert sera défini plus bas dans ce même fichier
            alert = StockAlert.objects.create(
                inventory_item=self,
                alert_type=alert_type,
                quantity_at_alert=self.quantity_in_stock,
                threshold_level=threshold_level
            )
            return alert, True

    def resolve_alerts_if_stock_sufficient(self):
        """Résoudre automatiquement les alertes si le stock est suffisant"""
        resolved_alerts = []

        # Résoudre les alertes de réapprovisionnement si le stock est au-dessus du seuil
        if self.quantity_in_stock > self.reorder_level:
            reorder_alerts = self.stock_alerts.filter(
                alert_type='reorder',
                status='active'
            )
            for alert in reorder_alerts:
                alert.resolve("Stock réapprovisionné automatiquement")
                resolved_alerts.append(alert)

        # Résoudre les alertes de stock faible si le stock est au-dessus du minimum
        if self.quantity_in_stock > self.minimum_stock_level:
            low_stock_alerts = self.stock_alerts.filter(
                alert_type='low_stock',
                status='active'
            )
            for alert in low_stock_alerts:
                alert.resolve("Stock reconstitué automatiquement")
                resolved_alerts.append(alert)

        # Résoudre les alertes de rupture de stock si il y a du stock
        if self.quantity_in_stock > 0:
            out_of_stock_alerts = self.stock_alerts.filter(
                alert_type='out_of_stock',
                status='active'
            )
            for alert in out_of_stock_alerts:
                alert.resolve("Stock reconstitué automatiquement")
                resolved_alerts.append(alert)

        return resolved_alerts

    def save(self, *args, **kwargs):
        """Override save pour vérifier automatiquement les alertes de stock"""
        # Sauvegarder d'abord l'objet
        super().save(*args, **kwargs)

        # Puis vérifier les alertes de stock
        self.resolve_alerts_if_stock_sufficient()
        self.check_stock_alerts()


class StockAlert(models.Model):
    """Modèle pour les alertes de réapprovisionnement automatiques"""
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='stock_alerts',
        verbose_name="Article d'inventaire"
    )

    # Type d'alerte
    ALERT_TYPE_CHOICES = [
        ('reorder', 'Réapprovisionnement'),
        ('low_stock', 'Stock faible'),
        ('out_of_stock', 'Rupture de stock'),
    ]
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPE_CHOICES,
        default='reorder',
        verbose_name="Type d'alerte"
    )

    # Statut de l'alerte
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Prise en compte'),
        ('resolved', 'Résolue'),
        ('dismissed', 'Ignorée'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Statut"
    )

    # Informations sur l'alerte
    alert_date = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'alerte")
    acknowledged_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de prise en compte")
    resolved_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de résolution")

    # Quantités au moment de l'alerte
    quantity_at_alert = models.IntegerField(verbose_name="Quantité au moment de l'alerte")
    threshold_level = models.IntegerField(verbose_name="Seuil déclenché")

    # Notes et actions
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    action_taken = models.TextField(blank=True, null=True, verbose_name="Action entreprise")

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Alerte de stock"
        verbose_name_plural = "Alertes de stock"
        ordering = ['-alert_date']
        unique_together = ['inventory_item', 'alert_type', 'status']

    def __str__(self):
        return f"Alerte {self.get_alert_type_display()} - {self.inventory_item.name} ({self.get_status_display()})"

    def acknowledge(self, notes=None):
        """Marquer l'alerte comme prise en compte"""
        from django.utils import timezone
        self.status = 'acknowledged'
        self.acknowledged_date = timezone.now()
        if notes:
            self.notes = notes
        self.save()

    def resolve(self, action_taken=None):
        """Marquer l'alerte comme résolue"""
        from django.utils import timezone
        self.status = 'resolved'
        self.resolved_date = timezone.now()
        if action_taken:
            self.action_taken = action_taken
        self.save()

    def dismiss(self, notes=None):
        """Ignorer l'alerte"""
        self.status = 'dismissed'
        if notes:
            self.notes = notes
        self.save()

    @property
    def is_active(self):
        """Vérifie si l'alerte est encore active"""
        return self.status == 'active'

    @property
    def days_since_alert(self):
        """Nombre de jours depuis la création de l'alerte"""
        from django.utils import timezone
        return (timezone.now() - self.alert_date).days


class Invoice(models.Model):
    """Modèle pour les factures"""
    # Numérotation automatique
    invoice_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de facture")

    # Relations
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices', verbose_name="Client")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Véhicule")

    # Dates
    invoice_date = models.DateField(verbose_name="Date de facture")

    # Montants
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Sous-total"
    )
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant TPS"
    )
    qst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant TVQ"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant total"
    )

    # Rabais simplifié
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Pourcentage de rabais (%)"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant du rabais"
    )
    is_dealer_discount = models.BooleanField(
        default=False,
        verbose_name="Rabais concessionnaire (30%)"
    )

    # Statut
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
        ('cancelled', 'Annulée'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")

    # Mode de paiement
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Argent comptant'),
        ('debit', 'Carte de débit'),
        ('credit', 'Carte de crédit'),
        ('cheque', 'Chèque'),
        ('transfer', 'Virement bancaire'),
        ('other', 'Autre'),
    ]
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True,
        verbose_name="Mode de paiement"
    )

    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    # Archivage
    archived_fiscal_year = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Année fiscale archivée",
        help_text="Si défini, cette facture fait partie d'une année fiscale archivée"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-invoice_date', '-invoice_number']

    def __str__(self):
        return f"Facture {self.invoice_number} - {self.client.full_name}"

    def save(self, *args, **kwargs):
        # Générer le numéro de facture automatiquement
        if not self.invoice_number:
            from datetime import datetime
            year = datetime.now().year
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=f"INV-{year}"
            ).order_by('-invoice_number').first()

            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.invoice_number = f"INV-{year}-{new_number:04d}"

        # Appliquer le rabais par défaut du client lors de la création
        if not self.pk and self.client:  # Nouvelle facture
            if (self.discount_percentage == Decimal('0.00') and
                not self.is_dealer_discount and
                self.client.default_discount_percentage > Decimal('0.00')):
                self.discount_percentage = self.client.default_discount_percentage

        # Vérifier si c'est une nouvelle facture ou si le statut change vers 'finalized'
        is_new = self.pk is None
        old_status = None

        if not is_new:
            try:
                old_invoice = Invoice.objects.get(pk=self.pk)
                old_status = old_invoice.status
            except Invoice.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Déclencher la consommation d'inventaire si la facture est finalisée
        if (is_new and self.status == 'finalized') or (old_status != 'finalized' and self.status == 'finalized'):
            self._consume_inventory_for_services()

    def _consume_inventory_for_services(self):
        """Consomme automatiquement l'inventaire pour les services de cette facture"""
        from .services import InventoryConsumptionService

        try:
            InventoryConsumptionService.consume_inventory_for_invoice(self)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de la consommation d'inventaire pour la facture {self.invoice_number}: {e}")

    def calculate_totals(self):
        """Calculer les totaux de la facture"""
        self.subtotal = sum(item.total_price for item in self.invoice_items.all())

        # Calculer le rabais selon la logique simplifiée
        if self.is_dealer_discount:
            # Rabais concessionnaire : 30%
            self.discount_percentage = Decimal('30.00')
        # Si pas de rabais concessionnaire, utiliser le pourcentage manuel ou par défaut du client
        elif self.discount_percentage == Decimal('0.00') and self.client.default_discount_percentage > Decimal('0.00'):
            # Appliquer le rabais par défaut du client si aucun rabais manuel
            self.discount_percentage = self.client.default_discount_percentage

        # Calculer le montant du rabais
        self.discount_amount = self.subtotal * (self.discount_percentage / Decimal('100'))

        # Sous-total après rabais (base pour le calcul des taxes)
        subtotal_after_discount = self.subtotal - self.discount_amount

        # Calculer les taxes (toujours calculées au Québec)
        # TPS (GST) : 5%
        # TVQ (QST) : 9.975%
        self.gst_amount = subtotal_after_discount * Decimal('0.05')  # TPS 5%
        self.qst_amount = subtotal_after_discount * Decimal('0.09975')  # TVQ 9.975%

        self.total_amount = subtotal_after_discount + self.gst_amount + self.qst_amount
        self.save()

    @property
    def subtotal_after_discount(self):
        """Sous-total après application du rabais"""
        return self.subtotal - self.discount_amount

    @property
    def is_paid(self):
        return self.status == 'paid'

# Propriété is_overdue supprimée car plus de date d'échéance

    def apply_client_default_discount(self):
        """Appliquer le rabais par défaut du client si aucun rabais n'est déjà appliqué"""
        if (self.discount_percentage == Decimal('0.00') and
            not self.is_dealer_discount and
            self.client.default_discount_percentage > Decimal('0.00')):
            self.discount_percentage = self.client.default_discount_percentage
            self.save()

    def force_apply_client_default_discount(self):
        """Forcer l'application du rabais par défaut du client (même si un rabais existe déjà)"""
        if (not self.is_dealer_discount and
            self.client.default_discount_percentage > Decimal('0.00')):
            self.discount_percentage = self.client.default_discount_percentage
            self.save()

    @property
    def subtotal_after_discount(self):
        """Sous-total après application du rabais"""
        return self.subtotal - self.discount_amount


class InvoiceItem(models.Model):
    """Modèle pour les éléments d'une facture"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_items', verbose_name="Facture")

    # Type d'élément : service ou article d'inventaire
    ITEM_TYPE_CHOICES = [
        ('service', 'Service'),
        ('inventory', 'Article d\'inventaire'),
    ]
    item_type = models.CharField(
        max_length=20,
        choices=ITEM_TYPE_CHOICES,
        default='service',
        verbose_name="Type d'élément"
    )

    # Relations (une seule sera utilisée selon le type)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Service"
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Article d'inventaire"
    )

    # Détails de l'élément
    description = models.TextField(blank=True, null=True, verbose_name="Description personnalisée")
    # Quantité supprimée - un seul service par ligne de facture
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Élément de facture"
        verbose_name_plural = "Éléments de facture"
        ordering = ['invoice', 'id']

    def __str__(self):
        if self.item_type == 'service' and self.service:
            return f"{self.service.name} - {self.invoice.invoice_number}"
        elif self.item_type == 'inventory' and self.inventory_item:
            return f"{self.inventory_item.name} - {self.invoice.invoice_number}"
        return f"Élément - {self.invoice.invoice_number}"

    @property
    def total_price(self):
        """Le prix total est simplement le prix (pas de quantité)"""
        return self.price if self.price is not None else Decimal('0.00')

    @property
    def item_name(self):
        """Retourner le nom de l'élément selon son type"""
        if self.item_type == 'service' and self.service:
            return self.service.name
        elif self.item_type == 'inventory' and self.inventory_item:
            return self.inventory_item.name
        return "Élément non défini"

    def save(self, *args, **kwargs):
        # Validation : s'assurer qu'un seul type d'élément est défini
        if self.item_type == 'service':
            self.inventory_item = None
            # Appliquer automatiquement le prix du service si pas encore défini
            if not self.price and self.service:
                self.price = self.service.default_price
        elif self.item_type == 'inventory':
            self.service = None
            # Appliquer automatiquement le prix de l'article si pas encore défini
            if not self.price and self.inventory_item:
                self.price = self.inventory_item.unit_price

        super().save(*args, **kwargs)

        # Décrémenter le stock si c'est un article d'inventaire et que la facture est finalisée
        # Note: Plus de quantité, donc on décrémente de 1
        if (self.item_type == 'inventory' and self.inventory_item and
            self.invoice.status in ['sent', 'paid']):
            self.inventory_item.quantity_in_stock -= 1
            self.inventory_item.save()

        # Recalculer les totaux de la facture
        self.invoice.calculate_totals()

    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError

        if self.item_type == 'service' and not self.service:
            raise ValidationError("Un service doit être sélectionné pour un élément de type service.")
        elif self.item_type == 'inventory' and not self.inventory_item:
            raise ValidationError("Un article d'inventaire doit être sélectionné pour un élément de type inventaire.")

        if self.item_type == 'inventory' and self.inventory_item:
            if self.quantity > self.inventory_item.quantity_in_stock:
                raise ValidationError(f"Quantité insuffisante en stock. Stock disponible: {self.inventory_item.quantity_in_stock}")


class Expense(models.Model):
    """Modèle pour les dépenses de l'entreprise"""
    description = models.CharField(max_length=200, verbose_name="Description")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant"
    )
    expense_date = models.DateField(verbose_name="Date de dépense")

    # Relation avec le fournisseur
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        verbose_name="Fournisseur"
    )

    # Catégories de dépenses
    EXPENSE_CATEGORY_CHOICES = [
        ('materials', 'Matériaux'),
        ('tools', 'Outils'),
        ('inventory', 'Inventaire/Marchandises'),
        ('rent', 'Loyer'),
        ('utilities', 'Services publics'),
        ('insurance', 'Assurance'),
        ('marketing', 'Marketing'),
        ('fuel', 'Carburant'),
        ('maintenance', 'Entretien'),
        ('office', 'Fournitures de bureau'),
        ('professional', 'Services professionnels'),
        ('other', 'Autre'),
    ]
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORY_CHOICES, default='other', verbose_name="Catégorie")

    # Taxes sur la dépense
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="TPS payée"
    )
    qst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="TVQ payée"
    )

    # Reçu numérisé
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True, verbose_name="Reçu")

    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    # Archivage
    archived_fiscal_year = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Année fiscale archivée",
        help_text="Si défini, cette dépense fait partie d'une année fiscale archivée"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.description} - {self.amount}$ ({self.expense_date})"

    @property
    def total_with_taxes(self):
        amount = self.amount or Decimal('0.00')
        gst = self.gst_amount or Decimal('0.00')
        qst = self.qst_amount or Decimal('0.00')
        return amount + gst + qst


class Payment(models.Model):
    """Modèle pour les paiements reçus"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name="Facture")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant"
    )
    payment_date = models.DateField(verbose_name="Date de paiement")

    # Méthodes de paiement
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Comptant'),
        ('check', 'Chèque'),
        ('credit_card', 'Carte de crédit'),
        ('debit_card', 'Carte de débit'),
        ('bank_transfer', 'Virement bancaire'),
        ('other', 'Autre'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash', verbose_name="Méthode de paiement")

    # Référence (numéro de chèque, transaction, etc.)
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="Référence")

    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"Paiement {self.amount}$ - {self.invoice.invoice_number} ({self.payment_date})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Vérifier si la facture est entièrement payée
        total_payments = sum(payment.amount for payment in self.invoice.payments.all())
        if total_payments >= self.invoice.total_amount:
            self.invoice.status = 'paid'
            self.invoice.save()


class FiscalYearArchive(models.Model):
    """Modèle pour gérer les archives des années fiscales"""
    fiscal_year = models.IntegerField(
        verbose_name="Année fiscale",
        help_text="Année de fin de la période fiscale (ex: 2024 pour la période 2023-2024)"
    )
    archive_date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'archivage")

    # Statistiques de l'année archivée
    total_invoices = models.IntegerField(default=0, verbose_name="Nombre de factures")
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Chiffre d'affaires total"
    )
    total_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total des dépenses"
    )
    total_gst_collected = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="TPS perçue"
    )
    total_qst_collected = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="TVQ perçue"
    )
    total_gst_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="TPS payée"
    )
    total_qst_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="TVQ payée"
    )

    # Métadonnées
    archived_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Archivé par"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    # Statut de l'archive
    is_locked = models.BooleanField(
        default=False,
        verbose_name="Verrouillé",
        help_text="Une fois verrouillé, l'archive ne peut plus être modifiée"
    )

    class Meta:
        verbose_name = "Archive d'année fiscale"
        verbose_name_plural = "Archives d'années fiscales"
        unique_together = ['fiscal_year']
        ordering = ['-fiscal_year']

    def __str__(self):
        return f"Archive année fiscale {self.fiscal_year}"

    def get_fiscal_period_display(self):
        """Retourne la période fiscale sous forme lisible"""
        company_profile = CompanyProfile.objects.first()
        if company_profile:
            start_date, end_date = company_profile.get_fiscal_year_period(self.fiscal_year)
            return f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
        return f"Année fiscale {self.fiscal_year}"

    def calculate_net_profit(self):
        """Calculer le bénéfice net"""
        return self.total_revenue - self.total_expenses

    def get_tax_summary(self):
        """Retourner un résumé des taxes"""
        return {
            'gst_net': self.total_gst_collected - self.total_gst_paid,
            'qst_net': self.total_qst_collected - self.total_qst_paid,
            'total_collected': self.total_gst_collected + self.total_qst_collected,
            'total_paid': self.total_gst_paid + self.total_qst_paid,
        }


class RecurringExpense(models.Model):
    """Modèle pour les dépenses récurrentes"""
    name = models.CharField(max_length=200, verbose_name="Nom de la dépense récurrente")
    description = models.CharField(max_length=200, verbose_name="Description")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant"
    )

    # Relation avec le fournisseur
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recurring_expenses',
        verbose_name="Fournisseur"
    )

    # Catégorie
    category = models.CharField(
        max_length=20,
        choices=Expense.EXPENSE_CATEGORY_CHOICES,
        default='other',
        verbose_name="Catégorie"
    )

    # Fréquence
    FREQUENCY_CHOICES = [
        ('daily', 'Quotidienne'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuelle'),
        ('quarterly', 'Trimestrielle'),
        ('yearly', 'Annuelle'),
    ]
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='monthly',
        verbose_name="Fréquence"
    )

    # Dates
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(blank=True, null=True, verbose_name="Date de fin (optionnelle)")
    next_due_date = models.DateField(verbose_name="Prochaine échéance")

    # Taxes
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="TPS"
    )
    qst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="TVQ"
    )

    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dépense récurrente"
        verbose_name_plural = "Dépenses récurrentes"
        ordering = ['next_due_date', 'name']

    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"

    def calculate_next_due_date(self):
        """Calculer la prochaine date d'échéance"""
        if self.frequency == 'daily':
            return self.next_due_date + timedelta(days=1)
        elif self.frequency == 'weekly':
            return self.next_due_date + timedelta(weeks=1)
        elif self.frequency == 'monthly':
            return self.next_due_date + relativedelta(months=1)
        elif self.frequency == 'quarterly':
            return self.next_due_date + relativedelta(months=3)
        elif self.frequency == 'yearly':
            return self.next_due_date + relativedelta(years=1)
        return self.next_due_date

    def create_expense(self):
        """Créer une dépense basée sur cette dépense récurrente"""
        expense = Expense.objects.create(
            description=self.description,
            amount=self.amount,
            expense_date=self.next_due_date,
            supplier=self.supplier,
            category=self.category,
            gst_amount=self.gst_amount,
            qst_amount=self.qst_amount,
            notes=f"Dépense récurrente: {self.name}"
        )

        # Mettre à jour la prochaine échéance
        self.next_due_date = self.calculate_next_due_date()
        self.save()

        return expense

    def is_due(self):
        """Vérifier si la dépense est due"""
        return date.today() >= self.next_due_date and self.is_active

    @property
    def total_with_taxes(self):
        """Calculer le total avec taxes"""
        return self.amount + self.gst_amount + self.qst_amount


class StockReceipt(models.Model):
    """Modèle pour les bons de réception de marchandises"""
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de bon de réception"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='stock_receipts',
        verbose_name="Fournisseur"
    )
    receipt_date = models.DateField(
        verbose_name="Date de réception"
    )
    supplier_invoice_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Numéro de facture fournisseur"
    )

    # Montants
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Sous-total"
    )
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="TPS"
    )
    qst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="TVQ"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant total"
    )

    # Statut
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('received', 'Reçu'),
        ('processed', 'Traité'),
        ('cancelled', 'Annulé'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Statut"
    )

    # Dépense créée automatiquement
    expense = models.OneToOneField(
        Expense,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_receipt',
        verbose_name="Dépense associée"
    )

    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bon de réception"
        verbose_name_plural = "Bons de réception"
        ordering = ['-receipt_date', '-created_at']

    def __str__(self):
        return f"{self.receipt_number} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        # Générer un numéro de bon de réception si pas défini
        if not self.receipt_number:
            from datetime import date
            today = date.today()
            last_receipt = StockReceipt.objects.filter(
                receipt_date__year=today.year
            ).order_by('-receipt_number').first()

            if last_receipt and last_receipt.receipt_number.startswith(f'BR-{today.year}-'):
                try:
                    last_num = int(last_receipt.receipt_number.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1

            self.receipt_number = f'BR-{today.year}-{new_num:04d}'

        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculer les totaux basés sur les éléments"""
        items = self.receipt_items.all()
        self.subtotal = sum(item.total_price for item in items)

        # Calculer les taxes (si applicable)
        # Pour simplifier, on peut utiliser les taux standards
        if self.supplier and hasattr(self.supplier, 'is_tax_applicable'):
            # Logique de calcul des taxes selon le fournisseur
            pass

        self.total_amount = self.subtotal + self.gst_amount + self.qst_amount
        self.save()

    def process_receipt(self):
        """Traiter le bon de réception : mettre à jour l'inventaire et créer la dépense"""
        if self.status != 'received':
            return False

        # Mettre à jour l'inventaire
        for item in self.receipt_items.all():
            inventory_item = item.inventory_item
            inventory_item.quantity_in_stock += item.quantity
            inventory_item.unit_cost = item.purchase_price  # Mettre à jour le prix d'achat
            inventory_item.save()

        # Créer la dépense associée
        if not self.expense:
            expense = Expense.objects.create(
                description=f"Réception de marchandises - {self.receipt_number}",
                supplier=self.supplier,
                amount=self.subtotal,
                expense_date=self.receipt_date,
                category='inventory',
                gst_amount=self.gst_amount,
                qst_amount=self.qst_amount,
                notes=f"Dépense créée automatiquement depuis le bon de réception {self.receipt_number}"
            )
            self.expense = expense

        # Marquer comme traité
        self.status = 'processed'
        self.save()

        return True


class StockReceiptItem(models.Model):
    """Modèle pour les lignes d'un bon de réception"""
    stock_receipt = models.ForeignKey(
        StockReceipt,
        on_delete=models.CASCADE,
        related_name='receipt_items',
        verbose_name="Bon de réception"
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        verbose_name="Article"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Quantité reçue"
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix d'achat unitaire"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Élément de réception"
        verbose_name_plural = "Éléments de réception"
        unique_together = ['stock_receipt', 'inventory_item']

    def __str__(self):
        return f"{self.inventory_item.name} - {self.quantity} unités"

    @property
    def total_price(self):
        """Calculer le prix total pour cette ligne"""
        return self.quantity * self.purchase_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculer les totaux du bon de réception
        self.stock_receipt.calculate_totals()


class Appointment(models.Model):
    """Modèle pour les rendez-vous"""
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    # Relations
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name="Client"
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name="Véhicule"
    )

    # Dates et heures
    start_datetime = models.DateTimeField(verbose_name="Date et heure de début")
    end_datetime = models.DateTimeField(verbose_name="Date et heure de fin")

    # Statut
    STATUS_CHOICES = [
        ('scheduled', 'Planifié'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('no_show', 'Absence'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name="Statut"
    )

    # Services prévus
    estimated_services = models.ManyToManyField(
        Service,
        blank=True,
        related_name='appointments',
        verbose_name="Services estimés"
    )

    # Prix estimé
    estimated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix estimé"
    )

    # Facture liée (si créée)
    invoice = models.OneToOneField(
        'Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointment',
        verbose_name="Facture"
    )

    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.title} - {self.client.full_name} ({self.start_datetime.strftime('%d/%m/%Y %H:%M')})"

    @property
    def duration(self):
        """Calculer la durée du rendez-vous"""
        return self.end_datetime - self.start_datetime

    @property
    def is_past(self):
        """Vérifier si le rendez-vous est passé"""
        return self.end_datetime < datetime.now()

    @property
    def is_today(self):
        """Vérifier si le rendez-vous est aujourd'hui"""
        return self.start_datetime.date() == date.today()

    def can_create_invoice(self):
        """Vérifier si une facture peut être créée"""
        return self.status in ['completed'] and not self.invoice

    def create_invoice_from_appointment(self):
        """Créer une facture basée sur ce rendez-vous"""
        if not self.can_create_invoice():
            return None

        # Créer la facture
        invoice = Invoice.objects.create(
            client=self.client,
            vehicle=self.vehicle,
            invoice_date=date.today(),
            notes=f"Facture créée depuis le rendez-vous: {self.title}"
        )

        # Ajouter les services estimés comme éléments de facture
        for service in self.estimated_services.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                service=service,
                quantity=Decimal('1.00'),
                unit_price=service.default_price,
                description=f"Service du rendez-vous: {self.title}"
            )

        # Calculer les totaux
        invoice.calculate_totals()

        # Lier la facture au rendez-vous
        self.invoice = invoice
        self.save()


# ==================== GESTION DES SOUMISSIONS ====================

class Quote(models.Model):
    """Modèle pour les soumissions/devis"""

    QUOTE_STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
        ('expired', 'Expirée'),
        ('converted', 'Convertie en facture'),
    ]



    # Informations de base
    quote_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de soumission")
    date = models.DateField(default=date.today, verbose_name="Date de création")
    valid_until = models.DateField(verbose_name="Valide jusqu'au")
    status = models.CharField(max_length=20, choices=QUOTE_STATUS_CHOICES, default='draft', verbose_name="Statut")

    # Relations
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='quotes', verbose_name="Client")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes', verbose_name="Véhicule")

    # Montants
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Sous-total")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name="Pourcentage de rabais")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Montant du rabais")
    is_dealer_discount = models.BooleanField(default=False, verbose_name="Rabais concessionnaire")
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Montant TPS")
    qst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Montant TVQ")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Montant total")

    # Informations supplémentaires
    notes = models.TextField(blank=True, null=True, verbose_name="Notes internes")
    terms_conditions = models.TextField(blank=True, null=True, verbose_name="Conditions générales")

    # Conversion
    converted_invoice = models.OneToOneField('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='source_quote', verbose_name="Facture convertie")

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Soumission"
        verbose_name_plural = "Soumissions"
        ordering = ['-date', '-quote_number']

    def __str__(self):
        return f"{self.quote_number} - {self.client.name}"

    def save(self, *args, **kwargs):
        if not self.quote_number:
            # Générer le numéro de soumission automatiquement
            today = date.today()
            existing_quotes = Quote.objects.filter(
                quote_number__startswith=f'QUO-{today.year}'
            ).count()
            new_num = existing_quotes + 1
            self.quote_number = f'QUO-{today.year}-{new_num:04d}'

        # Définir la date de validité par défaut (30 jours)
        if not self.valid_until:
            self.valid_until = self.date + timedelta(days=30)

        # Appliquer le rabais par défaut du client si aucun rabais n'est défini
        if (not self.is_dealer_discount and
            self.discount_percentage == Decimal('0.00') and
            self.client and
            self.client.default_discount_percentage > Decimal('0.00')):
            self.discount_percentage = self.client.default_discount_percentage

        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculer les totaux de la soumission"""
        self.subtotal = sum(item.total_price for item in self.quote_items.all())

        # Calculer le rabais selon la logique simplifiée
        if self.is_dealer_discount:
            # Rabais concessionnaire : 30%
            self.discount_percentage = Decimal('30.00')
        # Si pas de rabais concessionnaire, utiliser le pourcentage manuel ou par défaut du client
        elif self.discount_percentage == Decimal('0.00') and self.client.default_discount_percentage > Decimal('0.00'):
            # Appliquer le rabais par défaut du client si aucun rabais manuel
            self.discount_percentage = self.client.default_discount_percentage

        # Calculer le montant du rabais
        self.discount_amount = self.subtotal * (self.discount_percentage / Decimal('100'))

        # Sous-total après rabais (base pour le calcul des taxes)
        subtotal_after_discount = self.subtotal - self.discount_amount

        # Calculer les taxes (toujours calculées au Québec)
        # TPS (GST) : 5%
        # TVQ (QST) : 9.975%
        self.gst_amount = subtotal_after_discount * Decimal('0.05')  # TPS 5%
        self.qst_amount = subtotal_after_discount * Decimal('0.09975')  # TVQ 9.975%

        self.total_amount = subtotal_after_discount + self.gst_amount + self.qst_amount
        self.save()

    @property
    def subtotal_after_discount(self):
        """Sous-total après application du rabais"""
        return self.subtotal - self.discount_amount

    @property
    def is_expired(self):
        """Vérifier si la soumission est expirée"""
        return date.today() > self.valid_until and self.status not in ['accepted', 'converted', 'rejected']

    def can_be_converted(self):
        """Vérifier si la soumission peut être convertie en facture"""
        return self.status in ['sent', 'accepted'] and not self.converted_invoice

    def convert_to_invoice(self):
        """Convertir la soumission en facture"""
        if not self.can_be_converted():
            raise ValueError("Cette soumission ne peut pas être convertie en facture")

        # Créer la facture
        invoice = Invoice.objects.create(
            client=self.client,
            vehicle=self.vehicle,
            discount_percentage=self.discount_percentage,
            is_dealer_discount=self.is_dealer_discount,
            notes=self.notes
        )

        # Copier tous les éléments de la soumission vers la facture
        for quote_item in self.quote_items.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                item_type=quote_item.item_type,
                service=quote_item.service,
                inventory_item=quote_item.inventory_item,
                description=quote_item.description,
                price=quote_item.price
            )

        # Calculer les totaux de la facture
        invoice.calculate_totals()

        # Marquer la soumission comme convertie
        self.status = 'converted'
        self.converted_invoice = invoice
        self.save()

        return invoice


class QuoteItem(models.Model):
    """Modèle pour les éléments d'une soumission"""

    ITEM_TYPE_CHOICES = [
        ('service', 'Service'),
        ('inventory', 'Article d\'inventaire'),
    ]

    # Relations
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='quote_items', verbose_name="Soumission")
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='service', verbose_name="Type d'élément")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Service")
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Article d'inventaire")

    # Détails
    description = models.TextField(blank=True, null=True, verbose_name="Description personnalisée")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")

    # Détails spécifiques au lettrage (stockés en JSON)
    lettering_details = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Détails du lettrage",
        help_text="Détails du calcul de lettrage (surface, matériaux, heures, etc.)"
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Élément de soumission"
        verbose_name_plural = "Éléments de soumission"
        ordering = ['id']

    def __str__(self):
        if self.service:
            return f"{self.service.name} - {self.quote.quote_number}"
        elif self.inventory_item:
            return f"{self.inventory_item.name} - {self.quote.quote_number}"
        return f"Élément personnalisé - {self.quote.quote_number}"

    @property
    def total_price(self):
        """Le prix total est simplement le prix (pas de quantité)"""
        return self.price if self.price is not None else Decimal('0.00')

    def save(self, *args, **kwargs):
        # Auto-remplir le prix selon le type d'élément
        if self.service and not self.price:
            self.price = self.service.default_price
        elif self.inventory_item and not self.price:
            self.price = self.inventory_item.selling_price

        super().save(*args, **kwargs)

        # Recalculer les totaux de la soumission
        if self.quote_id:
            self.quote.calculate_totals()


# ==================== CALCULATEUR DE LETTRAGE ====================

class Material(models.Model):
    """Matériaux pour le lettrage (vinyles, laminations, encres)"""

    MATERIAL_TYPES = [
        ('vinyle', 'Vinyle'),
        ('vinyle_decoupe', 'Vinyle Découpé'),
        ('lamination', 'Lamination'),
        ('encre', 'Encre'),
        ('autre', 'Autre'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Nom du matériau",
        help_text="Ex: Vinyle Coulé 3M IJ180Cv3, Lamination Lustrée"
    )
    type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPES,
        verbose_name="Type de matériau"
    )
    cost_per_sqm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Coût par m²",
        help_text="Coût par mètre carré en CAD"
    )
    supplier = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Fournisseur"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Informations supplémentaires sur ce matériau"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Matériau actif"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Matériau"
        verbose_name_plural = "Matériaux"
        ordering = ['type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()}) - {self.cost_per_sqm}$/m²"


class LaborRate(models.Model):
    """Taux horaires pour différents types de tâches"""

    TASK_TYPES = [
        ('conception', 'Conception Graphique'),
        ('installation', 'Installation'),
        ('echenillage', 'Échenillage'),
        ('preparation', 'Préparation'),
        ('finition', 'Finition'),
    ]

    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPES,
        unique=True,
        verbose_name="Type de tâche"
    )
    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Taux horaire",
        help_text="Votre taux facturable par heure en CAD"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Description de ce type de tâche"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Taux actif"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Taux horaire"
        verbose_name_plural = "Taux horaires"
        ordering = ['task_type']

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.hourly_rate}$/h"


class OverheadConfiguration(models.Model):
    """Configuration des frais généraux pour le lettrage"""

    name = models.CharField(
        max_length=100,
        verbose_name="Nom de la configuration",
        help_text="Ex: Configuration Standard, Configuration Premium"
    )
    hourly_overhead_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Frais généraux par heure",
        help_text="Montant fixe en CAD à ajouter pour chaque heure de travail"
    )
    fixed_overhead_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Frais fixes",
        help_text="Montant fixe en CAD à ajouter à chaque projet"
    )
    percentage_overhead = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Pourcentage de frais généraux",
        help_text="Pourcentage du coût total à ajouter comme frais généraux"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Configuration active"
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Configuration par défaut"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration frais généraux"
        verbose_name_plural = "Configurations frais généraux"
        ordering = ['-is_default', 'name']

    def __str__(self):
        default_text = " (Défaut)" if self.is_default else ""
        return f"{self.name}{default_text}"

    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule configuration par défaut
        if self.is_default:
            OverheadConfiguration.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class LetteringQuote(models.Model):
    """Soumission de lettrage avec calcul automatique"""

    # Informations de base
    client = models.ForeignKey('Client', on_delete=models.CASCADE, verbose_name="Client")
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, verbose_name="Véhicule")

    # Paramètres du projet
    surface_area = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Surface totale (m²)",
        help_text="Surface totale à couvrir en mètres carrés"
    )
    waste_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.0,
        verbose_name="Taux de perte (%)",
        help_text="Pourcentage de perte de matériau"
    )

    # Matériaux sélectionnés
    vinyl_material = models.ForeignKey(
        'Material',
        on_delete=models.PROTECT,
        related_name='vinyl_quotes',
        limit_choices_to={'type': 'vinyle'},
        verbose_name="Vinyle"
    )
    lamination_material = models.ForeignKey(
        'Material',
        on_delete=models.PROTECT,
        related_name='lamination_quotes',
        limit_choices_to={'type': 'lamination'},
        blank=True,
        null=True,
        verbose_name="Lamination"
    )

    # Temps de travail
    design_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="Heures de conception",
        help_text="Temps estimé pour la conception graphique"
    )
    installation_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Heures d'installation",
        help_text="Temps estimé pour l'installation"
    )

    # Configuration utilisée
    overhead_config = models.ForeignKey(
        'OverheadConfiguration',
        on_delete=models.PROTECT,
        verbose_name="Configuration frais généraux"
    )

    # Marge bénéficiaire
    profit_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.0,
        verbose_name="Marge bénéficiaire (%)",
        help_text="Marge bénéficiaire en pourcentage"
    )

    # Coûts calculés (en lecture seule)
    material_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Coût matériaux",
        help_text="Coût total des matériaux calculé automatiquement"
    )
    labor_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Coût main-d'œuvre",
        help_text="Coût total de la main-d'œuvre calculé automatiquement"
    )
    overhead_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Frais généraux",
        help_text="Frais généraux calculés automatiquement"
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Coût total",
        help_text="Coût total avant marge"
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Prix avant taxes",
        help_text="Prix avec marge bénéficiaire avant taxes"
    )
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Montant TPS",
        help_text="Montant de la TPS (5%)"
    )
    qst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Montant TVQ",
        help_text="Montant de la TVQ (9.975%)"
    )
    final_price_with_taxes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Prix final avec taxes",
        help_text="Prix final incluant toutes les taxes"
    )

    # Métadonnées
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Notes supplémentaires sur ce projet"
    )
    is_converted_to_quote = models.BooleanField(
        default=False,
        verbose_name="Converti en soumission",
        help_text="Indique si ce calcul a été converti en soumission officielle"
    )
    related_quote = models.ForeignKey(
        'Quote',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Soumission liée",
        help_text="Soumission officielle créée à partir de ce calcul"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Calcul de lettrage"
        verbose_name_plural = "Calculs de lettrage"
        ordering = ['-created_at']

    def __str__(self):
        return f"Lettrage {self.vehicle} - {self.final_price_with_taxes}$ taxes incl. ({self.created_at.strftime('%Y-%m-%d')})"

    def calculate_costs(self):
        """Calcule tous les coûts automatiquement"""
        from decimal import Decimal

        # 1. Coût des matériaux
        surface_with_waste = self.surface_area * (1 + self.waste_percentage / 100)

        # Coût du vinyle
        vinyl_cost = surface_with_waste * self.vinyl_material.cost_per_sqm

        # Coût de la lamination (si applicable)
        lamination_cost = Decimal('0')
        if self.lamination_material:
            lamination_cost = surface_with_waste * self.lamination_material.cost_per_sqm

        self.material_cost = vinyl_cost + lamination_cost

        # 2. Coût de la main-d'œuvre
        design_rate = LaborRate.objects.filter(task_type='conception', is_active=True).first()
        installation_rate = LaborRate.objects.filter(task_type='installation', is_active=True).first()

        design_cost = Decimal('0')
        if design_rate and self.design_hours:
            design_cost = self.design_hours * design_rate.hourly_rate

        installation_cost = Decimal('0')
        if installation_rate and self.installation_hours:
            # Appliquer le multiplicateur de complexité du véhicule
            complexity_multiplier = self.vehicle.vehicle_type.complexity_multiplier if self.vehicle.vehicle_type else Decimal('1.0')
            installation_cost = self.installation_hours * installation_rate.hourly_rate * complexity_multiplier

        self.labor_cost = design_cost + installation_cost

        # 3. Frais généraux
        total_hours = self.design_hours + self.installation_hours
        hourly_overhead = total_hours * self.overhead_config.hourly_overhead_cost
        fixed_overhead = self.overhead_config.fixed_overhead_cost

        # Coût de base pour le calcul du pourcentage
        base_cost = self.material_cost + self.labor_cost
        percentage_overhead = base_cost * (self.overhead_config.percentage_overhead / 100)

        self.overhead_cost = hourly_overhead + fixed_overhead + percentage_overhead

        # 4. Coût total
        self.total_cost = self.material_cost + self.labor_cost + self.overhead_cost

        # 5. Prix avec marge (avant taxes)
        self.final_price = self.total_cost * (1 + self.profit_margin / 100)

        # 6. Calcul des taxes (Québec)
        gst_rate = Decimal('0.05')  # TPS 5%
        qst_rate = Decimal('0.09975')  # TVQ 9.975%

        self.gst_amount = self.final_price * gst_rate
        self.qst_amount = self.final_price * qst_rate
        self.final_price_with_taxes = self.final_price + self.gst_amount + self.qst_amount

        return {
            'material_cost': self.material_cost,
            'labor_cost': self.labor_cost,
            'overhead_cost': self.overhead_cost,
            'total_cost': self.total_cost,
            'final_price': self.final_price,
            'gst_amount': self.gst_amount,
            'qst_amount': self.qst_amount,
            'final_price_with_taxes': self.final_price_with_taxes
        }

    def save(self, *args, **kwargs):
        # Calculer automatiquement les coûts avant la sauvegarde
        self.calculate_costs()
        super().save(*args, **kwargs)

    def get_cost_breakdown(self):
        """Retourne un détail des coûts pour l'affichage"""
        return {
            'surface_with_waste': self.surface_area * (1 + self.waste_percentage / 100),
            'vinyl_cost': self.surface_area * (1 + self.waste_percentage / 100) * self.vinyl_material.cost_per_sqm,
            'lamination_cost': (self.surface_area * (1 + self.waste_percentage / 100) * self.lamination_material.cost_per_sqm) if self.lamination_material else 0,
            'design_cost': self.design_hours * LaborRate.objects.filter(task_type='conception', is_active=True).first().hourly_rate if LaborRate.objects.filter(task_type='conception', is_active=True).exists() else 0,
            'installation_cost': self.installation_hours * LaborRate.objects.filter(task_type='installation', is_active=True).first().hourly_rate * (self.vehicle.vehicle_type.complexity_multiplier if self.vehicle.vehicle_type else 1) if LaborRate.objects.filter(task_type='installation', is_active=True).exists() else 0,
            'complexity_multiplier': self.vehicle.vehicle_type.complexity_multiplier if self.vehicle.vehicle_type else 1,
        }
