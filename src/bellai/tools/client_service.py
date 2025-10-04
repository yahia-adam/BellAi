
import json
from datetime import datetime
from langchain.tools import tool

@tool
def get_current_time():
    """
        Retourne l'heure actuelle.
    """
    return datetime.now()

@tool
def get_client_profile() -> str:
    """
    Profil complet du client actuellement connecté ou recherché.
    
    Récupère depuis le système de gestion hôtelière :
    - Informations personnelles (nom, prénom)
    - Détails du séjour actuel (chambre, dates)
    
    Returns:
        str: JSON avec le profil client complet
    """
    client_data = {
        "identite": {
            "nom": "YAHIA",
            "prenom": "Adam",
            "titre": "M.",
            "id_client": "CLI_001_YAHIA_ADAM"
        },
        "sejour_actuel": {
            "chambre": "205",
            "nombre_nuits": 3,
            "date_checkin": "2024-09-01",
            "date_checkout": "2024-09-04"
        }
    }
    return json.dumps(client_data, ensure_ascii=False, indent=2)

@tool
def get_client_preferences() -> str:
    """
    Préférences personnalisées enregistrées pour améliorer l'expérience client.
    
    Stocke les préférences concernant :
    - Cuisine et restrictions alimentaires
    - Allergies et intolérances
    - Boissons préférées
    - Types de soins et massages
    - Langue de communication
    - Préférences de notification
    
    Returns:
        str: JSON avec toutes les préférences client
    """
    preferences_data = {
        "restauration": {
            "cuisine_favorite": "Cuisine française",
            "allergies": [],
            "restrictions_alimentaires": "Halal",
            "boisson_preferee": "Vin rouge",
        },
        "spa_wellness": {
            "massage_prefere": "Relaxant",
            "duree_preferee": "60 minutes",
            "intensite": "Moyenne"
        }
    }
    return json.dumps(preferences_data, ensure_ascii=False, indent=2)

@tool
def get_client_history() -> str:
    """
    Historique complet des services utilisés et habitudes du client.
    
    Analyse les données passées pour identifier :
    - Services récemment utilisés
    - Services favoris du client
    - Dernières commandes et achats
    - Score de satisfaction moyen
    - Fréquence d'utilisation des services
    
    Returns:
        str: JSON avec l'historique et les statistiques client
    """
    history_data = {
        "services_recents": [
            {
                "service": "room_service",
                "date": "2024-09-01",
                "details": "Menu gastronomique"
            },
            {
                "service": "massage",
                "date": "2024-08-15", 
                "details": "Massage relaxant 60min"
            },
            {
                "service": "conciergerie",
                "date": "2024-08-15",
                "details": "Taxie, aeroport"
            }
        ],
        "services_favoris": [
            {
                "service": "spa",
                "frequence": "Très élevée",
                "derniere_utilisation": "2024-08-15"
            },
            {
                "service": "room_service", 
                "frequence": "Élevée",
                "derniere_utilisation": "2024-09-01"
            }
        ],
        "satisfaction": {
            "score_moyen": 4.8,
            "sur": 5,
            "nombre_evaluations": 12
        },
        "statistiques": {
            "total_sejours": 8,
            "nuits_totales": 24,
            "depense_moyenne_sejour": 850.00
        }
    }
    return json.dumps(history_data, ensure_ascii=False, indent=2)

@tool
def get_client_reservations() -> str:
    """
    Toutes les réservations actuelles et historique des réservations du client.
    
    Gère les réservations pour tous les services :
    - Réservations en cours (confirmées et à venir)
    - Réservations passées (avec détails)
    - Statut de chaque réservation
    - Détails spécifiques par type de service
    
    Returns:
        str: JSON avec toutes les réservations du client
    """
    reservations_data = {
        "reservations_en_cours": [
            {
                "id": "RES_SPA_001",
                "service": "spa",
                "type": "Massage relaxant",
                "date": "2024-09-02",
                "heure": "15:00",
                "duree": "60 minutes",
                "statut": "Confirmée",
                "prix": 110.00
            },
            {
                "id": "RES_REST_001", 
                "service": "restaurant",
                "date": "2024-09-02",
                "heure": "20:00",
                "nombre_personnes": 2,
                "table": "Terrasse",
                "statut": "Confirmée",
                "demandes_speciales": "Vue dégagée"
            }
        ],
        "reservations_passees": [
            {
                "id": "RES_ROOM_001",
                "service": "room_service",
                "date": "2024-09-01", 
                "heure": "21:30",
                "commande": "Menu gastronomique",
                "statut": "Complétée",
                "montant": 180.50
            }
        ],
        "reservations_recurrentes": [],
        "total_reservations_actives": 2
    }
    return json.dumps(reservations_data, ensure_ascii=False, indent=2)

@tool
def get_client_stay_details() -> str:
    """
    Détails exhaustifs du séjour en cours du client.
    
    Compile toutes les informations du séjour :
    - Détails de la chambre assignée
    - Dates et heures précises d'arrivée/départ
    - Nombre d'occupants déclarés
    - Services inclus dans le forfait
    - Demandes spéciales accordées
    - Statut du séjour
    
    Returns:
        str: JSON avec tous les détails du séjour actuel
    """
    stay_data = {
        "chambre": {
            "numero": "205",
            "type": "Suite Supérieure",
            "etage": 2,
            "superficie": "45 m²",
            "vue": "Ville/Champs-Élysées",
            "equipements": [
                "Balcon privé",
                "Minibar",
                "Coffre-fort",
                "Climatisation",
                "TV écran plat"
            ]
        },
        "sejour": {
            "date_checkin": "2024-09-01",
            "heure_checkin": "15:00",
            "date_checkout": "2024-09-04", 
            "heure_checkout": "11:00",
            "nombre_nuits": 3,
            "nombre_occupants": 2
        },
        "services_inclus": [
            "Wi-Fi gratuit",
            "Accès spa et piscine",
            "Petit-déjeuner buffet",
            "Service de conciergerie"
        ],
        "demandes_speciales": [
            {
                "demande": "Vue sur Champs-Élysées",
                "statut": "Accordée"
            },
            {
                "demande": "Étage élevé",
                "statut": "Accordée"
            }
        ],
        "statut_sejour": "En cours"
    }
    return json.dumps(stay_data, ensure_ascii=False, indent=2)

@tool
def get_client_billing() -> str:
    """
    Facturation complète et détaillée du séjour du client.
    
    Calcule et présente :
    - Montant total de la facture actuelle
    - Détail de tous les services facturés
    - Dates et montants de chaque prestation
    - Mode de paiement enregistré
    - Options de checkout express
    - Historique des paiements
    
    Returns:
        str: JSON avec toute la facturation du client
    """
    billing_data = {
        "facture_actuelle": {
            "montant_total": 850.50,
            "devise": "EUR",
            "statut": "En cours",
            "derniere_mise_a_jour": "2024-09-02T10:30:00"
        },
        "detail_services": [
            {
                "service": "Hébergement",
                "description": "Suite Supérieure - 3 nuits",
                "montant_unitaire": 150.00,
                "quantite": 3,
                "montant_total": 450.00,
                "dates": "2024-09-01 au 2024-09-04"
            },
            {
                "service": "Restaurant",
                "description": "Dîner gastronomique",
                "montant_total": 180.50,
                "date": "2024-09-01"
            },
            {
                "service": "Spa",
                "description": "Massage relaxant 60min (réservé)",
                "montant_total": 110.00,
                "date": "2024-09-02"
            },
            {
                "service": "Minibar",
                "description": "Consommations",
                "montant_total": 35.00,
                "date": "2024-09-01"
            },
            {
                "service": "Parking",
                "description": "Parking privé - 3 jours",
                "montant_unitaire": 25.00,
                "quantite": 3,
                "montant_total": 75.00
            }
        ],
        "paiement": {
            "mode_paiement": "Carte de crédit enregistrée",
            "carte_masquee": "**** **** **** 1234",
            "checkout_express": True,
            "facturation_automatique": True
        },
        "taxes": {
            "taxe_sejour": {
                "montant_par_nuit": 8.00,
                "nombre_nuits": 3,
                "total": 24.00
            }
        }
    }
    return json.dumps(billing_data, ensure_ascii=False, indent=2)

def get_client_tools():
    return [
        get_client_profile,
        get_client_preferences, 
        get_client_history,
        get_client_reservations,
        get_client_stay_details,
        get_client_billing
    ]

__all__ = [
    "get_client_tools",
]