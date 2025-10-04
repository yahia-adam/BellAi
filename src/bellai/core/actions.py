import time
from typing import Dict, Any, List, Optional
from enum import Enum
import json

class IntentionType(Enum):
    """Types d'intentions détectées"""
    BOOKING_RESTAURANT = "booking_restaurant"
    BOOKING_SPA = "booking_spa" 
    BOOKING_ROOM_SERVICE = "booking_room_service"
    ESCALATE_HUMAN = "escalate_human"
    SEND_NOTIFICATION = "send_notification"
    GENERAL_INFO = "general_info"

class BackendAction:
    """Représente une action à envoyer au backend"""
    def __init__(self, action_type: str, data: Dict[str, Any], confirmation_needed: bool = True):
        self.action_type = action_type
        self.data = data
        self.confirmation_needed = confirmation_needed
        self.id = self._generate_id()

    def _generate_id(self) -> str:
        return str(int(time.time() * 1000))

    def to_tool_call(self) -> str:
        """Convertit l'action en format tool_call pour le backend"""
        return f"""<tool_call>
{{"name": "{self.action_type}", "arguments": {json.dumps(self.data)}, "id": "{self.id}"}}
</tool_call>"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API"""
        return {
            "action_type": self.action_type,
            "data": self.data,
            "confirmation_needed": self.confirmation_needed,
            "id": self.id
        }

class BackendActionManager:
    """Gestionnaire des actions pour le backend"""

    def __init__(self):
        self.pending_actions: Dict[str, BackendAction] = {}
        self.completed_actions: Dict[str, BackendAction] = {}

    def store_action(self, action: BackendAction) -> None:
        """Stocke une action en attente"""
        self.pending_actions[action.id] = action

    def get_pending_actions(self) -> List[BackendAction]:
        """Récupère toutes les actions en attente"""
        return list(self.pending_actions.values())

    def confirm_action(self, action_id: str) -> Optional[BackendAction]:
        """Confirme et exécute une action"""
        if action_id in self.pending_actions:
            action = self.pending_actions.pop(action_id)
            self.completed_actions[action_id] = action
            return action
        return None

    def cancel_action(self, action_id: str) -> bool:
        """Annule une action en attente"""
        if action_id in self.pending_actions:
            del self.pending_actions[action_id]
            return True
        return False

    def get_actions_for_frontend(self) -> List[Dict[str, Any]]:
        """Récupère les actions au format frontend/backend"""
        return [action.to_dict() for action in self.pending_actions.values()]

def _store_pending_action(action: BackendAction) -> None:
    """Fonction helper pour stocker une action"""
    action_manager.store_action(action)

# Instance globale
action_manager = BackendActionManager()
