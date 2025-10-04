"""Service de conciergerie utilisant Google Places API pour BellAI"""
from langchain.tools import tool
from langchain_google_community import GooglePlacesAPIWrapper

HOTEL_LOCATION = "52 Rue d'Oradour-sur-Glane, 75015 Paris"

google_places = GooglePlacesAPIWrapper(top_k_results=3)

@tool
def search_places(query: str) -> str:
    """
    Recherche des lieux (restaurants, sites touristiques, etc.) proches de l'hôtel.

    Args:
        query (str): Type de lieu à rechercher.

    Returns:
        str: top 3 Résultats de la recherche depuis l'API google_places.
    """
    full_query = f"{query} near {HOTEL_LOCATION}"
    result = google_places.run(full_query)
    return result

# Exemple d'utilisation
if __name__ == "__main__":
    print(search_places("restaurant italien"))
    print()
    print(search_places("pharmacie"))
    print()
    print(search_places("Tour Eiffel"))