from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil d'entreprise"
        verbose_name_plural = "Profils d'entreprise"

    def __str__(self):
        return self.name


class Client(models.Model):
    """Modèle pour les clients du garage"""
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom de famille")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    address = models.TextField(blank=True, null=True, verbose_name="Adresse")

    # Informations supplémentaires
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

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
    vin = models.CharField(max_length=17, blank=True, null=True, verbose_name="Numéro VIN")

    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        ordering = ['client__last_name', 'make', 'model']

    def __str__(self):
        return f"{self.year} {self.make} {self.model} - {self.client.full_name}"


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
        ('tinting', 'Vitres teintées'),
        ('ppf', 'Protection pare-pierre (PPF)'),
        ('wrapping', 'Wrapping'),
        ('hydrophobic', 'Protection hydrophobe'),
        ('detailing', 'Esthétique (compound, polissage)'),
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


class InventoryItem(models.Model):
    """Modèle pour la gestion de l'inventaire"""
    name = models.CharField(max_length=200, verbose_name="Nom de l'article")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    sku = models.CharField(max_length=50, unique=True, verbose_name="Code SKU")

    # Quantités et prix
    quantity_in_stock = models.IntegerField(default=0, verbose_name="Quantité en stock")
    minimum_stock_level = models.IntegerField(default=0, verbose_name="Niveau de stock minimum")
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
    def total_value(self):
        return self.quantity_in_stock * self.unit_cost


class Invoice(models.Model):
    """Modèle pour les factures"""
    # Numérotation automatique
    invoice_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de facture")

    # Relations
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices', verbose_name="Client")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Véhicule")

    # Dates
    invoice_date = models.DateField(verbose_name="Date de facture")
    due_date = models.DateField(verbose_name="Date d'échéance")

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

    # Statut
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
        ('cancelled', 'Annulée'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")

    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

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

        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculer les totaux de la facture"""
        self.subtotal = sum(item.total_price for item in self.invoice_items.all())

        # Calculer les taxes si l'entreprise est enregistrée
        company_profile = CompanyProfile.objects.first()
        if company_profile and company_profile.is_tax_registered:
            self.gst_amount = self.subtotal * Decimal('0.05')  # TPS 5%
            self.qst_amount = self.subtotal * Decimal('0.09975')  # TVQ 9.975%
        else:
            self.gst_amount = Decimal('0.00')
            self.qst_amount = Decimal('0.00')

        self.total_amount = self.subtotal + self.gst_amount + self.qst_amount
        self.save()

    @property
    def is_paid(self):
        return self.status == 'paid'

    @property
    def is_overdue(self):
        from datetime import date
        return self.due_date < date.today() and self.status not in ['paid', 'cancelled']


class InvoiceItem(models.Model):
    """Modèle pour les éléments d'une facture"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_items', verbose_name="Facture")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Service")

    # Détails de l'élément
    description = models.TextField(blank=True, null=True, verbose_name="Description personnalisée")
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Quantité"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix unitaire"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Élément de facture"
        verbose_name_plural = "Éléments de facture"
        ordering = ['invoice', 'id']

    def __str__(self):
        return f"{self.service.name} - {self.invoice.invoice_number}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        # Utiliser le prix par défaut du service si pas spécifié
        if not self.unit_price:
            self.unit_price = self.service.default_price
        super().save(*args, **kwargs)

        # Recalculer les totaux de la facture
        self.invoice.calculate_totals()


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

    # Catégories de dépenses
    EXPENSE_CATEGORY_CHOICES = [
        ('materials', 'Matériaux'),
        ('tools', 'Outils'),
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
        return self.amount + self.gst_amount + self.qst_amount


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
