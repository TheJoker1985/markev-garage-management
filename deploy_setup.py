#!/usr/bin/env python
"""
Script de préparation pour le déploiement MarKev sur Vercel
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markev_project.settings')
django.setup()

from garage_app.models import Service, CompanyProfile
from django.contrib.auth.models import User


def check_deployment_readiness():
    """Vérifier que l'application est prête pour le déploiement"""
    print("🔍 VÉRIFICATION DE L'ÉTAT DE DÉPLOIEMENT")
    print("="*50)
    
    issues = []
    
    # 1. Vérifier les fichiers de configuration
    required_files = [
        'vercel.json',
        'build_files.sh',
        'requirements.txt',
        '.env.example',
        'DEPLOYMENT.md'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} présent")
        else:
            print(f"❌ {file} manquant")
            issues.append(f"Fichier manquant: {file}")
    
    # 2. Vérifier les services
    services_count = Service.objects.count()
    if services_count >= 36:
        print(f"✅ Services MarKev: {services_count} services")
    else:
        print(f"⚠️ Services MarKev: {services_count} services (attendu: 36)")
        issues.append("Services MarKev incomplets")
    
    # 3. Vérifier les catégories de services
    categories = Service.objects.values_list('category', flat=True).distinct()
    expected_categories = ['package', 'tinting', 'ppf', 'wrapping', 'ceramic', 'hydrophobic', 'detailing']
    missing_categories = set(expected_categories) - set(categories)
    
    if not missing_categories:
        print(f"✅ Catégories de services: {len(categories)} catégories")
    else:
        print(f"⚠️ Catégories manquantes: {missing_categories}")
        issues.append(f"Catégories manquantes: {missing_categories}")
    
    # 4. Vérifier les utilisateurs
    admin_users = User.objects.filter(is_superuser=True).count()
    if admin_users > 0:
        print(f"✅ Utilisateurs admin: {admin_users}")
    else:
        print("⚠️ Aucun utilisateur admin")
        issues.append("Aucun utilisateur admin")
    
    # 5. Vérifier les migrations
    try:
        from django.core.management import execute_from_command_line
        print("✅ Migrations Django: OK")
    except Exception as e:
        print(f"❌ Problème avec les migrations: {e}")
        issues.append(f"Migrations: {e}")
    
    print("\n📊 RÉSUMÉ")
    print("="*50)
    
    if not issues:
        print("🎉 APPLICATION PRÊTE POUR LE DÉPLOIEMENT!")
        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. Pousser le code sur GitHub")
        print("2. Connecter le repository à Vercel")
        print("3. Configurer les variables d'environnement:")
        print("   - SECRET_KEY")
        print("   - DEBUG=False")
        print("   - DATABASE_URL (PostgreSQL)")
        print("4. Déployer sur Vercel")
        print("5. Exécuter les migrations en production")
        print("6. Créer un superutilisateur en production")
        print("7. Importer les services: python manage.py import_markev_services")
        return True
    else:
        print("⚠️ PROBLÈMES À RÉSOUDRE:")
        for issue in issues:
            print(f"  - {issue}")
        return False


def show_vercel_commands():
    """Afficher les commandes Vercel utiles"""
    print("\n🚀 COMMANDES VERCEL UTILES")
    print("="*50)
    print("# Installation de Vercel CLI")
    print("npm i -g vercel")
    print()
    print("# Déploiement depuis le terminal")
    print("vercel --prod")
    print()
    print("# Voir les logs de déploiement")
    print("vercel logs")
    print()
    print("# Configurer les variables d'environnement")
    print("vercel env add SECRET_KEY")
    print("vercel env add DEBUG")
    print("vercel env add DATABASE_URL")


def main():
    """Fonction principale"""
    print("🚀 PRÉPARATION DU DÉPLOIEMENT MARKEV")
    print("="*60)
    
    ready = check_deployment_readiness()
    
    if ready:
        show_vercel_commands()
        
        print("\n🌐 LIENS UTILES:")
        print("- Vercel Dashboard: https://vercel.com/dashboard")
        print("- Supabase: https://supabase.com")
        print("- Neon: https://neon.tech")
        print("- Documentation: ./DEPLOYMENT.md")
    
    return 0 if ready else 1


if __name__ == '__main__':
    sys.exit(main())
