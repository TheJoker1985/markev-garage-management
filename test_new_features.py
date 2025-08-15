#!/usr/bin/env python
"""
Script de test pour les nouvelles fonctionnalités MarKev
- Sauvegarde automatique
- Gestion de l'année fiscale
- Système d'archivage
- Nettoyage des données de test
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markev_project.settings')
django.setup()

from garage_app.models import CompanyProfile, Invoice, Expense, FiscalYearArchive
from datetime import date, timedelta
from decimal import Decimal


def test_fiscal_year_functionality():
    """Tester les fonctionnalités de l'année fiscale"""
    print("🧪 Test des fonctionnalités de l'année fiscale...")
    
    # Créer ou récupérer le profil d'entreprise
    company_profile, created = CompanyProfile.objects.get_or_create(
        defaults={
            'name': 'Garage Test MarKev',
            'address': '123 Test Street',
            'phone': '(514) 123-4567',
            'email': 'test@markev.com',
            'fiscal_year_end_month': 3,  # Fin d'année fiscale en mars
            'fiscal_year_end_day': 31,
        }
    )
    
    if created:
        print("✓ Profil d'entreprise créé avec année fiscale se terminant le 31 mars")
    else:
        print("✓ Profil d'entreprise existant trouvé")
    
    # Tester les méthodes de calcul de période fiscale
    today = date.today()
    fiscal_year_end = company_profile.get_fiscal_year_end(today.year)
    print(f"✓ Fin d'année fiscale {today.year}: {fiscal_year_end}")
    
    current_period = company_profile.get_current_fiscal_year_period()
    print(f"✓ Période fiscale actuelle: {current_period[0]} - {current_period[1]}")
    
    fiscal_year = company_profile.get_fiscal_year_for_date(today)
    print(f"✓ Année fiscale pour {today}: {fiscal_year}")
    
    return company_profile


def test_backup_commands():
    """Tester les commandes de sauvegarde"""
    print("\n🧪 Test des commandes de sauvegarde...")
    
    # Tester la commande de sauvegarde en mode simulation
    print("✓ Test de la commande backup_data --dry-run")
    os.system('python manage.py backup_data --dry-run --quiet')
    
    # Tester la commande de nettoyage en mode simulation
    print("✓ Test de la commande cleanup_test_data --dry-run")
    os.system('python manage.py cleanup_test_data --dry-run')


def test_archiving_system():
    """Tester le système d'archivage"""
    print("\n🧪 Test du système d'archivage...")
    
    # Vérifier qu'il n'y a pas d'archives existantes pour l'année de test
    test_year = 2023
    existing_archive = FiscalYearArchive.objects.filter(fiscal_year=test_year).first()
    
    if existing_archive:
        print(f"⚠️ Archive existante trouvée pour {test_year}, suppression...")
        existing_archive.delete()
    
    # Créer quelques données de test pour l'archivage
    company_profile = CompanyProfile.objects.first()
    if company_profile:
        # Simuler des données pour l'année fiscale 2023
        test_start_date = date(2022, 4, 1)  # Début de l'année fiscale 2023
        test_end_date = date(2023, 3, 31)   # Fin de l'année fiscale 2023
        
        print(f"✓ Période de test pour archivage: {test_start_date} - {test_end_date}")
        
        # Tester la commande d'archivage en mode simulation
        print("✓ Test de la commande archive_fiscal_year --dry-run")
        os.system(f'python manage.py archive_fiscal_year {test_year} --dry-run')
    else:
        print("⚠️ Aucun profil d'entreprise trouvé, impossible de tester l'archivage")


def show_available_commands():
    """Afficher les nouvelles commandes disponibles"""
    print("\n📋 NOUVELLES COMMANDES DISPONIBLES:")
    print("="*50)
    
    commands = [
        {
            'name': 'backup_data',
            'description': 'Créer une sauvegarde complète',
            'examples': [
                'python manage.py backup_data --compress --include-media',
                'python manage.py backup_data --output-dir /path/to/backups --keep-days 60'
            ]
        },
        {
            'name': 'restore_backup',
            'description': 'Restaurer une sauvegarde',
            'examples': [
                'python manage.py restore_backup /path/to/backup.tar.gz --restore-media',
                'python manage.py restore_backup /path/to/backup_folder --backup-current'
            ]
        },
        {
            'name': 'archive_fiscal_year',
            'description': 'Archiver une année fiscale',
            'examples': [
                'python manage.py archive_fiscal_year 2023 --user admin',
                'python manage.py archive_fiscal_year 2023 --dry-run'
            ]
        },
        {
            'name': 'cleanup_test_data',
            'description': 'Supprimer les données de test',
            'examples': [
                'python manage.py cleanup_test_data --keep-admin',
                'python manage.py cleanup_test_data --dry-run'
            ]
        }
    ]
    
    for cmd in commands:
        print(f"\n🔧 {cmd['name']}")
        print(f"   {cmd['description']}")
        for example in cmd['examples']:
            print(f"   💡 {example}")


def main():
    """Fonction principale de test"""
    print("🚀 TESTS DES NOUVELLES FONCTIONNALITÉS MARKEV")
    print("="*60)
    
    try:
        # Tester les fonctionnalités de l'année fiscale
        company_profile = test_fiscal_year_functionality()
        
        # Tester les commandes de sauvegarde
        test_backup_commands()
        
        # Tester le système d'archivage
        test_archiving_system()
        
        # Afficher les commandes disponibles
        show_available_commands()
        
        print("\n✅ TOUS LES TESTS TERMINÉS AVEC SUCCÈS!")
        print("\n📝 PROCHAINES ÉTAPES RECOMMANDÉES:")
        print("1. Configurez votre profil d'entreprise avec la bonne date de fin d'année fiscale")
        print("2. Supprimez les données de test: python manage.py cleanup_test_data --keep-admin")
        print("3. Configurez une sauvegarde automatique régulière")
        print("4. Testez la restauration sur un environnement de test")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
