"""
Commande Django pour créer les types de véhicules de base
"""
from django.core.management.base import BaseCommand
from garage_app.models import VehicleType


class Command(BaseCommand):
    help = 'Crée les types de véhicules de base avec leurs correspondances NHTSA'

    def handle(self, *args, **options):
        vehicle_types_data = [
            {
                'name': 'VUS',
                'description': 'Véhicule utilitaire sport (SUV)',
                'nhtsa_body_classes': ['SUV', 'Sport Utility Vehicle', 'Crossover']
            },
            {
                'name': 'Berline',
                'description': 'Voiture berline traditionnelle',
                'nhtsa_body_classes': ['Sedan', 'Saloon']
            },
            {
                'name': 'Coupé',
                'description': 'Voiture coupé 2 portes',
                'nhtsa_body_classes': ['Coupe', '2-Door']
            },
            {
                'name': 'Hatchback',
                'description': 'Voiture à hayon',
                'nhtsa_body_classes': ['Hatchback', 'Hatch']
            },
            {
                'name': 'Familiale',
                'description': 'Voiture familiale (wagon)',
                'nhtsa_body_classes': ['Wagon', 'Station Wagon', 'Estate']
            },
            {
                'name': 'Pickup',
                'description': 'Camionnette pickup',
                'nhtsa_body_classes': ['Pickup', 'Truck']
            },
            {
                'name': 'Fourgonnette',
                'description': 'Fourgonnette ou van',
                'nhtsa_body_classes': ['Van', 'Minivan', 'Cargo Van']
            },
            {
                'name': 'Cabriolet',
                'description': 'Voiture décapotable',
                'nhtsa_body_classes': ['Convertible', 'Cabriolet', 'Roadster']
            },
            {
                'name': 'Camion',
                'description': 'Camion commercial',
                'nhtsa_body_classes': ['Truck', 'Commercial Vehicle']
            },
            {
                'name': 'Moto',
                'description': 'Motocyclette',
                'nhtsa_body_classes': ['Motorcycle', 'Motorbike', 'Scooter']
            }
        ]

        created_count = 0
        updated_count = 0

        for data in vehicle_types_data:
            vehicle_type, created = VehicleType.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'nhtsa_body_classes': data['nhtsa_body_classes'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Créé: {vehicle_type.name}')
                )
            else:
                # Mettre à jour les correspondances NHTSA si nécessaire
                if vehicle_type.nhtsa_body_classes != data['nhtsa_body_classes']:
                    vehicle_type.nhtsa_body_classes = data['nhtsa_body_classes']
                    vehicle_type.description = data['description']
                    vehicle_type.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Mis à jour: {vehicle_type.name}')
                    )
                else:
                    self.stdout.write(f'Existe déjà: {vehicle_type.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTerminé! {created_count} types créés, {updated_count} mis à jour.'
            )
        )
