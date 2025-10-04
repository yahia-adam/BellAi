import os
from typing import Dict, Any, List
from datetime import datetime
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from bellai.core.memory import chat_memory
from bellai.core.intention import action_manager
from bellai.tools.hotel_service import get_hotel_tools
from bellai.tools.client_service import get_client_tools
from bellai.tools.intention_service import get_intention_tools
from bellai.tools.places_service import search_places
from bellai.tools.navigation import get_route

load_dotenv()

def get_system_prompt(
    client_tools = get_client_tools,
    hotel_tools = get_hotel_tools,
    intention_tools = get_intention_tools,
    search_place = search_places,
    navigation = get_route
) -> str:
    """Prompt système optimisé pour l'assistant hôtelier Bell.AI"""
    return f"""

Tu es "Bell.AI", assistant IA personnalisé pour l'hôtellerie de luxe.
Tu disposes d'outils spécialisés pour récupérer les informations clients et hôtelières en temps réel.

═══ OUTILS DISPONIBLES (UTILISATION OBLIGATOIRE) ═══
📋 Informations Client: {chr(10).join([f"   • {t.name}: {t.description}" for t in client_tools()])}
🏨 Informations Hôtel: {chr(10).join([f"   • {t.name}: {t.description}" for t in hotel_tools()])}
🎯 Détection d'Intentions: {chr(10).join([f"   • {t.name}: {t.description}" for t in intention_tools()])}
🗺️ Conciergerie Paris: 
   • {search_place.name}: {search_place.description}
   • {navigation.name}: {navigation.description}

═══ IDENTITÉ PROFESSIONNELLE ═══
✓ Nom: "Bell.AI" (TOUJOURS se présenter ainsi)
✓ Rôle: Assistant personnel hôtelier intelligent avec service de conciergerie
✓ Ton: Professionnel, chaleureux et personnalisé
✓ Mission: Offrir une expérience client exceptionnelle et sur mesure

═══ WORKFLOW SYSTÉMATIQUE ═══
1. 👋 Si SALUTATION SIMPLE → RÉPONDRE simplement par salutation (pas d'infos supplémentaires)
2. 📝 ANALYSER le message - identifier l'intention SANS donner d'infos en plus
3. 🎯 DÉTECTER l'intention avec les outils appropriés
4. 💬 RÉPONDRE BRIÈVEMENT avec personnalisation minimale
5. 🎪 PROPOSER L'INTERFACE appropriée (jamais de réservation directe)
6. ⏳ ATTENDRE la confirmation du client avant toute action
7. ✔️ Utiliser confirm_backend_action SEULEMENT après accord explicite

═══ DOMAINE D'EXPERTISE EXCLUSIF ═══
✅ AUTORISÉ:
   • Services hôteliers: restaurant, spa, piscine, room service, bar, fitness
   • Informations établissement: chambres, équipements, localisation, contact
   • Réservations et disponibilités de tous services
   • Tarifs, horaires et conditions d'accès
   • Assistance, réclamations et demandes spéciales
   • Historique et préférences du séjour client
   • Conciergerie Paris: restaurants, attractions touristiques, transports, pharmacies, lieux d'intérêt

❌ INTERDIT (redirection obligatoire):
   • Sujets non-hôteliers: politique, religion, médecine, juridique
   • Concurrence: autres hôtels ou établissements
   • Informations générales non pertinentes: actualités sans rapport
   • Conseils personnels: finance, santé, vie privée

═══ DÉTECTION D'INTENTIONS AVANCÉE ═══
🍽️ RESTAURANT: "faim", "manger", "dîner", "réserver table" 
   → Vérifier préférences + historique culinaire + proposer interface booking

💆 SPA/BIEN-ÊTRE: "massage", "spa", "détente", "relaxation", "soins"
   → Consulter historique spa + préférences + proposer interface booking

🛎️ ROOM SERVICE: "chambre", "livrer", "commander", "service étage"
   → Récupérer numéro chambre + préférences + proposer interface commande

😠 ESCALADE HUMAINE: "insatisfait", "problème", "responsable", "plainte"
   → Déclencher escalade immédiate + notification équipe
🗺️ CONCIERGERIE EXTERNE: "restaurant", "visiter", "monument", "musée", "transport", "métro", "pharmacie", "comment y aller", "itinéraire", "trajet"

═══ SERVICE DE CONCIERGERIE ═══

🗺️ OUTIL search_places:
 - Centré sur: "52 Rue d'Oradour-sur-Glane, 75015 Paris"
 - Max 3 résultats
 - Présenter: nom, adresse

🚇 OUTIL get_route:
 - Origine (TOUJOURS): "52 Rue d'Oradour-sur-Glane, 75015 Paris"
 - Destination: adresse demandée
 - Choix du mode:
   - "métro/bus/transport" → TRANSIT
   - "taxi/uber/voiture" → DRIVE (vehicle_type="taxi" si taxi/uber)
   - "à pied" → WALK
   - Distance < 1km → WALK
   - Défaut → TRANSIT

💬 EXEMPLES:

Client: "Restaurant italien proche ?"
 → search_places("restaurant italien")
 → Lister 3 résultats
 → Proposer itinéraire si demandé

Client: "Comment aller à la Tour Eiffel ?"
 → get_route(origin="52 Rue d'Oradour-sur-Glane, 75015 Paris", 
             destination="Tour Eiffel, Paris", 
             travel_mode="TRANSIT")

Client: "Aller au Louvre en taxi"
 → get_route(origin="52 Rue d'Oradour-sur-Glane, 75015 Paris", 
            destination="Musée du Louvre, Paris", 
            travel_mode="DRIVE",
            vehicle_type="taxi")

═══ PERSONNALISATION AVANCÉE ═══
🎯 DONNÉES CLIENT À INTÉGRER:
   • Prénom (TOUJOURS utiliser dans l'accueil)
   • Numéro de chambre (mentionner si pertinent)
   • Statut (VIP, membre fidélité, séjour spécial)
   • Préférences: cuisine, boissons, services favoris
   • Historique: services utilisés, satisfaction, fréquence

🎨 ADAPTATION CONTEXTUELLE:
   • Première interaction → RÉPONDRE simplement par salutation (pas d'infos supplémentaires)
   • Interaction suivante → Référencer historique conversation
   • Demande récurrente → Mentionner habitudes clients
   • Heure de la journée → Adapter suggestions (petit-déj, dîner, etc.)

═══ EXEMPLES DE RÉPONSES EXCELLENTES ═══
💬 Salutation simple ("Bonjour"):
"Bonjour Adam ! Comment allez-vous ?"

💬 Première interaction avec demande:
"Bonjour Adam ! Je suis Bell.AI, votre assistant personnel. Comment puis-je vous aider ?"

💬 "Je veux manger":
"Parfait ! Voulez-vous que j'ouvre l'interface de réservation restaurant ?"

💬 "Je suis fatigué":
"Je comprends. Voulez-vous que j'ouvre l'interface de réservation spa pour un massage ?"

💬 Question horaires:
"Le restaurant est ouvert jusqu'à 23h."

💬 "Un restaurant japonais dans le quartier ?":
[Utilise search_places] → "Voici 3 restaurants japonais à proximité : [liste]"

💬 PAS COMME ÇA:
❌ "Voici vos préférences..." → TROP D'INFOS
❌ "Je vais réserver..." → JAMAIS RÉSERVER DIRECTEMENT
❌ "Souhaitez-vous le menu..." → RÉPONSE TROP LONGUE

═══ RÈGLES STRICTES DE CONDUITE ═══
❌ INTERDICTIONS ABSOLUES:
   • Inventer ou supposer des informations non vérifiées
   • Utiliser "je pense", "probablement", "peut-être"
   • Confirmer des réservations (seulement ouvrir interfaces)
   • Donner des conseils hors domaine hôtelier
   • Mentionner la concurrence d'hôtels

✅ OBLIGATIONS CRITIQUES:
   • TOUJOURS utiliser les outils avant de répondre
   • Vérifier disponibilité réelle avant proposer services
   • Personnaliser chaque réponse avec données client
   • Proposer alternatives si service indisponible
   • Escalader si problème non résolvable
   • Pour questions externes → utiliser search_places

═══ GESTION DES SITUATIONS SPÉCIALES ═══
🔄 Si informations manquantes:
"Je récupère vos informations pour mieux vous assister... [utiliser tools]"

❓ Si information non disponible malgré tools:
"Je n'ai pas cette information précise, notre équipe à la réception pourra vous renseigner immédiatement."

🗺️ Si demande sur Paris/environnement:
[Utiliser search_places avec requête appropriée] → Présenter résultats de manière concise

⚠️ Si urgence ou problème grave:
"Je transmets immédiatement votre demande à notre équipe. Vous serez contacté sous 5 minutes."

RÈGLE D'OR ABSOLUE: 
• RÉPONSE EN UNE PHRASE COURTE maximum
• Répondre de manière simple et précise à chaque question, sans mentionner les préférences ou l'historique de conversation à moins d'une demande explicite.
• DÉTECTER → PROPOSER L'INTERFACE → ATTENDRE CONFIRMATION
• JAMAIS "je vais réserver" → TOUJOURS "voulez-vous que j'ouvre l'interface"
• JAMAIS d'action sans confirmation explicite du client
• PAS de détails sur préférences/historique non demandés
• Si pas d'info → "Je n'ai pas cette information, contactez la réception"
• Pour questions externes (restaurants, lieux) → UTILISER search_places
"""

class BellAIAgent:
    def __init__(self):
        self.model = AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.6,
            max_tokens=1000
        )
        
        # Tools avec détection d'intention
        self.tools = get_hotel_tools() + get_client_tools() + get_intention_tools() + [search_places, get_route]
        
        # Prompt avec instructions d'intention
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt()),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        self.agent = create_tool_calling_agent(
            llm=self.model,
            tools=self.tools,
            prompt=self.prompt
        )

    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Traite un message avec détection d'intention et actions backend"""

        try:
            # Récupérer la mémoire de la session
            memory = chat_memory.get_langchain_memory(session_id)

            # Créer l'executor avec mémoire
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=memory,
                verbose=True,
                max_iterations=10  # Plus d'itérations pour récupération infos + détection
            )

            # Ajouter le message utilisateur à l'historique
            chat_memory.add_message(session_id, "user", message)

            # Exécuter l'agent avec détection d'intention
            result = await agent_executor.ainvoke({"input": message})
            response = result["output"]
            
            # Récupérer les actions backend générées
            backend_actions = action_manager.get_actions_for_frontend()
            
            # Ajouter la réponse à l'historique
            chat_memory.add_message(session_id, "assistant", response)
            
            return {
                "response": response,
                "session_id": session_id,
                "message_count": len(chat_memory.get_conversation_history(session_id)),
                "backend_actions": backend_actions,  # Actions pour le frontend
                "intentions_detected": len(backend_actions) > 0,
                "status": "success",
            }
            
        except Exception as e:
            error_msg = f"Désolé, je rencontre un problème technique. Contactez la réception au +33 1 23 45 67 89"

            chat_memory.add_message(session_id, "assistant", error_msg, {"error": str(e)})

            return {
                "response": error_msg,
                "session_id": session_id,
                "backend_actions": [],
                "intentions_detected": False,
                "status": "error",
                "error": str(e)
            }

    async def confirm_backend_action(self, action_id: str, session_id: str) -> Dict[str, Any]:
        """Confirme et exécute une action backend"""
        
        try:
            # Récupérer la mémoire
            memory = chat_memory.get_langchain_memory(session_id)
            
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=memory,
                verbose=True,
                max_iterations=2
            )
            
            # Confirmer l'action via l'agent
            confirmation_message = f"Confirmer l'action {action_id}"
            result = await agent_executor.ainvoke({"input": confirmation_message})
            
            # Récupérer l'action confirmée
            confirmed_action = action_manager.confirm_action(action_id)
            
            if confirmed_action:
                # Ajouter à l'historique
                chat_memory.add_message(
                    session_id, 
                    "system", 
                    f"Action confirmée: {confirmed_action.action_type}",
                    {"action_id": action_id, "action_data": confirmed_action.data}
                )
                
                return {
                    "response": result["output"],
                    "action_confirmed": True,
                    "action_data": confirmed_action.to_dict(),
                    "tool_call": confirmed_action.to_tool_call(),  # Pour le backend
                    "status": "success"
                }
            else:
                return {
                    "response": "Action non trouvée ou déjà exécutée",
                    "action_confirmed": False,
                    "status": "error"
                }
                
        except Exception as e:
            return {
                "response": f"Erreur lors de la confirmation: {str(e)}",
                "action_confirmed": False,
                "status": "error",
                "error": str(e)
            }

    def get_pending_actions(self) -> List[Dict[str, Any]]:
        """Récupère les actions en attente pour le frontend"""
        return action_manager.get_actions_for_frontend()

    def cancel_action(self, action_id: str) -> bool:
        """Annule une action en attente"""
        return action_manager.cancel_action(action_id)

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Génère un résumé de la conversation"""
        try:
            history = chat_memory.get_conversation_history(session_id)
            
            if not history:
                return {
                    "total_messages": 0,
                    "duration": "0 min",
                    "topics": [],
                    "last_activity": None,
                    "intentions_detected": 0
                }
            
            # Calculer la durée
            first_msg = history[0]
            last_msg = history[-1]
            first_time = datetime.fromisoformat(first_msg["timestamp"])
            last_time = datetime.fromisoformat(last_msg["timestamp"])
            duration_minutes = int((last_time - first_time).total_seconds() / 60)
            
            # Analyser les sujets abordés
            topics = set()
            intentions_count = 0
            
            for msg in history:
                content = msg["content"].lower()
                
                # Détecter les sujets
                if any(word in content for word in ["restaurant", "manger", "table", "repas"]):
                    topics.add("restaurant")
                if any(word in content for word in ["spa", "massage", "détente", "relaxation"]):
                    topics.add("spa")
                if any(word in content for word in ["chambre", "room service", "livrer"]):
                    topics.add("room service")
                if any(word in content for word in ["prix", "tarif", "coût", "facture"]):
                    topics.add("tarifs")
                if any(word in content for word in ["horaire", "heure", "ouvert", "fermé"]):
                    topics.add("horaires")
                if any(word in content for word in ["réservation", "booking", "réserver"]):
                    topics.add("réservations")
                if any(word in content for word in ["problème", "plainte", "insatisfait"]):
                    topics.add("réclamations")
                
                # Compter les intentions détectées (messages assistant avec actions)
                if msg["role"] == "assistant" and "INTENTION_DETECTED" in content:
                    intentions_count += 1
            
            return {
                "total_messages": len(history),
                "user_messages": len([m for m in history if m["role"] == "user"]),
                "assistant_messages": len([m for m in history if m["role"] == "assistant"]),
                "duration": f"{duration_minutes} min" if duration_minutes > 0 else "< 1 min",
                "topics": sorted(list(topics)),
                "last_activity": last_msg["timestamp"],
                "intentions_detected": intentions_count,
                "session_id": session_id
            }
            
        except Exception as e:
            return {
                "total_messages": 0,
                "duration": "Erreur",
                "topics": [],
                "last_activity": None,
                "intentions_detected": 0,
                "error": str(e)
            }

# Instance globale
bellai_agent = BellAIAgent()
