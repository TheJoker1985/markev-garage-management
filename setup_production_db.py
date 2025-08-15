#!/usr/bin/env python
"""
Script pour configurer la base de données de production MarKev
À exécuter après le déploiement sur Vercel
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markev_project.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from garage_app.models import Service


def run_migrations():
    """Appliquer les migrations Django"""
    print("🔄 Application des migrations Django...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations appliquées avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors des migrations: {e}")
        return False


def create_superuser():
    """Créer un superutilisateur si nécessaire"""
    print("👤 Vérification du superutilisateur...")
    
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superutilisateur déjà existant")
        return True
    
    try:
        # Créer le superutilisateur par défaut
        User.objects.create_superuser(
            username='admin',
            email='admin@markev.com',
            password='admin123'
        )
        print("✅ Superutilisateur créé: admin / admin123")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du superutilisateur: {e}")
        return False


def import_services():
    """Importer les services MarKev"""
    print("🛠️ Importation des services MarKev...")
    
    # Vérifier si les services existent déjà
    if Service.objects.count() >= 36:
        print(f"✅ Services déjà importés: {Service.objects.count()} services")
        return True
    
    try:
        execute_from_command_line(['manage.py', 'import_markev_services'])
        print(f"✅ Services importés: {Service.objects.count()} services")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'importation des services: {e}")
        return False


def verify_setup():
    """Vérifier que tout est correctement configuré"""
    print("🔍 Vérification de la configuration...")
    
    issues = []
    
    # Vérifier les services
    services_count = Service.objects.count()
    if services_count >= 36:
        print(f"✅ Services: {services_count}")
    else:
        issues.append(f"Services insuffisants: {services_count}/36")
    
    # Vérifier les utilisateurs admin
    admin_count = User.objects.filter(is_superuser=True).count()
    if admin_count > 0:
        print(f"✅ Administrateurs: {admin_count}")
    else:
        issues.append("Aucun administrateur")
    
    # Vérifier la base de données
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Connexion base de données: OK")
    except Exception as e:
        issues.append(f"Base de données: {e}")
    
    return len(issues) == 0, issues


def main():
    """Fonction principale"""
    print("🚀 CONFIGURATION DE LA BASE DE DONNÉES MARKEV")
    print("="*60)
    
    success = True
    
    # 1. Migrations
    if not run_migrations():
        success = False
    
    # 2. Superutilisateur
    if not create_superuser():
        success = False
    
    # 3. Services
    if not import_services():
        success = False
    
    # 4. Vérification
    verification_ok, issues = verify_setup()
    if not verification_ok:
        print("\n⚠️ PROBLÈMES DÉTECTÉS:")
        for issue in issues:
            print(f"  - {issue}")
        success = False
    
    print("\n📊 RÉSUMÉ")
    print("="*50)
    
    if success:
        print("🎉 CONFIGURATION TERMINÉE AVEC SUCCÈS!")
        print("\n✅ L'application MarKev est prête:")
        print("- Base de données PostgreSQL configurée")
        print("- Migrations appliquées")
        print("- Superutilisateur créé (admin/admin123)")
        print("- 36 services MarKev importés")
        print("\n🌐 Accédez à votre application:")
        print("- Interface: https://markev-garage-management-njohnk9n6-keven-lesperances-projects.vercel.app")
        print("- Admin: https://markev-garage-management-njohnk9n6-keven-lesperances-projects.vercel.app/admin")
    else:
        print("❌ CONFIGURATION INCOMPLÈTE")
        print("Vérifiez les erreurs ci-dessus et réessayez.")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
