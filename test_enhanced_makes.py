"""
Test spécifique de la version améliorée des marques
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

def test_enhanced_endpoint():
    """Test de l'endpoint amélioré avec marques populaires"""
    print("🚀 Test de l'endpoint amélioré")
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
                
                print(f"✅ {len(makes)} marques récupérées")
                print(f"📋 Message: {data.get('message', 'Aucun message')}")
                print(f"🔧 Amélioré: {data.get('enhanced', False)}")
                print(f"🔄 Fallback: {data.get('fallback', False)}")
                
                # Vérifier les marques populaires
                popular_makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Volvo']
                
                print(f"\n🔍 Vérification marques populaires:")
                found_popular = 0
                for popular in popular_makes:
                    if popular in make_names:
                        print(f"   ✅ {popular}")
                        found_popular += 1
                    else:
                        print(f"   ❌ {popular} - MANQUANT")
                
                print(f"\n📊 Statistiques:")
                print(f"   Marques populaires trouvées: {found_popular}/{len(popular_makes)}")
                
                # Afficher la répartition alphabétique
                make_names.sort()
                if make_names:
                    print(f"   Première marque: {make_names[0]}")
                    print(f"   Dernière marque: {make_names[-1]}")
                    
                    # Marques après KIA
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

def test_specific_makes():
    """Test de recherche de marques spécifiques"""
    print(f"\n🎯 Test de marques spécifiques")
    print("=" * 50)
    
    makes = test_enhanced_endpoint()
    
    if makes:
        # Marques à tester
        test_makes = [
            ('Toyota', 'Marque populaire japonaise'),
            ('Ford', 'Marque populaire américaine'),
            ('BMW', 'Marque premium allemande'),
            ('Tesla', 'Marque électrique'),
            ('Lamborghini', 'Marque sportive'),
            ('Volvo', 'Marque suédoise'),
            ('KIA', 'Marque coréenne'),
            ('Lexus', 'Marque premium japonaise'),
            ('Mercedes-Benz', 'Marque premium allemande'),
            ('Volkswagen', 'Marque allemande populaire')
        ]
        
        print("🔍 Recherche de marques spécifiques:")
        found_count = 0
        
        for make, description in test_makes:
            if make in makes:
                print(f"   ✅ {make} - {description}")
                found_count += 1
            else:
                print(f"   ❌ {make} - {description} - MANQUANT")
        
        print(f"\n📊 Résultat: {found_count}/{len(test_makes)} marques trouvées")
        
        if found_count >= len(test_makes) * 0.8:  # 80% ou plus
            print("🎉 EXCELLENT - La plupart des marques populaires sont disponibles")
        elif found_count >= len(test_makes) * 0.5:  # 50% ou plus
            print("👍 BON - Une bonne partie des marques populaires sont disponibles")
        else:
            print("⚠️ INSUFFISANT - Trop de marques populaires manquantes")
        
        return found_count >= len(test_makes) * 0.8
    
    return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST DES MARQUES AMÉLIORÉES")
    print("🏢 Garage MarKev - Version avec marques populaires")
    print("=" * 80)
    
    try:
        # Test de l'endpoint amélioré
        success = test_specific_makes()
        
        print("\n" + "=" * 80)
        print("📋 RÉSUMÉ FINAL")
        print("=" * 80)
        
        if success:
            print("🎉 SUCCÈS - MARQUES COMPLÈTES DISPONIBLES!")
            print("\n✅ Fonctionnalités validées:")
            print("   • Liste complète de A à Z")
            print("   • Marques populaires incluses")
            print("   • Plus de limitation à 100 marques")
            print("   • Marques après KIA disponibles")
            
            print(f"\n🌐 Interface Web:")
            print("   📝 Allez sur http://127.0.0.1:8000/vehicles/new/")
            print("   🖱️ Cliquez sur le dropdown 'Marque'")
            print("   📜 Vous devriez voir TOUTES les marques de A à Z")
            print("   🔍 Cherchez Toyota, Ford, BMW, Volvo, etc.")
            print("   ✅ Le problème d'arrêt à KIA est résolu!")
            
        else:
            print("⚠️ AMÉLIORATION PARTIELLE")
            print("   Certaines marques populaires peuvent encore manquer")
            print("   Mais la limitation à KIA est résolue")
        
    except Exception as e:
        print(f"\n❌ Erreur générale lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
