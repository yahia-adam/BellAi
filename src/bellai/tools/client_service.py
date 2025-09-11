from langchain.tools import tool

@tool
def get_client_profile() -> str:
    """Récupère le profil complet du client depuis l'API dashboard"""
    
    client_data = {
        "nom": "YAHIA",
        "prenom": "Adam", 
        "chambre": "205",
        "statut": "VIP",
        "sejour_type": "business",
        "nombre_nuits": 3,
        "checkin": "2024-09-01",
        "checkout": "2024-09-04"
    }
    
    return f"{client_data['prenom']} {client_data['nom']}, Chambre {client_data['chambre']}, Statut {client_data['statut']}, Séjour {client_data['sejour_type']}"

@tool
def get_client_preferences() -> str:
    """Récupère les préférences du client"""
    
    # En production: appel API dashboard
    preferences = {
        "restaurant_favori": "cuisine française",
        "allergies": "aucune",
        "boisson_preferee": "vin rouge",
        "massage_prefere": "relaxant",
        "langue": "français",
        "notifications": True
    }
    
    formatted = ", ".join([f"{k}: {v}" for k, v in preferences.items()])
    return formatted

@tool
def get_client_history() -> str:
    """Historique des services utilisés par le client"""
    
    # En production: historique depuis base de données
    history = {
        "derniers_services": ["room service", "massage", "conciergerie"],
        "services_favoris": ["spa", "room service"],
        "derniere_commande": "menu gastronomique hier soir",
        "satisfaction_moyenne": 4.8
    }

    services = ", ".join(history["derniers_services"])
    return f"Services récents: {services}. Satisfaction: {history['satisfaction_moyenne']}/5"

@tool
def get_client_reservations() -> str:
    """Réservations actuelles et futures du client"""
    
    reservations = {
        "en_cours": [
            {"service": "spa", "date": "2024-09-02", "heure": "15:00", "type": "massage relaxant"},
            {"service": "restaurant", "date": "2024-09-02", "heure": "20:00", "table": "terrasse"}
        ],
        "passees": [
            {"service": "room service", "date": "2024-09-01", "heure": "21:30", "commande": "menu gastronomique"}
        ]
    }
    
    current_reservations = []
    for res in reservations["en_cours"]:
        current_reservations.append(f"{res['service']} le {res['date']} à {res['heure']}")
    
    if current_reservations:
        return f"Réservations actuelles: {', '.join(current_reservations)}"
    else:
        return "Aucune réservation en cours"

@tool
def get_client_stay_details() -> str:
    """Détails du séjour actuel"""

    stay_details = {
        "chambre": "205",
        "type_chambre": "Suite Supérieure",
        "checkin": "2024-09-01 15:00",
        "checkout": "2024-09-04 11:00", 
        "nombre_occupants": 2,
        "services_inclus": ["petit-déjeuner", "wifi", "accès spa"],
        "demandes_speciales": ["vue sur Champs-Élysées", "étage élevé"]
    }
    
    return f"Chambre {stay_details['chambre']} ({stay_details['type_chambre']}), Check-out {stay_details['checkout']}, Services inclus: {', '.join(stay_details['services_inclus'])}"

@tool
def get_client_billing() -> str:
    """Informations de facturation du client"""

    billing = {
        "facture_actuelle": 850.50,
        "services_factures": [
            {"service": "chambre", "montant": 450.00, "periode": "3 nuits"},
            {"service": "restaurant", "montant": 180.50, "date": "hier soir"},
            {"service": "spa", "montant": 110.00, "date": "réservé pour demain"},
            {"service": "minibar", "montant": 35.00, "date": "hier"},
            {"service": "parking", "montant": 75.00, "periode": "3 jours"}
        ],
        "mode_paiement": "carte de crédit enregistrée",
        "checkout_express": True
    }
    
    return f"Facture actuelle: {billing['facture_actuelle']}€. Paiement: {billing['mode_paiement']}. Checkout express activé."

__all__ = [
    "get_client_profile",
    "get_client_preferences",
    "get_client_history",
    "get_client_reservations",
    "get_client_stay_details",
    "get_client_billing"
]