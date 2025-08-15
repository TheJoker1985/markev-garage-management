from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CompanyProfile, Client, Vehicle, Service, InventoryItem,
    Invoice, InvoiceItem, Expense, FiscalYearArchive,
    Supplier, RecurringExpense, Appointment
)


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_tax_registered', 'created_at']
    list_filter = ['is_tax_registered', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'address', 'phone', 'email', 'website', 'logo')
        }),
        ('Informations fiscales', {
            'fields': ('gst_number', 'qst_number', 'is_tax_registered')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class VehicleInline(admin.TabularInline):
    model = Vehicle
    extra = 0
    fields = ['make', 'model', 'year', 'color', 'license_plate']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'vehicle_count', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [VehicleInline]

    fieldsets = (
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Adresse et notes', {
            'fields': ('address', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def vehicle_count(self, obj):
        return obj.vehicles.count()
    vehicle_count.short_description = 'Nombre de véhicules'


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'category', 'is_active', 'total_expenses']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'email', 'phone']
    readonly_fields = ['total_expenses', 'created_at', 'updated_at']

    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'contact_person', 'email', 'phone', 'address', 'website')
        }),
        ('Informations commerciales', {
            'fields': ('account_number', 'payment_terms', 'category')
        }),
        ('Statut et notes', {
            'fields': ('is_active', 'notes')
        }),
        ('Statistiques', {
            'fields': ('total_expenses',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'client', 'year', 'color', 'license_plate', 'created_at']
    list_filter = ['make', 'year', 'created_at']
    search_fields = ['make', 'model', 'license_plate', 'vin', 'client__first_name', 'client__last_name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations du véhicule', {
            'fields': ('client', 'make', 'model', 'year', 'color')
        }),
        ('Identification', {
            'fields': ('license_plate', 'vin')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'default_price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations du service', {
            'fields': ('name', 'description', 'category')
        }),
        ('Prix et statut', {
            'fields': ('default_price', 'is_active')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'supplier', 'category', 'quantity_in_stock', 'stock_status', 'unit_cost', 'unit_price', 'is_active']
    list_filter = ['supplier', 'category', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description', 'supplier__name']
    readonly_fields = ['created_at', 'updated_at', 'total_value']

    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'sku', 'supplier', 'category')
        }),
        ('Inventaire', {
            'fields': ('quantity_in_stock', 'minimum_stock_level')
        }),
        ('Prix', {
            'fields': ('unit_cost', 'unit_price', 'total_value')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def stock_status(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red;">Stock bas</span>')
        return format_html('<span style="color: green;">OK</span>')
    stock_status.short_description = 'Statut du stock'


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ['service', 'description', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['total_price']



@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'invoice_date', 'due_date', 'total_amount', 'status', 'payment_method', 'payment_status']
    list_filter = ['status', 'payment_method', 'invoice_date', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'client__first_name', 'client__last_name']
    readonly_fields = ['invoice_number', 'subtotal', 'gst_amount', 'qst_amount', 'total_amount', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]

    fieldsets = (
        ('Informations de base', {
            'fields': ('invoice_number', 'client', 'vehicle', 'invoice_date', 'due_date')
        }),
        ('Montants', {
            'fields': ('subtotal', 'gst_amount', 'qst_amount', 'total_amount')
        }),
        ('Statut et paiement', {
            'fields': ('status', 'payment_method', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def payment_status(self, obj):
        if obj.is_paid:
            return format_html('<span style="color: green;">Payée</span>')
        elif obj.is_overdue:
            return format_html('<span style="color: red;">En retard</span>')
        return format_html('<span style="color: orange;">En attente</span>')
    payment_status.short_description = 'Statut de paiement'

    actions = ['mark_as_paid', 'calculate_totals']

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} facture(s) marquée(s) comme payée(s).')
    mark_as_paid.short_description = "Marquer comme payées"

    def calculate_totals(self, request, queryset):
        for invoice in queryset:
            invoice.calculate_totals()
        self.message_user(request, f'Totaux recalculés pour {queryset.count()} facture(s).')
    calculate_totals.short_description = "Recalculer les totaux"


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'item_type', 'item_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['item_type', 'service__category', 'inventory_item__category', 'created_at']
    search_fields = ['invoice__invoice_number', 'service__name', 'inventory_item__name', 'description']
    readonly_fields = ['total_price', 'item_name', 'created_at', 'updated_at']

    fieldsets = (
        ('Type d\'élément', {
            'fields': ('item_type',)
        }),
        ('Élément', {
            'fields': ('service', 'inventory_item', 'item_name')
        }),
        ('Détails', {
            'fields': ('description', 'quantity', 'unit_price', 'total_price')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'supplier', 'amount', 'category', 'expense_date', 'has_receipt', 'total_with_taxes']
    list_filter = ['supplier', 'category', 'expense_date', 'created_at']
    search_fields = ['description', 'supplier__name', 'notes']
    readonly_fields = ['total_with_taxes', 'created_at', 'updated_at']

    fieldsets = (
        ('Informations de base', {
            'fields': ('description', 'supplier', 'amount', 'expense_date', 'category')
        }),
        ('Taxes', {
            'fields': ('gst_amount', 'qst_amount', 'total_with_taxes')
        }),
        ('Reçu et notes', {
            'fields': ('receipt', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_receipt(self, obj):
        if obj.receipt:
            return format_html('<span style="color: green;">Oui</span>')
        return format_html('<span style="color: red;">Non</span>')
    has_receipt.short_description = 'Reçu'


@admin.register(FiscalYearArchive)
class FiscalYearArchiveAdmin(admin.ModelAdmin):
    list_display = ['fiscal_year', 'archive_date', 'total_invoices', 'total_revenue', 'total_expenses', 'calculate_net_profit', 'is_locked', 'archived_by']
    list_filter = ['is_locked', 'archive_date', 'archived_by']
    search_fields = ['fiscal_year', 'notes']
    readonly_fields = ['archive_date', 'get_fiscal_period_display', 'calculate_net_profit', 'get_tax_summary_display']

    fieldsets = (
        ('Informations de base', {
            'fields': ('fiscal_year', 'get_fiscal_period_display', 'archive_date', 'archived_by', 'is_locked')
        }),
        ('Statistiques financières', {
            'fields': ('total_invoices', 'total_revenue', 'total_expenses', 'calculate_net_profit')
        }),
        ('Taxes', {
            'fields': ('total_gst_collected', 'total_qst_collected', 'total_gst_paid', 'total_qst_paid', 'get_tax_summary_display')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    def get_tax_summary_display(self, obj):
        """Afficher un résumé des taxes"""
        tax_summary = obj.get_tax_summary()
        return format_html(
            '<strong>TPS nette:</strong> {:.2f} $<br>'
            '<strong>TVQ nette:</strong> {:.2f} $<br>'
            '<strong>Total perçu:</strong> {:.2f} $<br>'
            '<strong>Total payé:</strong> {:.2f} $',
            tax_summary['gst_net'],
            tax_summary['qst_net'],
            tax_summary['total_collected'],
            tax_summary['total_paid']
        )
    get_tax_summary_display.short_description = 'Résumé des taxes'

    def has_delete_permission(self, request, obj=None):
        """Empêcher la suppression des archives verrouillées"""
        if obj and obj.is_locked:
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """Limiter la modification des archives verrouillées"""
        if obj and obj.is_locked:
            return request.user.is_superuser
        return super().has_change_permission(request, obj)


@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier', 'amount', 'frequency', 'next_due_date', 'is_active', 'total_with_taxes']
    list_filter = ['supplier', 'category', 'frequency', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'supplier__name']
    readonly_fields = ['total_with_taxes', 'created_at', 'updated_at']

    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'supplier', 'category')
        }),
        ('Montant et taxes', {
            'fields': ('amount', 'gst_amount', 'qst_amount', 'total_with_taxes')
        }),
        ('Récurrence', {
            'fields': ('frequency', 'start_date', 'end_date', 'next_due_date')
        }),
        ('Statut et notes', {
            'fields': ('is_active', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['create_expenses_for_due_items']

    def create_expenses_for_due_items(self, request, queryset):
        """Action pour créer des dépenses pour les éléments dus"""
        created_count = 0
        for recurring_expense in queryset:
            if recurring_expense.is_due():
                recurring_expense.create_expense()
                created_count += 1

        self.message_user(request, f'{created_count} dépense(s) créée(s) avec succès.')
    create_expenses_for_due_items.short_description = "Créer les dépenses pour les éléments dus"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'vehicle', 'start_datetime', 'end_datetime', 'status', 'has_invoice']
    list_filter = ['status', 'start_datetime', 'created_at']
    search_fields = ['title', 'client__first_name', 'client__last_name', 'description']
    readonly_fields = ['duration', 'is_past', 'is_today', 'created_at', 'updated_at']

    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'description', 'client', 'vehicle')
        }),
        ('Planification', {
            'fields': ('start_datetime', 'end_datetime', 'duration', 'status')
        }),
        ('Services et prix', {
            'fields': ('estimated_services', 'estimated_price')
        }),
        ('Facture', {
            'fields': ('invoice',)
        }),
        ('Statut', {
            'fields': ('is_past', 'is_today')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    filter_horizontal = ['estimated_services']

    def has_invoice(self, obj):
        """Afficher si le rendez-vous a une facture"""
        if obj.invoice:
            return format_html('<span style="color: green;">Oui</span>')
        return format_html('<span style="color: red;">Non</span>')
    has_invoice.short_description = 'Facture'

    actions = ['create_invoices_for_completed']

    def create_invoices_for_completed(self, request, queryset):
        """Action pour créer des factures pour les rendez-vous terminés"""
        created_count = 0
        for appointment in queryset:
            if appointment.can_create_invoice():
                appointment.create_invoice_from_appointment()
                created_count += 1

        self.message_user(request, f'{created_count} facture(s) créée(s) avec succès.')
    create_invoices_for_completed.short_description = "Créer des factures pour les rendez-vous terminés"


# Personnalisation de l'interface d'administration
admin.site.site_header = "Administration MarKev"
admin.site.site_title = "MarKev Admin"
admin.site.index_title = "Bienvenue dans l'administration MarKev"
