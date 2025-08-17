"""
Test rapide pour voir exactement quels modèles Toyota 2023 sont retournés
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markev_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_exact_toyota_2023():
    """Test exact de ce que retourne l'endpoint pour Toyota 2023"""
    print("🔍 TEST EXACT - Toyota 2023")
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
        # Test exact de ce qui est appelé dans l'interface
        response = client.get('/api/vehicle-models/?make=TOYOTA&year=2023')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                models = data.get('models', [])
                model_names = [model['name'] for model in models]
                model_names.sort()  # Tri alphabétique
                
                print(f"✅ {len(models)} modèles récupérés pour Toyota 2023")
                print(f"📋 Liste complète des modèles (triés alphabétiquement):")
                
                for i, model in enumerate(model_names, 1):
                    marker = "🎯" if 'bZ4X' in model or 'BZ4X' in model else "  "
                    print(f"   {i:2d}. {marker} {model}")
                
                # Vérification spécifique du bZ4X
                bz4x_found = [model for model in model_names if 'bZ4X' in model or 'BZ4X' in model]
                if bz4x_found:
                    print(f"\n🎉 bZ4X TROUVÉ: {bz4x_found}")
                    print(f"   Position dans la liste: {model_names.index(bz4x_found[0]) + 1}")
                else:
                    print(f"\n❌ bZ4X NON TROUVÉ dans la liste")
                    
                    # Chercher des modèles similaires
                    b_models = [model for model in model_names if model.upper().startswith('B')]
                    print(f"   Modèles commençant par B: {b_models}")
                    
                    z_models = [model for model in model_names if 'Z' in model.upper()]
                    print(f"   Modèles contenant Z: {z_models}")
                
                return model_names
            else:
                print(f"❌ Réponse success=False: {data.get('message')}")
                return []
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def test_without_year():
    """Test sans spécifier d'année"""
    print(f"\n🔍 TEST SANS ANNÉE - Toyota (tous modèles)")
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
        response = client.get('/api/vehicle-models/?make=TOYOTA')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                models = data.get('models', [])
                model_names = [model['name'] for model in models]
                model_names.sort()
                
                print(f"✅ {len(models)} modèles récupérés pour Toyota (sans année)")
                
                # Chercher bZ4X
                bz4x_found = [model for model in model_names if 'bZ4X' in model or 'BZ4X' in model]
                if bz4x_found:
                    print(f"🎉 bZ4X TROUVÉ: {bz4x_found}")
                else:
                    print(f"❌ bZ4X NON TROUVÉ")
                
                # Afficher les 20 premiers modèles
                print(f"📋 Les 20 premiers modèles:")
                for i, model in enumerate(model_names[:20], 1):
                    print(f"   {i:2d}. {model}")
                
                return model_names
            else:
                print(f"❌ Réponse success=False: {data.get('message')}")
                return []
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def main():
    """Fonction principale"""
    print("🧪 DIAGNOSTIC RAPIDE - TOYOTA BZ4X")
    print("🏢 Garage MarKev - Vérification Interface")
    print("=" * 80)
    
    # Test avec année 2023
    models_2023 = test_exact_toyota_2023()
    
    # Test sans année
    models_all = test_without_year()
    
    print("\n" + "=" * 80)
    print("📊 DIAGNOSTIC")
    print("=" * 80)
    
    if models_2023:
        has_bz4x_2023 = any('bZ4X' in model or 'BZ4X' in model for model in models_2023)
        print(f"🔍 Toyota 2023: {len(models_2023)} modèles, bZ4X présent: {'✅ OUI' if has_bz4x_2023 else '❌ NON'}")
    
    if models_all:
        has_bz4x_all = any('bZ4X' in model or 'BZ4X' in model for model in models_all)
        print(f"🔍 Toyota (tous): {len(models_all)} modèles, bZ4X présent: {'✅ OUI' if has_bz4x_all else '❌ NON'}")
    
    print(f"\n💡 RECOMMANDATION:")
    print("   1. Saisissez '2023' dans le champ Année AVANT de sélectionner Toyota")
    print("   2. Puis sélectionnez Toyota dans Marque")
    print("   3. Le champ Modèle devrait se recharger avec les modèles 2023")
    print("   4. Cherchez 'bZ4X' au début de la liste")

if __name__ == "__main__":
    main()
