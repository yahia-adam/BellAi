import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Configuration de la page
st.set_page_config(
    page_title="BellAI Test Interface",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)
# try:
from bellai.core.agent import bellai_agent
from bellai.core.memory import chat_memory
from bellai.tools.intention_service import action_manager
# except ImportError:
#     st.error("⚠️ Impossible d'importer les modules BellAI. Vérifiez votre structure de projet.")
#     st.stop()

# =============================================================================
# ÉTAT DE SESSION STREAMLIT
# =============================================================================

if 'session_id' not in st.session_state:
    st.session_state.session_id = chat_memory.get_session_id("streamlit_user")

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'pending_actions' not in st.session_state:
    st.session_state.pending_actions = []

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

async def process_message_async(message: str) -> Dict[str, Any]:
    """Traite un message de manière asynchrone"""
    return await bellai_agent.process_message(
        message, 
        st.session_state.session_id
    )

def process_message_sync(message: str) -> Dict[str, Any]:
    """Wrapper synchrone pour Streamlit"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(process_message_async(message))
    finally:
        loop.close()

async def confirm_action_async(action_id: str) -> Dict[str, Any]:
    """Confirme une action de manière asynchrone"""
    return await bellai_agent.confirm_backend_action(
        action_id,
        st.session_state.session_id
    )

def confirm_action_sync(action_id: str) -> Dict[str, Any]:
    """Wrapper synchrone pour confirmation"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(confirm_action_async(action_id))
    finally:
        loop.close()

# =============================================================================
# INTERFACE PRINCIPALE
# =============================================================================

def main():
    st.title("🏨 BellAI - Interface de Test")
    st.markdown("---")
    
    # Sidebar pour les informations de session
    with st.sidebar:
        st.header("📊 Informations de Session")
        st.write(f"**Session ID:** `{st.session_state.session_id[-8:]}`")
        st.write(f"**Messages:** {len(st.session_state.conversation_history)}")
        
        # Bouton pour nouvelle session
        if st.button("🆕 Nouvelle Session"):
            st.session_state.session_id = chat_memory.get_session_id("streamlit_user")
            st.session_state.conversation_history = []
            st.session_state.pending_actions = []
            st.rerun()
        
        # Affichage des statistiques
        st.subheader("📈 Statistiques")
        all_actions = bellai_agent.get_pending_actions()
        st.metric("Actions en attente", len(all_actions))
        
        completed_actions = len(action_manager.completed_actions)
        st.metric("Actions confirmées", completed_actions)
        
        # Export de la conversation
        if st.button("💾 Exporter Conversation"):
            history = chat_memory.get_conversation_history(st.session_state.session_id)
            st.download_button(
                "📥 Télécharger JSON",
                data=json.dumps(history, indent=2, ensure_ascii=False),
                file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Zone principale divisée en deux colonnes
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat avec BellAI")
        
        # Zone de conversation
        chat_container = st.container()
        
        with chat_container:
            # Afficher l'historique
            for i, msg in enumerate(st.session_state.conversation_history):
                if msg['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(msg['content'])
                else:
                    with st.chat_message("assistant"):
                        st.write(msg['content'])
                        
                        # Afficher les intentions détectées
                        if msg.get('intentions_detected'):
                            st.info(f"🎯 {len(msg['backend_actions'])} intention(s) détectée(s)")
        
        # Zone de saisie
        st.markdown("---")
        
        # Messages de test rapide
        st.subheader("⚡ Messages de Test Rapide")
        test_buttons_col1, test_buttons_col2, test_buttons_col3 = st.columns(3)
        
        with test_buttons_col1:
            if st.button("🍽️ J'ai faim"):
                process_test_message("J'ai faim, je voudrais manger")
            if st.button("💆 Je veux un massage"):
                process_test_message("Je voudrais un massage relaxant")
        
        with test_buttons_col2:
            if st.button("🛎️ Room service"):
                process_test_message("Pouvez-vous livrer quelque chose dans ma chambre ?")
            if st.button("🚗 Besoin taxi"):
                process_test_message("J'ai besoin d'un taxi pour l'aéroport")
        
        with test_buttons_col3:
            if st.button("😠 Pas satisfait"):
                process_test_message("Je ne suis pas satisfait, je veux parler au responsable")
            if st.button("ℹ️ Info hôtel"):
                process_test_message("Présentez-moi votre hôtel")
        
        # Saisie manuelle
        st.subheader("✏️ Message Personnalisé")
        user_input = st.text_input("Tapez votre message:", key="user_input")
        
        col_send, col_clear = st.columns([1, 1])
        with col_send:
            if st.button("📤 Envoyer", type="primary") and user_input:
                process_test_message(user_input)
                # Effacer le champ après envoi
                st.session_state.user_input = ""
                st.rerun()
        
        with col_clear:
            if st.button("🗑️ Effacer Chat"):
                st.session_state.conversation_history = []
                st.rerun()
    
    with col2:
        st.header("🎯 Actions Backend")
        
        # Actions en attente
        pending_actions = bellai_agent.get_pending_actions()
        
        if pending_actions:
            st.subheader("⏳ Actions en Attente")
            
            for action in pending_actions:
                with st.expander(f"📋 {action['action_type']}", expanded=True):
                    st.write(f"**ID:** `{action['id']}`")
                    st.write(f"**Service:** {action['data'].get('service', 'N/A')}")
                    st.write(f"**Message:** {action['data'].get('user_message', 'N/A')}")
                    
                    # Boutons d'action
                    action_col1, action_col2 = st.columns(2)
                    
                    with action_col1:
                        if st.button(f"✅ Confirmer", key=f"confirm_{action['id']}"):
                            confirm_backend_action(action['id'])
                    
                    with action_col2:
                        if st.button(f"❌ Annuler", key=f"cancel_{action['id']}"):
                            cancel_backend_action(action['id'])
                    
                    # Afficher les données complètes
                    if st.checkbox("🔍 Voir Données Complètes", key=f"show_data_{action['id']}"):
                        st.json(action['data'])
        else:
            st.info("Aucune action en attente")
        
        # Historique des actions confirmées
        st.subheader("✅ Actions Confirmées")
        
        completed_actions = list(action_manager.completed_actions.values())
        
        if completed_actions:
            for action in completed_actions[-5:]:  # 5 dernières
                st.success(f"✅ {action.action_type}")
        else:
            st.info("Aucune action confirmée")
        
        # Zone de debug
        st.subheader("🔧 Debug")
        
        if st.checkbox("Mode Debug"):
            st.write("**Session State:**")
            st.json({
                "session_id": st.session_state.session_id,
                "conversation_length": len(st.session_state.conversation_history),
                "pending_actions": len(pending_actions)
            })

# =============================================================================
# FONCTIONS DE TRAITEMENT
# =============================================================================

def process_test_message(message: str):
    """Traite un message de test"""
    
    # Ajouter le message utilisateur
    st.session_state.conversation_history.append({
        'role': 'user',
        'content': message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Afficher un spinner pendant le traitement
    with st.spinner("🤖 BellAI réfléchit..."):
        try:
            # Traiter le message
            result = process_message_sync(message)
            
            # Ajouter la réponse
            response_msg = {
                'role': 'assistant',
                'content': result['response'],
                'timestamp': datetime.now().isoformat(),
                'intentions_detected': result['intentions_detected'],
                'backend_actions': result['backend_actions']
            }
            
            st.session_state.conversation_history.append(response_msg)
            
            # Mettre à jour les actions en attente
            st.session_state.pending_actions = result['backend_actions']
            
            # Message de succès
            if result['intentions_detected']:
                st.success(f"🎯 {len(result['backend_actions'])} intention(s) détectée(s) !")
            
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            # Ajouter message d'erreur à l'historique
            st.session_state.conversation_history.append({
                'role': 'assistant',
                'content': f"Désolé, une erreur s'est produite: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'intentions_detected': False,
                'backend_actions': []
            })
    
    # Recharger l'interface
    st.rerun()

def confirm_backend_action(action_id: str):
    """Confirme une action backend"""
    
    with st.spinner("⚙️ Confirmation en cours..."):
        try:
            result = confirm_action_sync(action_id)
            
            if result['action_confirmed']:
                st.success("✅ Action confirmée !")
                
                # Afficher le tool call généré
                if result.get('tool_call'):
                    st.code(result['tool_call'], language='json')
                
                # Ajouter à l'historique de conversation
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': result['response'],
                    'timestamp': datetime.now().isoformat(),
                    'intentions_detected': False,
                    'backend_actions': []
                })
                
            else:
                st.error("❌ Échec de confirmation")
                
        except Exception as e:
            st.error(f"❌ Erreur de confirmation: {str(e)}")
    
    st.rerun()

def cancel_backend_action(action_id: str):
    """Annule une action backend"""
    
    try:
        success = bellai_agent.cancel_action(action_id)
        
        if success:
            st.success("❌ Action annulée")
        else:
            st.error("Action non trouvée")
            
    except Exception as e:
        st.error(f"Erreur d'annulation: {str(e)}")
    
    st.rerun()

# =============================================================================
# ZONE D'EXEMPLES ET AIDE
# =============================================================================

def show_examples():
    """Affiche des exemples d'utilisation"""
    
    st.header("📚 Exemples d'Utilisation")
    
    examples = [
        {
            "category": "🍽️ Restaurant",
            "examples": [
                "J'ai faim",
                "Je voudrais manger",
                "Pouvez-vous me recommander votre restaurant ?",
                "Réserver une table"
            ]
        },
        {
            "category": "💆 Spa",
            "examples": [
                "Je veux un massage",
                "Besoin de détente",
                "Services spa disponibles ?",
                "Réserver un soin"
            ]
        },
        {
            "category": "🛎️ Services",
            "examples": [
                "Room service disponible ?",
                "Livraison en chambre",
                "J'ai besoin d'aide",
                "Contacter la réception"
            ]
        },
        {
            "category": "😠 Escalade",
            "examples": [
                "Je ne suis pas satisfait",
                "Parler au responsable",
                "J'ai une plainte",
                "Problème urgent"
            ]
        }
    ]
    
    for example_group in examples:
        with st.expander(example_group["category"]):
            for example in example_group["examples"]:
                st.code(f'"{example}"')

# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    # Navigation dans la sidebar
    with st.sidebar:
        st.markdown("---")
        page = st.selectbox(
            "📄 Navigation",
            ["💬 Chat Principal", "📚 Exemples", "🔧 Configuration"]
        )
    
    if page == "💬 Chat Principal":
        main()
    elif page == "📚 Exemples":
        show_examples()
    elif page == "🔧 Configuration":
        st.header("🔧 Configuration")
        st.info("Configuration des paramètres BellAI (à implémenter)")
        
        # Paramètres de debug
        st.subheader("🐛 Debug")
        if st.button("🧹 Nettoyer toutes les sessions"):
            action_manager.pending_actions.clear()
            action_manager.completed_actions.clear()
            st.success("Sessions nettoyées")
        
        st.subheader("📊 Statistiques Globales")
        st.json({
            "total_sessions": len(chat_memory.conversations),
            "pending_actions": len(action_manager.pending_actions),
            "completed_actions": len(action_manager.completed_actions)
        })