"""
Commande pour initialiser les données de base du calculateur de lettrage
"""
from django.core.management.base import BaseCommand
from garage_app.models import Material, LaborRate, OverheadConfiguration, VehicleType
from decimal import Decimal


class Command(BaseCommand):
    help = 'Initialise les données de base pour le calculateur de lettrage'

    def handle(self, *args, **options):
        if options.get('reset'):
            self.stdout.write(self.style.WARNING('🗑️  Suppression des données existantes...'))
            Material.objects.all().delete()
            LaborRate.objects.all().delete()
            OverheadConfiguration.objects.all().delete()
            self.stdout.write('✅ Données supprimées')

        self.stdout.write(self.style.SUCCESS('🚀 Initialisation du calculateur de lettrage...'))

        # Créer les matériaux de base
        self.create_materials()

        # Créer les taux horaires
        self.create_labor_rates()

        # Créer la configuration des frais généraux
        self.create_overhead_configuration()

        # Mettre à jour les multiplicateurs de complexité des véhicules
        self.update_vehicle_complexity()

        self.stdout.write(self.style.SUCCESS('✅ Calculateur de lettrage initialisé avec succès!'))

    def create_materials(self):
        """Créer les matériaux de base"""
        self.stdout.write('📦 Création des matériaux...')
        
        materials_data = [
            # Vinyles
            {
                'name': 'Vinyle Coulé 3M IJ180Cv3',
                'type': 'vinyle',
                'cost_per_sqm': Decimal('25.00'),
                'supplier': '3M',
                'notes': 'Vinyle coulé premium pour applications complexes'
            },
            {
                'name': 'Vinyle Calendré 3M IJ35C',
                'type': 'vinyle',
                'cost_per_sqm': Decimal('12.00'),
                'supplier': '3M',
                'notes': 'Vinyle calendré pour applications simples'
            },
            {
                'name': 'Vinyle Avery Dennison MPI 1105',
                'type': 'vinyle',
                'cost_per_sqm': Decimal('22.00'),
                'supplier': 'Avery Dennison',
                'notes': 'Vinyle coulé haute performance'
            },
            
            # Laminations
            {
                'name': 'Lamination Lustrée 3M 8518',
                'type': 'lamination',
                'cost_per_sqm': Decimal('8.00'),
                'supplier': '3M',
                'notes': 'Protection lustrée standard'
            },
            {
                'name': 'Lamination Mate 3M 8519',
                'type': 'lamination',
                'cost_per_sqm': Decimal('9.00'),
                'supplier': '3M',
                'notes': 'Protection mate anti-reflets'
            },
            {
                'name': 'Lamination Texturée Avery DOL 1460',
                'type': 'lamination',
                'cost_per_sqm': Decimal('12.00'),
                'supplier': 'Avery Dennison',
                'notes': 'Lamination avec texture spéciale'
            },
            
            # Encres
            {
                'name': 'Encre Ecosol MAX Roland',
                'type': 'encre',
                'cost_per_sqm': Decimal('3.50'),
                'supplier': 'Roland',
                'notes': 'Encre écosolvant standard'
            },
            {
                'name': 'Encre Latex HP 831',
                'type': 'encre',
                'cost_per_sqm': Decimal('4.20'),
                'supplier': 'HP',
                'notes': 'Encre latex haute qualité'
            },
        ]
        
        created_count = 0
        for material_data in materials_data:
            material, created = Material.objects.get_or_create(
                name=material_data['name'],
                defaults=material_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ {material.name}')
            else:
                self.stdout.write(f'  ⏭️  {material.name} (existe déjà)')
        
        self.stdout.write(f'📦 {created_count} nouveaux matériaux créés')

    def create_labor_rates(self):
        """Créer les taux horaires"""
        self.stdout.write('⏰ Création des taux horaires...')
        
        labor_rates_data = [
            {
                'task_type': 'conception',
                'hourly_rate': Decimal('75.00'),
                'description': 'Création graphique, mise en page, préparation des fichiers'
            },
            {
                'task_type': 'installation',
                'hourly_rate': Decimal('85.00'),
                'description': 'Pose du lettrage sur le véhicule'
            },
            {
                'task_type': 'echenillage',
                'hourly_rate': Decimal('65.00'),
                'description': 'Découpe et échenillage des vinyles'
            },
            {
                'task_type': 'preparation',
                'hourly_rate': Decimal('70.00'),
                'description': 'Nettoyage et préparation de la surface'
            },
            {
                'task_type': 'finition',
                'hourly_rate': Decimal('80.00'),
                'description': 'Finitions, retouches et contrôle qualité'
            },
        ]
        
        created_count = 0
        for rate_data in labor_rates_data:
            rate, created = LaborRate.objects.get_or_create(
                task_type=rate_data['task_type'],
                defaults=rate_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ {rate.get_task_type_display()} - {rate.hourly_rate}$/h')
            else:
                self.stdout.write(f'  ⏭️  {rate.get_task_type_display()} (existe déjà)')
        
        self.stdout.write(f'⏰ {created_count} nouveaux taux horaires créés')

    def create_overhead_configuration(self):
        """Créer la configuration des frais généraux"""
        self.stdout.write('💰 Création de la configuration des frais généraux...')
        
        config, created = OverheadConfiguration.objects.get_or_create(
            name='Configuration Standard',
            defaults={
                'hourly_overhead_cost': Decimal('15.00'),
                'fixed_overhead_cost': Decimal('25.00'),
                'percentage_overhead': Decimal('5.00'),
                'is_default': True,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✅ Configuration Standard créée')
            self.stdout.write(f'    - Frais horaires: {config.hourly_overhead_cost}$/h')
            self.stdout.write(f'    - Frais fixes: {config.fixed_overhead_cost}$')
            self.stdout.write(f'    - Pourcentage: {config.percentage_overhead}%')
        else:
            self.stdout.write('  ⏭️  Configuration Standard (existe déjà)')

    def update_vehicle_complexity(self):
        """Mettre à jour les multiplicateurs de complexité des véhicules"""
        self.stdout.write('🚗 Mise à jour des multiplicateurs de complexité...')
        
        # Multiplicateurs basés sur la complexité d'installation
        complexity_mapping = {
            'Berline': Decimal('1.0'),      # Base de référence
            'Coupé': Decimal('1.1'),        # Lignes plus complexes
            'Cabriolet': Decimal('1.2'),    # Formes particulières
            'Hatchback': Decimal('1.0'),    # Similaire à berline
            'Familiale': Decimal('1.1'),    # Plus de surface
            'VUS': Decimal('1.3'),          # Plus haut, angles différents
            'Pickup': Decimal('1.2'),       # Caisse ouverte, défis particuliers
            'Fourgonnette': Decimal('1.5'), # Grande surface, hauteur
            'Camion': Decimal('1.6'),       # Très complexe, hauteur importante
            'Moto': Decimal('0.8'),         # Plus petit, mais précis
        }
        
        updated_count = 0
        for vehicle_type in VehicleType.objects.all():
            if vehicle_type.name in complexity_mapping:
                new_multiplier = complexity_mapping[vehicle_type.name]
                if vehicle_type.complexity_multiplier != new_multiplier:
                    vehicle_type.complexity_multiplier = new_multiplier
                    vehicle_type.save()
                    updated_count += 1
                    self.stdout.write(f'  ✅ {vehicle_type.name}: {new_multiplier}')
                else:
                    self.stdout.write(f'  ⏭️  {vehicle_type.name}: {vehicle_type.complexity_multiplier} (inchangé)')
            else:
                self.stdout.write(f'  ⚠️  {vehicle_type.name}: multiplicateur non défini (reste à {vehicle_type.complexity_multiplier})')
        
        self.stdout.write(f'🚗 {updated_count} multiplicateurs mis à jour')

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Supprimer toutes les données existantes avant de recréer',
        )
