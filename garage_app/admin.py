from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CompanyProfile, Client, Vehicle, Service, InventoryItem,
    Invoice, InvoiceItem, Expense, Payment
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
    list_display = ['name', 'sku', 'category', 'quantity_in_stock', 'stock_status', 'unit_cost', 'unit_price', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at', 'total_value']

    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'sku', 'category')
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


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ['amount', 'payment_date', 'payment_method', 'reference']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'invoice_date', 'due_date', 'total_amount', 'status', 'payment_status']
    list_filter = ['status', 'invoice_date', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'client__first_name', 'client__last_name']
    readonly_fields = ['invoice_number', 'subtotal', 'gst_amount', 'qst_amount', 'total_amount', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline, PaymentInline]

    fieldsets = (
        ('Informations de base', {
            'fields': ('invoice_number', 'client', 'vehicle', 'invoice_date', 'due_date')
        }),
        ('Montants', {
            'fields': ('subtotal', 'gst_amount', 'qst_amount', 'total_amount')
        }),
        ('Statut et notes', {
            'fields': ('status', 'notes')
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
    list_display = ['invoice', 'service', 'quantity', 'unit_price', 'total_price']
    list_filter = ['service__category', 'created_at']
    search_fields = ['invoice__invoice_number', 'service__name', 'description']
    readonly_fields = ['total_price', 'created_at', 'updated_at']

    fieldsets = (
        ('Informations de base', {
            'fields': ('invoice', 'service', 'description')
        }),
        ('Quantité et prix', {
            'fields': ('quantity', 'unit_price', 'total_price')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'category', 'expense_date', 'has_receipt', 'total_with_taxes']
    list_filter = ['category', 'expense_date', 'created_at']
    search_fields = ['description', 'notes']
    readonly_fields = ['total_with_taxes', 'created_at', 'updated_at']

    fieldsets = (
        ('Informations de base', {
            'fields': ('description', 'amount', 'expense_date', 'category')
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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'payment_date', 'payment_method', 'reference']
    list_filter = ['payment_method', 'payment_date', 'created_at']
    search_fields = ['invoice__invoice_number', 'reference', 'notes']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations de base', {
            'fields': ('invoice', 'amount', 'payment_date')
        }),
        ('Méthode et référence', {
            'fields': ('payment_method', 'reference')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Personnalisation de l'interface d'administration
admin.site.site_header = "Administration MarKev"
admin.site.site_title = "MarKev Admin"
admin.site.index_title = "Bienvenue dans l'administration MarKev"
