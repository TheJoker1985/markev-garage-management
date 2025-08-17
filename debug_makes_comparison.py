"""
Debug de la comparaison des marques pour comprendre pourquoi les marques populaires ne sont pas ajoutées
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markev_project.settings')
django.setup()

import requests

def debug_makes_comparison():
    """Debug de la logique de comparaison des marques"""
    print("🔍 DEBUG - Comparaison des marques")
    print("=" * 50)
    
    # Marques populaires à rechercher
    essential_makes = [
        'Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'Hyundai', 'Kia',
        'Mazda', 'Subaru', 'Volkswagen', 'Mercedes-Benz', 'Audi', 'Volvo'
    ]
    
    try:
        # Récupérer depuis l'API NHTSA
        url = "https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/car"
        params = {'format': 'json'}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('Count', 0) > 0:
            # Récupérer tous les noms de marques de l'API
            api_make_names = set()
            api_makes_list = []
            
            for result in data.get('Results', []):
                make_name = result.get('MakeName', '').strip()
                if make_name:
                    api_make_names.add(make_name.upper())
                    api_makes_list.append(make_name)
            
            print(f"📊 {len(api_makes_list)} marques dans l'API NHTSA")
            
            # Afficher quelques exemples de noms exacts
            print(f"\n📋 Exemples de noms exacts dans l'API:")
            sorted_makes = sorted(api_makes_list)
            for i, make in enumerate(sorted_makes[:20]):
                print(f"   {i+1:2d}. '{make}'")
            
            print(f"\n🔍 Recherche des marques populaires:")
            for essential in essential_makes:
                essential_upper = essential.upper()
                if essential_upper in api_make_names:
                    print(f"   ✅ {essential} -> Trouvé comme '{essential}'")
                else:
                    # Chercher des variantes
                    matches = [make for make in api_makes_list if essential.upper() in make.upper()]
                    if matches:
                        print(f"   🔍 {essential} -> Variantes trouvées: {matches}")
                    else:
                        print(f"   ❌ {essential} -> AUCUNE CORRESPONDANCE")
            
            # Chercher spécifiquement quelques marques connues
            print(f"\n🎯 Recherche spécifique de marques connues:")
            known_patterns = {
                'Toyota': ['TOYOTA', 'TOYOTA MOTOR'],
                'Honda': ['HONDA', 'HONDA MOTOR'],
                'Ford': ['FORD', 'FORD MOTOR'],
                'BMW': ['BMW'],
                'Mercedes': ['MERCEDES', 'MERCEDES-BENZ', 'DAIMLER'],
                'Volkswagen': ['VOLKSWAGEN', 'VW'],
                'Audi': ['AUDI'],
                'Volvo': ['VOLVO']
            }
            
            for brand, patterns in known_patterns.items():
                found_matches = []
                for pattern in patterns:
                    matches = [make for make in api_makes_list if pattern in make.upper()]
                    found_matches.extend(matches)
                
                if found_matches:
                    print(f"   ✅ {brand}: {found_matches}")
                else:
                    print(f"   ❌ {brand}: Aucune correspondance")
            
            # Afficher toutes les marques qui commencent par certaines lettres
            print(f"\n📝 Marques commençant par T, H, F, V:")
            for letter in ['T', 'H', 'F', 'V']:
                letter_makes = [make for make in sorted_makes if make.upper().startswith(letter)]
                print(f"   {letter}: {letter_makes[:10]}")  # Limiter à 10 pour la lisibilité
            
        else:
            print("❌ Aucune marque trouvée dans l'API")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale de debug"""
    print("🐛 DEBUG DES MARQUES DE VÉHICULES")
    print("🏢 Garage MarKev - Analyse des noms de marques")
    print("=" * 80)
    
    debug_makes_comparison()

if __name__ == "__main__":
    main()
