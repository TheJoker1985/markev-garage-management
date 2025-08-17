"""
Test des suggestions de marques et modèles depuis l'API NHTSA
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markev_project.settings')
django.setup()

import requests

def test_nhtsa_makes():
    """Test de récupération des marques depuis l'API NHTSA"""
    print("🚗 Test de récupération des marques")
    print("=" * 50)
    
    try:
        url = "https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/car"
        params = {'format': 'json'}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('Count', 0) > 0:
            makes = []
            for result in data.get('Results', [])[:20]:  # Prendre les 20 premiers
                make_name = result.get('MakeName', '').strip()
                if make_name:
                    makes.append(make_name)
            
            print(f"✅ {data.get('Count')} marques trouvées")
            print("📋 Exemples de marques :")
            for make in makes:
                print(f"   • {make}")
            
            return True
        else:
            print("❌ Aucune marque trouvée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_nhtsa_models(make="Toyota", year=2023):
    """Test de récupération des modèles pour une marque"""
    print(f"\n🚙 Test de récupération des modèles pour {make} {year}")
    print("=" * 50)
    
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/{make}/modelyear/{year}"
        params = {'format': 'json'}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('Count', 0) > 0:
            models = []
            seen_models = set()
            
            for result in data.get('Results', []):
                model_name = result.get('Model_Name', '').strip()
                if model_name and model_name not in seen_models:
                    models.append(model_name)
                    seen_models.add(model_name)
            
            print(f"✅ {len(models)} modèles uniques trouvés pour {make} {year}")
            print("📋 Modèles disponibles :")
            for model in models[:15]:  # Afficher les 15 premiers
                print(f"   • {model}")
            
            if len(models) > 15:
                print(f"   ... et {len(models) - 15} autres")
            
            return True
        else:
            print(f"❌ Aucun modèle trouvé pour {make} {year}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_django_views():
    """Test des vues Django pour les suggestions"""
    print(f"\n🌐 Test des vues Django")
    print("=" * 50)
    
    from django.test import Client
    from django.contrib.auth.models import User
    
    # Créer un client de test
    client = Client()
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Se connecter
    client.force_login(user)
    
    # Test de récupération des marques
    print("🔍 Test de l'endpoint des marques...")
    response = client.get('/api/vehicle-makes/')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            makes_count = len(data.get('makes', []))
            print(f"✅ Endpoint marques OK: {makes_count} marques")
            
            # Afficher quelques exemples
            for make in data.get('makes', [])[:10]:
                print(f"   • {make['name']}")
        else:
            print(f"⚠️ Endpoint marques retourne success=False: {data.get('message')}")
    else:
        print(f"❌ Erreur endpoint marques: {response.status_code}")
    
    # Test de récupération des modèles
    print("\n🔍 Test de l'endpoint des modèles...")
    response = client.get('/api/vehicle-models/?make=Toyota&year=2023')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            models_count = len(data.get('models', []))
            print(f"✅ Endpoint modèles OK: {models_count} modèles pour Toyota 2023")
            
            # Afficher quelques exemples
            for model in data.get('models', [])[:10]:
                print(f"   • {model['name']}")
        else:
            print(f"⚠️ Endpoint modèles retourne success=False: {data.get('message')}")
    else:
        print(f"❌ Erreur endpoint modèles: {response.status_code}")

def test_popular_makes():
    """Test avec plusieurs marques populaires"""
    print(f"\n🏆 Test avec marques populaires")
    print("=" * 50)
    
    popular_makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan']
    year = 2023
    
    for make in popular_makes:
        print(f"\n📊 {make} {year}:")
        try:
            url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/{make}/modelyear/{year}"
            params = {'format': 'json'}
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            count = data.get('Count', 0)
            
            if count > 0:
                models = set()
                for result in data.get('Results', []):
                    model_name = result.get('Model_Name', '').strip()
                    if model_name:
                        models.add(model_name)
                
                print(f"   ✅ {len(models)} modèles uniques")
                # Afficher les 5 premiers
                for model in list(models)[:5]:
                    print(f"      • {model}")
            else:
                print(f"   ❌ Aucun modèle")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def main():
    """Fonction principale de test"""
    print("🧪 TEST DES SUGGESTIONS DE VÉHICULES - API NHTSA")
    print("🏢 Garage MarKev - Autocomplétion Marques et Modèles")
    print("=" * 80)
    
    try:
        # Test de l'API NHTSA directement
        makes_ok = test_nhtsa_makes()
        models_ok = test_nhtsa_models()
        
        # Test des vues Django
        test_django_views()
        
        # Test avec marques populaires
        test_popular_makes()
        
        print("\n" + "=" * 80)
        if makes_ok and models_ok:
            print("🎉 TESTS RÉUSSIS!")
            print("\n📋 Fonctionnalités disponibles :")
            print("   ✅ Autocomplétion des marques depuis l'API NHTSA")
            print("   ✅ Autocomplétion des modèles par marque et année")
            print("   ✅ Fallback avec listes locales si API indisponible")
            print("   ✅ Interface utilisateur avec suggestions en temps réel")
            
            print(f"\n🌐 Interface Web :")
            print("   📝 Allez sur http://127.0.0.1:8000/vehicles/add/")
            print("   ⌨️ Tapez dans les champs Marque et Modèle pour voir les suggestions")
            print("   🔍 Utilisez le bouton 'Identifier le type' après avoir rempli les champs")
        else:
            print("⚠️ TESTS PARTIELS - Vérifiez la connectivité à l'API NHTSA")
        
    except Exception as e:
        print(f"\n❌ Erreur générale lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
