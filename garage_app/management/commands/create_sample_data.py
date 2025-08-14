from django.core.management.base import BaseCommand
from garage_app.models import CompanyProfile, Client, Vehicle, Service, Invoice, InvoiceItem, Expense
from datetime import date, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Créer des données d\'exemple pour tester l\'application MarKev'

    def handle(self, *args, **options):
        self.stdout.write('Création des données d\'exemple...')
        
        # Créer le profil d'entreprise
        company_profile, created = CompanyProfile.objects.get_or_create(
            defaults={
                'name': 'Garage MarKev',
                'address': '123 Rue Principale\nMontréal, QC H1A 1A1',
                'phone': '(514) 123-4567',
                'email': 'info@markev.com',
                'website': 'https://www.markev.com',
                'gst_number': '123456789RT0001',
                'qst_number': '1234567890TQ0001',
                'is_tax_registered': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Profil d\'entreprise créé'))
        
        # Créer des services
        services_data = [
            ('Vitres teintées - Avant', 'Installation de films teintés sur vitres avant', Decimal('150.00'), 'tinting'),
            ('Vitres teintées - Arrière', 'Installation de films teintés sur vitres arrière', Decimal('200.00'), 'tinting'),
            ('PPF - Pare-chocs avant', 'Protection pare-pierre sur pare-chocs avant', Decimal('300.00'), 'ppf'),
            ('PPF - Capot complet', 'Protection pare-pierre sur capot complet', Decimal('500.00'), 'ppf'),
            ('Wrapping - Toit', 'Wrapping du toit du véhicule', Decimal('400.00'), 'wrapping'),
            ('Protection hydrophobe', 'Traitement hydrophobe pour vitres', Decimal('100.00'), 'hydrophobic'),
            ('Polissage complet', 'Polissage et compound du véhicule', Decimal('250.00'), 'detailing'),
        ]
        
        for name, description, price, category in services_data:
            service, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'default_price': price,
                    'category': category,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'✓ Service créé: {name}')
        
        # Créer des clients
        clients_data = [
            ('Jean', 'Tremblay', '(514) 555-0101', 'jean.tremblay@email.com', '456 Rue Saint-Denis\nMontréal, QC H2X 3K8'),
            ('Marie', 'Dubois', '(450) 555-0102', 'marie.dubois@email.com', '789 Boulevard René-Lévesque\nLaval, QC H7M 2Y5'),
            ('Pierre', 'Gagnon', '(514) 555-0103', 'pierre.gagnon@email.com', '321 Avenue du Parc\nMontréal, QC H2W 2N4'),
            ('Sophie', 'Leblanc', '(450) 555-0104', 'sophie.leblanc@email.com', '654 Rue Sherbrooke\nLongueuil, QC J4K 2M8'),
        ]
        
        for first_name, last_name, phone, email, address in clients_data:
            client, created = Client.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={
                    'phone': phone,
                    'email': email,
                    'address': address,
                }
            )
            if created:
                self.stdout.write(f'✓ Client créé: {first_name} {last_name}')
        
        # Créer des véhicules
        vehicles_data = [
            ('Jean Tremblay', 'Toyota', 'Camry', 2020, 'Noir', 'ABC 123'),
            ('Marie Dubois', 'Honda', 'Civic', 2019, 'Blanc', 'DEF 456'),
            ('Pierre Gagnon', 'BMW', 'X3', 2021, 'Gris', 'GHI 789'),
            ('Sophie Leblanc', 'Audi', 'A4', 2018, 'Bleu', 'JKL 012'),
        ]
        
        for client_name, make, model, year, color, license_plate in vehicles_data:
            first_name, last_name = client_name.split(' ', 1)
            try:
                client = Client.objects.get(first_name=first_name, last_name=last_name)
                vehicle, created = Vehicle.objects.get_or_create(
                    client=client,
                    make=make,
                    model=model,
                    year=year,
                    defaults={
                        'color': color,
                        'license_plate': license_plate,
                    }
                )
                if created:
                    self.stdout.write(f'✓ Véhicule créé: {year} {make} {model}')
            except Client.DoesNotExist:
                continue
        
        # Créer quelques factures d'exemple
        clients = Client.objects.all()[:2]  # Prendre les 2 premiers clients
        services = Service.objects.all()[:3]  # Prendre les 3 premiers services
        
        for i, client in enumerate(clients):
            vehicle = client.vehicles.first()
            
            # Créer une facture
            invoice = Invoice.objects.create(
                client=client,
                vehicle=vehicle,
                invoice_date=date.today() - timedelta(days=i*10),
                due_date=date.today() + timedelta(days=30-i*10),
                status='sent' if i == 0 else 'paid',
                notes=f'Facture d\'exemple pour {client.full_name}'
            )
            
            # Ajouter des éléments à la facture
            for j, service in enumerate(services[:2]):  # 2 services par facture
                InvoiceItem.objects.create(
                    invoice=invoice,
                    service=service,
                    quantity=Decimal('1.00'),
                    unit_price=service.default_price,
                    description=f'Service {j+1} pour {vehicle}'
                )
            
            # Calculer les totaux
            invoice.calculate_totals()
            
            self.stdout.write(f'✓ Facture créée: {invoice.invoice_number}')

        # Créer quelques dépenses d'exemple
        expenses_data = [
            ('Achat de films teintés', Decimal('450.00'), 'materials', Decimal('22.50'), Decimal('44.89')),
            ('Loyer du garage - Janvier', Decimal('1200.00'), 'rent', Decimal('60.00'), Decimal('119.70')),
            ('Assurance responsabilité', Decimal('300.00'), 'insurance', Decimal('15.00'), Decimal('29.93')),
            ('Carburant véhicule de service', Decimal('80.00'), 'fuel', Decimal('4.00'), Decimal('7.98')),
            ('Outils de polissage', Decimal('250.00'), 'tools', Decimal('12.50'), Decimal('24.94')),
        ]

        for description, amount, category, gst, qst in expenses_data:
            expense, created = Expense.objects.get_or_create(
                description=description,
                defaults={
                    'amount': amount,
                    'expense_date': date.today() - timedelta(days=15),
                    'category': category,
                    'gst_amount': gst,
                    'qst_amount': qst,
                    'notes': f'Dépense d\'exemple pour {description.lower()}'
                }
            )
            if created:
                self.stdout.write(f'✓ Dépense créée: {description}')

        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Données d\'exemple créées avec succès!\n'
                'Vous pouvez maintenant tester l\'application avec:\n'
                '- Profil d\'entreprise configuré\n'
                '- 7 services disponibles\n'
                '- 4 clients avec leurs véhicules\n'
                '- 2 factures d\'exemple\n'
                '- 5 dépenses d\'exemple\n'
            )
        )
