from django.core.management.base import BaseCommand
from garage_app.models import Discount
from decimal import Decimal


class Command(BaseCommand):
    help = 'Créer des rabais par défaut pour MarKev'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher les rabais qui seraient créés sans les créer réellement',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Rabais prédéfinis pour MarKev
        default_discounts = [
            {
                'name': 'Concessionnaire',
                'description': 'Rabais pour les concessionnaires automobiles',
                'discount_type': 'percentage',
                'value': Decimal('15.00'),
            },
            {
                'name': 'Client fidèle',
                'description': 'Rabais pour les clients réguliers (5+ factures)',
                'discount_type': 'percentage',
                'value': Decimal('10.00'),
            },
            {
                'name': 'Employé',
                'description': 'Rabais pour les employés de MarKev',
                'discount_type': 'percentage',
                'value': Decimal('20.00'),
            },
            {
                'name': 'Famille/Ami',
                'description': 'Rabais pour la famille et les amis',
                'discount_type': 'percentage',
                'value': Decimal('12.00'),
            },
            {
                'name': 'Promotion été',
                'description': 'Rabais promotionnel pour la saison estivale',
                'discount_type': 'percentage',
                'value': Decimal('8.00'),
            },
            {
                'name': 'Rabais volume',
                'description': 'Rabais fixe pour les gros montants',
                'discount_type': 'fixed',
                'value': Decimal('100.00'),
            },
            {
                'name': 'Première visite',
                'description': 'Rabais de bienvenue pour les nouveaux clients',
                'discount_type': 'fixed',
                'value': Decimal('50.00'),
            },
        ]

        if dry_run:
            self.stdout.write(
                self.style.WARNING('Mode dry-run activé - Aucun rabais ne sera créé')
            )
            self.stdout.write('')

        created_count = 0
        updated_count = 0

        for discount_data in default_discounts:
            discount, created = Discount.objects.get_or_create(
                name=discount_data['name'],
                defaults=discount_data
            ) if not dry_run else (None, True)

            if dry_run:
                self.stdout.write(
                    f"Créerait: {discount_data['name']} "
                    f"({discount_data['value']}{'%' if discount_data['discount_type'] == 'percentage' else '$'})"
                )
            elif created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Créé: {discount.name} "
                        f"({discount.value}{'%' if discount.discount_type == 'percentage' else '$'})"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️ Existe déjà: {discount.name}"
                    )
                )

        if not dry_run:
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 Terminé! {created_count} rabais créés, {updated_count} existaient déjà.'
                )
            )
        else:
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(
                    f'Mode dry-run: {len(default_discounts)} rabais seraient créés.'
                )
            )
