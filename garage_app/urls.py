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

    # Gestion des véhicules
    path('vehicles/new/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/new/<int:client_id>/', views.vehicle_create, name='vehicle_create_for_client'),
    path('vehicles/<int:vehicle_id>/edit/', views.vehicle_update, name='vehicle_update'),
    path('vehicles/<int:vehicle_id>/delete/', views.vehicle_delete, name='vehicle_delete'),

    # Gestion des services
    path('services/', views.service_list, name='service_list'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),
    path('services/new/', views.service_create, name='service_create'),
    path('services/<int:service_id>/edit/', views.service_update, name='service_update'),
    path('services/<int:service_id>/delete/', views.service_delete, name='service_delete'),

    # Gestion des factures
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/new/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:invoice_id>/edit/', views.invoice_update, name='invoice_update'),
    path('invoices/<int:invoice_id>/mark-paid/', views.invoice_mark_paid, name='invoice_mark_paid'),
    path('invoices/<int:invoice_id>/pdf/', views.generate_invoice_pdf, name='generate_invoice_pdf'),

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
]
