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

    # Relation avec le fournisseur
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_items',
        verbose_name="Fournisseur"
    )

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
        if self.unit_cost is not None:
            return self.quantity_in_stock * self.unit_cost
        return 0


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
        if self.item_type == 'service' and self.service:
            return f"{self.service.name} - {self.invoice.invoice_number}"
        elif self.item_type == 'inventory' and self.inventory_item:
            return f"{self.inventory_item.name} - {self.invoice.invoice_number}"
        return f"Élément - {self.invoice.invoice_number}"

    @property
    def total_price(self):
        if self.unit_price is not None:
            return self.quantity * self.unit_price
        return Decimal('0.00')

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
            if not self.unit_price and self.service:
                self.unit_price = self.service.default_price
        elif self.item_type == 'inventory':
            self.service = None
            if not self.unit_price and self.inventory_item:
                self.unit_price = self.inventory_item.unit_price

        super().save(*args, **kwargs)

        # Décrémenter le stock si c'est un article d'inventaire et que la facture est finalisée
        if (self.item_type == 'inventory' and self.inventory_item and
            self.invoice.status in ['sent', 'paid']):
            self.inventory_item.quantity_in_stock -= int(self.quantity)
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
            due_date=date.today() + timedelta(days=30),
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

        return invoice
