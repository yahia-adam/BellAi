import os
import json
import requests
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

GOOGLE_ROUTE_API = os.getenv("GOOGLE_ROUTE_API")

@tool
def get_route(origin: str, destination: str, travel_mode="TRANSIT", departure_time=None, vehicle_type="car"):
    """
    Récupère l'itinéraire et retourne une description formatée.
    
    Args:
        origin (str): Adresse de départ (ex: "Tour Eiffel, Paris" ou "1 Rue de Rivoli, 75001 Paris")
        destination (str): Adresse d'arrivée (ex: "Arc de Triomphe, Paris")
        travel_mode: "TRANSIT", "WALK", "DRIVE", "BICYCLE"
        departure_time: datetime, timedelta, string ISO ou None (défaut: maintenant + 1 min)
        vehicle_type: "car" ou "taxi" (juste pour l'affichage si DRIVE)
    
    Returns:
        str: Description formatée de l'itinéraire ou message d'erreur
    """
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    
    # FieldMask adapté selon le mode
    if travel_mode == "TRANSIT":
        field_mask = "routes.duration,routes.distanceMeters,routes.legs.steps,routes.legs.steps.transitDetails,routes.legs.steps.transitDetails.stopDetails,routes.legs.steps.transitDetails.localizedValues,routes.legs.steps.travelMode,routes.legs.steps.distanceMeters,routes.legs.steps.staticDuration,routes.legs.steps.navigationInstruction,routes.legs.steps.localizedValues"
    else:
        field_mask = "routes.duration,routes.distanceMeters,routes.legs.steps,routes.legs.steps.travelMode,routes.legs.steps.distanceMeters,routes.legs.steps.staticDuration,routes.legs.steps.navigationInstruction,routes.legs.steps.localizedValues,routes.polyline"
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'X-Goog-Api-Key': GOOGLE_ROUTE_API,
        'X-Goog-FieldMask': field_mask
    }
    
    data = {
        'origin': {
            'address': origin
        },
        'destination': {
            'address': destination
        },
        'travelMode': travel_mode
    }

    if travel_mode == "TRANSIT":
        data['transitPreferences'] = {
            'allowedTravelModes': ['BUS', 'SUBWAY', 'TRAIN', "LIGHT_RAIL"]
        }
        if departure_time:
            data['departureTime'] = departure_time

    elif travel_mode == "DRIVE":
        data['routingPreference'] = 'TRAFFIC_AWARE'
        if departure_time:
            data['departureTime'] = departure_time
    try:
        r = requests.post(url, headers=headers, data=json.dumps(data), timeout=10).json()

        # Vérifier s'il y a une erreur
        if 'error' in r:
            return f"❌ Erreur: {r['error']['message']}"

        # Construire la string de résultat
        result = []

        route = r['routes'][0]
        leg = route['legs'][0]

        # En-tête
        distance_km = route['distanceMeters'] / 1000
        duree_min = int(route['duration'].replace('s', '')) // 60

        # Emoji et texte selon le mode
        if travel_mode == "WALK":
            mode_emoji = "🚶"
            mode_text = "À PIED"
        elif travel_mode == "TRANSIT":
            mode_emoji = "🚇"
            mode_text = "TRANSPORT EN COMMUN"
        elif travel_mode == "BICYCLE":
            mode_emoji = "🚴"
            mode_text = "VÉLO"
        elif travel_mode == "DRIVE":
            if vehicle_type == "taxi":
                mode_emoji = "🚕"
                mode_text = "TAXI"
            else:
                mode_emoji = "🚗"
                mode_text = "VOITURE"
        else:
            mode_text = travel_mode
            mode_emoji = ""

        result.append(f"{mode_emoji} Mode: {mode_text}")
        result.append(f"📍 Distance totale: {distance_km:.1f} km")
        result.append(f"⏱️  Durée totale: {duree_min} minutes")
        result.append(f"\n{'='*60}")
        result.append("ITINÉRAIRE DÉTAILLÉ")
        result.append(f"{'='*60}\n")

        # Parcourir les étapes
        for i, step in enumerate(leg['steps'], 1):
            mode = step.get('travelMode', 'UNKNOWN')

            # Récupérer distance et durée de manière sécurisée
            distance = step.get('localizedValues', {}).get('distance', {}).get('text', 'N/A')
            duree = step.get('localizedValues', {}).get('staticDuration', {}).get('text', 'N/A')

            if mode == 'WALK':
                # Récupérer l'instruction de manière sécurisée
                instruction = step.get('navigationInstruction', {}).get('instructions', 'Marcher')
                result.append(f"Étape {i}: 🚶 MARCHE")
                result.append(f"  ➜ {instruction}")
                result.append(f"  📏 {distance} • ⏱️ {duree}")
                result.append("")

            elif mode == 'TRANSIT':
                transit = step.get('transitDetails', {})
                ligne = transit.get('transitLine', {}).get('name', 'N/A')
                direction = transit.get('headsign', 'N/A')

                depart_stop = transit.get('stopDetails', {}).get('departureStop', {}).get('name', 'N/A')
                arrivee_stop = transit.get('stopDetails', {}).get('arrivalStop', {}).get('name', 'N/A')
                
                depart_time = transit.get('localizedValues', {}).get('departureTime', {}).get('time', {}).get('text', 'N/A')
                arrivee_time = transit.get('localizedValues', {}).get('arrivalTime', {}).get('time', {}).get('text', 'N/A')

                nb_arrets = transit.get('stopCount', 0)
                vehicle_type_transit = transit.get('transitLine', {}).get('vehicle', {}).get('name', {}).get('text', 'Transport')

                result.append(f"Étape {i}: 🚇 {vehicle_type_transit.upper()} LIGNE {ligne}")
                result.append(f"  ➜ Direction: {direction}")
                result.append(f"  🚏 Montée: {depart_stop} à {depart_time}")
                result.append(f"  🚏 Descente: {arrivee_stop} à {arrivee_time}")
                result.append(f"  📊 {nb_arrets} arrêts • 📏 {distance} • ⏱️ {duree}")
                result.append("")

            else:
                # Pour DRIVE, BICYCLE, etc.
                instruction = step.get('navigationInstruction', {}).get('instructions', 'Continuer')
                result.append(f"Étape {i}: {mode_emoji} {instruction}")
                result.append(f"  📏 {distance} • ⏱️ {duree}")
                result.append("")

        result.append(f"{'='*60}")

        return "\n".join(result)

    except requests.exceptions.Timeout:
        return "❌ Timeout: La requête a pris trop de temps"
    except requests.exceptions.RequestException as e:
        return f"❌ Erreur de requête: {e}"
    except Exception as e:
        return f"❌ Erreur inattendue: {e}"

if __name__ == "__main__":

    origin="Louvre Museum, Paris",
    destination="Notre-Dame Cathedral, Paris",
    
    # Test tous les modes
    modes = [
        ("WALK", "car"),
        ("TRANSIT", "car"),
        ("DRIVE", "car"),
        ("DRIVE", "taxi"),
        ("BICYCLE", "car")
    ]
    for travel_mode, veh_type in modes:
        print(get_route(origin, destination, travel_mode=travel_mode, vehicle_type=veh_type))
        print("\n" + "="*70 + "\n")