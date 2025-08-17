"""
Test spécifique pour le modèle Toyota BZ4X
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markev_project.settings')
django.setup()

import requests
from django.test import Client
from django.contrib.auth.models import User

def test_toyota_models_direct_api():
    """Test direct de l'API NHTSA pour les modèles Toyota"""
    print("🔍 Test direct API NHTSA - Modèles Toyota")
    print("=" * 60)
    
    # Tester différentes années
    years_to_test = [2022, 2023, 2024, 2025]
    
    for year in years_to_test:
        print(f"\n📅 Année {year}:")
        try:
            url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/TOYOTA/modelyear/{year}"
            params = {'format': 'json'}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('Count', 0) > 0:
                models = []
                for result in data.get('Results', []):
                    model_name = result.get('Model_Name', '').strip()
                    if model_name:
                        models.append(model_name)
                
                # Supprimer les doublons et trier
                unique_models = sorted(list(set(models)))
                
                print(f"   ✅ {len(unique_models)} modèles trouvés")
                
                # Chercher spécifiquement BZ4X
                bz4x_variants = [model for model in unique_models if 'BZ4X' in model.upper()]
                if bz4x_variants:
                    print(f"   🎯 BZ4X trouvé: {bz4x_variants}")
                else:
                    print(f"   ❌ BZ4X non trouvé")
                
                # Chercher des modèles électriques ou récents
                electric_keywords = ['BZ', 'ELECTRIC', 'EV', 'HYBRID', 'PRIME']
                electric_models = []
                for model in unique_models:
                    for keyword in electric_keywords:
                        if keyword in model.upper():
                            electric_models.append(model)
                            break
                
                if electric_models:
                    print(f"   🔋 Modèles électriques/hybrides: {electric_models[:10]}")
                
                # Afficher tous les modèles pour cette année
                print(f"   📋 Tous les modèles {year}: {', '.join(unique_models[:15])}")
                if len(unique_models) > 15:
                    print(f"       ... et {len(unique_models) - 15} autres")
                    
            else:
                print(f"   ❌ Aucun modèle trouvé pour {year}")
                
        except Exception as e:
            print(f"   ❌ Erreur pour {year}: {e}")

def test_toyota_models_without_year():
    """Test des modèles Toyota sans spécifier d'année"""
    print(f"\n🔍 Test API NHTSA - Tous les modèles Toyota (sans année)")
    print("=" * 60)
    
    try:
        url = "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/TOYOTA"
        params = {'format': 'json'}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('Count', 0) > 0:
            models = []
            for result in data.get('Results', []):
                model_name = result.get('Model_Name', '').strip()
                if model_name:
                    models.append(model_name)
            
            # Supprimer les doublons et trier
            unique_models = sorted(list(set(models)))
            
            print(f"✅ {len(unique_models)} modèles uniques trouvés (toutes années)")
            
            # Chercher BZ4X
            bz4x_variants = [model for model in unique_models if 'BZ4X' in model.upper()]
            if bz4x_variants:
                print(f"🎯 BZ4X trouvé: {bz4x_variants}")
            else:
                print(f"❌ BZ4X non trouvé dans la liste complète")
            
            # Chercher des modèles commençant par B
            b_models = [model for model in unique_models if model.upper().startswith('B')]
            print(f"📋 Modèles commençant par B: {b_models}")
            
            # Afficher quelques modèles récents/électriques
            recent_keywords = ['BZ', 'PRIME', 'HYBRID', 'ELECTRIC', 'EV']
            recent_models = []
            for model in unique_models:
                for keyword in recent_keywords:
                    if keyword in model.upper():
                        recent_models.append(model)
                        break
            
            if recent_models:
                print(f"🔋 Modèles électriques/récents: {recent_models}")
            
            return unique_models
        else:
            print("❌ Aucun modèle trouvé")
            return []
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def test_django_endpoint_toyota():
    """Test de l'endpoint Django pour les modèles Toyota"""
    print(f"\n🌐 Test endpoint Django - Modèles Toyota")
    print("=" * 60)
    
    # Créer un client de test
    client = Client()
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Se connecter
    client.force_login(user)
    
    # Tester différentes années
    years_to_test = [2022, 2023, 2024]
    
    for year in years_to_test:
        print(f"\n📅 Test Django - Toyota {year}:")
        try:
            response = client.get(f'/api/vehicle-models/?make=TOYOTA&year={year}')
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    models = data.get('models', [])
                    model_names = [model['name'] for model in models]
                    
                    print(f"   ✅ {len(models)} modèles récupérés")
                    
                    # Chercher BZ4X
                    bz4x_found = [name for name in model_names if 'BZ4X' in name.upper()]
                    if bz4x_found:
                        print(f"   🎯 BZ4X trouvé: {bz4x_found}")
                    else:
                        print(f"   ❌ BZ4X non trouvé")
                    
                    # Afficher quelques modèles
                    print(f"   📋 Exemples: {', '.join(model_names[:10])}")
                    
                else:
                    print(f"   ❌ Réponse success=False: {data.get('message')}")
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def search_alternative_spellings():
    """Rechercher des variantes d'orthographe du BZ4X"""
    print(f"\n🔤 Recherche de variantes d'orthographe")
    print("=" * 60)
    
    # Variantes possibles
    variants = [
        'BZ4X', 'bZ4X', 'BZ-4X', 'BZ 4X', 'BZ4-X',
        'TOYOTA BZ4X', 'TOYOTA bZ4X', 'SOLTERRA'  # Solterra est le nom Subaru du même véhicule
    ]
    
    try:
        # Test avec l'API sans année pour avoir tous les modèles
        url = "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/TOYOTA"
        params = {'format': 'json'}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('Count', 0) > 0:
            all_models = []
            for result in data.get('Results', []):
                model_name = result.get('Model_Name', '').strip()
                if model_name:
                    all_models.append(model_name)
            
            print(f"📊 {len(all_models)} modèles totaux à analyser")
            
            for variant in variants:
                matches = [model for model in all_models if variant.upper() in model.upper()]
                if matches:
                    print(f"   ✅ '{variant}' trouvé dans: {matches}")
                else:
                    print(f"   ❌ '{variant}' non trouvé")
            
            # Recherche plus large avec des mots-clés
            keywords = ['BZ', '4X', 'ELECTRIC', 'EV']
            print(f"\n🔍 Recherche par mots-clés:")
            for keyword in keywords:
                matches = [model for model in all_models if keyword in model.upper()]
                if matches:
                    print(f"   '{keyword}': {matches[:5]}")  # Limiter à 5 résultats
                    
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale de test"""
    print("🧪 INVESTIGATION TOYOTA BZ4X")
    print("🏢 Garage MarKev - Recherche de modèle spécifique")
    print("=" * 80)
    
    try:
        # Tests multiples
        test_toyota_models_direct_api()
        all_models = test_toyota_models_without_year()
        test_django_endpoint_toyota()
        search_alternative_spellings()
        
        print("\n" + "=" * 80)
        print("📋 ANALYSE DES RÉSULTATS")
        print("=" * 80)
        
        print("🔍 Raisons possibles de l'absence du BZ4X:")
        print("   1. 📅 Modèle trop récent (2022+) - API pas encore mise à jour")
        print("   2. 🏷️ Nom différent dans la base NHTSA")
        print("   3. 🚗 Catégorisé différemment (SUV vs Car)")
        print("   4. 🌍 Disponibilité régionale (pas encore au Canada/US)")
        print("   5. 📝 Orthographe différente (bZ4X vs BZ4X)")
        
        print(f"\n💡 Solutions possibles:")
        print("   1. 🔄 Ajouter manuellement les modèles récents")
        print("   2. 🌐 Utiliser une API alternative ou plus récente")
        print("   3. 📝 Permettre la saisie manuelle de modèles")
        print("   4. 🔍 Tester avec d'autres catégories de véhicules")
        
        print(f"\n🛠️ Actions recommandées:")
        print("   1. Vérifier si le BZ4X est dans la catégorie 'truck' ou 'multipurpose'")
        print("   2. Ajouter une option de saisie manuelle pour les modèles récents")
        print("   3. Créer une liste locale de modèles récents en fallback")
        
    except Exception as e:
        print(f"\n❌ Erreur générale lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
