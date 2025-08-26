from django.urls import path
from . import views

app_name = 'garage_app'

urlpatterns = [
    # Dashboard et authentification
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('company-profile/', views.company_profile, name='company_profile'),

    # Gestion des clients
    path('clients/', views.client_list, name='client_list'),
    path('clients/<int:client_id>/', views.client_detail, name='client_detail'),
    path('clients/new/', views.client_create, name='client_create'),
    path('clients/<int:client_id>/edit/', views.client_update, name='client_update'),
    path('clients/<int:client_id>/delete/', views.client_delete, name='client_delete'),
    path('clients/<int:client_id>/vehicles/', views.client_vehicles_ajax, name='client_vehicles_ajax'),

    # Gestion des véhicules
    path('vehicles/new/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/new/<int:client_id>/', views.vehicle_create, name='vehicle_create_for_client'),
    path('vehicles/<int:vehicle_id>/edit/', views.vehicle_update, name='vehicle_update'),
    path('vehicles/<int:vehicle_id>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('vehicles/identify-type/', views.identify_vehicle_type, name='identify_vehicle_type'),
    path('api/vehicle-makes/', views.get_vehicle_makes, name='get_vehicle_makes'),
    path('api/vehicle-models/', views.get_vehicle_models, name='get_vehicle_models'),

    # Calculateur de lettrage
    path('lettering/calculator/', views.lettering_calculator, name='lettering_calculator'),
    path('api/lettering/calculate/', views.lettering_calculate_ajax, name='lettering_calculate_ajax'),
    path('api/lettering/save-quote/', views.lettering_save_quote, name='lettering_save_quote'),

    # Gestion des services
    path('services/', views.service_list, name='service_list'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),
    path('services/new/', views.service_create, name='service_create'),
    path('services/<int:service_id>/edit/', views.service_update, name='service_update'),
    path('services/<int:service_id>/delete/', views.service_delete, name='service_delete'),

    # Gestion des factures
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/print/', views.invoice_print, name='invoice_print'),
    path('invoices/new/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:invoice_id>/edit/', views.invoice_update, name='invoice_update'),
    path('invoices/<int:invoice_id>/mark-paid/', views.invoice_mark_paid, name='invoice_mark_paid'),
    path('invoices/<int:invoice_id>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<int:invoice_id>/pdf/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('invoices/<int:invoice_id>/send/', views.send_invoice_email, name='send_invoice_email'),

    # Gestion des soumissions
    path('quotes/', views.quote_list, name='quote_list'),
    path('quotes/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('quotes/new/', views.quote_create, name='quote_create'),
    path('quotes/<int:quote_id>/edit/', views.quote_update, name='quote_update'),
    path('quotes/<int:quote_id>/delete/', views.quote_delete, name='quote_delete'),
    path('quotes/<int:quote_id>/convert/', views.quote_convert_to_invoice, name='quote_convert_to_invoice'),

    # Gestion des dépenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/<int:expense_id>/', views.expense_detail, name='expense_detail'),
    path('expenses/new/', views.expense_create, name='expense_create'),
    path('expenses/<int:expense_id>/edit/', views.expense_update, name='expense_update'),
    path('expenses/<int:expense_id>/delete/', views.expense_delete, name='expense_delete'),

    # Rapports financiers
    path('reports/', views.financial_reports, name='financial_reports'),

    # AJAX endpoints
    path('ajax/get-vehicles/<int:client_id>/', views.get_client_vehicles, name='get_client_vehicles'),
    path('ajax/get-client-info/<int:client_id>/', views.get_client_info, name='get_client_info'),
    path('ajax/get-services/', views.get_services, name='get_services'),

    # URLs pour les fournisseurs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', views.supplier_delete, name='supplier_delete'),

    # URLs pour les dépenses récurrentes
    path('recurring-expenses/', views.recurring_expense_list, name='recurring_expense_list'),
    path('recurring-expenses/create/', views.recurring_expense_create, name='recurring_expense_create'),
    path('recurring-expenses/<int:recurring_expense_id>/', views.recurring_expense_detail, name='recurring_expense_detail'),
    path('recurring-expenses/<int:recurring_expense_id>/edit/', views.recurring_expense_edit, name='recurring_expense_edit'),
    path('recurring-expenses/<int:recurring_expense_id>/delete/', views.recurring_expense_delete, name='recurring_expense_delete'),
    path('recurring-expenses/create-due/', views.create_due_recurring_expenses, name='create_due_recurring_expenses'),

    # URLs pour les rendez-vous
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/edit/', views.appointment_edit, name='appointment_edit'),
    path('appointments/<int:appointment_id>/delete/', views.appointment_delete, name='appointment_delete'),
    path('appointments/<int:appointment_id>/create-invoice/', views.appointment_create_invoice, name='appointment_create_invoice'),
    path('appointments/calendar/', views.appointment_calendar, name='appointment_calendar'),
    path('api/appointments/', views.appointment_calendar_api, name='appointment_calendar_api'),
    path('appointments/api/date/<str:date>/', views.appointment_date_api, name='appointment_date_api'),
    path('ajax/get-services/', views.get_services_ajax, name='get_services_ajax'),

    # URLs pour l'inventaire
    path('inventory/', views.inventory_list, name='inventory_list'),

    # URLs pour les alertes de stock
    path('stock-alerts/', views.stock_alerts_dashboard, name='stock_alerts_dashboard'),
    path('stock-alerts/<int:alert_id>/', views.stock_alert_detail, name='stock_alert_detail'),
    path('stock-alerts/run-check/', views.run_stock_check, name='run_stock_check'),

    # URLs pour les bons de réception
    path('stock-receipts/', views.stock_receipt_list, name='stock_receipt_list'),
    path('stock-receipts/create/', views.stock_receipt_create, name='stock_receipt_create'),
    path('stock-receipts/<int:stock_receipt_id>/', views.stock_receipt_detail, name='stock_receipt_detail'),
    path('stock-receipts/<int:stock_receipt_id>/edit/', views.stock_receipt_edit, name='stock_receipt_edit'),
    path('stock-receipts/<int:stock_receipt_id>/delete/', views.stock_receipt_delete, name='stock_receipt_delete'),
    path('stock-receipts/<int:stock_receipt_id>/process/', views.stock_receipt_process, name='stock_receipt_process'),
]
