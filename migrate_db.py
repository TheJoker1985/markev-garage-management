#!/usr/bin/env python
"""
Script simple pour appliquer les migrations Django en production
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markev_project.settings')

# Configuration des variables d'environnement pour la production
os.environ['SECRET_KEY'] = 'django-markev-production-secret-key-2025-secure-garage-management-app-v1'
os.environ['DEBUG'] = 'False'
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_zGMI9yBRFqp6@ep-square-fog-aezxelmf-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require'

django.setup()

from django.core.management import execute_from_command_line

def main():
    """Appliquer les migrations"""
    print("🔄 Application des migrations Django...")
    
    try:
        # Appliquer les migrations
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations appliquées avec succès!")
        
        # Créer un superutilisateur si nécessaire
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@markev.com',
                password='admin123'
            )
            print("✅ Superutilisateur créé: admin / admin123")
        else:
            print("✅ Superutilisateur déjà existant")
        
        # Importer les services MarKev
        from garage_app.models import Service
        if Service.objects.count() < 36:
            execute_from_command_line(['manage.py', 'import_markev_services'])
            print(f"✅ Services importés: {Service.objects.count()} services")
        else:
            print(f"✅ Services déjà importés: {Service.objects.count()} services")
            
        print("\n🎉 Configuration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
