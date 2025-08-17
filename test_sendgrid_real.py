"""
Test réel de l'envoi d'emails avec SendGrid
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markev_project.settings')
django.setup()

from django.core.mail import EmailMessage
from django.conf import settings

def test_sendgrid_real():
    """Test d'envoi réel d'email"""
    print("📧 Test d'envoi réel avec SendGrid")
    print("=" * 50)
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"SENDGRID_SANDBOX_MODE_IN_DEBUG: {getattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG', 'Non défini')}")
    
    api_key = settings.SENDGRID_API_KEY
    if api_key:
        print(f"SENDGRID_API_KEY: {'*' * 20}{api_key[-10:] if len(api_key) > 10 else api_key}")
    else:
        print("❌ SENDGRID_API_KEY non configurée")
        return False
    
    # Demander l'email de destination
    email_dest = input("\nEntrez votre adresse email pour le test : ").strip()
    if not email_dest:
        print("❌ Adresse email requise")
        return False
    
    try:
        # Créer un email de test
        subject = "Test SendGrid - Garage MarKev"
        message = f"""
Bonjour,

Ceci est un test d'envoi d'email depuis le système Garage MarKev.

Si vous recevez ce message, la configuration SendGrid fonctionne correctement !

Configuration actuelle :
- Backend : {settings.EMAIL_BACKEND}
- Expéditeur : {settings.DEFAULT_FROM_EMAIL}
- Mode sandbox : {getattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG', 'Non défini')}

Cordialement,
Système Garage MarKev
        """
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_dest],
        )
        
        print(f"\n🚀 Envoi de l'email de test à {email_dest}...")
        email.send()
        
        print("✅ Email envoyé avec succès !")
        print(f"📧 Vérifiez votre boîte de réception : {email_dest}")
        print("📧 Vérifiez aussi vos spams si vous ne le trouvez pas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi : {str(e)}")
        
        # Diagnostics supplémentaires
        if "403" in str(e):
            print("\n🔍 Diagnostic :")
            print("   L'erreur 403 indique généralement que l'adresse d'expédition")
            print("   n'est pas vérifiée dans SendGrid.")
            print("\n📋 Actions à effectuer :")
            print("   1. Connectez-vous à SendGrid Dashboard")
            print("   2. Allez dans Settings > Sender Authentication")
            print("   3. Vérifiez l'adresse Garage.MarKev@outlook.com")
            print("   4. Ou utilisez une adresse déjà vérifiée")
        
        return False

def main():
    """Fonction principale"""
    print("🧪 TEST RÉEL SENDGRID - GARAGE MARKEV")
    print("=" * 60)
    
    if test_sendgrid_real():
        print("\n🎉 Test terminé avec succès !")
    else:
        print("\n❌ Test échoué - vérifiez la configuration")

if __name__ == "__main__":
    main()
