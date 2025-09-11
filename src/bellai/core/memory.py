from typing import Dict, List
from datetime import datetime
import json
from langchain.memory import ConversationBufferWindowMemory

class ChatMemoryManager:
    """Gestionnaire de mémoire pour les conversations avec BellAI"""

    def __init__(self):
        # Stockage des conversations par session
        self.conversations: Dict[str, List[Dict]] = {}
        # Mémoire LangChain par session
        self.langchain_memories: Dict[str, ConversationBufferWindowMemory] = {}
        # Limite de messages par conversation
        self.max_messages = 20

    def get_session_id(self, user_id: str = "default") -> str:
        """Génère un ID de session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{user_id}_{timestamp}"

    def create_session(self, session_id: str) -> None:
        """Crée une nouvelle session de chat"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            self.langchain_memories[session_id] = ConversationBufferWindowMemory(
                k=self.max_messages,  # Garde les 20 derniers messages
                return_messages=True,
                memory_key="chat_history"
            )

    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None) -> None:
        """Ajoute un message à l'historique"""
        self.create_session(session_id)

        # Ajouter au stockage simple
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversations[session_id].append(message)

        # Ajouter à la mémoire LangChain
        if role == "user":
            self.langchain_memories[session_id].chat_memory.add_user_message(content)
        elif role == "assistant":
            self.langchain_memories[session_id].chat_memory.add_ai_message(content)

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Récupère l'historique complet d'une conversation"""
        return self.conversations.get(session_id, [])

    def get_langchain_memory(self, session_id: str) -> ConversationBufferWindowMemory:
        """Récupère la mémoire LangChain pour une session"""
        self.create_session(session_id)
        return self.langchain_memories[session_id]

    def get_recent_context(self, session_id: str, last_n: int = 5) -> str:
        """Récupère le contexte récent sous forme de texte"""
        history = self.get_conversation_history(session_id)
        recent = history[-last_n:] if history else []

        context = []
        for msg in recent:
            role = "Client" if msg["role"] == "user" else "BellAI"
            context.append(f"{role}: {msg['content']}")

        return "\n".join(context)

    def clear_session(self, session_id: str) -> None:
        """Efface l'historique d'une session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
        if session_id in self.langchain_memories:
            del self.langchain_memories[session_id]

    def list_sessions(self, user_id: str = None) -> List[Dict]:
        """Liste les sessions disponibles"""
        sessions = []
        for session_id, messages in self.conversations.items():
            if user_id and not session_id.startswith(user_id):
                continue

            first_message = messages[0] if messages else None
            last_message = messages[-1] if messages else None

            sessions.append({
                "session_id": session_id,
                "message_count": len(messages),
                "first_message": first_message,
                "last_message": last_message,
                "created_at": first_message["timestamp"] if first_message else None
            })

        return sorted(sessions, key=lambda x: x.get("created_at", ""), reverse=True)

    def save_to_file(self, filepath: str) -> None:
        """Sauvegarde les conversations dans un fichier"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath: str) -> None:
        """Charge les conversations depuis un fichier"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.conversations = json.load(f)

            # Recréer les mémoires LangChain
            for session_id, messages in self.conversations.items():
                self.create_session(session_id)
                for msg in messages:
                    if msg["role"] == "user":
                        self.langchain_memories[session_id].chat_memory.add_user_message(msg["content"])
                    elif msg["role"] == "assistant":
                        self.langchain_memories[session_id].chat_memory.add_ai_message(msg["content"])
        except FileNotFoundError:
            self.conversations = {}

# Instance globale
chat_memory = ChatMemoryManager()
