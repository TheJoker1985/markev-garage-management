from django import forms
from django.forms import inlineformset_factory
from .models import (
    CompanyProfile, Client, Vehicle, Service, Invoice, InvoiceItem, Expense,
    Supplier, RecurringExpense, Appointment, InventoryItem, StockReceipt, StockReceiptItem,
    Quote, QuoteItem
)
from datetime import date, timedelta, datetime


class CompanyProfileForm(forms.ModelForm):
    """Formulaire pour le profil de l'entreprise"""
    
    class Meta:
        model = CompanyProfile
        fields = [
            'name', 'address', 'phone', 'email', 'website', 'logo',
            'gst_number', 'qst_number', 'is_tax_registered',
            'fiscal_year_end_month', 'fiscal_year_end_day'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'entreprise'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse complète'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(514) 123-4567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@entreprise.com'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.entreprise.com'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456789RT0001'}),
            'qst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890TQ0001'}),
            'is_tax_registered': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fiscal_year_end_month': forms.Select(attrs={'class': 'form-select'}),
            'fiscal_year_end_day': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '31'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Rendre certains champs obligatoires
        self.fields['name'].required = True
        self.fields['address'].required = True
        self.fields['phone'].required = True
        self.fields['email'].required = True
        
        # Ajouter des labels en français
        self.fields['name'].label = 'Nom de l\'entreprise'
        self.fields['address'].label = 'Adresse complète'
        self.fields['phone'].label = 'Téléphone'
        self.fields['email'].label = 'Email'
        self.fields['website'].label = 'Site web'
        self.fields['logo'].label = 'Logo'
        self.fields['gst_number'].label = 'Numéro TPS'
        self.fields['qst_number'].label = 'Numéro TVQ'
        self.fields['is_tax_registered'].label = 'Inscrit aux taxes'
        
        # Ajouter des textes d'aide
        self.fields['gst_number'].help_text = 'Numéro d\'enregistrement TPS (si applicable)'
        self.fields['qst_number'].help_text = 'Numéro d\'enregistrement TVQ (si applicable)'
        self.fields['is_tax_registered'].help_text = 'Cochez si votre entreprise est inscrite aux taxes TPS/TVQ'


class ClientForm(forms.ModelForm):
    """Formulaire pour la gestion des clients"""

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'notes', 'default_discount_percentage']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(514) 123-4567'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse complète'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes sur le client'}),
            'default_discount_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'max': '100',
                'step': '0.01'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Champs obligatoires
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone'].required = True

        # Labels en français
        self.fields['first_name'].label = 'Prénom'
        self.fields['last_name'].label = 'Nom de famille'
        self.fields['email'].label = 'Email'
        self.fields['phone'].label = 'Téléphone'
        self.fields['address'].label = 'Adresse'
        self.fields['notes'].label = 'Notes'


class VehicleForm(forms.ModelForm):
    """Formulaire pour la gestion des véhicules"""

    # Champs personnalisés pour les dropdowns
    make = forms.CharField(
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_make'}),
        required=True
    )

    model = forms.CharField(
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_model', 'disabled': True}),
        required=True
    )

    class Meta:
        model = Vehicle
        fields = ['client', 'make', 'model', 'year', 'vehicle_type', 'color', 'license_plate', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2030}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Noir, Blanc, etc.'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC 123'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Champs obligatoires
        self.fields['client'].required = True
        self.fields['make'].required = True
        self.fields['model'].required = True
        self.fields['year'].required = True

        # Labels en français
        self.fields['client'].label = 'Client'
        self.fields['make'].label = 'Marque'
        self.fields['model'].label = 'Modèle'
        self.fields['year'].label = 'Année'
        self.fields['vehicle_type'].label = 'Type de véhicule'
        self.fields['color'].label = 'Couleur'
        self.fields['license_plate'].label = 'Plaque d\'immatriculation'
        self.fields['notes'].label = 'Notes'


class ServiceForm(forms.ModelForm):
    """Formulaire pour la gestion des services"""

    class Meta:
        model = Service
        fields = ['name', 'description', 'default_price', 'category', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du service'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description détaillée'}),
            'default_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Champs obligatoires
        self.fields['name'].required = True
        self.fields['default_price'].required = True

        # Labels en français
        self.fields['name'].label = 'Nom du service'
        self.fields['description'].label = 'Description'
        self.fields['default_price'].label = 'Prix par défaut ($)'
        self.fields['category'].label = 'Catégorie'
        self.fields['is_active'].label = 'Service actif'


class InvoiceForm(forms.ModelForm):
    """Formulaire pour la création et modification de factures"""

    # Choix de pourcentages prédéfinis
    DISCOUNT_CHOICES = [
        ('', 'Aucun rabais'),
        ('5.00', '5%'),
        ('10.00', '10%'),
        ('15.00', '15%'),
        ('20.00', '20%'),
        ('25.00', '25%'),
        ('30.00', '30%'),
        ('35.00', '35%'),
        ('40.00', '40%'),
    ]

    discount_percentage = forms.ChoiceField(
        choices=DISCOUNT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_discount_percentage'}),
        label='Rabais'
    )

    is_dealer_discount = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_dealer_discount'}),
        label='Rabais Concessionnaire (30%)'
    )

    class Meta:
        model = Invoice
        fields = ['client', 'vehicle', 'invoice_date', 'payment_method', 'notes', 'discount_percentage', 'is_dealer_discount']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes sur la facture'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Champs obligatoires
        self.fields['client'].required = True
        self.fields['invoice_date'].required = True

        # Labels en français
        self.fields['client'].label = 'Client'
        self.fields['vehicle'].label = 'Véhicule (optionnel)'
        self.fields['invoice_date'].label = 'Date de facture'
        self.fields['notes'].label = 'Notes'

        # Valeurs par défaut
        if not self.instance.pk:  # Nouvelle facture
            self.fields['invoice_date'].initial = date.today()
        else:
            # Pour une facture existante, initialiser les champs de rabais
            if self.instance.discount_percentage:
                self.fields['discount_percentage'].initial = str(self.instance.discount_percentage)
            self.fields['is_dealer_discount'].initial = self.instance.is_dealer_discount

        # Filtrer les véhicules selon le client sélectionné
        client_id = None

        # Récupérer l'ID du client depuis les données POST ou l'instance
        if self.data and 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
            except (ValueError, TypeError):
                client_id = None
        elif self.instance.pk and self.instance.client:
            client_id = self.instance.client.id

        # Filtrer les véhicules selon le client
        if client_id:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(client_id=client_id)
            # Maintenir la sélection du véhicule si elle existe dans les données
            if self.data and 'vehicle' in self.data:
                try:
                    vehicle_id = int(self.data.get('vehicle'))
                    if Vehicle.objects.filter(id=vehicle_id, client_id=client_id).exists():
                        self.fields['vehicle'].initial = vehicle_id
                except (ValueError, TypeError):
                    pass
        else:
            self.fields['vehicle'].queryset = Vehicle.objects.none()


class InvoiceItemForm(forms.ModelForm):
    """Formulaire pour les éléments de facture"""

    class Meta:
        model = InvoiceItem
        fields = ['item_type', 'service', 'inventory_item', 'description', 'price']
        widgets = {
            'item_type': forms.HiddenInput(),  # Champ caché avec valeur par défaut
            'service': forms.Select(attrs={'class': 'form-select'}),
            'inventory_item': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description personnalisée'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        inventory_item = cleaned_data.get('inventory_item')
        price = cleaned_data.get('price')

        # Si aucun service ni article d'inventaire n'est sélectionné, c'est un formulaire vide
        if not service and not inventory_item:
            return cleaned_data  # Formulaire vide, pas d'erreur

        # Si un service ou article est sélectionné, le prix est requis
        if (service or inventory_item) and not price:
            raise forms.ValidationError("Le prix est requis quand un service est sélectionné.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Labels en français
        self.fields['service'].label = 'Service'
        self.fields['description'].label = 'Description'
        self.fields['price'].label = 'Prix ($)'

        # Valeur par défaut pour item_type
        if not self.instance.pk:  # Nouveau formulaire
            self.fields['item_type'].initial = 'service'

        # Filtrer les services et articles d'inventaire actifs seulement
        self.fields['inventory_item'].queryset = InventoryItem.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)


# Formset pour gérer plusieurs éléments de facture
class InvoiceItemFormSet(forms.BaseInlineFormSet):
    """Formset personnalisé pour les éléments de facture"""

    def clean(self):
        """Validation personnalisée du formset"""
        if any(self.errors):
            return

        # Compter les formulaires valides (non vides)
        valid_forms = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                service = form.cleaned_data.get('service')
                inventory_item = form.cleaned_data.get('inventory_item')
                if service or inventory_item:
                    valid_forms += 1

        # Au moins un service doit être sélectionné
        if valid_forms == 0:
            raise forms.ValidationError("Au moins un service doit être ajouté à la facture.")

InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    formset=InvoiceItemFormSet,
    extra=1,  # Une ligne vide par défaut
    min_num=0,  # Pas de minimum requis
    can_delete=True
)


class ExpenseForm(forms.ModelForm):
    """Formulaire pour la gestion des dépenses"""

    class Meta:
        model = Expense
        fields = ['description', 'supplier', 'amount', 'expense_date', 'category', 'gst_amount', 'qst_amount', 'receipt', 'notes']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description de la dépense'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'gst_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00'}),
            'qst_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes sur la dépense'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrer les fournisseurs actifs
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        self.fields['supplier'].empty_label = "Sélectionner un fournisseur (optionnel)"

        # Champs obligatoires
        self.fields['description'].required = True
        self.fields['amount'].required = True
        self.fields['expense_date'].required = True

        # Labels en français
        self.fields['description'].label = 'Description'
        self.fields['amount'].label = 'Montant ($)'
        self.fields['expense_date'].label = 'Date de dépense'
        self.fields['category'].label = 'Catégorie'
        self.fields['gst_amount'].label = 'TPS payée ($)'
        self.fields['qst_amount'].label = 'TVQ payée ($)'
        self.fields['receipt'].label = 'Reçu (fichier)'
        self.fields['notes'].label = 'Notes'

        # Valeur par défaut pour la date
        if not self.instance.pk:
            self.fields['expense_date'].initial = date.today()

        # Textes d'aide
        self.fields['gst_amount'].help_text = 'Montant de TPS payé sur cette dépense'
        self.fields['qst_amount'].help_text = 'Montant de TVQ payé sur cette dépense'
        self.fields['receipt'].help_text = 'Téléversez une copie numérique du reçu'


class SupplierForm(forms.ModelForm):
    """Formulaire pour les fournisseurs"""

    class Meta:
        model = Supplier
        fields = [
            'name', 'contact_person', 'email', 'phone', 'address', 'website',
            'account_number', 'payment_terms', 'category', 'is_active', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du fournisseur'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Personne contact'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@fournisseur.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(514) 123-4567'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse complète'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.fournisseur.com'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de compte'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Net 30, 2/10 Net 30, etc.'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes additionnelles'}),
        }


class RecurringExpenseForm(forms.ModelForm):
    """Formulaire pour les dépenses récurrentes"""

    class Meta:
        model = RecurringExpense
        fields = [
            'name', 'description', 'supplier', 'amount', 'category', 'frequency',
            'start_date', 'end_date', 'next_due_date', 'gst_amount', 'qst_amount',
            'is_active', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la dépense récurrente'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gst_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00'}),
            'qst_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes additionnelles'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les fournisseurs actifs
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        self.fields['supplier'].empty_label = "Sélectionner un fournisseur (optionnel)"

        # Définir la date de début par défaut
        if not self.instance.pk:
            self.fields['start_date'].initial = date.today()
            self.fields['next_due_date'].initial = date.today()


class AppointmentForm(forms.ModelForm):
    """Formulaire pour les rendez-vous"""

    class Meta:
        model = Appointment
        fields = [
            'title', 'description', 'client', 'vehicle', 'start_datetime', 'end_datetime',
            'status', 'estimated_services', 'estimated_price', 'notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du rendez-vous'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description détaillée'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'start_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'step': '900'  # 15 minutes en secondes
            }),
            'end_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'step': '900'  # 15 minutes en secondes
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'estimated_services': forms.CheckboxSelectMultiple(),
            'estimated_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes additionnelles'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les services actifs
        self.fields['estimated_services'].queryset = Service.objects.filter(is_active=True)

        # Définir des valeurs par défaut
        if not self.instance.pk:
            now = datetime.now()
            # Arrondir aux 15 minutes les plus proches
            minutes = (now.minute // 15) * 15
            start_time = now.replace(minute=minutes, second=0, microsecond=0)
            # Si on est déjà passé ce quart d'heure, passer au suivant
            if now.minute % 15 > 0:
                start_time = start_time + timedelta(minutes=15)

            self.fields['start_datetime'].initial = start_time
            self.fields['end_datetime'].initial = start_time + timedelta(hours=1)


class StockReceiptForm(forms.ModelForm):
    """Formulaire pour les bons de réception"""

    class Meta:
        model = StockReceipt
        fields = [
            'supplier', 'receipt_date', 'supplier_invoice_number', 'status',
            'gst_amount', 'qst_amount', 'notes'
        ]
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'receipt_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier_invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de facture fournisseur'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'gst_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00'}),
            'qst_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.00'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes additionnelles'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les fournisseurs actifs
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)

        # Définir la date par défaut
        if not self.instance.pk:
            self.fields['receipt_date'].initial = date.today()


class StockReceiptItemForm(forms.ModelForm):
    """Formulaire pour les éléments de bon de réception"""

    class Meta:
        model = StockReceiptItem
        fields = ['inventory_item', 'quantity', 'purchase_price']
        widgets = {
            'inventory_item': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }


# ==================== FORMULAIRES SOUMISSIONS ====================

class QuoteForm(forms.ModelForm):
    """Formulaire pour les soumissions"""

    class Meta:
        model = Quote
        fields = ['client', 'vehicle', 'valid_until', 'discount_percentage', 'is_dealer_discount', 'notes', 'terms_conditions']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'is_dealer_discount': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes internes...'}),
            'terms_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Conditions générales de la soumission...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Labels en français
        self.fields['client'].label = 'Client'
        self.fields['vehicle'].label = 'Véhicule'
        self.fields['valid_until'].label = 'Valide jusqu\'au'
        self.fields['discount_percentage'].label = 'Rabais (%)'
        self.fields['is_dealer_discount'].label = 'Rabais concessionnaire (30%)'
        self.fields['notes'].label = 'Notes internes'
        self.fields['terms_conditions'].label = 'Conditions générales'

        # Définir la date de validité par défaut (30 jours)
        if not self.instance.pk:
            from datetime import date, timedelta
            self.fields['valid_until'].initial = date.today() + timedelta(days=30)

        # Filtrer les véhicules selon le client sélectionné
        client_id = None

        # Récupérer l'ID du client depuis les données POST ou l'instance
        if self.data and 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
            except (ValueError, TypeError):
                client_id = None
        elif self.instance.pk and self.instance.client:
            client_id = self.instance.client.id

        # Filtrer les véhicules selon le client
        if client_id:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(client_id=client_id)
            # Maintenir la sélection du véhicule si elle existe dans les données
            if self.data and 'vehicle' in self.data:
                try:
                    vehicle_id = int(self.data.get('vehicle'))
                    if Vehicle.objects.filter(id=vehicle_id, client_id=client_id).exists():
                        self.fields['vehicle'].initial = vehicle_id
                except (ValueError, TypeError):
                    pass
        else:
            self.fields['vehicle'].queryset = Vehicle.objects.none()


class QuoteItemForm(forms.ModelForm):
    """Formulaire pour les éléments de soumission"""

    class Meta:
        model = QuoteItem
        fields = ['item_type', 'service', 'inventory_item', 'description', 'price']
        widgets = {
            'item_type': forms.HiddenInput(),  # Champ caché avec valeur par défaut
            'service': forms.Select(attrs={'class': 'form-select'}),
            'inventory_item': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description personnalisée'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Labels en français
        self.fields['service'].label = 'Service'
        self.fields['inventory_item'].label = 'Article d\'inventaire'
        self.fields['description'].label = 'Description'
        self.fields['price'].label = 'Prix ($)'

        # Valeur par défaut pour item_type
        if not self.instance.pk:  # Nouveau formulaire
            self.fields['item_type'].initial = 'service'

        # Filtrer les services et articles d'inventaire actifs seulement
        self.fields['inventory_item'].queryset = InventoryItem.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)


# Formset pour les éléments de soumission (un service par défaut, ajout/suppression possible)
QuoteItemFormSet = forms.inlineformset_factory(
    Quote,
    QuoteItem,
    form=QuoteItemForm,
    extra=1,  # Un seul service par défaut
    can_delete=True,  # Permettre la suppression
    min_num=1,  # Au minimum un service requis
    validate_min=True
)


# Formset pour les éléments de facture (définition supprimée - utilise celle du haut)

# Formset pour les éléments de bon de réception
StockReceiptItemFormSet = inlineformset_factory(
    StockReceipt,
    StockReceiptItem,
    form=StockReceiptItemForm,
    extra=1,
    can_delete=True,
    fields=['inventory_item', 'quantity', 'purchase_price']
)
