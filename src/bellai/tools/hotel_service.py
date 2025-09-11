import json
from langchain.tools import tool

@tool
def get_hotel_info() -> str:
    """
    Récupère les informations générales de l'hôtel Oceania Paris Porte de Versailles.
    
    Retourne les données de base incluant :
    - Nom et classification de l'hôtel
    - Nombre total de chambres
    - Adresse complète
    - Informations de connexion Wi-Fi (SSID et mot de passe)
    
    Returns:
        str: JSON contenant toutes les informations de base de l'hôtel
    """
    hotel_data = {
        "nom": "Oceania Paris Porte de Versailles",
        "classification": "4 étoiles",
        "nombre_chambres": 250,
        "adresse": {
            "rue": "52 Rue d'Oradour-sur-Glane",
            "code_postal": "75015",
            "ville": "Paris",
            "pays": "France"
        },
        "wifi": {
            "disponible": True,
            "ssid": "Oceania_Hotel_WiFi",
            "mot_de_passe": "Oceania2025",
            "gratuit": True
        }
    }
    return json.dumps(hotel_data, ensure_ascii=False, indent=2)

@tool
def get_contact() -> str:
    """
    Fournit toutes les coordonnées de contact de l'hôtel.
    
    Inclut les moyens de communication disponibles :
    - Numéro de téléphone principal
    - Adresse email de contact
    - Adresse postale complète
    - Horaires de disponibilité du standard
    
    Returns:
        str: JSON avec les coordonnées complètes de l'hôtel
    """
    contact_data = {
        "telephone": "+33 1 56 09 09 09",
        "email": "oceania.paris@oceaniahotels.com",
        "adresse": {
            "complete": "52 Rue d'Oradour-sur-Glane, 75015 Paris",
            "rue": "52 Rue d'Oradour-sur-Glane",
            "code_postal": "75015",
            "ville": "Paris"
        },
        "horaires_standard": "24h/24, 7j/7"
    }
    return json.dumps(contact_data, ensure_ascii=False, indent=2)

@tool
def get_checkin_checkout() -> str:
    """
    Horaires officiels de check-in et check-out de l'hôtel.
    
    Détaille les créneaux horaires pour :
    - Heure de début et limite du check-in
    - Heure limite du check-out
    - Possibilités de check-in tardif ou check-out anticipé
    
    Returns:
        str: JSON avec les horaires d'arrivée et de départ
    """
    checkin_checkout_data = {
        "checkin": {
            "heure_debut": "15:00",
            "heure_limite": "23:30",
            "checkin_tardif": {
                "disponible": True,
                "procedure": "Contacter la réception"
            }
        },
        "checkout": {
            "heure_limite": "12:00",
            "checkout_express": {
                "disponible": True,
                "procedure": "Automatique avec carte enregistrée"
            }
        }
    }
    return json.dumps(checkin_checkout_data, ensure_ascii=False, indent=2)

@tool
def get_services_hours() -> str:
    """
    List et horaires détaillés de tous les services et équipements de l'hôtel.
    
    Couvre les horaires de :
    - Petit-déjeuner (différencié semaine/week-end)
    - Restaurant Le Patio (déjeuner et dîner)
    - Bar Le Patio
    - Spa, piscine, hammam et salle de sport
    - Service en chambre (room service)
    
    Returns:
        str: JSON avec tous les horaires par service et jour
    """
    services_data = {
        "petit_dejeuner": {
            "lieu": "Restaurant Le Patio",
            "type": "Buffet",
            "horaires": {
                "lundi_vendredi": {
                    "ouverture": "07:00",
                    "fermeture": "10:30"
                },
                "samedi_dimanche": {
                    "ouverture": "07:30",
                    "fermeture": "11:00"
                }
            }
        },
        "restaurant": {
            "nom": "Le Patio",
            "type": "Restaurant gastronomique",
            "horaires": {
                "lundi_vendredi": {
                    "dejeuner": "12:00 - 14:30",
                    "diner": "18:30 - 22:30"
                },
                "samedi_dimanche": {
                    "dejeuner": "Fermé",
                    "diner": "18:30 - 22:30"
                }
            }
        },
        "bar": {
            "nom": "Bar Le Patio",
            "horaires": {
                "lundi_vendredi": "10:00 - 00:00",
                "samedi_dimanche": "17:00 - 00:00"
            }
        },
        "spa_wellness": {
            "nom": "Espace Bien-être",
            "services": ["Spa", "Piscine", "Hammam", "Salle de sport"],
            "horaires": "10:30 - 23:00",
            "acces": "Clients de l'hôtel uniquement",
            "jours": "7j/7"
        },
        "room_service": {
            "horaires": "17:00 - 22:30",
            "jours": "7j/7",
            "zone_livraison": "Toutes les chambres"
        }
    }
    return json.dumps(services_data, ensure_ascii=False, indent=2)

@tool
def get_prices() -> str:
    """
    Tarification complète des services et prestations additionnelles.
    
    Inclut les prix pour :
    - Petit-déjeuner buffet (adultes et enfants)
    - Parking privé (tarif par nuit)
    - Animaux de compagnie (conditions et tarifs)
    - Services optionnels disponibles
    
    Returns:
        str: JSON avec tous les tarifs en euros
    """
    pricing_data = {
        "petit_dejeuner": {
            "type": "Buffet",
            "prix_adulte": 22.00,
            "prix_enfant": 22.00,
            "age_limite_enfant": "Aucune distinction",
            "inclus_dans_sejour": False
        },
        "parking": {
            "type": "Parking privé sur place",
            "prix_par_nuit": 31.00,
            "reservation_requise": True,
            "places_limitees": True
        },
    }
    return json.dumps(pricing_data, ensure_ascii=False, indent=2)

def get_hotel_tools():
    return [
        get_hotel_info,
        get_contact, 
        get_checkin_checkout,
        get_services_hours,
        get_prices,
    ]

__all__ = [
    "get_hotel_tools"
]
