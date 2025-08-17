"""
Test pour vérifier toutes les marques de véhicules disponibles
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

def test_nhtsa_api_direct():
    """Test direct de l'API NHTSA pour voir toutes les marques"""
    print("🌐 Test direct de l'API NHTSA")
    print("=" * 50)
    
    try:
        url = "https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/car"
        params = {'format': 'json'}
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('Count', 0) > 0:
            makes = []
            for result in data.get('Results', []):
                make_name = result.get('MakeName', '').strip()
                if make_name:
                    makes.append(make_name)
            
            # Trier par nom
            makes.sort()
            
            print(f"✅ {len(makes)} marques trouvées dans l'API NHTSA")
            
            # Afficher par groupes alphabétiques
            current_letter = ''
            count_by_letter = {}
            
            for make in makes:
                first_letter = make[0].upper()
                if first_letter != current_letter:
                    current_letter = first_letter
                    count_by_letter[first_letter] = 0
                count_by_letter[first_letter] += 1
            
            print("\n📊 Répartition par lettre :")
            for letter in sorted(count_by_letter.keys()):
                print(f"   {letter}: {count_by_letter[letter]} marques")
            
            # Afficher quelques exemples de chaque section
            print(f"\n📋 Exemples de marques :")
            print(f"   A-E: {', '.join([m for m in makes if m[0].upper() in 'ABCDE'][:5])}")
            print(f"   F-J: {', '.join([m for m in makes if m[0].upper() in 'FGHIJ'][:5])}")
            print(f"   K-O: {', '.join([m for m in makes if m[0].upper() in 'KLMNO'][:5])}")
            print(f"   P-T: {', '.join([m for m in makes if m[0].upper() in 'PQRST'][:5])}")
            print(f"   U-Z: {', '.join([m for m in makes if m[0].upper() in 'UVWXYZ'][:5])}")
            
            # Vérifier les marques populaires
            popular_makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Volvo']
            print(f"\n🔍 Vérification marques populaires :")
            for popular in popular_makes:
                if popular in makes:
                    print(f"   ✅ {popular}")
                else:
                    print(f"   ❌ {popular} - MANQUANT")
            
            return makes
        else:
            print("❌ Aucune marque trouvée")
            return []
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def test_django_endpoint():
    """Test de l'endpoint Django après correction"""
    print(f"\n🌐 Test de l'endpoint Django corrigé")
    print("=" * 50)
    
    # Créer un client de test
    client = Client()
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Se connecter
    client.force_login(user)
    
    try:
        response = client.get('/api/vehicle-makes/')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                makes = data.get('makes', [])
                make_names = [make['name'] for make in makes]
                make_names.sort()
                
                print(f"✅ {len(makes)} marques récupérées via Django")
                
                # Vérifier la répartition alphabétique
                if make_names:
                    first_make = make_names[0]
                    last_make = make_names[-1]
                    print(f"   Première marque: {first_make}")
                    print(f"   Dernière marque: {last_make}")
                    
                    # Compter par lettre
                    letters = set(make[0].upper() for make in make_names)
                    print(f"   Lettres couvertes: {sorted(letters)}")
                    print(f"   Nombre de lettres: {len(letters)}")
                    
                    # Vérifier si on a des marques après KIA
                    after_kia = [make for make in make_names if make > 'KIA']
                    print(f"   Marques après KIA: {len(after_kia)}")
                    if after_kia:
                        print(f"   Exemples après KIA: {', '.join(after_kia[:10])}")
                
                return make_names
            else:
                print(f"❌ Réponse success=False: {data.get('message')}")
                return []
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def compare_results(api_makes, django_makes):
    """Comparer les résultats de l'API directe vs Django"""
    print(f"\n📊 Comparaison des résultats")
    print("=" * 50)
    
    print(f"API NHTSA directe: {len(api_makes)} marques")
    print(f"Endpoint Django: {len(django_makes)} marques")
    
    if len(api_makes) == len(django_makes):
        print("✅ Même nombre de marques - Parfait!")
    else:
        print(f"⚠️ Différence de {abs(len(api_makes) - len(django_makes))} marques")
    
    # Vérifier les marques manquantes
    api_set = set(api_makes)
    django_set = set(django_makes)
    
    missing_in_django = api_set - django_set
    extra_in_django = django_set - api_set
    
    if missing_in_django:
        print(f"\n❌ Marques manquantes dans Django ({len(missing_in_django)}):")
        for make in sorted(list(missing_in_django)[:10]):
            print(f"   • {make}")
        if len(missing_in_django) > 10:
            print(f"   ... et {len(missing_in_django) - 10} autres")
    
    if extra_in_django:
        print(f"\n➕ Marques supplémentaires dans Django ({len(extra_in_django)}):")
        for make in sorted(list(extra_in_django)[:10]):
            print(f"   • {make}")

def main():
    """Fonction principale de test"""
    print("🧪 TEST COMPLET DES MARQUES DE VÉHICULES")
    print("🏢 Garage MarKev - Vérification après correction")
    print("=" * 80)
    
    try:
        # Test de l'API NHTSA directe
        api_makes = test_nhtsa_api_direct()
        
        # Test de l'endpoint Django
        django_makes = test_django_endpoint()
        
        # Comparaison
        if api_makes and django_makes:
            compare_results(api_makes, django_makes)
        
        print("\n" + "=" * 80)
        print("📋 RÉSUMÉ")
        print("=" * 80)
        
        if django_makes:
            # Vérifier si le problème est résolu
            after_kia_count = len([make for make in django_makes if make > 'KIA'])
            
            if after_kia_count > 0:
                print("🎉 PROBLÈME RÉSOLU!")
                print(f"   ✅ {len(django_makes)} marques disponibles")
                print(f"   ✅ {after_kia_count} marques après KIA")
                print(f"   ✅ Liste complète de A à Z")
                
                # Afficher quelques marques après KIA
                after_kia_examples = [make for make in django_makes if make > 'KIA'][:10]
                print(f"   📋 Exemples après KIA: {', '.join(after_kia_examples)}")
                
                print(f"\n🌐 Testez maintenant l'interface:")
                print("   📝 Allez sur http://127.0.0.1:8000/vehicles/new/")
                print("   🖱️ Cliquez sur le dropdown 'Marque'")
                print("   📜 Vous devriez voir toutes les marques de A à Z")
                print("   🔍 Cherchez Toyota, Volvo, etc.")
            else:
                print("❌ PROBLÈME PERSISTE")
                print("   La liste s'arrête toujours à KIA")
        else:
            print("❌ ÉCHEC DU TEST")
            print("   Impossible de récupérer les marques")
        
    except Exception as e:
        print(f"\n❌ Erreur générale lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
