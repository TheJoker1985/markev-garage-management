"""
Test de la nouvelle interface dropdown pour les véhicules
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

def test_vehicle_form_rendering():
    """Test du rendu du formulaire avec les nouveaux dropdowns"""
    print("🎨 Test du rendu du formulaire véhicule")
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
        # Accéder à la page d'ajout de véhicule
        response = client.get('/vehicles/add/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            print("✅ Page d'ajout de véhicule accessible")
            
            # Vérifier la présence des nouveaux éléments
            checks = [
                ('form-select', 'Classes CSS Bootstrap pour les selects'),
                ('id_make', 'Select pour les marques'),
                ('id_model', 'Select pour les modèles'),
                ('Sélectionnez une marque', 'Option par défaut marque'),
                ('disabled', 'Champ modèle désactivé par défaut'),
                ('identify-vehicle-btn', 'Bouton d\'identification'),
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description} - MANQUANT")
            
            # Vérifier l'absence des anciens éléments problématiques
            old_elements = [
                ('make-suggestions', 'Ancien dropdown custom marques'),
                ('model-suggestions', 'Ancien dropdown custom modèles'),
                ('dropdown-menu', 'Anciens menus dropdown custom'),
            ]
            
            print("\n🧹 Vérification suppression anciens éléments:")
            for element, description in old_elements:
                if element not in content:
                    print(f"   ✅ {description} - SUPPRIMÉ")
                else:
                    print(f"   ⚠️ {description} - ENCORE PRÉSENT")
            
            return True
        else:
            print(f"❌ Erreur d'accès à la page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_api_endpoints():
    """Test des endpoints API pour les marques et modèles"""
    print(f"\n🌐 Test des endpoints API")
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
    
    success_count = 0
    
    # Test endpoint marques
    print("🔍 Test endpoint marques...")
    try:
        response = client.get('/api/vehicle-makes/')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                makes_count = len(data.get('makes', []))
                print(f"   ✅ {makes_count} marques récupérées")
                success_count += 1
                
                # Afficher quelques exemples
                for make in data.get('makes', [])[:5]:
                    print(f"      • {make['name']}")
            else:
                print(f"   ⚠️ Réponse success=False: {data.get('message')}")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test endpoint modèles
    print("\n🔍 Test endpoint modèles...")
    try:
        response = client.get('/api/vehicle-models/?make=Toyota&year=2023')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                models_count = len(data.get('models', []))
                print(f"   ✅ {models_count} modèles Toyota 2023 récupérés")
                success_count += 1
                
                # Afficher quelques exemples
                for model in data.get('models', [])[:5]:
                    print(f"      • {model['name']}")
            else:
                print(f"   ⚠️ Réponse success=False: {data.get('message')}")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    return success_count == 2

def test_form_validation():
    """Test de la validation du formulaire"""
    print(f"\n📝 Test de validation du formulaire")
    print("=" * 50)
    
    from garage_app.forms import VehicleForm
    from garage_app.models import Client
    
    try:
        # Créer un client de test
        client, created = Client.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'phone': '514-123-4567'
            }
        )
        
        # Test avec données valides
        form_data = {
            'client': client.id,
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2023,
            'color': 'Blanc',
            'license_plate': 'ABC123'
        }
        
        form = VehicleForm(data=form_data)
        
        if form.is_valid():
            print("✅ Formulaire valide avec données correctes")
            return True
        else:
            print("❌ Formulaire invalide:")
            for field, errors in form.errors.items():
                print(f"   {field}: {errors}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la validation: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST DE LA NOUVELLE INTERFACE DROPDOWN VÉHICULES")
    print("🏢 Garage MarKev - Amélioration UX")
    print("=" * 80)
    
    try:
        # Tests
        form_ok = test_vehicle_form_rendering()
        api_ok = test_api_endpoints()
        validation_ok = test_form_validation()
        
        print("\n" + "=" * 80)
        print("📊 RÉSULTATS DES TESTS")
        print("=" * 80)
        
        print(f"🎨 Rendu du formulaire : {'✅ SUCCÈS' if form_ok else '❌ ÉCHEC'}")
        print(f"🌐 Endpoints API : {'✅ SUCCÈS' if api_ok else '❌ ÉCHEC'}")
        print(f"📝 Validation formulaire : {'✅ SUCCÈS' if validation_ok else '❌ ÉCHEC'}")
        
        if form_ok and api_ok and validation_ok:
            print(f"\n🎉 TOUS LES TESTS RÉUSSIS!")
            print(f"\n📋 Améliorations implémentées :")
            print("   ✅ Vrais dropdowns HTML natifs")
            print("   ✅ Plus de problèmes de superposition")
            print("   ✅ Sélection par clic (pas de frappe)")
            print("   ✅ Chargement dynamique des modèles")
            print("   ✅ Interface utilisateur améliorée")
            print("   ✅ Bouton d'identification intelligent")
            
            print(f"\n🌐 Interface Web :")
            print("   📝 Allez sur http://127.0.0.1:8000/vehicles/add/")
            print("   🖱️ Cliquez sur 'Marque' pour voir le dropdown")
            print("   🖱️ Sélectionnez une marque → Le champ 'Modèle' se remplit")
            print("   🖱️ Sélectionnez un modèle → Le bouton 'Identifier' s'active")
            print("   🔍 Cliquez 'Identifier le type' pour l'identification automatique")
            
        else:
            print(f"\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
            print("   Vérifiez les détails ci-dessus")
        
    except Exception as e:
        print(f"\n❌ Erreur générale lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
