from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User
from garage_app.models import CompanyProfile, Invoice, Expense, FiscalYearArchive
from datetime import date
from decimal import Decimal


class Command(BaseCommand):
    help = 'Archiver les données d\'une année fiscale terminée'

    def add_arguments(self, parser):
        parser.add_argument(
            'fiscal_year',
            type=int,
            help='Année fiscale à archiver (année de fin, ex: 2024 pour 2023-2024)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer l\'archivage sans confirmation'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler l\'archivage sans effectuer les modifications'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Nom d\'utilisateur qui effectue l\'archivage'
        )

    def handle(self, *args, **options):
        self.fiscal_year = options['fiscal_year']
        self.force = options['force']
        self.dry_run = options['dry_run']
        self.username = options.get('user')
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODE SIMULATION - Aucune modification ne sera effectuée')
            )
        
        try:
            # Vérifier les prérequis
            self.validate_prerequisites()
            
            # Analyser les données à archiver
            data_summary = self.analyze_data()
            
            # Afficher le résumé
            self.display_summary(data_summary)
            
            # Demander confirmation si pas forcé et pas en mode simulation
            if not self.force and not self.dry_run:
                if not self.confirm_archiving():
                    self.stdout.write('❌ Archivage annulé par l\'utilisateur')
                    return
            
            if not self.dry_run:
                # Effectuer l'archivage
                self.perform_archiving(data_summary)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Archivage de l\'année fiscale {self.fiscal_year} terminé avec succès!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Simulation terminée. Utilisez --force pour effectuer l\'archivage.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de l\'archivage: {str(e)}')
            )
            raise

    def validate_prerequisites(self):
        """Valider les prérequis pour l'archivage"""
        # Vérifier qu'il y a un profil d'entreprise
        company_profile = CompanyProfile.objects.first()
        if not company_profile:
            raise CommandError("Aucun profil d'entreprise configuré")
        
        self.company_profile = company_profile
        
        # Vérifier que l'année fiscale est terminée
        current_fiscal_year_start, current_fiscal_year_end = company_profile.get_current_fiscal_year_period()
        if self.fiscal_year >= current_fiscal_year_end.year:
            raise CommandError(
                f"L'année fiscale {self.fiscal_year} n'est pas encore terminée. "
                f"Année fiscale actuelle: {current_fiscal_year_start.year}-{current_fiscal_year_end.year}"
            )
        
        # Vérifier que l'archive n'existe pas déjà
        if FiscalYearArchive.objects.filter(fiscal_year=self.fiscal_year).exists():
            raise CommandError(f"L'année fiscale {self.fiscal_year} est déjà archivée")
        
        # Vérifier l'utilisateur si spécifié
        self.user = None
        if self.username:
            try:
                self.user = User.objects.get(username=self.username)
            except User.DoesNotExist:
                raise CommandError(f"Utilisateur '{self.username}' introuvable")

    def analyze_data(self):
        """Analyser les données à archiver"""
        fiscal_start, fiscal_end = self.company_profile.get_fiscal_year_period(self.fiscal_year)
        
        # Trouver les factures de cette période
        invoices = Invoice.objects.filter(
            invoice_date__gte=fiscal_start,
            invoice_date__lte=fiscal_end,
            archived_fiscal_year__isnull=True
        )
        
        # Trouver les dépenses de cette période
        expenses = Expense.objects.filter(
            expense_date__gte=fiscal_start,
            expense_date__lte=fiscal_end,
            archived_fiscal_year__isnull=True
        )
        
        # Calculer les statistiques
        total_revenue = sum(invoice.total_amount for invoice in invoices)
        total_expenses_amount = sum(expense.amount for expense in expenses)
        
        total_gst_collected = sum(invoice.gst_amount for invoice in invoices)
        total_qst_collected = sum(invoice.qst_amount for invoice in invoices)
        total_gst_paid = sum(expense.gst_amount for expense in expenses)
        total_qst_paid = sum(expense.qst_amount for expense in expenses)
        
        return {
            'fiscal_start': fiscal_start,
            'fiscal_end': fiscal_end,
            'invoices': invoices,
            'expenses': expenses,
            'total_invoices': invoices.count(),
            'total_revenue': total_revenue,
            'total_expenses': total_expenses_amount,
            'total_gst_collected': total_gst_collected,
            'total_qst_collected': total_qst_collected,
            'total_gst_paid': total_gst_paid,
            'total_qst_paid': total_qst_paid,
            'net_profit': total_revenue - total_expenses_amount,
            'net_gst': total_gst_collected - total_gst_paid,
            'net_qst': total_qst_collected - total_qst_paid,
        }

    def display_summary(self, data):
        """Afficher le résumé des données à archiver"""
        self.stdout.write('\n' + '='*70)
        self.stdout.write(f'📊 RÉSUMÉ DE L\'ARCHIVAGE - ANNÉE FISCALE {self.fiscal_year}')
        self.stdout.write('='*70)
        
        self.stdout.write(f'📅 Période: {data["fiscal_start"].strftime("%d/%m/%Y")} - {data["fiscal_end"].strftime("%d/%m/%Y")}')
        self.stdout.write(f'📄 Factures: {data["total_invoices"]}')
        self.stdout.write(f'💰 Dépenses: {data["expenses"].count()}')
        
        self.stdout.write('\n💵 RÉSUMÉ FINANCIER:')
        self.stdout.write(f'   Chiffre d\'affaires: {data["total_revenue"]:,.2f} $')
        self.stdout.write(f'   Total dépenses: {data["total_expenses"]:,.2f} $')
        self.stdout.write(f'   Bénéfice net: {data["net_profit"]:,.2f} $')
        
        self.stdout.write('\n🏛️ RÉSUMÉ DES TAXES:')
        self.stdout.write(f'   TPS perçue: {data["total_gst_collected"]:,.2f} $')
        self.stdout.write(f'   TVQ perçue: {data["total_qst_collected"]:,.2f} $')
        self.stdout.write(f'   TPS payée: {data["total_gst_paid"]:,.2f} $')
        self.stdout.write(f'   TVQ payée: {data["total_qst_paid"]:,.2f} $')
        self.stdout.write(f'   TPS nette: {data["net_gst"]:,.2f} $')
        self.stdout.write(f'   TVQ nette: {data["net_qst"]:,.2f} $')
        
        self.stdout.write('='*70 + '\n')

    def confirm_archiving(self):
        """Demander confirmation à l'utilisateur"""
        self.stdout.write(
            self.style.WARNING(
                f'⚠️ ATTENTION: Vous allez archiver l\'année fiscale {self.fiscal_year}'
            )
        )
        self.stdout.write(
            'Les données seront marquées comme archivées et ne pourront plus être modifiées facilement.'
        )
        
        response = input(f'\nConfirmer l\'archivage de l\'année fiscale {self.fiscal_year}? (oui/non): ')
        return response.lower() in ['oui', 'o', 'yes', 'y']

    @transaction.atomic
    def perform_archiving(self, data):
        """Effectuer l'archivage des données"""
        self.stdout.write(f'📦 Archivage de l\'année fiscale {self.fiscal_year}...')
        
        # Créer l'enregistrement d'archive
        archive = FiscalYearArchive.objects.create(
            fiscal_year=self.fiscal_year,
            total_invoices=data['total_invoices'],
            total_revenue=data['total_revenue'],
            total_expenses=data['total_expenses'],
            total_gst_collected=data['total_gst_collected'],
            total_qst_collected=data['total_qst_collected'],
            total_gst_paid=data['total_gst_paid'],
            total_qst_paid=data['total_qst_paid'],
            archived_by=self.user,
            notes=f'Archive créée automatiquement le {date.today().strftime("%d/%m/%Y")}'
        )
        
        # Marquer les factures comme archivées
        invoices_updated = data['invoices'].update(archived_fiscal_year=self.fiscal_year)
        self.stdout.write(f'✓ {invoices_updated} facture(s) marquée(s) comme archivées')
        
        # Marquer les dépenses comme archivées
        expenses_updated = data['expenses'].update(archived_fiscal_year=self.fiscal_year)
        self.stdout.write(f'✓ {expenses_updated} dépense(s) marquée(s) comme archivées')
        
        self.stdout.write(f'✓ Archive créée: {archive}')
        
        # Afficher les statistiques finales
        self.stdout.write('\n📈 STATISTIQUES DE L\'ARCHIVE:')
        self.stdout.write(f'   Bénéfice net: {archive.calculate_net_profit():,.2f} $')
        
        tax_summary = archive.get_tax_summary()
        self.stdout.write(f'   Taxes nettes à payer/recevoir:')
        self.stdout.write(f'     TPS: {tax_summary["gst_net"]:,.2f} $')
        self.stdout.write(f'     TVQ: {tax_summary["qst_net"]:,.2f} $')
