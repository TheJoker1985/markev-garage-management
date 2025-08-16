from django.core.management.base import BaseCommand
from django.db import transaction
from garage_app.utils.stock_monitoring import (
    check_all_inventory_stock_alerts,
    get_stock_alerts_summary,
    get_items_needing_attention,
    cleanup_old_resolved_alerts
)
from garage_app.models import InventoryItem, StockAlert


class Command(BaseCommand):
    help = 'Vérifier les niveaux de stock et créer les alertes de réapprovisionnement'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler la vérification sans créer d\'alertes'
        )
        parser.add_argument(
            '--cleanup-old',
            action='store_true',
            help='Nettoyer les anciennes alertes résolues (90+ jours)'
        )
        parser.add_argument(
            '--cleanup-days',
            type=int,
            default=90,
            help='Nombre de jours pour le nettoyage des alertes (défaut: 90)'
        )
        parser.add_argument(
            '--summary-only',
            action='store_true',
            help='Afficher seulement le résumé sans créer de nouvelles alertes'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Affichage détaillé'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.cleanup_old = options['cleanup_old']
        self.cleanup_days = options['cleanup_days']
        self.summary_only = options['summary_only']
        self.verbose = options['verbose']

        self.stdout.write('🔍 Vérification des niveaux de stock...\n')

        try:
            # Afficher le résumé actuel
            self.display_current_summary()

            if not self.summary_only:
                # Vérifier les stocks et créer les alertes
                self.check_and_create_alerts()

            if self.cleanup_old:
                # Nettoyer les anciennes alertes
                self.cleanup_old_alerts()

            self.stdout.write('\n✅ Vérification terminée avec succès!')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la vérification des stocks: {str(e)}')
            )
            raise

    def display_current_summary(self):
        """Afficher le résumé actuel des alertes"""
        summary = get_stock_alerts_summary()
        items = get_items_needing_attention()

        self.stdout.write('📊 Résumé actuel des stocks:')
        self.stdout.write(f'   • Articles en rupture de stock: {len(items["out_of_stock"])}')
        self.stdout.write(f'   • Articles nécessitant réapprovisionnement: {len(items["needs_reorder"])}')
        self.stdout.write(f'   • Articles en stock faible: {len(items["low_stock"])}')
        self.stdout.write(f'   • Articles OK: {len(items["ok"])}')

        self.stdout.write('\n🚨 Résumé des alertes:')
        self.stdout.write(f'   • Total des alertes: {summary["total_alerts"]}')
        self.stdout.write(f'   • Alertes actives: {summary["active_alerts"]}')
        self.stdout.write(f'   • Alertes prises en compte: {summary["acknowledged_alerts"]}')
        self.stdout.write(f'   • Alertes résolues: {summary["resolved_alerts"]}')

        if self.verbose and summary["active_alerts"] > 0:
            self.stdout.write('\n📋 Détail des alertes actives:')
            active_alerts = StockAlert.objects.filter(status='active').select_related('inventory_item')
            for alert in active_alerts:
                self.stdout.write(
                    f'   • {alert.inventory_item.name} ({alert.get_alert_type_display()}) - '
                    f'Stock: {alert.quantity_at_alert}, Seuil: {alert.threshold_level}'
                )

    def check_and_create_alerts(self):
        """Vérifier les stocks et créer les alertes"""
        if self.dry_run:
            self.stdout.write('\n🔍 Mode simulation - aucune alerte ne sera créée')
        else:
            self.stdout.write('\n🔍 Vérification des stocks en cours...')

        # Vérifier tous les articles d'inventaire
        if self.dry_run:
            # En mode dry-run, on simule sans sauvegarder
            stats = self.simulate_stock_check()
        else:
            stats = check_all_inventory_stock_alerts()

        # Afficher les résultats
        self.stdout.write('\n📈 Résultats de la vérification:')
        self.stdout.write(f'   • Articles vérifiés: {stats["items_checked"]}')
        self.stdout.write(f'   • Nouvelles alertes créées: {stats["alerts_created"]}')
        self.stdout.write(f'   • Alertes résolues automatiquement: {stats["alerts_resolved"]}')

        if stats["items_needing_reorder"] > 0:
            self.stdout.write(
                self.style.WARNING(f'   ⚠️  Articles nécessitant réapprovisionnement: {stats["items_needing_reorder"]}')
            )

        if stats["items_out_of_stock"] > 0:
            self.stdout.write(
                self.style.ERROR(f'   🚨 Articles en rupture de stock: {stats["items_out_of_stock"]}')
            )

    def simulate_stock_check(self):
        """Simuler la vérification des stocks sans créer d'alertes"""
        stats = {
            'items_checked': 0,
            'alerts_created': 0,
            'alerts_resolved': 0,
            'items_needing_reorder': 0,
            'items_low_stock': 0,
            'items_out_of_stock': 0,
        }

        inventory_items = InventoryItem.objects.filter(is_active=True)

        for item in inventory_items:
            stats['items_checked'] += 1

            # Simuler la création d'alertes
            if item.needs_reorder:
                existing_reorder = item.stock_alerts.filter(
                    alert_type='reorder', status='active'
                ).exists()
                if not existing_reorder:
                    stats['alerts_created'] += 1
                stats['items_needing_reorder'] += 1

            if item.is_low_stock:
                existing_low_stock = item.stock_alerts.filter(
                    alert_type='low_stock', status='active'
                ).exists()
                if not existing_low_stock:
                    stats['alerts_created'] += 1
                stats['items_low_stock'] += 1

            if item.quantity_in_stock == 0:
                existing_out_of_stock = item.stock_alerts.filter(
                    alert_type='out_of_stock', status='active'
                ).exists()
                if not existing_out_of_stock:
                    stats['alerts_created'] += 1
                stats['items_out_of_stock'] += 1

        return stats

    def cleanup_old_alerts(self):
        """Nettoyer les anciennes alertes résolues"""
        self.stdout.write(f'\n🧹 Nettoyage des alertes résolues de plus de {self.cleanup_days} jours...')

        if self.dry_run:
            # En mode dry-run, compter sans supprimer
            from django.utils import timezone
            cutoff_date = timezone.now() - timezone.timedelta(days=self.cleanup_days)
            count = StockAlert.objects.filter(
                status__in=['resolved', 'dismissed'],
                resolved_date__lt=cutoff_date
            ).count()
            self.stdout.write(f'   📊 {count} alerte(s) seraient supprimée(s) (mode simulation)')
        else:
            count = cleanup_old_resolved_alerts(self.cleanup_days)
            self.stdout.write(f'   ✅ {count} alerte(s) supprimée(s)')


# Fonction utilitaire pour être appelée depuis d'autres endroits
def check_stock_alerts():
    """Fonction utilitaire pour vérifier les alertes de stock"""
    from django.core.management import call_command
    call_command('check_stock_alerts')


# Exemple d'utilisation dans une tâche cron
"""
# Ajouter cette ligne dans votre crontab pour exécuter quotidiennement à 8h00:
# 0 8 * * * cd /path/to/your/project && python manage.py check_stock_alerts

# Ou pour une vérification avec nettoyage hebdomadaire:
# 0 8 * * 1 cd /path/to/your/project && python manage.py check_stock_alerts --cleanup-old

# Pour un résumé quotidien sans créer de nouvelles alertes:
# 0 17 * * * cd /path/to/your/project && python manage.py check_stock_alerts --summary-only
"""
