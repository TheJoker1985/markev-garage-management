"""
Test complet d'envoi d'email de facture avec PDF
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markev_project.settings')
django.setup()

from garage_app.models import Client, Vehicle, Invoice, Service, VehicleType
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.conf import settings

def create_test_data():
    """Créer des données de test pour la facture"""
    print("📋 Création des données de test...")
    
    # Créer un client de test
    client, created = Client.objects.get_or_create(
        email='the_adicts@hotmail.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'SendGrid',
            'phone': '514-123-4567',
            'address': '123 Rue Test, Montréal, QC'
        }
    )
    
    if created:
        print(f"✅ Client créé : {client.first_name} {client.last_name}")
    else:
        print(f"✅ Client existant : {client.first_name} {client.last_name}")
    
    # Créer un type de véhicule
    vehicle_type, _ = VehicleType.objects.get_or_create(
        name='Berline',
        defaults={'description': 'Véhicule de type berline'}
    )
    
    # Créer un véhicule de test
    vehicle, created = Vehicle.objects.get_or_create(
        client=client,
        make='Toyota',
        model='Camry',
        year=2023,
        defaults={
            'vehicle_type': vehicle_type,
            'color': 'Blanc',
            'license_plate': 'TEST123'
        }
    )
    
    if created:
        print(f"✅ Véhicule créé : {vehicle.make} {vehicle.model} {vehicle.year}")
    else:
        print(f"✅ Véhicule existant : {vehicle.make} {vehicle.model} {vehicle.year}")
    
    # Créer des services de test
    service1, _ = Service.objects.get_or_create(
        name='Vitre Teintée - Standard',
        defaults={
            'category': 'vitres_teintees',
            'quality_level': 'standard',
            'price': 299.99,
            'description': 'Installation de vitres teintées standard'
        }
    )
    
    service2, _ = Service.objects.get_or_create(
        name='Protection Céramique - Premium',
        defaults={
            'category': 'protection_ceramique',
            'quality_level': 'premium',
            'price': 899.99,
            'description': 'Application de protection céramique premium'
        }
    )
    
    print(f"✅ Services disponibles : {service1.name}, {service2.name}")
    
    return client, vehicle, [service1, service2]

def create_test_invoice(client, vehicle, services):
    """Créer une facture de test"""
    print("\n📄 Création de la facture de test...")

    from django.utils import timezone

    # Créer la facture
    invoice = Invoice.objects.create(
        client=client,
        vehicle=vehicle,
        status='finalized',
        invoice_date=timezone.now().date(),
        notes='Facture de test pour validation SendGrid'
    )
    
    # Ajouter les services
    for service in services:
        invoice.services.add(service)
    
    # Calculer le total
    invoice.calculate_total()
    invoice.save()
    
    print(f"✅ Facture créée : #{invoice.id}")
    print(f"   Client : {client.first_name} {client.last_name}")
    print(f"   Véhicule : {vehicle.make} {vehicle.model} {vehicle.year}")
    print(f"   Services : {invoice.services.count()}")
    print(f"   Total : ${invoice.total_amount:.2f}")
    
    return invoice

def test_email_sending(invoice):
    """Tester l'envoi d'email avec la facture"""
    print(f"\n📧 Test d'envoi d'email pour la facture #{invoice.id}...")

    try:
        # Générer le PDF de la facture
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from io import BytesIO

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Contenu du PDF
        p.drawString(100, 750, f"FACTURE #{invoice.id}")
        p.drawString(100, 720, f"Garage MarKev")
        p.drawString(100, 690, f"Client: {invoice.client.first_name} {invoice.client.last_name}")
        p.drawString(100, 660, f"Véhicule: {invoice.vehicle.make} {invoice.vehicle.model} {invoice.vehicle.year}")
        p.drawString(100, 630, f"Total: ${invoice.total_amount:.2f}")
        p.drawString(100, 600, f"Date: {invoice.created_at.strftime('%Y-%m-%d')}")

        # Services
        y_position = 570
        p.drawString(100, y_position, "Services:")
        for service in invoice.services.all():
            y_position -= 20
            p.drawString(120, y_position, f"• {service.name} - ${service.price:.2f}")

        p.showPage()
        p.save()

        # Créer l'email
        subject = f"Facture #{invoice.id} - Garage MarKev"
        message = f"""
Bonjour {invoice.client.first_name},

Veuillez trouver ci-joint votre facture #{invoice.id}.

Détails:
- Véhicule: {invoice.vehicle.make} {invoice.vehicle.model} {invoice.vehicle.year}
- Montant total: ${invoice.total_amount:.2f}
- Date: {invoice.created_at.strftime('%Y-%m-%d')}

Merci de votre confiance !

Cordialement,
L'équipe Garage MarKev
        """

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.client.email],
        )

        # Attacher le PDF
        buffer.seek(0)
        email.attach(f'facture_{invoice.id}.pdf', buffer.getvalue(), 'application/pdf')

        # Envoyer l'email
        email.send()

        print("✅ Email envoyé avec succès !")
        print(f"📧 Destinataire : {invoice.client.email}")
        print(f"📄 Facture : #{invoice.id}")
        print(f"💰 Montant : ${invoice.total_amount:.2f}")

        print(f"\n📋 Détails de l'envoi :")
        print(f"   Expéditeur : {settings.DEFAULT_FROM_EMAIL}")
        print(f"   Destinataire : {invoice.client.email}")
        print(f"   Sujet : {subject}")
        print(f"   PDF inclus : Oui")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'envoi : {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_action():
    """Tester l'action d'administration SendGrid"""
    print(f"\n🔧 Test de l'action d'administration...")
    
    from django.test import RequestFactory
    from garage_app.admin import VehicleAdmin
    from garage_app.models import Vehicle
    
    # Créer une requête factice
    factory = RequestFactory()
    request = factory.get('/admin/')
    
    # Créer un utilisateur admin
    user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'the_adicts@hotmail.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    request.user = user
    
    # Tester l'action
    admin = VehicleAdmin(Vehicle, None)
    queryset = Vehicle.objects.all()[:1]  # Prendre un véhicule
    
    try:
        admin.test_sendgrid_config(request, queryset)
        print("✅ Action d'administration exécutée")
        return True
    except Exception as e:
        print(f"❌ Erreur action admin : {str(e)}")
        return False

def cleanup_test_data():
    """Nettoyer les données de test (optionnel)"""
    response = input("\n🗑️ Voulez-vous supprimer les données de test ? (y/N) : ")
    
    if response.lower() == 'y':
        print("🧹 Nettoyage des données de test...")
        
        # Supprimer les factures de test
        test_invoices = Invoice.objects.filter(
            notes__contains='test pour validation SendGrid'
        )
        count = test_invoices.count()
        test_invoices.delete()
        
        print(f"✅ {count} facture(s) de test supprimée(s)")
    else:
        print("✅ Données de test conservées")

def main():
    """Fonction principale de test"""
    print("📧 TEST COMPLET D'ENVOI D'EMAIL DE FACTURE")
    print("🏢 Garage MarKev - Validation SendGrid")
    print("=" * 80)
    
    try:
        # Créer les données de test
        client, vehicle, services = create_test_data()
        
        # Créer une facture de test
        invoice = create_test_invoice(client, vehicle, services)
        
        # Tester l'envoi d'email
        email_success = test_email_sending(invoice)
        
        # Tester l'action d'administration
        admin_success = test_admin_action()
        
        print("\n" + "=" * 80)
        print("📊 RÉSULTATS DES TESTS")
        print("=" * 80)
        
        print(f"📧 Envoi d'email de facture : {'✅ SUCCÈS' if email_success else '❌ ÉCHEC'}")
        print(f"🔧 Action d'administration : {'✅ SUCCÈS' if admin_success else '❌ ÉCHEC'}")
        
        if email_success:
            print(f"\n🎉 SENDGRID FONCTIONNE PARFAITEMENT !")
            print(f"📧 Vérifiez votre boîte email : {client.email}")
            print(f"📄 Vous devriez avoir reçu la facture #{invoice.id} en PDF")
            print(f"💰 Montant de la facture : ${invoice.total_amount:.2f}")
            
            print(f"\n🚀 Prochaines étapes :")
            print("   1. Vérifiez la réception de l'email")
            print("   2. Ouvrez le PDF de la facture")
            print("   3. Testez depuis l'interface web")
            print("   4. L'envoi d'emails est maintenant opérationnel !")
        else:
            print(f"\n❌ PROBLÈME DÉTECTÉ")
            print("   Vérifiez les logs pour plus de détails")
        
        # Proposer le nettoyage
        cleanup_test_data()
        
    except Exception as e:
        print(f"\n❌ Erreur générale lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
