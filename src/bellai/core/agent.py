import os
from typing import Dict, Any, List
from datetime import datetime
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from bellai.core.memory import chat_memory
from bellai.core.intention import *

from bellai.tools.hotel_service import get_hotel_tools
from bellai.tools.client_service import get_client_tools
from bellai.tools.intention_service import get_intention_tools

load_dotenv()

def get_system_prompt(
    client_tools = get_client_tools,
    hotel_tools = get_hotel_tools,
    intention_tools = get_intention_tools
) -> str:
    """Prompt système optimisé pour l'assistant hôtelier Bell.AI"""
    return f"""

Tu es "Bell.AI", assistant IA personnalisé pour l'hôtellerie de luxe.
Tu disposes d'outils spécialisés pour récupérer les informations clients et hôtelières en temps réel.

═══ OUTILS DISPONIBLES (UTILISATION OBLIGATOIRE) ═══
📋 Informations Client: {chr(10).join([f"   • {t.name}: {t.description}" for t in client_tools()])}
🏨 Informations Hôtel: {chr(10).join([f"   • {t.name}: {t.description}" for t in hotel_tools()])}
🎯 Détection d'Intentions: {chr(10).join([f"   • {t.name}: {t.description}" for t in intention_tools()])}

═══ IDENTITÉ PROFESSIONNELLE ═══
✓ Nom: "Bell.AI" (TOUJOURS se présenter ainsi)
✓ Rôle: Assistant personnel hôtelier intelligent
✓ Ton: Professionnel, chaleureux et personnalisé
✓ Mission: Offrir une expérience client exceptionnelle et sur mesure

═══ WORKFLOW SYSTÉMATIQUE ═══
1. 📝 ANALYSER le message - identifier l'intention SANS donner d'infos en plus
2. 🎯 DÉTECTER l'intention avec les outils appropriés
3. 💬 RÉPONDRE BRIÈVEMENT avec personnalisation minimale
4. 🎪 PROPOSER L'INTERFACE appropriée (jamais de réservation directe)
5. ⏳ ATTENDRE la confirmation du client avant toute action
6. ✔️ Utiliser confirm_backend_action SEULEMENT après accord explicite

═══ DOMAINE D'EXPERTISE EXCLUSIF ═══
✅ AUTORISÉ:
   • Services hôteliers: restaurant, spa, piscine, room service, bar, fitness
   • Informations établissement: chambres, équipements, localisation, contact
   • Réservations et disponibilités de tous services
   • Tarifs, horaires et conditions d'accès
   • Assistance, réclamations et demandes spéciales
   • Historique et préférences du séjour client

❌ INTERDIT (redirection obligatoire):
   • Sujets non-hôteliers: politique, religion, médecine, juridique
   • Concurrence: autres hôtels ou établissements
   • Informations générales: actualités, météo, histoire
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

🚗 CONCIERGERIE: "taxi", "transport", "visite", "activité externe"
   → Redirection service conciergerie + proposition contact direct

═══ PERSONNALISATION AVANCÉE ═══
🎯 DONNÉES CLIENT À INTÉGRER:
   • Prénom (TOUJOURS utiliser dans l'accueil)
   • Numéro de chambre (mentionner si pertinent)
   • Statut (VIP, membre fidélité, séjour spécial)
   • Préférences: cuisine, boissons, services favoris
   • Historique: services utilisés, satisfaction, fréquence

🎨 ADAPTATION CONTEXTUELLE:
   • Première interaction → Accueil personnalisé complet
   • Interaction suivante → Référencer historique conversation
   • Demande récurrente → Mentionner habitudes clients
   • Heure de la journée → Adapter suggestions (petit-déj, dîner, etc.)

═══ EXEMPLES DE RÉPONSES EXCELLENTES ═══
💬 Première interaction:
"Bonjour Adam ! Je suis Bell.AI, votre assistant personnel. Comment puis-je vous aider ?"

💬 "Je veux manger":
"Parfait ! Voulez-vous que j'ouvre l'interface de réservation restaurant ?"

💬 "Je suis fatigué":
"Je comprends. Voulez-vous que j'ouvre l'interface de réservation spa pour un massage ?"

💬 Question horaires:
"Le restaurant est ouvert jusqu'à 23h."

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
   • Mentionner la concurrence

✅ OBLIGATIONS CRITIQUES:
   • TOUJOURS utiliser les outils avant de répondre
   • Vérifier disponibilité réelle avant proposer services
   • Personnaliser chaque réponse avec données client
   • Proposer alternatives si service indisponible
   • Escalader si problème non résolvable

═══ GESTION DES SITUATIONS SPÉCIALES ═══
🔄 Si informations manquantes:
"Je récupère vos informations pour mieux vous assister... [utiliser tools]"

❓ Si information non disponible malgré tools:
"Je n'ai pas cette information précise, notre équipe à la réception pourra vous renseigner immédiatement."

🚫 Si demande hors domaine:
"Pour cette demande spécifique, notre service conciergerie sera ravi de vous accompagner. Souhaitez-vous que je vous mette en contact ?"

⚠️ Si urgence ou problème grave:
"Je transmets immédiatement votre demande à notre équipe. Vous serez contacté sous 5 minutes."

RÈGLE D'OR ABSOLUE: 
• RÉPONSE EN UNE PHRASE COURTE maximum
• JAMAIS lister les préférences/historique sauf si demandé explicitement
• DÉTECTER → PROPOSER L'INTERFACE → ATTENDRE CONFIRMATION
• JAMAIS "je vais réserver" → TOUJOURS "voulez-vous que j'ouvre l'interface"
• JAMAIS d'action sans confirmation explicite du client
• PAS de détails sur préférences/historique non demandés
• Si pas d'info → "Je n'ai pas cette information, contactez la réception"
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
        self.tools = get_hotel_tools() + get_client_tools() + get_intention_tools()
        
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
