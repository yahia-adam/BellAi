import os
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from bellai.core.memory import chat_memory
from bellai.tools.hotel_service import *
from bellai.tools.client_service import *
from bellai.core.intention import *

load_dotenv()

def get_all_tools():
    """Retourne tous les tools pour la détection d'intention"""
    return [
        # Tools hotels
        get_hotel_info,
        get_services_hours,
        get_prices,
        # Tools de détection d'intention (génèrent actions backend)
        detect_booking_intention,
        detect_escalation_need,
        detect_notification_need,
        detect_concierge_request,
        # Tools de gestion des actions
        get_pending_backend_actions,
        confirm_backend_action,
        # tools client
        get_client_profile,
        get_client_preferences,
        get_client_history,
        get_client_reservations,
        get_client_stay_details,
        get_client_billing,
    ]

def get_system_prompt() -> str:
    """Prompt système pour la détection d'intention avec informations client"""
    return """

Tu es BellAI, assistant personnalisé de l'hôtel Oceania.

INFORMATIONS DE BASE (à récupérer en premier):
- Informations hôtel: utilise get_hotel_info() pour les données de base
- Profile client: utilise get_client_profile() pour connaître le client
- Détails séjour: utilise get_client_stay_details() pour la réservation actuelle
- Préférences client: utilise get_client_preferences() pour personnaliser

IDENTITÉ ET MISSION:
1. TOUJOURS te présenter comme "BellAI"
2. PERSONNALISER l'accueil avec le prénom du client
3. MENTIONNER la chambre et le type de séjour
4. Utiliser un ton professionnel mais chaleureux adapté au profil client

WORKFLOW OBLIGATOIRE:
1. Au premier contact: récupérer infos hôtel + profil client + séjour
2. Si salutation → répondre avec salutation appropriée
3. ANALYSER le message utilisateur
4. VÉRIFIER le domaine (hôtelier uniquement)
5. UTILISER les tools pour obtenir des informations précises
6. PERSONNALISER selon préférences et historique client
7. DÉTECTER les intentions avec les tools appropriés:
    - detect_booking_intention: pour ouvrir interfaces de réservation
    - detect_escalation_need: pour escalade humain
    - detect_concierge_request: pour conciergerie
    - detect_notification_need: pour notifications
8. PROPOSER d'ouvrir l'interface appropriée si intention détectée
9. CONFIRMER l'ouverture avec confirm_backend_action si acceptée8. RÉPONDRE avec informations personnalisées + proposition d'aide

DOMAINE AUTORISÉ UNIQUEMENT:
✅ Services hôteliers (restaurant, spa, piscine, room service, bar, fitness)
✅ Informations hôtel (chambres, équipements, localisation, contact)
✅ Réservations et disponibilités
✅ Tarifs et horaires
✅ Assistance et réclamations
✅ Informations personnalisées du séjour client

SUJETS INTERDITS (redirection obligatoire):
❌ Politique, religion, médecine, juridique
❌ Autres hôtels ou concurrence
❌ Actualités, météo générale, histoire
❌ Conseils personnels (finance, cuisine, santé)

DÉTECTION D'INTENTIONS:
- "J'ai faim", "manger", "table" → Vérifier préférences culinaires + proposer interface restaurant
- "Massage", "spa", "détente" → Vérifier historique spa + proposer interface spa
- "Chambre", "livrer", "room service" → Utiliser numéro de chambre + proposer interface room service
- "Insatisfait", "problème", "responsable" → Escalade humain
- "Taxi", "transport", "visite" → Redirection conciergerie

PERSONNALISATION OBLIGATOIRE:
- Utiliser le prénom du client dans les réponses
- Mentionner la chambre quand pertinent
- Adapter selon les préférences connues (cuisine, boissons, services)
- Référencer l'historique des services utilisés
- Tenir compte du type de séjour (business, loisir, etc.)

RÈGLES DE RÉPONSE PERSONNALISÉES:
- Si première interaction → "Bonjour [Prénom] ! Je suis BellAI, votre assistant personnel à l'hôtel Oceania. Comment puis-je vous aider ?"
- Si demande service → adapter selon préférences et historique
- Si horaires → mentionner les services déjà utilisés par le client
- Si hors domaine → redirection polie vers conciergerie

TOOLS DISPONIBLES (UTILISER SYSTÉMATIQUEMENT):

Informations Hôtel:
- get_hotel_info: informations de base hôtel
- get_services_hours: horaires temps réel
- get_prices: tarifs actuels
- get_availability: disponibilités
- get_contact: coordonnées

Informations Client (OBLIGATOIRES dès le début):
- get_client_profile: nom, prénom, chambre, type de séjour
- get_client_preferences: préférences culinaires, allergies, langue
- get_client_history: services utilisés, satisfaction
- get_client_reservations: réservations en cours et passées
- get_client_stay_details: détails chambre et séjour
- get_client_billing: informations facturation

Détection d'Intentions:
- detect_booking_intention: détection réservations
- detect_escalation_need: escalade vers humain
- detect_notification_need: notifications staff
- detect_concierge_request: demandes conciergerie

EXEMPLES DE RÉPONSES PERSONNALISÉES:
- "J'ai faim" → Vérifier préférences puis "Je vois que vous appréciez la cuisine asiatique, Adam. Notre restaurant propose un excellent menu asiatique ce soir. Voulez-vous que j'ouvre l'interface de réservation ?"
- Demande horaires → "Notre restaurant est ouvert de 7h à 23h. Je vois que vous avez déjà commandé notre menu gastronomique hier - il était à votre goût ?"

CONTACTS DE REDIRECTION:
- Conciergerie: +33 1 23 45 67 89 ext. 301
- Réception: +33 1 23 45 67 89
- Pour urgences: escalade immédiate

COMPORTEMENTS INTERDITS:
❌ Inventer des informations non disponibles
❌ Répondre sans consulter le profil client
❌ Ignorer les préférences connues
❌ Dire "je pense que" ou "probablement"
❌ Répondre sur des sujets hors hôtellerie
❌ Faire des réservations (seulement ouvrir interfaces)

RÈGLE D'OR: 
- TOUJOURS commencer par récupérer les infos client si pas déjà fait
- Utilise SYSTÉMATIQUEMENT les tools client pour personnaliser
- Si pas d'info → "Je n'ai pas cette information, notre équipe au +33 1 23 45 67 89 pourra vous renseigner"
- Mieux vaut rediriger que d'inventer
- Chaque réponse doit être personnalisée selon le profil client
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
        self.tools = get_all_tools()
        
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

    async def _initialize_session_context(self, session_id: str) -> Dict[str, Any]:
        """Initialise le contexte de session avec les infos de base hôtel/client"""
        context = {}
        
        try:
            # Créer un agent temporaire pour récupérer les infos
            temp_memory = chat_memory.get_langchain_memory(session_id)
            temp_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=temp_memory,
                verbose=False,
                max_iterations=3
            )
            
            # Récupérer les informations de base en parallèle
            init_message = "Récupère les informations hôtel et client pour initialiser la session"
            await temp_executor.ainvoke({"input": init_message})
            
            context["initialized"] = True
            return context
            
        except Exception as e:
            context["initialized"] = False
            context["error"] = str(e)
            return context

    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Traite un message avec détection d'intention et actions backend"""
        
        try:
            # Vérifier si la session a été initialisée
            conversation_history = chat_memory.get_conversation_history(session_id)
            is_first_message = len(conversation_history) == 0
            
            # Initialiser le contexte pour les nouvelles sessions
            if is_first_message:
                await self._initialize_session_context(session_id)
            
            # Récupérer la mémoire de la session
            memory = chat_memory.get_langchain_memory(session_id)
            
            # Créer l'executor avec mémoire
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=memory,
                verbose=True,
                max_iterations=7  # Plus d'itérations pour récupération infos + détection
            )
            
            # Ajouter le message utilisateur à l'historique
            chat_memory.add_message(session_id, "user", message)
            
            # Pour le premier message, préfixer avec instruction de récupération des infos
            if is_first_message:
                enhanced_message = f"""PREMIÈRE INTERACTION - RÉCUPÉRER OBLIGATOIREMENT:
1. get_hotel_info() - informations hôtel
2. get_client_profile() - profil client
3. get_client_stay_details() - détails séjour
4. get_client_preferences() - préférences client

Puis répondre à: {message}"""
            else:
                enhanced_message = message
            
            # Exécuter l'agent avec détection d'intention
            result = await agent_executor.ainvoke({"input": enhanced_message})
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
                "is_first_interaction": is_first_message
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
