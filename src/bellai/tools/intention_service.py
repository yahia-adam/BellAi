from langchain.tools import tool
from datetime import datetime
from bellai.core.intention import BackendAction
from bellai.core.intention import action_manager

def _store_pending_action(action: BackendAction) -> None:
    """Fonction helper pour stocker une action"""
    action_manager.store_action(action)

@tool
def detect_booking_intention(user_message: str, service_type: str = None) -> str:
    """Détecte une intention de réservation et prépare l'action backend"""

    # Mots-clés par service
    booking_keywords = {
        "restaurant": ["manger", "faim", "dîner", "déjeuner", "table", "restaurant", "repas"],
        "spa": ["massage", "détente", "relaxer", "spa", "soin", "bien-être"],
        "room_service": ["chambre", "livrer", "apporter", "room service", "service chambre"]
    }

    message_lower = user_message.lower()
    detected_service = service_type

    # Détection automatique si pas spécifié
    if not detected_service:
        for service, keywords in booking_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_service = service
                break

    if detected_service:
        # Créer l'action backend
        action = BackendAction(
            action_type=f"create_booking_{detected_service}",
            data={
                "service": detected_service,
                "user_message": user_message,
                "detected_keywords": [kw for kw in booking_keywords.get(detected_service, []) 
                                    if kw in message_lower],
                "timestamp": str(datetime.now().isoformat())
            },
            confirmation_needed=True
        )

        # Stocker l'action pour le backend
        _store_pending_action(action)

        return f"INTENTION_DETECTED: {detected_service} booking | ACTION_PREPARED: {action.id}"

    return "NO_BOOKING_INTENTION_DETECTED"

@tool
def detect_escalation_need(user_message: str, context: str = "") -> str:
    """Détecte si escalade vers humain nécessaire"""
    
    escalation_triggers = [
        "parler à quelqu'un", "responsable", "manager", "plainte", "problème grave",
        "insatisfait", "remboursement", "annulation", "urgence", "aide humaine"
    ]
    
    message_lower = user_message.lower()
    context_lower = context.lower()
    
    # Vérifier les déclencheurs
    triggered_words = [word for word in escalation_triggers 
                    if word in message_lower or word in context_lower]
    
    if triggered_words:
        action = BackendAction(
            action_type="escalate_to_human",
            data={
                "reason": "escalation_requested",
                "triggered_words": triggered_words,
                "user_message": user_message,
                "context": context,
                "priority": "high" if any(word in ["urgence", "grave", "plainte"] 
                                        for word in triggered_words) else "normal"
            },
            confirmation_needed=False  # Escalade immédiate
        )
        
        _store_pending_action(action)
        return f"ESCALATION_NEEDED | ACTION_PREPARED: {action.id}"
    
    return "NO_ESCALATION_NEEDED"

@tool
def detect_notification_need(user_message: str, notification_type: str = None) -> str:
    """Détecte besoin d'envoyer une notification"""
    
    notification_triggers = {
        "reservation_confirmation": ["confirmé", "réservé", "booking confirmé"],
        "service_update": ["changement", "modification", "update", "mise à jour"],
        "special_request": ["allergie", "handicap", "demande spéciale", "besoin particulier"],
        "vip_alert": ["vip", "célèbre", "important", "personnalité"]
    }
    
    message_lower = user_message.lower()
    detected_type = notification_type
    
    if not detected_type:
        for notif_type, keywords in notification_triggers.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_type = notif_type
                break
    
    if detected_type:
        action = BackendAction(
            action_type="send_notification",
            data={
                "notification_type": detected_type,
                "message": user_message,
                "recipient": "hotel_staff",
                "urgency": "normal"
            },
            confirmation_needed=False
        )
        
        _store_pending_action(action)
        return f"NOTIFICATION_NEEDED: {detected_type} | ACTION_PREPARED: {action.id}"
    
    return "NO_NOTIFICATION_NEEDED"

@tool
def detect_concierge_request(user_message: str) -> str:
    """Détecte demande pour la conciergerie"""
    
    concierge_keywords = [
        "transport", "taxi", "réservation externe", "théâtre", "spectacle",
        "restaurant ville", "activité", "visite", "tour", "excursion",
        "shopping", "recommandation", "billet", "ticket"
    ]
    
    message_lower = user_message.lower()
    matched_keywords = [kw for kw in concierge_keywords if kw in message_lower]
    
    if matched_keywords:
        action = BackendAction(
            action_type="concierge_request",
            data={
                "request_type": "general_assistance",
                "keywords": matched_keywords,
                "message": user_message,
                "service_level": "standard"
            },
            confirmation_needed=True
        )
        
        _store_pending_action(action)
        return f"CONCIERGE_REQUEST | ACTION_PREPARED: {action.id}"
    
    return "NO_CONCIERGE_REQUEST"

@tool
def get_pending_backend_actions() -> str:
    """Récupère les actions backend en attente"""
    actions = action_manager.get_pending_actions()
    
    if not actions:
        return "NO_PENDING_ACTIONS"
    
    action_list = []
    for action in actions:
        action_list.append(f"- {action.action_type} (ID: {action.id})")
    
    return f"PENDING_ACTIONS: {', '.join(action_list)}"

@tool
def confirm_backend_action(action_id: str) -> str:
    """Confirme une action backend"""
    action = action_manager.confirm_action(action_id)
    
    if action:
        return f"ACTION_CONFIRMED: {action.action_type} | TOOL_CALL: {action.to_tool_call()}"
    else:
        return f"ACTION_NOT_FOUND: {action_id}"

def get_intention_tools():
    return [
        detect_booking_intention,
        detect_escalation_need,
        detect_notification_need,
        detect_concierge_request,
        get_pending_backend_actions,
        confirm_backend_action
    ]

__all__ = [
    "get_intention_tools"
]