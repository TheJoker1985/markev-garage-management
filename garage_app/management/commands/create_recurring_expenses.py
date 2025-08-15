from django.core.management.base import BaseCommand
from django.db import transaction
from garage_app.models import RecurringExpense
from datetime import date


class Command(BaseCommand):
    help = 'Créer les dépenses récurrentes qui sont dues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler la création sans effectuer les modifications'
        )
        parser.add_argument(
            '--force-all',
            action='store_true',
            help='Forcer la création pour toutes les dépenses récurrentes actives'
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=0,
            help='Créer les dépenses dues dans X jours (défaut: 0 = aujourd\'hui seulement)'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.force_all = options['force_all']
        self.days_ahead = options['days_ahead']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODE SIMULATION - Aucune dépense ne sera créée')
            )
        
        try:
            # Obtenir les dépenses récurrentes à traiter
            recurring_expenses = self.get_due_recurring_expenses()
            
            if not recurring_expenses:
                self.stdout.write('ℹ️ Aucune dépense récurrente due trouvée')
                return
            
            # Afficher le résumé
            self.display_summary(recurring_expenses)
            
            if not self.dry_run:
                # Créer les dépenses
                created_count = self.create_expenses(recurring_expenses)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {created_count} dépense(s) créée(s) avec succès!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Simulation terminée. Retirez --dry-run pour créer les dépenses.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la création des dépenses récurrentes: {str(e)}')
            )
            raise

    def get_due_recurring_expenses(self):
        """Obtenir les dépenses récurrentes dues"""
        if self.force_all:
            # Toutes les dépenses récurrentes actives
            return RecurringExpense.objects.filter(is_active=True)
        
        # Dépenses dues aujourd'hui ou dans les X jours
        target_date = date.today()
        if self.days_ahead > 0:
            from datetime import timedelta
            target_date = date.today() + timedelta(days=self.days_ahead)
        
        return RecurringExpense.objects.filter(
            is_active=True,
            next_due_date__lte=target_date
        )

    def display_summary(self, recurring_expenses):
        """Afficher le résumé des dépenses à créer"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📋 RÉSUMÉ DES DÉPENSES RÉCURRENTES À CRÉER')
        self.stdout.write('='*60)
        
        total_amount = 0
        for expense in recurring_expenses:
            self.stdout.write(
                f'💰 {expense.name} - {expense.supplier or "Aucun fournisseur"}'
            )
            self.stdout.write(
                f'   Montant: {expense.total_with_taxes:.2f}$ - '
                f'Échéance: {expense.next_due_date.strftime("%d/%m/%Y")} - '
                f'Fréquence: {expense.get_frequency_display()}'
            )
            total_amount += expense.total_with_taxes
        
        self.stdout.write(f'\n💵 TOTAL: {total_amount:.2f}$')
        self.stdout.write(f'📊 NOMBRE: {recurring_expenses.count()} dépense(s)')
        self.stdout.write('='*60 + '\n')

    @transaction.atomic
    def create_expenses(self, recurring_expenses):
        """Créer les dépenses à partir des dépenses récurrentes"""
        created_count = 0
        
        for recurring_expense in recurring_expenses:
            try:
                # Créer la dépense
                expense = recurring_expense.create_expense()
                
                self.stdout.write(
                    f'✓ Créé: {expense.description} - {expense.total_with_taxes:.2f}$ '
                    f'(Échéance suivante: {recurring_expense.next_due_date.strftime("%d/%m/%Y")})'
                )
                
                created_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Erreur lors de la création de "{recurring_expense.name}": {str(e)}'
                    )
                )
                continue
        
        return created_count

    def get_statistics(self):
        """Obtenir des statistiques sur les dépenses récurrentes"""
        total_active = RecurringExpense.objects.filter(is_active=True).count()
        total_inactive = RecurringExpense.objects.filter(is_active=False).count()
        
        # Dépenses par fréquence
        frequencies = RecurringExpense.objects.filter(is_active=True).values_list('frequency', flat=True)
        frequency_counts = {}
        for freq in frequencies:
            frequency_counts[freq] = frequency_counts.get(freq, 0) + 1
        
        return {
            'total_active': total_active,
            'total_inactive': total_inactive,
            'frequency_counts': frequency_counts
        }

    def display_statistics(self):
        """Afficher les statistiques des dépenses récurrentes"""
        stats = self.get_statistics()
        
        self.stdout.write('\n📊 STATISTIQUES DES DÉPENSES RÉCURRENTES:')
        self.stdout.write(f'   Actives: {stats["total_active"]}')
        self.stdout.write(f'   Inactives: {stats["total_inactive"]}')
        
        if stats['frequency_counts']:
            self.stdout.write('\n📅 RÉPARTITION PAR FRÉQUENCE:')
            for freq, count in stats['frequency_counts'].items():
                freq_display = dict(RecurringExpense.FREQUENCY_CHOICES).get(freq, freq)
                self.stdout.write(f'   {freq_display}: {count}')


# Fonction utilitaire pour être appelée depuis d'autres endroits
def create_due_recurring_expenses():
    """Fonction utilitaire pour créer les dépenses récurrentes dues"""
    from django.core.management import call_command
    call_command('create_recurring_expenses')


# Exemple d'utilisation dans une tâche cron
"""
# Ajouter cette ligne dans votre crontab pour exécuter quotidiennement à 9h00:
# 0 9 * * * cd /path/to/your/project && python manage.py create_recurring_expenses

# Ou pour une vérification avec 3 jours d'avance:
# 0 9 * * * cd /path/to/your/project && python manage.py create_recurring_expenses --days-ahead 3
"""
