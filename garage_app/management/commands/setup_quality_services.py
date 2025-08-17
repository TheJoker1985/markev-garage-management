"""
Commande Django pour créer des services spécifiques par qualité
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from garage_app.models import Service


class Command(BaseCommand):
    help = 'Crée des services spécifiques par qualité pour la tarification dynamique'

    def handle(self, *args, **options):
        # Services de vitres teintées par qualité
        tinting_services = [
            {
                'name': 'Vitre Teintée - Standard',
                'description': 'Film de qualité standard pour vitres teintées',
                'category': 'tinting',
                'base_price': Decimal('200.00')
            },
            {
                'name': 'Vitre Teintée - Céramique',
                'description': 'Film céramique haute performance pour vitres teintées',
                'category': 'tinting',
                'base_price': Decimal('350.00')
            },
            {
                'name': 'Vitre Teintée - Premium',
                'description': 'Film premium haut de gamme pour vitres teintées',
                'category': 'tinting',
                'base_price': Decimal('500.00')
            }
        ]
        
        # Services PPF par qualité
        ppf_services = [
            {
                'name': 'PPF Pare-chocs - Standard',
                'description': 'Protection pare-pierre standard pour pare-chocs',
                'category': 'ppf',
                'base_price': Decimal('400.00')
            },
            {
                'name': 'PPF Pare-chocs - Premium',
                'description': 'Protection pare-pierre premium auto-cicatrisante',
                'category': 'ppf',
                'base_price': Decimal('650.00')
            },
            {
                'name': 'PPF Pare-chocs - Ultra Premium',
                'description': 'Protection pare-pierre ultra premium avec garantie étendue',
                'category': 'ppf',
                'base_price': Decimal('900.00')
            },
            {
                'name': 'PPF Capot Complet - Standard',
                'description': 'Protection pare-pierre standard pour capot complet',
                'category': 'ppf',
                'base_price': Decimal('800.00')
            },
            {
                'name': 'PPF Capot Complet - Premium',
                'description': 'Protection pare-pierre premium pour capot complet',
                'category': 'ppf',
                'base_price': Decimal('1200.00')
            },
            {
                'name': 'PPF Capot Complet - Ultra Premium',
                'description': 'Protection pare-pierre ultra premium pour capot complet',
                'category': 'ppf',
                'base_price': Decimal('1600.00')
            }
        ]
        
        # Services de protection céramique par qualité
        ceramic_services = [
            {
                'name': 'Protection Céramique - Standard',
                'description': 'Revêtement céramique de base 2 ans',
                'category': 'ceramic',
                'base_price': Decimal('600.00')
            },
            {
                'name': 'Protection Céramique - Premium',
                'description': 'Revêtement céramique premium 5 ans',
                'category': 'ceramic',
                'base_price': Decimal('1000.00')
            },
            {
                'name': 'Protection Céramique - Ultra Premium',
                'description': 'Revêtement céramique ultra premium 10 ans',
                'category': 'ceramic',
                'base_price': Decimal('1500.00')
            }
        ]
        
        all_services = tinting_services + ppf_services + ceramic_services
        
        created_count = 0
        updated_count = 0
        
        for service_data in all_services:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'category': service_data['category'],
                    'default_price': service_data['base_price'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Créé: {service.name} - {service.default_price}$')
                )
            else:
                # Mettre à jour le prix si différent
                if service.default_price != service_data['base_price']:
                    service.default_price = service_data['base_price']
                    service.description = service_data['description']
                    service.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Mis à jour: {service.name} - {service.default_price}$')
                    )
                else:
                    self.stdout.write(f'Existe déjà: {service.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nTerminé! {created_count} services créés, {updated_count} mis à jour.'
            )
        )
        
        # Afficher un résumé des services par catégorie
        self.stdout.write('\n=== Résumé des services par catégorie ===')
        categories = ['tinting', 'ppf', 'ceramic']
        
        for category in categories:
            services = Service.objects.filter(category=category, is_active=True).order_by('default_price')
            category_name = dict(Service.CATEGORY_CHOICES).get(category, category)
            self.stdout.write(f'\n{category_name}:')
            
            for service in services:
                self.stdout.write(f'  - {service.name}: {service.default_price}$')
