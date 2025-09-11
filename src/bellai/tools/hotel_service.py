from langchain.tools import tool

@tool
def get_hotel_info() -> str:
    """Informations de base de l'hôtel Oceania Paris Porte de Versailles."""
    return (
        "Oceania Paris Porte de Versailles, hôtel 4 étoiles, 250 chambres. "
        "Adresse : 52 Rue d'Oradour-sur-Glane, 75015 Paris. "
        "Wi-Fi gratuit disponible pour les clients. "
        "Nom du réseau (SSID) : Oceania_Hotel_WiFi | Mot de passe : Oceania2025"
    )

@tool
def get_services_hours() -> str:
    """Horaires des principaux services (restaurant, petit-déjeuner, spa, piscine, bar, room service)."""
    services = {
        "Petit-déjeuner (jours de semaine)": "7 h – 10 h 30",
        "Petit-déjeuner (week-ends)": "7 h 30 – 11 h",
        "Restaurant Le Patio (lun-ven)": "12 h – 14 h 30 et 18 h 30 – 22 h 30",
        "Restaurant Le Patio (week-ends)": "18 h 30 – 22 h 30",
        "Bar Le Patio (lun-ven)": "10 h – minuit",
        "Bar Le Patio (week-ends)": "17 h – minuit",
        "Spa / piscine / hammam / gym (guests only)": "10 h 30 – 23 h",
        "Room service": "17 h – 22 h 30",
    }
    lines = [f"{service}: {hours}" for service, hours in services.items()]
    return " | ".join(lines)

@tool
def get_prices() -> str:
    """Tarifs approximatifs des prestations principales."""
    return (
        "Petit-déjeuner buffet (par adulte ou enfant) : environ 22 € | "
        "Parking privé sur place : 30–32 €/nuit (selon source) | "
        "Animaux de compagnie : 20 €/nuit (1 animal par chambre) | "
        "Taxe de séjour : environ 8 € par personne/nuit."
    )

@tool
def get_contact() -> str:
    """Coordonnées de l'hôtel."""
    return (
        "Téléphone : +33 1 56 09 09 09 | Email : oceania.paris@oceaniahotels.com | "
        "Adresse : 52 Rue d'Oradour-sur-Glane, 75015 Paris."
    )

@tool
def get_checkin_checkout() -> str:
    """Horaires de check-in et check-out."""
    return "Check-in à partir de 15 h (jusqu’à 23 h30 environ) | Check-out jusqu’à 12 h (ou 11 h selon sources)."

___all__ = [
    "get_hotel_info",
    "get_services_hours",
    "get_prices",
    "get_contact",
    "get_checkin_checkout"
]
