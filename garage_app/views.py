from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from datetime import date, timedelta
from .models import (
    Invoice, Expense, Payment, Client, Service, CompanyProfile, Vehicle, InvoiceItem,
    Supplier, RecurringExpense, Appointment, InventoryItem, StockReceipt, StockReceiptItem
)
from .forms import (
    CompanyProfileForm, ClientForm, VehicleForm, ServiceForm, InvoiceForm,
    InvoiceItemFormSet, ExpenseForm, SupplierForm, RecurringExpenseForm, AppointmentForm,
    StockReceiptForm, StockReceiptItemFormSet
)
from django.core.paginator import Paginator
from django.db.models import Q

# Imports pour la génération de PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
import io


@login_required
def dashboard(request):
    """Vue du tableau de bord principal"""
    # Obtenir le profil d'entreprise pour les périodes fiscales
    company_profile = CompanyProfile.objects.first()

    # Statistiques financières
    today = date.today()
    current_month = today.replace(day=1)

    # Utiliser la période fiscale si un profil d'entreprise existe
    if company_profile:
        fiscal_year_start, fiscal_year_end = company_profile.get_current_fiscal_year_period()
        current_fiscal_year = fiscal_year_start
        fiscal_year_label = f"Année fiscale {company_profile.get_fiscal_year_for_date(today)}"
    else:
        # Fallback vers l'année civile si pas de profil configuré
        current_fiscal_year = today.replace(month=1, day=1)
        fiscal_year_label = f"Année {today.year}"

    # Revenus
    monthly_revenue = Invoice.objects.filter(
        invoice_date__gte=current_month,
        status='paid',
        archived_fiscal_year__isnull=True  # Exclure les données archivées
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    yearly_revenue = Invoice.objects.filter(
        invoice_date__gte=current_fiscal_year,
        status='paid',
        archived_fiscal_year__isnull=True  # Exclure les données archivées
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Dépenses
    monthly_expenses = Expense.objects.filter(
        expense_date__gte=current_month,
        archived_fiscal_year__isnull=True  # Exclure les données archivées
    ).aggregate(total=Sum('amount'))['total'] or 0

    yearly_expenses = Expense.objects.filter(
        expense_date__gte=current_fiscal_year,
        archived_fiscal_year__isnull=True  # Exclure les données archivées
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Profit
    monthly_profit = monthly_revenue - monthly_expenses
    yearly_profit = yearly_revenue - yearly_expenses

    # Factures en attente
    pending_invoices = Invoice.objects.filter(status__in=['sent', 'draft']).count()
    overdue_invoices = Invoice.objects.filter(
        due_date__lt=today,
        status__in=['sent', 'draft']
    ).count()

    # Clients et services
    total_clients = Client.objects.count()
    total_services = Service.objects.filter(is_active=True).count()

    context = {
        'monthly_revenue': monthly_revenue,
        'yearly_revenue': yearly_revenue,
        'monthly_expenses': monthly_expenses,
        'yearly_expenses': yearly_expenses,
        'monthly_profit': monthly_profit,
        'yearly_profit': yearly_profit,
        'pending_invoices': pending_invoices,
        'overdue_invoices': overdue_invoices,
        'total_clients': total_clients,
        'total_services': total_services,
        'current_month': current_month.strftime('%B %Y'),
        'fiscal_year_label': fiscal_year_label,
        'has_company_profile': company_profile is not None,
    }

    return render(request, 'garage_app/dashboard.html', context)


def login_view(request):
    """Vue de connexion personnalisée"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'garage_app:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')

    return render(request, 'registration/login.html')


def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('garage_app:login')


@login_required
def company_profile(request):
    """Vue pour gérer le profil de l'entreprise"""
    try:
        profile = CompanyProfile.objects.get()
    except CompanyProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil de l\'entreprise mis à jour avec succès.')
            return redirect('garage_app:company_profile')
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'garage_app/company_profile.html', {'form': form, 'profile': profile})


# ==================== GESTION DES CLIENTS ====================

@login_required
def client_list(request):
    """Vue pour lister tous les clients avec recherche"""
    search_query = request.GET.get('search', '')
    clients = Client.objects.all()

    if search_query:
        clients = clients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(clients, 20)  # 20 clients par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_clients': clients.count()
    }

    return render(request, 'garage_app/clients/client_list.html', context)


@login_required
def client_detail(request, client_id):
    """Vue pour afficher les détails d'un client"""
    client = get_object_or_404(Client, id=client_id)
    vehicles = client.vehicles.all()
    invoices = client.invoices.all().order_by('-invoice_date')[:10]  # 10 dernières factures

    context = {
        'client': client,
        'vehicles': vehicles,
        'recent_invoices': invoices
    }

    return render(request, 'garage_app/clients/client_detail.html', context)


@login_required
def client_create(request):
    """Vue pour créer un nouveau client"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Client {client.full_name} créé avec succès.')
            return redirect('garage_app:client_detail', client_id=client.id)
    else:
        form = ClientForm()

    return render(request, 'garage_app/clients/client_form.html', {
        'form': form,
        'title': 'Nouveau client',
        'submit_text': 'Créer le client'
    })


@login_required
def client_update(request, client_id):
    """Vue pour modifier un client existant"""
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client {client.full_name} mis à jour avec succès.')
            return redirect('garage_app:client_detail', client_id=client.id)
    else:
        form = ClientForm(instance=client)

    return render(request, 'garage_app/clients/client_form.html', {
        'form': form,
        'client': client,
        'title': f'Modifier {client.full_name}',
        'submit_text': 'Mettre à jour'
    })


@login_required
def client_delete(request, client_id):
    """Vue pour supprimer un client"""
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        client_name = client.full_name
        client.delete()
        messages.success(request, f'Client {client_name} supprimé avec succès.')
        return redirect('garage_app:client_list')

    return render(request, 'garage_app/clients/client_confirm_delete.html', {'client': client})


# ==================== GESTION DES SERVICES ====================

@login_required
def service_list(request):
    """Vue pour lister tous les services"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    services = Service.objects.all()

    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        services = services.filter(category=category_filter)

    # Pagination
    paginator = Paginator(services, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Catégories pour le filtre
    categories = Service.CATEGORY_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
        'total_services': services.count()
    }

    return render(request, 'garage_app/services/service_list.html', context)


@login_required
def service_detail(request, service_id):
    """Vue pour afficher les détails d'un service"""
    service = get_object_or_404(Service, id=service_id)

    # Statistiques d'utilisation du service
    recent_invoices = Invoice.objects.filter(
        invoice_items__service=service
    ).distinct().order_by('-invoice_date')[:10]

    context = {
        'service': service,
        'recent_invoices': recent_invoices
    }

    return render(request, 'garage_app/services/service_detail.html', context)


@login_required
def service_create(request):
    """Vue pour créer un nouveau service"""
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.name}" créé avec succès.')
            return redirect('garage_app:service_detail', service_id=service.id)
    else:
        form = ServiceForm()

    return render(request, 'garage_app/services/service_form.html', {
        'form': form,
        'title': 'Nouveau service',
        'submit_text': 'Créer le service'
    })


@login_required
def service_update(request, service_id):
    """Vue pour modifier un service existant"""
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f'Service "{service.name}" mis à jour avec succès.')
            return redirect('garage_app:service_detail', service_id=service.id)
    else:
        form = ServiceForm(instance=service)

    return render(request, 'garage_app/services/service_form.html', {
        'form': form,
        'service': service,
        'title': f'Modifier "{service.name}"',
        'submit_text': 'Mettre à jour'
    })


@login_required
def service_delete(request, service_id):
    """Vue pour supprimer un service"""
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        service_name = service.name
        service.delete()
        messages.success(request, f'Service "{service_name}" supprimé avec succès.')
        return redirect('garage_app:service_list')

    return render(request, 'garage_app/services/service_confirm_delete.html', {'service': service})


# ==================== GESTION DES VÉHICULES ====================

@login_required
def vehicle_create(request, client_id=None):
    """Vue pour créer un nouveau véhicule"""
    client = None
    if client_id:
        client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f'Véhicule {vehicle} ajouté avec succès.')
            return redirect('garage_app:client_detail', client_id=vehicle.client.id)
    else:
        initial_data = {}
        if client:
            initial_data['client'] = client
        form = VehicleForm(initial=initial_data)

    return render(request, 'garage_app/vehicles/vehicle_form.html', {
        'form': form,
        'client': client,
        'title': 'Nouveau véhicule',
        'submit_text': 'Ajouter le véhicule'
    })


@login_required
def vehicle_update(request, vehicle_id):
    """Vue pour modifier un véhicule existant"""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f'Véhicule {vehicle} mis à jour avec succès.')
            return redirect('garage_app:client_detail', client_id=vehicle.client.id)
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'garage_app/vehicles/vehicle_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': f'Modifier {vehicle}',
        'submit_text': 'Mettre à jour'
    })


@login_required
def vehicle_delete(request, vehicle_id):
    """Vue pour supprimer un véhicule"""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    client_id = vehicle.client.id

    if request.method == 'POST':
        vehicle_str = str(vehicle)
        vehicle.delete()
        messages.success(request, f'Véhicule {vehicle_str} supprimé avec succès.')
        return redirect('garage_app:client_detail', client_id=client_id)

    return render(request, 'garage_app/vehicles/vehicle_confirm_delete.html', {'vehicle': vehicle})


# ==================== GESTION DES FACTURES ====================

@login_required
def invoice_list(request):
    """Vue pour lister toutes les factures"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    invoices = Invoice.objects.all()

    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(client__first_name__icontains=search_query) |
            Q(client__last_name__icontains=search_query)
        )

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    # Pagination
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statuts pour le filtre
    statuses = Invoice.STATUS_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'statuses': statuses,
        'total_invoices': invoices.count()
    }

    return render(request, 'garage_app/invoices/invoice_list.html', context)


@login_required
def invoice_detail(request, invoice_id):
    """Vue pour afficher les détails d'une facture"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice_items = invoice.invoice_items.all()
    payments = invoice.payments.all()

    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'payments': payments
    }

    return render(request, 'garage_app/invoices/invoice_detail.html', context)


@login_required
def invoice_print(request, invoice_id):
    """Vue pour l'impression d'une facture avec logo"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice_items = invoice.invoice_items.all()

    # Récupérer le profil de l'entreprise pour l'en-tête
    try:
        company_profile = CompanyProfile.objects.first()
    except CompanyProfile.DoesNotExist:
        company_profile = None

    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'company_profile': company_profile
    }

    return render(request, 'garage_app/invoices/invoice_print.html', context)


@login_required
def invoice_create(request):
    """Vue pour créer une nouvelle facture"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()

            # Calculer les totaux
            invoice.calculate_totals()

            messages.success(request, f'Facture {invoice.invoice_number} créée avec succès.')
            return redirect('garage_app:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': 'Nouvelle facture',
        'submit_text': 'Créer la facture'
    }

    return render(request, 'garage_app/invoices/invoice_form.html', context)


@login_required
def invoice_update(request, invoice_id):
    """Vue pour modifier une facture existante"""
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            # Recalculer les totaux
            invoice.calculate_totals()

            messages.success(request, f'Facture {invoice.invoice_number} mise à jour avec succès.')
            return redirect('garage_app:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceItemFormSet(instance=invoice)

    context = {
        'form': form,
        'formset': formset,
        'invoice': invoice,
        'title': f'Modifier {invoice.invoice_number}',
        'submit_text': 'Mettre à jour'
    }

    return render(request, 'garage_app/invoices/invoice_form.html', context)


@login_required
def invoice_mark_paid(request, invoice_id):
    """Vue pour marquer une facture comme payée"""
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == 'POST':
        # Créer un paiement pour le montant total
        Payment.objects.create(
            invoice=invoice,
            amount=invoice.total_amount,
            payment_date=date.today(),
            payment_method='cash',  # Par défaut
            notes='Paiement marqué comme reçu via l\'interface'
        )

        messages.success(request, f'Facture {invoice.invoice_number} marquée comme payée.')
        return redirect('garage_app:invoice_detail', invoice_id=invoice.id)

    return render(request, 'garage_app/invoices/invoice_mark_paid.html', {'invoice': invoice})


@login_required
def generate_invoice_pdf(request, invoice_id):
    """Génération de PDF pour une facture conforme aux exigences du Québec"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    company_profile = CompanyProfile.objects.first()

    # Créer la réponse HTTP pour le PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{invoice.invoice_number}.pdf"'

    # Créer le document PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_LEFT
    )

    # Contenu du PDF
    story = []

    # En-tête avec informations de l'entreprise
    if company_profile:
        # Logo (si disponible)
        if company_profile.logo:
            try:
                logo = Image(company_profile.logo.path, width=2*inch, height=1*inch)
                logo.hAlign = 'LEFT'
                story.append(logo)
                story.append(Spacer(1, 12))
            except:
                pass  # Ignorer si le logo ne peut pas être chargé

        # Informations de l'entreprise
        company_info = f"""
        <b>{company_profile.name}</b><br/>
        {company_profile.address.replace(chr(10), '<br/>')}<br/>
        Tél: {company_profile.phone}<br/>
        Email: {company_profile.email}
        """

        if company_profile.is_tax_registered:
            if company_profile.gst_number:
                company_info += f"<br/>No TPS: {company_profile.gst_number}"
            if company_profile.qst_number:
                company_info += f"<br/>No TVQ: {company_profile.qst_number}"

        story.append(Paragraph(company_info, header_style))
        story.append(Spacer(1, 30))

    # Titre de la facture
    story.append(Paragraph(f"FACTURE {invoice.invoice_number}", title_style))

    # Informations de facturation
    invoice_info_data = [
        ['Date de facture:', invoice.invoice_date.strftime('%d/%m/%Y')],
        ['Date d\'échéance:', invoice.due_date.strftime('%d/%m/%Y')],
        ['Statut:', invoice.get_status_display()],
    ]

    client_info_data = [
        ['Facturé à:', ''],
        ['', invoice.client.full_name],
        ['', invoice.client.phone],
    ]

    if invoice.client.email:
        client_info_data.append(['', invoice.client.email])

    if invoice.client.address:
        client_info_data.append(['', invoice.client.address])

    if invoice.vehicle:
        client_info_data.append(['Véhicule:', str(invoice.vehicle)])

    # Créer le tableau d'informations
    info_table = Table([invoice_info_data, client_info_data], colWidths=[2.5*inch, 2.5*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(info_table)
    story.append(Spacer(1, 30))

    # Tableau des éléments de facture
    items_data = [['Description', 'Quantité', 'Prix unitaire', 'Total']]

    for item in invoice.invoice_items.all():
        description = item.service.name
        if item.description:
            description += f" - {item.description}"

        items_data.append([
            description,
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item.total_price:.2f}"
        ])

    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Description alignée à gauche
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(items_table)
    story.append(Spacer(1, 30))

    # Tableau des totaux
    totals_data = [
        ['Sous-total:', f"${invoice.subtotal:.2f}"],
    ]

    if company_profile and company_profile.is_tax_registered:
        totals_data.extend([
            ['TPS (5%):', f"${invoice.gst_amount:.2f}"],
            ['TVQ (9.975%):', f"${invoice.qst_amount:.2f}"],
        ])

    totals_data.append(['TOTAL:', f"${invoice.total_amount:.2f}"])

    totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
    ]))

    story.append(totals_table)

    # Notes (si présentes)
    if invoice.notes:
        story.append(Spacer(1, 30))
        story.append(Paragraph("Notes:", styles['Heading3']))
        story.append(Paragraph(invoice.notes, styles['Normal']))

    # Pied de page avec informations légales
    story.append(Spacer(1, 50))
    legal_text = """
    <i>Cette facture est conforme aux exigences de Revenu Québec et de l'Agence du revenu du Canada.
    Paiement dû dans les 30 jours suivant la date d'émission sauf indication contraire.</i>
    """
    story.append(Paragraph(legal_text, styles['Normal']))

    # Construire le PDF
    doc.build(story)

    # Retourner le PDF
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response


# ==================== GESTION DES DÉPENSES ====================

@login_required
def expense_list(request):
    """Vue pour lister toutes les dépenses"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    expenses = Expense.objects.all()

    if search_query:
        expenses = expenses.filter(
            Q(description__icontains=search_query) |
            Q(notes__icontains=search_query)
        )

    if category_filter:
        expenses = expenses.filter(category=category_filter)

    # Pagination
    paginator = Paginator(expenses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Catégories pour le filtre
    categories = Expense.EXPENSE_CATEGORY_CHOICES

    # Statistiques
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_with_taxes = sum(expense.total_with_taxes for expense in expenses)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
        'total_expenses': expenses.count(),
        'total_amount': total_amount,
        'total_with_taxes': total_with_taxes,
    }

    return render(request, 'garage_app/expenses/expense_list.html', context)


@login_required
def expense_detail(request, expense_id):
    """Vue pour afficher les détails d'une dépense"""
    expense = get_object_or_404(Expense, id=expense_id)

    context = {
        'expense': expense
    }

    return render(request, 'garage_app/expenses/expense_detail.html', context)


@login_required
def expense_create(request):
    """Vue pour créer une nouvelle dépense"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save()
            messages.success(request, f'Dépense "{expense.description}" créée avec succès.')
            return redirect('garage_app:expense_detail', expense_id=expense.id)
    else:
        form = ExpenseForm()

    return render(request, 'garage_app/expenses/expense_form.html', {
        'form': form,
        'title': 'Nouvelle dépense',
        'submit_text': 'Enregistrer la dépense'
    })


@login_required
def expense_update(request, expense_id):
    """Vue pour modifier une dépense existante"""
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, f'Dépense "{expense.description}" mise à jour avec succès.')
            return redirect('garage_app:expense_detail', expense_id=expense.id)
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'garage_app/expenses/expense_form.html', {
        'form': form,
        'expense': expense,
        'title': f'Modifier "{expense.description}"',
        'submit_text': 'Mettre à jour'
    })


@login_required
def expense_delete(request, expense_id):
    """Vue pour supprimer une dépense"""
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == 'POST':
        expense_description = expense.description
        expense.delete()
        messages.success(request, f'Dépense "{expense_description}" supprimée avec succès.')
        return redirect('garage_app:expense_list')

    return render(request, 'garage_app/expenses/expense_confirm_delete.html', {'expense': expense})


# ==================== RAPPORTS FINANCIERS ====================

@login_required
def financial_reports(request):
    """Vue pour les rapports financiers"""
    # Obtenir le profil d'entreprise pour les périodes fiscales
    company_profile = CompanyProfile.objects.first()

    # Période sélectionnée
    period = request.GET.get('period', 'current_month')

    today = date.today()

    if period == 'current_month':
        start_date = today.replace(day=1)
        end_date = today
        period_name = f"{start_date.strftime('%B %Y')}"
    elif period == 'current_fiscal_year':
        if company_profile:
            start_date, end_date = company_profile.get_current_fiscal_year_period()
            end_date = min(end_date, today)  # Ne pas dépasser aujourd'hui
            fiscal_year = company_profile.get_fiscal_year_for_date(today)
            period_name = f"Année fiscale {fiscal_year}"
        else:
            # Fallback vers l'année civile
            start_date = today.replace(month=1, day=1)
            end_date = today
            period_name = f"Année {today.year}"
    elif period == 'current_year':
        start_date = today.replace(month=1, day=1)
        end_date = today
        period_name = f"Année civile {today.year}"
    elif period == 'last_fiscal_year':
        if company_profile:
            current_fiscal_year = company_profile.get_fiscal_year_for_date(today)
            start_date, end_date = company_profile.get_fiscal_year_period(current_fiscal_year - 1)
            period_name = f"Année fiscale {current_fiscal_year - 1}"
        else:
            # Fallback vers l'année civile précédente
            start_date = today.replace(year=today.year-1, month=1, day=1)
            end_date = today.replace(year=today.year-1, month=12, day=31)
            period_name = f"Année {today.year - 1}"
    elif period == 'last_month':
        if today.month == 1:
            start_date = today.replace(year=today.year-1, month=12, day=1)
            end_date = today.replace(day=1) - timedelta(days=1)
        else:
            start_date = today.replace(month=today.month-1, day=1)
            if today.month == 1:
                end_date = today.replace(year=today.year-1, month=12, day=31)
            else:
                next_month = today.replace(month=today.month, day=1)
                end_date = next_month - timedelta(days=1)
        period_name = f"{start_date.strftime('%B %Y')}"
    else:
        start_date = today.replace(day=1)
        end_date = today
        period_name = f"{start_date.strftime('%B %Y')}"

    # Calculs financiers
    # Revenus (exclure les données archivées)
    paid_invoices = Invoice.objects.filter(
        invoice_date__gte=start_date,
        invoice_date__lte=end_date,
        status='paid',
        archived_fiscal_year__isnull=True
    )

    total_revenue = paid_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    total_subtotal = paid_invoices.aggregate(total=Sum('subtotal'))['total'] or 0
    total_gst_collected = paid_invoices.aggregate(total=Sum('gst_amount'))['total'] or 0
    total_qst_collected = paid_invoices.aggregate(total=Sum('qst_amount'))['total'] or 0

    # Dépenses (exclure les données archivées)
    period_expenses = Expense.objects.filter(
        expense_date__gte=start_date,
        expense_date__lte=end_date,
        archived_fiscal_year__isnull=True
    )

    total_expenses = period_expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_gst_paid = period_expenses.aggregate(total=Sum('gst_amount'))['total'] or 0
    total_qst_paid = period_expenses.aggregate(total=Sum('qst_amount'))['total'] or 0

    # Profit/Perte
    net_profit = total_subtotal - total_expenses

    # Taxes nettes
    net_gst = total_gst_collected - total_gst_paid
    net_qst = total_qst_collected - total_qst_paid

    # Analyse des modes de paiement
    payment_methods_data = {}
    cash_total = paid_invoices.filter(payment_method='cash').aggregate(total=Sum('total_amount'))['total'] or 0
    debit_total = paid_invoices.filter(payment_method='debit').aggregate(total=Sum('total_amount'))['total'] or 0
    credit_total = paid_invoices.filter(payment_method='credit').aggregate(total=Sum('total_amount'))['total'] or 0
    cheque_total = paid_invoices.filter(payment_method='cheque').aggregate(total=Sum('total_amount'))['total'] or 0
    transfer_total = paid_invoices.filter(payment_method='transfer').aggregate(total=Sum('total_amount'))['total'] or 0
    other_total = paid_invoices.filter(payment_method='other').aggregate(total=Sum('total_amount'))['total'] or 0
    no_method_total = paid_invoices.filter(payment_method__isnull=True).aggregate(total=Sum('total_amount'))['total'] or 0

    # Regroupement pour faciliter l'affichage
    payment_methods_data = {
        'cash': {'name': 'Argent comptant', 'total': cash_total, 'icon': 'fas fa-money-bill-wave', 'color': 'success'},
        'debit': {'name': 'Carte de débit', 'total': debit_total, 'icon': 'fas fa-credit-card', 'color': 'primary'},
        'credit': {'name': 'Carte de crédit', 'total': credit_total, 'icon': 'fas fa-credit-card', 'color': 'warning'},
        'cheque': {'name': 'Chèque', 'total': cheque_total, 'icon': 'fas fa-money-check', 'color': 'info'},
        'transfer': {'name': 'Virement bancaire', 'total': transfer_total, 'icon': 'fas fa-exchange-alt', 'color': 'secondary'},
        'other': {'name': 'Autre', 'total': other_total, 'icon': 'fas fa-question', 'color': 'dark'},
        'no_method': {'name': 'Non spécifié', 'total': no_method_total, 'icon': 'fas fa-minus', 'color': 'muted'},
    }

    # Calculs pour dépôts bancaires vs argent en main
    bank_deposits = debit_total + credit_total + transfer_total + cheque_total  # Argent qui va directement en banque
    cash_in_hand = cash_total  # Argent comptant à déposer manuellement
    total_tracked_payments = sum(data['total'] for data in payment_methods_data.values())

    # Différence entre revenus totaux et paiements trackés
    payment_tracking_difference = total_revenue - total_tracked_payments

    # Répartition par catégorie
    expense_by_category = period_expenses.values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')

    revenue_by_service = paid_invoices.values(
        'invoice_items__service__category'
    ).annotate(
        total=Sum('invoice_items__unit_price')
    ).order_by('-total')

    context = {
        'period': period,
        'period_name': period_name,
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'total_subtotal': total_subtotal,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'total_gst_collected': total_gst_collected,
        'total_qst_collected': total_qst_collected,
        'total_gst_paid': total_gst_paid,
        'total_qst_paid': total_qst_paid,
        'net_gst': net_gst,
        'net_qst': net_qst,
        'expense_by_category': expense_by_category,
        'revenue_by_service': revenue_by_service,
        'paid_invoices_count': paid_invoices.count(),
        'expenses_count': period_expenses.count(),
        # Nouveaux données de paiement
        'payment_methods_data': payment_methods_data,
        'bank_deposits': bank_deposits,
        'cash_in_hand': cash_in_hand,
        'total_tracked_payments': total_tracked_payments,
        'payment_tracking_difference': payment_tracking_difference,
        # Informations sur les périodes fiscales
        'has_company_profile': company_profile is not None,
        'company_profile': company_profile,
    }

    return render(request, 'garage_app/reports/financial_reports.html', context)


# ==================== VUES AJAX ====================

@login_required
def get_client_vehicles(request, client_id):
    """Vue AJAX pour récupérer les véhicules d'un client"""
    try:
        client = get_object_or_404(Client, id=client_id)
        vehicles = client.vehicles.all()

        vehicles_data = []
        for vehicle in vehicles:
            vehicles_data.append({
                'id': vehicle.id,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'color': vehicle.color or '',
            })

        return JsonResponse({'vehicles': vehicles_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ==================== VUES POUR LES FOURNISSEURS ====================

@login_required
def supplier_list(request):
    """Vue pour lister les fournisseurs"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    suppliers = Supplier.objects.all()

    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    if category_filter:
        suppliers = suppliers.filter(category=category_filter)

    suppliers = suppliers.order_by('name')

    # Pagination
    paginator = Paginator(suppliers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Catégories pour le filtre
    categories = Supplier.SUPPLIER_CATEGORY_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
    }

    return render(request, 'garage_app/suppliers/supplier_list.html', context)


@login_required
def supplier_detail(request, supplier_id):
    """Vue pour afficher les détails d'un fournisseur"""
    supplier = get_object_or_404(Supplier, id=supplier_id)

    # Statistiques du fournisseur
    recent_expenses = supplier.expenses.order_by('-expense_date')[:10]
    total_expenses = supplier.expenses.aggregate(total=Sum('amount'))['total'] or 0
    expense_count = supplier.expenses.count()

    context = {
        'supplier': supplier,
        'recent_expenses': recent_expenses,
        'total_expenses': total_expenses,
        'expense_count': expense_count,
    }

    return render(request, 'garage_app/suppliers/supplier_detail.html', context)


@login_required
def supplier_create(request):
    """Vue pour créer un nouveau fournisseur"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Fournisseur "{supplier.name}" créé avec succès.')
            return redirect('garage_app:supplier_detail', supplier_id=supplier.id)
    else:
        form = SupplierForm()

    context = {
        'form': form,
        'title': 'Nouveau fournisseur',
    }

    return render(request, 'garage_app/suppliers/supplier_form.html', context)


@login_required
def supplier_edit(request, supplier_id):
    """Vue pour modifier un fournisseur"""
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Fournisseur "{supplier.name}" modifié avec succès.')
            return redirect('garage_app:supplier_detail', supplier_id=supplier.id)
    else:
        form = SupplierForm(instance=supplier)

    context = {
        'form': form,
        'supplier': supplier,
        'title': f'Modifier {supplier.name}',
    }

    return render(request, 'garage_app/suppliers/supplier_form.html', context)


@login_required
def supplier_delete(request, supplier_id):
    """Vue pour supprimer un fournisseur"""
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        supplier_name = supplier.name
        supplier.delete()
        messages.success(request, f'Fournisseur "{supplier_name}" supprimé avec succès.')
        return redirect('garage_app:supplier_list')

    context = {
        'supplier': supplier,
    }

    return render(request, 'garage_app/suppliers/supplier_confirm_delete.html', context)


# ==================== VUES POUR LES DÉPENSES RÉCURRENTES ====================

@login_required
def recurring_expense_list(request):
    """Vue pour lister les dépenses récurrentes"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    recurring_expenses = RecurringExpense.objects.all()

    if search_query:
        recurring_expenses = recurring_expenses.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )

    if status_filter == 'active':
        recurring_expenses = recurring_expenses.filter(is_active=True)
    elif status_filter == 'inactive':
        recurring_expenses = recurring_expenses.filter(is_active=False)
    elif status_filter == 'due':
        recurring_expenses = recurring_expenses.filter(
            is_active=True,
            next_due_date__lte=date.today()
        )

    recurring_expenses = recurring_expenses.order_by('next_due_date', 'name')

    # Pagination
    paginator = Paginator(recurring_expenses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistiques
    due_count = RecurringExpense.objects.filter(
        is_active=True,
        next_due_date__lte=date.today()
    ).count()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'due_count': due_count,
    }

    return render(request, 'garage_app/recurring_expenses/recurring_expense_list.html', context)


@login_required
def recurring_expense_detail(request, recurring_expense_id):
    """Vue pour afficher les détails d'une dépense récurrente"""
    recurring_expense = get_object_or_404(RecurringExpense, id=recurring_expense_id)

    # Historique des dépenses créées
    related_expenses = Expense.objects.filter(
        description__icontains=recurring_expense.name
    ).order_by('-expense_date')[:10]

    context = {
        'recurring_expense': recurring_expense,
        'related_expenses': related_expenses,
    }

    return render(request, 'garage_app/recurring_expenses/recurring_expense_detail.html', context)


@login_required
def recurring_expense_create(request):
    """Vue pour créer une nouvelle dépense récurrente"""
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST)
        if form.is_valid():
            recurring_expense = form.save()
            messages.success(request, f'Dépense récurrente "{recurring_expense.name}" créée avec succès.')
            return redirect('garage_app:recurring_expense_detail', recurring_expense_id=recurring_expense.id)
    else:
        form = RecurringExpenseForm()

    context = {
        'form': form,
        'title': 'Nouvelle dépense récurrente',
    }

    return render(request, 'garage_app/recurring_expenses/recurring_expense_form.html', context)


@login_required
def recurring_expense_edit(request, recurring_expense_id):
    """Vue pour modifier une dépense récurrente"""
    recurring_expense = get_object_or_404(RecurringExpense, id=recurring_expense_id)

    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST, instance=recurring_expense)
        if form.is_valid():
            recurring_expense = form.save()
            messages.success(request, f'Dépense récurrente "{recurring_expense.name}" modifiée avec succès.')
            return redirect('garage_app:recurring_expense_detail', recurring_expense_id=recurring_expense.id)
    else:
        form = RecurringExpenseForm(instance=recurring_expense)

    context = {
        'form': form,
        'recurring_expense': recurring_expense,
        'title': f'Modifier {recurring_expense.name}',
    }

    return render(request, 'garage_app/recurring_expenses/recurring_expense_form.html', context)


@login_required
def recurring_expense_delete(request, recurring_expense_id):
    """Vue pour supprimer une dépense récurrente"""
    recurring_expense = get_object_or_404(RecurringExpense, id=recurring_expense_id)

    if request.method == 'POST':
        recurring_expense_name = recurring_expense.name
        recurring_expense.delete()
        messages.success(request, f'Dépense récurrente "{recurring_expense_name}" supprimée avec succès.')
        return redirect('garage_app:recurring_expense_list')

    context = {
        'recurring_expense': recurring_expense,
    }

    return render(request, 'garage_app/recurring_expenses/recurring_expense_confirm_delete.html', context)


@login_required
def create_due_recurring_expenses(request):
    """Vue pour créer les dépenses récurrentes dues"""
    if request.method == 'POST':
        from django.core.management import call_command
        from io import StringIO

        # Capturer la sortie de la commande
        output = StringIO()
        try:
            call_command('create_recurring_expenses', stdout=output)
            messages.success(request, 'Dépenses récurrentes créées avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création des dépenses: {str(e)}')

        return redirect('garage_app:recurring_expense_list')

    # Obtenir les dépenses dues
    due_expenses = RecurringExpense.objects.filter(
        is_active=True,
        next_due_date__lte=date.today()
    )

    context = {
        'due_expenses': due_expenses,
    }

    return render(request, 'garage_app/recurring_expenses/create_due_expenses.html', context)


# ==================== VUES POUR LES RENDEZ-VOUS ====================

@login_required
def appointment_list(request):
    """Vue pour lister les rendez-vous"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')

    appointments = Appointment.objects.all()

    if search_query:
        appointments = appointments.filter(
            Q(title__icontains=search_query) |
            Q(client__first_name__icontains=search_query) |
            Q(client__last_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    if date_filter == 'today':
        appointments = appointments.filter(start_datetime__date=date.today())
    elif date_filter == 'week':
        from datetime import timedelta
        week_start = date.today() - timedelta(days=date.today().weekday())
        week_end = week_start + timedelta(days=6)
        appointments = appointments.filter(
            start_datetime__date__gte=week_start,
            start_datetime__date__lte=week_end
        )
    elif date_filter == 'month':
        appointments = appointments.filter(
            start_datetime__year=date.today().year,
            start_datetime__month=date.today().month
        )

    appointments = appointments.order_by('start_datetime')

    # Pagination
    paginator = Paginator(appointments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistiques
    today_count = Appointment.objects.filter(start_datetime__date=date.today()).count()
    pending_count = Appointment.objects.filter(status__in=['scheduled', 'confirmed']).count()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'today_count': today_count,
        'pending_count': pending_count,
        'status_choices': Appointment.STATUS_CHOICES,
    }

    return render(request, 'garage_app/appointments/appointment_list.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """Vue pour afficher les détails d'un rendez-vous"""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    context = {
        'appointment': appointment,
    }

    return render(request, 'garage_app/appointments/appointment_detail.html', context)


@login_required
def appointment_create(request):
    """Vue pour créer un nouveau rendez-vous"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, f'Rendez-vous "{appointment.title}" créé avec succès.')
            return redirect('garage_app:appointment_detail', appointment_id=appointment.id)
    else:
        form = AppointmentForm()

    context = {
        'form': form,
        'title': 'Nouveau rendez-vous',
    }

    return render(request, 'garage_app/appointments/appointment_form.html', context)


@login_required
def appointment_edit(request, appointment_id):
    """Vue pour modifier un rendez-vous"""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, f'Rendez-vous "{appointment.title}" modifié avec succès.')
            return redirect('garage_app:appointment_detail', appointment_id=appointment.id)
    else:
        form = AppointmentForm(instance=appointment)

    context = {
        'form': form,
        'appointment': appointment,
        'title': f'Modifier {appointment.title}',
    }

    return render(request, 'garage_app/appointments/appointment_form.html', context)


@login_required
def appointment_delete(request, appointment_id):
    """Vue pour supprimer un rendez-vous"""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        appointment_title = appointment.title
        appointment.delete()
        messages.success(request, f'Rendez-vous "{appointment_title}" supprimé avec succès.')
        return redirect('garage_app:appointment_list')

    context = {
        'appointment': appointment,
    }

    return render(request, 'garage_app/appointments/appointment_confirm_delete.html', context)


@login_required
def appointment_create_invoice(request, appointment_id):
    """Vue pour créer une facture à partir d'un rendez-vous"""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if not appointment.can_create_invoice():
        messages.error(request, 'Impossible de créer une facture pour ce rendez-vous.')
        return redirect('garage_app:appointment_detail', appointment_id=appointment.id)

    if request.method == 'POST':
        try:
            invoice = appointment.create_invoice_from_appointment()
            messages.success(request, f'Facture {invoice.invoice_number} créée avec succès.')
            return redirect('garage_app:invoice_detail', invoice_id=invoice.id)
        except Exception as e:
            messages.error(request, f'Erreur lors de la création de la facture: {str(e)}')

    context = {
        'appointment': appointment,
    }

    return render(request, 'garage_app/appointments/appointment_create_invoice.html', context)


@login_required
def appointment_calendar(request):
    """Vue pour afficher le calendrier des rendez-vous"""
    # Cette vue servira la page du calendrier
    # Le calendrier sera géré par JavaScript côté client

    context = {
        'title': 'Calendrier des rendez-vous',
    }

    return render(request, 'garage_app/appointments/appointment_calendar.html', context)


@login_required
def appointment_calendar_api(request):
    """API pour récupérer les rendez-vous au format JSON pour le calendrier"""
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    appointments = Appointment.objects.all()

    if start_date and end_date:
        from datetime import datetime
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        appointments = appointments.filter(
            start_datetime__gte=start,
            end_datetime__lte=end
        )

    events = []
    for appointment in appointments:
        # Couleurs selon le statut
        color_map = {
            'scheduled': '#6c757d',  # Gris
            'confirmed': '#0d6efd',  # Bleu
            'in_progress': '#fd7e14', # Orange
            'completed': '#198754',  # Vert
            'cancelled': '#dc3545',  # Rouge
            'no_show': '#6f42c1',    # Violet
        }

        events.append({
            'id': appointment.id,
            'title': f"{appointment.title} - {appointment.client.full_name}",
            'start': appointment.start_datetime.isoformat(),
            'end': appointment.end_datetime.isoformat(),
            'backgroundColor': color_map.get(appointment.status, '#6c757d'),
            'borderColor': color_map.get(appointment.status, '#6c757d'),
            'extendedProps': {
                'client': appointment.client.full_name,
                'vehicle': f"{appointment.vehicle.year} {appointment.vehicle.make} {appointment.vehicle.model}" if appointment.vehicle else '',
                'status': appointment.get_status_display(),
                'description': appointment.description or '',
                'estimated_price': str(appointment.estimated_price) if appointment.estimated_price else '',
            }
        })

    return JsonResponse(events, safe=False)


# ==================== VUES POUR L'INVENTAIRE ====================

@login_required
def inventory_list(request):
    """Vue pour lister les articles d'inventaire"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    supplier_filter = request.GET.get('supplier', '')

    inventory_items = InventoryItem.objects.all()

    if search_query:
        inventory_items = inventory_items.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        inventory_items = inventory_items.filter(category=category_filter)

    if supplier_filter:
        inventory_items = inventory_items.filter(supplier_id=supplier_filter)

    inventory_items = inventory_items.order_by('name')

    # Pagination
    paginator = Paginator(inventory_items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Données pour les filtres
    categories = InventoryItem.INVENTORY_CATEGORY_CHOICES
    suppliers = Supplier.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'supplier_filter': supplier_filter,
        'categories': categories,
        'suppliers': suppliers,
    }

    return render(request, 'garage_app/inventory/inventory_list.html', context)


# ==================== VUES POUR LES BONS DE RÉCEPTION ====================

@login_required
def stock_receipt_list(request):
    """Vue pour lister les bons de réception"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    supplier_filter = request.GET.get('supplier', '')

    stock_receipts = StockReceipt.objects.all()

    if search_query:
        stock_receipts = stock_receipts.filter(
            Q(receipt_number__icontains=search_query) |
            Q(supplier__name__icontains=search_query) |
            Q(supplier_invoice_number__icontains=search_query)
        )

    if status_filter:
        stock_receipts = stock_receipts.filter(status=status_filter)

    if supplier_filter:
        stock_receipts = stock_receipts.filter(supplier_id=supplier_filter)

    stock_receipts = stock_receipts.order_by('-receipt_date', '-created_at')

    # Pagination
    paginator = Paginator(stock_receipts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Données pour les filtres
    suppliers = Supplier.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'supplier_filter': supplier_filter,
        'suppliers': suppliers,
        'status_choices': StockReceipt.STATUS_CHOICES,
    }

    return render(request, 'garage_app/stock_receipts/stock_receipt_list.html', context)


@login_required
def stock_receipt_detail(request, stock_receipt_id):
    """Vue pour afficher les détails d'un bon de réception"""
    stock_receipt = get_object_or_404(StockReceipt, id=stock_receipt_id)

    context = {
        'stock_receipt': stock_receipt,
    }

    return render(request, 'garage_app/stock_receipts/stock_receipt_detail.html', context)


@login_required
def stock_receipt_create(request):
    """Vue pour créer un nouveau bon de réception"""
    if request.method == 'POST':
        form = StockReceiptForm(request.POST)
        formset = StockReceiptItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            stock_receipt = form.save()
            formset.instance = stock_receipt
            formset.save()

            # Calculer les totaux
            stock_receipt.calculate_totals()

            messages.success(request, f'Bon de réception {stock_receipt.receipt_number} créé avec succès.')
            return redirect('garage_app:stock_receipt_detail', stock_receipt_id=stock_receipt.id)
    else:
        form = StockReceiptForm()
        formset = StockReceiptItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': 'Nouveau bon de réception',
    }

    return render(request, 'garage_app/stock_receipts/stock_receipt_form.html', context)


@login_required
def stock_receipt_edit(request, stock_receipt_id):
    """Vue pour modifier un bon de réception"""
    stock_receipt = get_object_or_404(StockReceipt, id=stock_receipt_id)

    if request.method == 'POST':
        form = StockReceiptForm(request.POST, instance=stock_receipt)
        formset = StockReceiptItemFormSet(request.POST, instance=stock_receipt)

        if form.is_valid() and formset.is_valid():
            stock_receipt = form.save()
            formset.save()

            # Calculer les totaux
            stock_receipt.calculate_totals()

            messages.success(request, f'Bon de réception {stock_receipt.receipt_number} modifié avec succès.')
            return redirect('garage_app:stock_receipt_detail', stock_receipt_id=stock_receipt.id)
    else:
        form = StockReceiptForm(instance=stock_receipt)
        formset = StockReceiptItemFormSet(instance=stock_receipt)

    context = {
        'form': form,
        'formset': formset,
        'stock_receipt': stock_receipt,
        'title': f'Modifier {stock_receipt.receipt_number}',
    }

    return render(request, 'garage_app/stock_receipts/stock_receipt_form.html', context)


@login_required
def stock_receipt_delete(request, stock_receipt_id):
    """Vue pour supprimer un bon de réception"""
    stock_receipt = get_object_or_404(StockReceipt, id=stock_receipt_id)

    if request.method == 'POST':
        receipt_number = stock_receipt.receipt_number
        stock_receipt.delete()
        messages.success(request, f'Bon de réception {receipt_number} supprimé avec succès.')
        return redirect('garage_app:stock_receipt_list')

    context = {
        'stock_receipt': stock_receipt,
    }

    return render(request, 'garage_app/stock_receipts/stock_receipt_confirm_delete.html', context)


@login_required
def stock_receipt_process(request, stock_receipt_id):
    """Vue pour traiter un bon de réception (mettre à jour l'inventaire et créer la dépense)"""
    stock_receipt = get_object_or_404(StockReceipt, id=stock_receipt_id)

    if request.method == 'POST':
        if stock_receipt.status == 'received':
            if stock_receipt.process_receipt():
                messages.success(request, f'Bon de réception {stock_receipt.receipt_number} traité avec succès. Inventaire mis à jour et dépense créée.')
            else:
                messages.error(request, 'Erreur lors du traitement du bon de réception.')
        else:
            messages.error(request, 'Seuls les bons de réception avec le statut "Reçu" peuvent être traités.')

        return redirect('garage_app:stock_receipt_detail', stock_receipt_id=stock_receipt.id)

    context = {
        'stock_receipt': stock_receipt,
    }

    return render(request, 'garage_app/stock_receipts/stock_receipt_process.html', context)
