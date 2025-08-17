"""
Services pour l'intégration avec des APIs externes et la logique métier
"""
import requests
import logging
from typing import Optional, Dict, List
from django.conf import settings
from .models import VehicleType, Vehicle

logger = logging.getLogger(__name__)


class NHTSAService:
    """Service pour intégrer l'API NHTSA et identifier automatiquement les types de véhicules"""
    
    BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"
    
    # Mapping des Body Class NHTSA vers nos types de véhicules
    BODY_CLASS_MAPPING = {
        'SUV': ['VUS', 'SUV'],
        'Sedan': ['Berline', 'Sedan'],
        'Coupe': ['Coupé', 'Coupe'],
        'Hatchback': ['Berline', 'Hatchback'],
        'Wagon': ['Familiale', 'Wagon'],
        'Pickup': ['Pickup', 'Camionnette'],
        'Van': ['Fourgonnette', 'Van'],
        'Convertible': ['Cabriolet', 'Convertible'],
        'Truck': ['Camion', 'Truck'],
        'Motorcycle': ['Moto', 'Motorcycle'],
    }
    
    @classmethod
    def get_vehicle_info(cls, make: str, model: str, year: int) -> Optional[Dict]:
        """
        Récupère les informations d'un véhicule depuis l'API NHTSA

        Args:
            make: Marque du véhicule
            model: Modèle du véhicule
            year: Année du véhicule

        Returns:
            Dict avec les informations du véhicule ou None si erreur
        """
        try:
            # Approche 1: Essayer avec l'API de décodage VIN partiel
            url = f"{cls.BASE_URL}/DecodeVinValuesExtended/5{make[:2].upper()}{model[:3].upper()}{str(year)[-2:]}"
            params = {'format': 'json'}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('Count', 0) > 0:
                result = data['Results'][0]
                body_class = result.get('BodyClass', '').strip()

                if body_class:
                    return {
                        'make': result.get('Make', make),
                        'model': result.get('Model', model),
                        'year': year,
                        'body_class': body_class,
                        'vehicle_type': result.get('VehicleType', ''),
                    }

            # Approche 2: Utiliser une base de données locale basée sur les modèles connus
            return cls._get_vehicle_info_from_local_db(make, model, year)

        except requests.RequestException as e:
            logger.warning(f"API NHTSA non disponible, utilisation de la base locale: {e}")
            return cls._get_vehicle_info_from_local_db(make, model, year)
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'identification du véhicule: {e}")
            return cls._get_vehicle_info_from_local_db(make, model, year)
    
    @classmethod
    def _get_vehicle_info_from_local_db(cls, make: str, model: str, year: int) -> Optional[Dict]:
        """
        Base de données locale pour identifier les types de véhicules
        basée sur les modèles connus
        """
        # Base de données locale des modèles et leurs types
        VEHICLE_DATABASE = {
            'toyota': {
                'camry': 'Sedan',
                'corolla': 'Sedan',
                'rav4': 'SUV',
                'highlander': 'SUV',
                'prius': 'Hatchback',
                'tacoma': 'Pickup',
                'tundra': 'Pickup',
                'sienna': 'Van',
                '4runner': 'SUV',
                'sequoia': 'SUV',
                'avalon': 'Sedan',
                'yaris': 'Hatchback',
                'c-hr': 'SUV',
                'venza': 'SUV',
            },
            'honda': {
                'civic': 'Sedan',
                'accord': 'Sedan',
                'cr-v': 'SUV',
                'pilot': 'SUV',
                'fit': 'Hatchback',
                'ridgeline': 'Pickup',
                'odyssey': 'Van',
                'hr-v': 'SUV',
                'passport': 'SUV',
                'insight': 'Sedan',
            },
            'ford': {
                'f-150': 'Pickup',
                'f-250': 'Pickup',
                'f-350': 'Pickup',
                'escape': 'SUV',
                'explorer': 'SUV',
                'expedition': 'SUV',
                'mustang': 'Coupe',
                'focus': 'Sedan',
                'fusion': 'Sedan',
                'edge': 'SUV',
                'ranger': 'Pickup',
                'bronco': 'SUV',
                'transit': 'Van',
            },
            'chevrolet': {
                'silverado': 'Pickup',
                'equinox': 'SUV',
                'tahoe': 'SUV',
                'suburban': 'SUV',
                'malibu': 'Sedan',
                'impala': 'Sedan',
                'camaro': 'Coupe',
                'corvette': 'Coupe',
                'traverse': 'SUV',
                'colorado': 'Pickup',
                'blazer': 'SUV',
            },
            'nissan': {
                'altima': 'Sedan',
                'sentra': 'Sedan',
                'rogue': 'SUV',
                'pathfinder': 'SUV',
                'murano': 'SUV',
                'frontier': 'Pickup',
                'titan': 'Pickup',
                'armada': 'SUV',
                'kicks': 'SUV',
                'versa': 'Sedan',
                '370z': 'Coupe',
                'maxima': 'Sedan',
            }
        }

        make_lower = make.lower()
        model_lower = model.lower().replace(' ', '-')

        if make_lower in VEHICLE_DATABASE:
            make_models = VEHICLE_DATABASE[make_lower]
            if model_lower in make_models:
                body_class = make_models[model_lower]
                return {
                    'make': make,
                    'model': model,
                    'year': year,
                    'body_class': body_class,
                    'vehicle_type': body_class,
                }

        # Si pas trouvé, essayer de deviner basé sur le nom du modèle
        model_indicators = {
            'SUV': ['suv', 'crossover', 'cx', 'rav', 'cr-v', 'escape', 'rogue', 'equinox'],
            'Pickup': ['pickup', 'truck', 'f-150', 'silverado', 'ram', 'tacoma', 'frontier'],
            'Sedan': ['sedan', 'camry', 'accord', 'altima', 'malibu', 'fusion'],
            'Coupe': ['coupe', 'mustang', 'camaro', 'corvette', '370z'],
            'Van': ['van', 'minivan', 'odyssey', 'sienna', 'caravan'],
            'Hatchback': ['hatch', 'fit', 'yaris', 'prius']
        }

        for body_type, indicators in model_indicators.items():
            for indicator in indicators:
                if indicator in model_lower:
                    return {
                        'make': make,
                        'model': model,
                        'year': year,
                        'body_class': body_type,
                        'vehicle_type': body_type,
                    }

        logger.warning(f"Type de véhicule non identifié pour {make} {model} {year}")
        return None
    
    @classmethod
    def identify_vehicle_type(cls, vehicle: Vehicle) -> Optional[VehicleType]:
        """
        Identifie automatiquement le type d'un véhicule en utilisant l'API NHTSA
        
        Args:
            vehicle: Instance du véhicule à identifier
            
        Returns:
            VehicleType correspondant ou None si non trouvé
        """
        # Récupérer les infos depuis l'API NHTSA
        vehicle_info = cls.get_vehicle_info(vehicle.make, vehicle.model, vehicle.year)
        
        if not vehicle_info:
            return None
        
        body_class = vehicle_info.get('body_class', '').strip()
        
        if not body_class:
            return None
        
        # Chercher un VehicleType correspondant
        return cls._find_matching_vehicle_type(body_class)
    
    @classmethod
    def _find_matching_vehicle_type(cls, body_class: str) -> Optional[VehicleType]:
        """
        Trouve le VehicleType correspondant au Body Class NHTSA
        """
        try:
            # Chercher d'abord dans les correspondances JSON des VehicleType existants
            vehicle_types = VehicleType.objects.filter(is_active=True)
            
            for vt in vehicle_types:
                if body_class in vt.nhtsa_body_classes:
                    return vt
            
            # Si pas trouvé, utiliser le mapping par défaut
            for nhtsa_class, our_types in cls.BODY_CLASS_MAPPING.items():
                if nhtsa_class.lower() in body_class.lower():
                    # Chercher si un de nos types existe
                    for our_type in our_types:
                        try:
                            return VehicleType.objects.get(name=our_type, is_active=True)
                        except VehicleType.DoesNotExist:
                            continue
            
            logger.warning(f"Aucun type de véhicule trouvé pour Body Class: {body_class}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche du type de véhicule: {e}")
            return None
    
    @classmethod
    def auto_identify_and_update_vehicle(cls, vehicle: Vehicle) -> bool:
        """
        Identifie automatiquement et met à jour le type d'un véhicule
        
        Args:
            vehicle: Véhicule à mettre à jour
            
        Returns:
            True si mis à jour avec succès, False sinon
        """
        try:
            vehicle_type = cls.identify_vehicle_type(vehicle)
            
            if vehicle_type:
                vehicle.vehicle_type = vehicle_type
                vehicle.auto_identified_type = True
                vehicle.save()
                
                logger.info(f"Type de véhicule identifié automatiquement: {vehicle} -> {vehicle_type}")
                return True
            
            logger.warning(f"Impossible d'identifier automatiquement le type pour: {vehicle}")
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour automatique du véhicule {vehicle}: {e}")
            return False


class InventoryConsumptionService:
    """Service pour gérer la consommation automatique d'inventaire"""
    
    @classmethod
    def consume_inventory_for_invoice(cls, invoice):
        """
        Consomme automatiquement l'inventaire pour une facture
        
        Args:
            invoice: Instance de la facture
        """
        from .models import ServiceConsumption, InventoryItem
        
        if not invoice.vehicle or not invoice.vehicle.vehicle_type:
            logger.warning(f"Impossible de consommer l'inventaire pour la facture {invoice.invoice_number}: véhicule ou type manquant")
            return
        
        vehicle_type = invoice.vehicle.vehicle_type
        
        # Parcourir tous les services de la facture
        for invoice_item in invoice.invoice_items.filter(item_type='service'):
            if not invoice_item.service:
                continue
            
            # Chercher les règles de consommation pour ce service et type de véhicule
            consumption_rules = ServiceConsumption.objects.filter(
                service=invoice_item.service,
                vehicle_type=vehicle_type,
                is_active=True
            )
            
            for rule in consumption_rules:
                cls._apply_consumption_rule(rule, 1)  # Une seule unité par ligne de facture
    
    @classmethod
    def _apply_consumption_rule(cls, rule, service_quantity: int = 1):
        """
        Applique une règle de consommation à l'inventaire
        """
        try:
            inventory_item = rule.inventory_item
            consumption_amount = rule.consumption_rate * service_quantity
            
            if inventory_item.quantity_in_stock >= consumption_amount:
                inventory_item.quantity_in_stock -= consumption_amount
                inventory_item.save()
                
                logger.info(f"Inventaire consommé: {inventory_item.name} - {consumption_amount} {rule.unit}")
            else:
                logger.warning(f"Stock insuffisant pour {inventory_item.name}: {inventory_item.quantity_in_stock} < {consumption_amount}")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'application de la règle de consommation {rule}: {e}")
