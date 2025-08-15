from django.core.management.base import BaseCommand
from garage_app.models import Service
from decimal import Decimal


class Command(BaseCommand):
    help = 'Importer la liste officielle des services MarKev'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Remplacer tous les services existants'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher les services qui seraient importés sans les créer'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Importation des services MarKev...')
        
        # Liste officielle des services MarKev
        services_data = [
            # FORFAITS SIGNATURE MARKEV
            {
                'name': 'Forfait "Protection Essentielle"',
                'description': 'Combine nos services les plus populaires pour une protection de base. Inclus : Pellicule Pare-Pierre "Partiel Avant" + Vitres Teintées qualité Carbone (complet).',
                'default_price': Decimal('1250.00'),
                'category': 'package',
            },
            {
                'name': 'Forfait "Ultime Véhicule Neuf"',
                'description': 'La protection ultime pour préserver l\'état neuf de votre véhicule. Inclus : Pellicule Pare-Pierre "Complet Avant" + Vitres Teintées qualité Céramique (complet) + Protection hydrophobe pour toutes les vitres.',
                'default_price': Decimal('2600.00'),
                'category': 'package',
            },
            
            # VITRES TEINTÉES (FILM SUNTEK) - Qualité Carbone
            {
                'name': 'Vitres Teintées Carbone - Arrière seulement (3 fenêtres)',
                'description': 'Protection UV, réduction de la chaleur et de l\'éblouissement. Qualité Carbone - Look classique, bonne durabilité.',
                'default_price': Decimal('250.00'),
                'category': 'tinting',
            },
            {
                'name': 'Vitres Teintées Carbone - Fenêtres avant seulement (2)',
                'description': 'Protection UV, réduction de la chaleur et de l\'éblouissement. Qualité Carbone - Look classique, bonne durabilité.',
                'default_price': Decimal('150.00'),
                'category': 'tinting',
            },
            {
                'name': 'Vitres Teintées Carbone - Coupé (2 portes)',
                'description': 'Protection UV, réduction de la chaleur et de l\'éblouissement. Qualité Carbone - Look classique, bonne durabilité.',
                'default_price': Decimal('320.00'),
                'category': 'tinting',
            },
            {
                'name': 'Vitres Teintées Carbone - Berline (4 portes)',
                'description': 'Protection UV, réduction de la chaleur et de l\'éblouissement. Qualité Carbone - Look classique, bonne durabilité.',
                'default_price': Decimal('380.00'),
                'category': 'tinting',
            },
            {
                'name': 'Vitres Teintées Carbone - VUS / Camion',
                'description': 'Protection UV, réduction de la chaleur et de l\'éblouissement. Qualité Carbone - Look classique, bonne durabilité.',
                'default_price': Decimal('420.00'),
                'category': 'tinting',
            },
            
            # VITRES TEINTÉES - Qualité Céramique
            {
                'name': 'Vitres Teintées Céramique - Arrière seulement (3 fenêtres)',
                'description': 'Protection UV, réduction de la chaleur et de l\'éblouissement. Qualité Céramique - Rejet de chaleur supérieur, clarté optimale.',
                'default_price': Decimal('350.00'),
                'category': 'tinting',
            },
            {
                'name': 'Vitres Teintées Céramique - Fenêtres avant seulement (2)',
                'description': 'Protection UV, réduction de la chaleur et de l\'éblouissement. Qualité Céramique - Rejet de chaleur supérieur, clarté optimale.',
                'default_price': Decimal('200.00'),
                'category': 'tinting',
            },
            {
                'name': 'Vitres Teintées Céramique - Coupé (2 portes)',
                'description': 'Protection UV, réduction de la chaleur et de l\'éblouissement. Qualité Céramique - Rejet de chaleur supérieur, clarté optimale.',
                'default_price': Decimal('450.00'),
                'category': 'tinting',
            },
            {
                'name': 'Vitres Teintées Céramique - Berline (4 portes)',
                'description': 'Protection UV, réduction de la chaleur et de l\'éblouissement. Qualité Céramique - Rejet de chaleur supérieur, clarté optimale.',
                'default_price': Decimal('520.00'),
                'category': 'tinting',
            },
            {
                'name': 'Vitres Teintées Céramique - VUS / Camion',
                'description': 'Protection UV, réduction de la chaleur et de l\'éblouissement. Qualité Céramique - Rejet de chaleur supérieur, clarté optimale.',
                'default_price': Decimal('580.00'),
                'category': 'tinting',
            },
            
            # Options Vitres Teintées
            {
                'name': 'Toit ouvrant - Teinte',
                'description': 'Application de film teinté sur toit ouvrant.',
                'default_price': Decimal('80.00'),
                'category': 'tinting',
            },
            {
                'name': 'Bande pare-soleil (pare-brise)',
                'description': 'Bande teintée en haut du pare-brise pour réduire l\'éblouissement.',
                'default_price': Decimal('70.00'),
                'category': 'tinting',
            },

            # PELLICULE PARE-PIERRE (PPF - BODYFENCE) - Forfaits
            {
                'name': 'PPF Ensemble "Partiel Avant"',
                'description': 'Pellicule transparente et auto-cicatrisante. Inclus : Pare-chocs, 1/4 du capot, 1/4 des ailes, miroirs.',
                'default_price': Decimal('950.00'),
                'category': 'ppf',
            },
            {
                'name': 'PPF Ensemble "Complet Avant"',
                'description': 'Pellicule transparente et auto-cicatrisante. Inclus : Pare-chocs, capot complet, ailes complètes, miroirs.',
                'default_price': Decimal('1900.00'),
                'category': 'ppf',
            },
            {
                'name': 'PPF Ensemble "Piste"',
                'description': 'Pellicule transparente et auto-cicatrisante. Inclus : Pare-chocs, bas de caisse, zone d\'impact derrière les roues arrière.',
                'default_price': Decimal('1400.00'),
                'category': 'ppf',
            },
            {
                'name': 'PPF Véhicule Complet',
                'description': 'Protection complète du véhicule avec pellicule pare-pierre. Sur devis selon le véhicule.',
                'default_price': Decimal('5500.00'),
                'category': 'ppf',
            },

            # PPF - Protection à la Carte
            {
                'name': 'PPF Pare-chocs avant',
                'description': 'Protection du pare-chocs avant avec pellicule transparente auto-cicatrisante.',
                'default_price': Decimal('450.00'),
                'category': 'ppf',
            },
            {
                'name': 'PPF Capot complet',
                'description': 'Protection complète du capot avec pellicule transparente auto-cicatrisante.',
                'default_price': Decimal('600.00'),
                'category': 'ppf',
            },
            {
                'name': 'PPF Phares',
                'description': 'Protection des phares avec pellicule transparente.',
                'default_price': Decimal('150.00'),
                'category': 'ppf',
            },
            {
                'name': 'PPF Ensemble "Essentiel du quotidien"',
                'description': 'Protection des zones les plus sollicitées : Seuil de coffre, seuils de portes, intérieur des poignées.',
                'default_price': Decimal('250.00'),
                'category': 'ppf',
            },

            # WRAPPING / PERSONNALISATION (3M / KPMF)
            {
                'name': 'Wrapping - Changement de couleur complet',
                'description': 'Personnalisez l\'apparence de votre véhicule avec un large éventail de couleurs et de finis.',
                'default_price': Decimal('3500.00'),
                'category': 'wrapping',
            },
            {
                'name': 'Wrapping - "Chrome Delete"',
                'description': 'Suppression des éléments chromés (contours des fenêtres, logos, etc.) avec film adhésif.',
                'default_price': Decimal('400.00'),
                'category': 'wrapping',
            },
            {
                'name': 'Wrapping - Toit seulement (fini noir lustré/satiné)',
                'description': 'Application de film adhésif sur le toit uniquement.',
                'default_price': Decimal('400.00'),
                'category': 'wrapping',
            },
            {
                'name': 'Wrapping - Capot seulement',
                'description': 'Application de film adhésif sur le capot uniquement.',
                'default_price': Decimal('350.00'),
                'category': 'wrapping',
            },

            # PROTECTION CÉRAMIQUE
            {
                'name': 'Protection Céramique Bronze (1 an)',
                'description': 'Couche de protection vitreuse offrant brillance intense et propriétés hydrophobes. Polissage requis (facturé en supplément).',
                'default_price': Decimal('450.00'),
                'category': 'ceramic',
            },
            {
                'name': 'Protection Céramique Argent (3 ans)',
                'description': 'Couche de protection vitreuse offrant brillance intense et propriétés hydrophobes. Polissage requis (facturé en supplément).',
                'default_price': Decimal('800.00'),
                'category': 'ceramic',
            },
            {
                'name': 'Protection Céramique Or (5+ ans)',
                'description': 'Couche de protection vitreuse offrant brillance intense et propriétés hydrophobes. Polissage requis (facturé en supplément).',
                'default_price': Decimal('1200.00'),
                'category': 'ceramic',
            },
            {
                'name': 'Protection céramique pour jantes (4)',
                'description': 'Application de protection céramique sur les 4 jantes du véhicule.',
                'default_price': Decimal('250.00'),
                'category': 'ceramic',
            },
            {
                'name': 'Protection céramique pour vitres (toutes)',
                'description': 'Application de protection céramique sur toutes les vitres du véhicule.',
                'default_price': Decimal('200.00'),
                'category': 'ceramic',
            },

            # ESTHÉTIQUE & CORRECTION DE PEINTURE
            {
                'name': 'Décontamination complète',
                'description': 'Décontamination chimique et mécanique à la barre d\'argile pour restaurer l\'éclat du véhicule.',
                'default_price': Decimal('150.00'),
                'category': 'detailing',
            },
            {
                'name': 'Polissage 1 étape',
                'description': 'Rehaussement de la brillance, enlève ~60% des défauts de peinture.',
                'default_price': Decimal('350.00'),
                'category': 'detailing',
            },
            {
                'name': 'Polissage 2 étapes',
                'description': 'Correction avancée de la peinture, enlève ~85% des défauts.',
                'default_price': Decimal('600.00'),
                'category': 'detailing',
            },
            {
                'name': 'Application de Cire/Scellant longue durée (6 mois)',
                'description': 'Application d\'une protection longue durée pour maintenir l\'éclat de la peinture.',
                'default_price': Decimal('150.00'),
                'category': 'detailing',
            },
            {
                'name': 'Protection Hydrophobe pour Pare-brise',
                'description': 'Traitement hydrophobe spécialement conçu pour le pare-brise.',
                'default_price': Decimal('80.00'),
                'category': 'hydrophobic',
            },
        ]
        
        if options['dry_run']:
            self.stdout.write('🔍 MODE SIMULATION - Aucun service ne sera créé')
            self.stdout.write(f'📊 {len(services_data)} services seraient importés:')
            for service in services_data:
                self.stdout.write(f'  - {service["name"]} (${service["default_price"]})')
            return
        
        if options['replace']:
            self.stdout.write('🗑️ Suppression des services existants...')
            deleted_count = Service.objects.all().delete()[0]
            self.stdout.write(f'✓ {deleted_count} service(s) supprimé(s)')
        
        created_count = 0
        updated_count = 0
        
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'default_price': service_data['default_price'],
                    'category': service_data['category'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'✓ Service créé: {service.name}')
            else:
                # Mettre à jour le service existant
                service.description = service_data['description']
                service.default_price = service_data['default_price']
                service.category = service_data['category']
                service.is_active = True
                service.save()
                updated_count += 1
                self.stdout.write(f'↻ Service mis à jour: {service.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Importation terminée!\n'
                f'✓ {created_count} service(s) créé(s)\n'
                f'↻ {updated_count} service(s) mis à jour\n'
                f'📊 Total: {created_count + updated_count} services MarKev'
            )
        )
