from django.core.management.base import BaseCommand
from django.db import transaction
from garage_app.models import CompanyProfile, Client, Vehicle, Service, Invoice, InvoiceItem, Expense
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Supprimer toutes les données de test créées par create_sample_data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la suppression sans confirmation'
        )
        parser.add_argument(
            '--keep-admin',
            action='store_true',
            help='Conserver le compte administrateur'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher ce qui serait supprimé sans effectuer la suppression'
        )

    def handle(self, *args, **options):
        self.force = options['force']
        self.keep_admin = options['keep_admin']
        self.dry_run = options['dry_run']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODE SIMULATION - Aucune donnée ne sera supprimée')
            )
        
        try:
            # Analyser les données à supprimer
            self.analyze_data()
            
            # Demander confirmation si pas forcé et pas en mode simulation
            if not self.force and not self.dry_run:
                if not self.confirm_deletion():
                    self.stdout.write('❌ Suppression annulée par l\'utilisateur')
                    return
            
            if not self.dry_run:
                # Effectuer la suppression
                self.cleanup_data()
                self.stdout.write(
                    self.style.SUCCESS('✅ Nettoyage des données de test terminé avec succès!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Simulation terminée. Utilisez --force pour effectuer la suppression.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors du nettoyage: {str(e)}')
            )
            raise

    def analyze_data(self):
        """Analyser les données qui seront supprimées"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📊 ANALYSE DES DONNÉES À SUPPRIMER')
        self.stdout.write('='*60)
        
        # Compter les différents types de données
        company_profiles = CompanyProfile.objects.all()
        clients = Client.objects.all()
        vehicles = Vehicle.objects.all()
        services = Service.objects.all()
        invoices = Invoice.objects.all()
        invoice_items = InvoiceItem.objects.all()
        expenses = Expense.objects.all()
        users = User.objects.all()
        
        self.stdout.write(f'👤 Utilisateurs: {users.count()}')
        if not self.keep_admin:
            self.stdout.write('   ⚠️ TOUS les utilisateurs seront supprimés (y compris admin)')
        else:
            admin_users = users.filter(is_superuser=True)
            self.stdout.write(f'   ✓ {admin_users.count()} administrateur(s) seront conservés')
            self.stdout.write(f'   🗑️ {users.count() - admin_users.count()} utilisateur(s) non-admin seront supprimés')
        
        self.stdout.write(f'🏢 Profils d\'entreprise: {company_profiles.count()}')
        self.stdout.write(f'👥 Clients: {clients.count()}')
        self.stdout.write(f'🚗 Véhicules: {vehicles.count()}')
        self.stdout.write(f'🔧 Services: {services.count()}')
        self.stdout.write(f'📄 Factures: {invoices.count()}')
        self.stdout.write(f'📋 Éléments de facture: {invoice_items.count()}')
        self.stdout.write(f'💰 Dépenses: {expenses.count()}')
        
        # Afficher quelques exemples de données
        if company_profiles.exists():
            self.stdout.write('\n📋 Exemples de profils d\'entreprise:')
            for profile in company_profiles[:3]:
                self.stdout.write(f'   - {profile.name}')
        
        if clients.exists():
            self.stdout.write('\n👥 Exemples de clients:')
            for client in clients[:5]:
                self.stdout.write(f'   - {client.full_name}')
        
        if services.exists():
            self.stdout.write('\n🔧 Exemples de services:')
            for service in services[:5]:
                self.stdout.write(f'   - {service.name} ({service.default_price}$)')
        
        self.stdout.write('='*60 + '\n')

    def confirm_deletion(self):
        """Demander confirmation à l'utilisateur"""
        self.stdout.write(
            self.style.WARNING(
                '⚠️ ATTENTION: Cette opération va supprimer TOUTES les données de test!'
            )
        )
        self.stdout.write(
            'Cette action est IRRÉVERSIBLE. Assurez-vous d\'avoir une sauvegarde si nécessaire.'
        )
        
        response = input('\nÊtes-vous sûr de vouloir continuer? (tapez "SUPPRIMER" pour confirmer): ')
        return response == 'SUPPRIMER'

    @transaction.atomic
    def cleanup_data(self):
        """Effectuer le nettoyage des données"""
        self.stdout.write('🧹 Début du nettoyage des données...')
        
        # Supprimer dans l'ordre pour respecter les contraintes de clés étrangères
        
        # 1. Supprimer les éléments de facture
        invoice_items_count = InvoiceItem.objects.count()
        if invoice_items_count > 0:
            InvoiceItem.objects.all().delete()
            self.stdout.write(f'✓ {invoice_items_count} élément(s) de facture supprimé(s)')
        
        # 2. Supprimer les factures
        invoices_count = Invoice.objects.count()
        if invoices_count > 0:
            Invoice.objects.all().delete()
            self.stdout.write(f'✓ {invoices_count} facture(s) supprimée(s)')
        
        # 3. Supprimer les dépenses
        expenses_count = Expense.objects.count()
        if expenses_count > 0:
            Expense.objects.all().delete()
            self.stdout.write(f'✓ {expenses_count} dépense(s) supprimée(s)')
        
        # 4. Supprimer les véhicules
        vehicles_count = Vehicle.objects.count()
        if vehicles_count > 0:
            Vehicle.objects.all().delete()
            self.stdout.write(f'✓ {vehicles_count} véhicule(s) supprimé(s)')
        
        # 5. Supprimer les clients
        clients_count = Client.objects.count()
        if clients_count > 0:
            Client.objects.all().delete()
            self.stdout.write(f'✓ {clients_count} client(s) supprimé(s)')
        
        # 6. Supprimer les services
        services_count = Service.objects.count()
        if services_count > 0:
            Service.objects.all().delete()
            self.stdout.write(f'✓ {services_count} service(s) supprimé(s)')
        
        # 7. Supprimer les profils d'entreprise
        company_profiles_count = CompanyProfile.objects.count()
        if company_profiles_count > 0:
            CompanyProfile.objects.all().delete()
            self.stdout.write(f'✓ {company_profiles_count} profil(s) d\'entreprise supprimé(s)')
        
        # 8. Supprimer les utilisateurs (sauf admin si demandé)
        if self.keep_admin:
            non_admin_users = User.objects.filter(is_superuser=False)
            non_admin_count = non_admin_users.count()
            if non_admin_count > 0:
                non_admin_users.delete()
                self.stdout.write(f'✓ {non_admin_count} utilisateur(s) non-admin supprimé(s)')
            
            admin_count = User.objects.filter(is_superuser=True).count()
            self.stdout.write(f'ℹ️ {admin_count} administrateur(s) conservé(s)')
        else:
            users_count = User.objects.count()
            if users_count > 0:
                User.objects.all().delete()
                self.stdout.write(f'✓ {users_count} utilisateur(s) supprimé(s)')
        
        self.stdout.write('\n🎯 Vérification finale...')
        
        # Vérifier que tout a été supprimé
        remaining_data = {
            'Profils d\'entreprise': CompanyProfile.objects.count(),
            'Clients': Client.objects.count(),
            'Véhicules': Vehicle.objects.count(),
            'Services': Service.objects.count(),
            'Factures': Invoice.objects.count(),
            'Éléments de facture': InvoiceItem.objects.count(),
            'Dépenses': Expense.objects.count(),
        }
        
        if self.keep_admin:
            remaining_data['Utilisateurs non-admin'] = User.objects.filter(is_superuser=False).count()
            remaining_data['Administrateurs'] = User.objects.filter(is_superuser=True).count()
        else:
            remaining_data['Utilisateurs'] = User.objects.count()
        
        total_remaining = sum(count for key, count in remaining_data.items() 
                            if not (self.keep_admin and key == 'Administrateurs'))
        
        if total_remaining == 0:
            self.stdout.write('✅ Toutes les données de test ont été supprimées avec succès!')
        else:
            self.stdout.write('⚠️ Données restantes:')
            for data_type, count in remaining_data.items():
                if count > 0:
                    if self.keep_admin and data_type == 'Administrateurs':
                        self.stdout.write(f'   ✓ {data_type}: {count} (conservés)')
                    else:
                        self.stdout.write(f'   ⚠️ {data_type}: {count}')

    def cleanup_media_files(self):
        """Nettoyer les fichiers média orphelins (optionnel)"""
        # Cette méthode pourrait être étendue pour supprimer les fichiers média
        # qui ne sont plus référencés par aucun objet
        pass
