from django import forms
from django.forms import inlineformset_factory
from .models import CompanyProfile, Client, Vehicle, Service, Invoice, InvoiceItem, Expense
from datetime import date, timedelta


class CompanyProfileForm(forms.ModelForm):
    """Formulaire pour le profil de l'entreprise"""
    
    class Meta:
        model = CompanyProfile
        fields = [
            'name', 'address', 'phone', 'email', 'website', 'logo',
            'gst_number', 'qst_number', 'is_tax_registered'
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
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(514) 123-4567'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse complète'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes sur le client'}),
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

    class Meta:
        model = Vehicle
        fields = ['client', 'make', 'model', 'year', 'color', 'license_plate', 'vin', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Toyota, Honda, etc.'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Camry, Civic, etc.'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2030}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Noir, Blanc, etc.'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC 123'}),
            'vin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '17 caractères'}),
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
        self.fields['color'].label = 'Couleur'
        self.fields['license_plate'].label = 'Plaque d\'immatriculation'
        self.fields['vin'].label = 'Numéro VIN'
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

    class Meta:
        model = Invoice
        fields = ['client', 'vehicle', 'invoice_date', 'due_date', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes sur la facture'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Champs obligatoires
        self.fields['client'].required = True
        self.fields['invoice_date'].required = True
        self.fields['due_date'].required = True

        # Labels en français
        self.fields['client'].label = 'Client'
        self.fields['vehicle'].label = 'Véhicule (optionnel)'
        self.fields['invoice_date'].label = 'Date de facture'
        self.fields['due_date'].label = 'Date d\'échéance'
        self.fields['notes'].label = 'Notes'

        # Valeurs par défaut
        if not self.instance.pk:  # Nouvelle facture
            self.fields['invoice_date'].initial = date.today()
            self.fields['due_date'].initial = date.today() + timedelta(days=30)

        # Filtrer les véhicules selon le client sélectionné
        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['vehicle'].queryset = Vehicle.objects.filter(client_id=client_id)
            except (ValueError, TypeError):
                self.fields['vehicle'].queryset = Vehicle.objects.none()
        elif self.instance.pk and self.instance.client:
            self.fields['vehicle'].queryset = self.instance.client.vehicles.all()
        else:
            self.fields['vehicle'].queryset = Vehicle.objects.none()


class InvoiceItemForm(forms.ModelForm):
    """Formulaire pour les éléments de facture"""

    class Meta:
        model = InvoiceItem
        fields = ['service', 'description', 'quantity', 'unit_price']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description personnalisée'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Labels en français
        self.fields['service'].label = 'Service'
        self.fields['description'].label = 'Description'
        self.fields['quantity'].label = 'Quantité'
        self.fields['unit_price'].label = 'Prix unitaire ($)'

        # Filtrer les services actifs seulement
        self.fields['service'].queryset = Service.objects.filter(is_active=True)


# Formset pour gérer plusieurs éléments de facture
InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,  # Une ligne vide par défaut
    min_num=1,  # Au moins un élément requis
    validate_min=True,
    can_delete=True
)


class ExpenseForm(forms.ModelForm):
    """Formulaire pour la gestion des dépenses"""

    class Meta:
        model = Expense
        fields = ['description', 'amount', 'expense_date', 'category', 'gst_amount', 'qst_amount', 'receipt', 'notes']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description de la dépense'}),
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
