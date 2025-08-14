from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import HttpResponse, JsonResponse
from datetime import date, timedelta
from .models import Invoice, Expense, Payment, Client, Service, CompanyProfile, Vehicle, InvoiceItem
from .forms import CompanyProfileForm, ClientForm, VehicleForm, ServiceForm, InvoiceForm, InvoiceItemFormSet, ExpenseForm
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
    # Statistiques financières
    today = date.today()
    current_month = today.replace(day=1)
    current_year = today.replace(month=1, day=1)

    # Revenus
    monthly_revenue = Invoice.objects.filter(
        invoice_date__gte=current_month,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    yearly_revenue = Invoice.objects.filter(
        invoice_date__gte=current_year,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Dépenses
    monthly_expenses = Expense.objects.filter(
        expense_date__gte=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    yearly_expenses = Expense.objects.filter(
        expense_date__gte=current_year
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
        'current_year': current_year.year,
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
    # Période sélectionnée
    period = request.GET.get('period', 'current_month')

    today = date.today()

    if period == 'current_month':
        start_date = today.replace(day=1)
        end_date = today
        period_name = f"{start_date.strftime('%B %Y')}"
    elif period == 'current_year':
        start_date = today.replace(month=1, day=1)
        end_date = today
        period_name = f"Année {today.year}"
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
    # Revenus
    paid_invoices = Invoice.objects.filter(
        invoice_date__gte=start_date,
        invoice_date__lte=end_date,
        status='paid'
    )

    total_revenue = paid_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    total_subtotal = paid_invoices.aggregate(total=Sum('subtotal'))['total'] or 0
    total_gst_collected = paid_invoices.aggregate(total=Sum('gst_amount'))['total'] or 0
    total_qst_collected = paid_invoices.aggregate(total=Sum('qst_amount'))['total'] or 0

    # Dépenses
    period_expenses = Expense.objects.filter(
        expense_date__gte=start_date,
        expense_date__lte=end_date
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
