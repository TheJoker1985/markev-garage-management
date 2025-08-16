"""
Utilitaires pour la surveillance automatique des stocks
"""
from django.db import transaction
from django.utils import timezone
from ..models import InventoryItem, StockAlert


def check_all_inventory_stock_alerts():
    """
    Vérifier tous les articles d'inventaire et créer les alertes nécessaires
    
    Returns:
        dict: Statistiques sur les alertes créées
    """
    stats = {
        'items_checked': 0,
        'alerts_created': 0,
        'alerts_resolved': 0,
        'items_needing_reorder': 0,
        'items_low_stock': 0,
        'items_out_of_stock': 0,
    }
    
    # Obtenir tous les articles actifs
    inventory_items = InventoryItem.objects.filter(is_active=True)
    
    with transaction.atomic():
        for item in inventory_items:
            stats['items_checked'] += 1
            
            # Résoudre les alertes si le stock est suffisant
            resolved_alerts = item.resolve_alerts_if_stock_sufficient()
            stats['alerts_resolved'] += len(resolved_alerts)
            
            # Vérifier et créer de nouvelles alertes
            new_alerts = item.check_stock_alerts()
            stats['alerts_created'] += len(new_alerts)
            
            # Compter les différents types de problèmes de stock
            if item.needs_reorder:
                stats['items_needing_reorder'] += 1
            if item.is_low_stock:
                stats['items_low_stock'] += 1
            if item.quantity_in_stock == 0:
                stats['items_out_of_stock'] += 1
    
    return stats


def get_active_stock_alerts():
    """
    Obtenir toutes les alertes de stock actives
    
    Returns:
        QuerySet: Alertes de stock actives
    """
    return StockAlert.objects.filter(status='active').select_related('inventory_item')


def get_stock_alerts_summary():
    """
    Obtenir un résumé des alertes de stock
    
    Returns:
        dict: Résumé des alertes par type et statut
    """
    alerts = StockAlert.objects.all()
    
    summary = {
        'total_alerts': alerts.count(),
        'active_alerts': alerts.filter(status='active').count(),
        'acknowledged_alerts': alerts.filter(status='acknowledged').count(),
        'resolved_alerts': alerts.filter(status='resolved').count(),
        'dismissed_alerts': alerts.filter(status='dismissed').count(),
        'by_type': {
            'reorder': alerts.filter(alert_type='reorder').count(),
            'low_stock': alerts.filter(alert_type='low_stock').count(),
            'out_of_stock': alerts.filter(alert_type='out_of_stock').count(),
        },
        'active_by_type': {
            'reorder': alerts.filter(alert_type='reorder', status='active').count(),
            'low_stock': alerts.filter(alert_type='low_stock', status='active').count(),
            'out_of_stock': alerts.filter(alert_type='out_of_stock', status='active').count(),
        }
    }
    
    return summary


def get_items_needing_attention():
    """
    Obtenir les articles nécessitant une attention particulière
    
    Returns:
        dict: Articles classés par priorité
    """
    inventory_items = InventoryItem.objects.filter(is_active=True)
    
    items = {
        'out_of_stock': [],
        'needs_reorder': [],
        'low_stock': [],
        'ok': []
    }
    
    for item in inventory_items:
        if item.quantity_in_stock == 0:
            items['out_of_stock'].append(item)
        elif item.needs_reorder:
            items['needs_reorder'].append(item)
        elif item.is_low_stock:
            items['low_stock'].append(item)
        else:
            items['ok'].append(item)
    
    return items


def bulk_acknowledge_alerts(alert_ids, notes=None):
    """
    Marquer plusieurs alertes comme prises en compte
    
    Args:
        alert_ids (list): Liste des IDs d'alertes
        notes (str, optional): Notes à ajouter
    
    Returns:
        int: Nombre d'alertes mises à jour
    """
    alerts = StockAlert.objects.filter(id__in=alert_ids, status='active')
    count = 0
    
    with transaction.atomic():
        for alert in alerts:
            alert.acknowledge(notes)
            count += 1
    
    return count


def bulk_resolve_alerts(alert_ids, action_taken=None):
    """
    Marquer plusieurs alertes comme résolues
    
    Args:
        alert_ids (list): Liste des IDs d'alertes
        action_taken (str, optional): Action entreprise
    
    Returns:
        int: Nombre d'alertes mises à jour
    """
    alerts = StockAlert.objects.filter(id__in=alert_ids, status__in=['active', 'acknowledged'])
    count = 0
    
    with transaction.atomic():
        for alert in alerts:
            alert.resolve(action_taken)
            count += 1
    
    return count


def cleanup_old_resolved_alerts(days_old=90):
    """
    Nettoyer les anciennes alertes résolues
    
    Args:
        days_old (int): Nombre de jours après lesquels supprimer les alertes résolues
    
    Returns:
        int: Nombre d'alertes supprimées
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
    
    old_alerts = StockAlert.objects.filter(
        status__in=['resolved', 'dismissed'],
        resolved_date__lt=cutoff_date
    )
    
    count = old_alerts.count()
    old_alerts.delete()
    
    return count
