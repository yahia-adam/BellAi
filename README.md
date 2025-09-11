# BellAI - Assistant IA pour Hôtellerie

## 📝 Description

BellAI est un assistant conversationnel intelligent conçu spécifiquement pour l'industrie hôtelière. Il utilise l'IA pour fournir un service client personnalisé, détecter les intentions des clients et automatiser les processus de réservation et de service.

## 🏨 Contexte

Le projet simule l'assistant IA de l'**Hôtel Oceania Paris Porte de Versailles**, un établissement 4 étoiles de 250 chambres situé au 52 Rue d'Oradour-sur-Glane, 75015 Paris.

## ✨ Fonctionnalités Principales

### 🤖 Assistant Conversationnel Intelligent
- **Personnalisation automatique** : Récupère le profil client et adapte les réponses
- **Mémoire conversationnelle** : Maintien du contexte sur plusieurs interactions
- **Réponses contextualisées** : Utilise l'historique et les préférences du client

### 🎯 Détection d'Intentions Avancée
- **Réservations automatiques** : Restaurant, spa, room service
- **Escalade intelligente** : Détection des problèmes nécessitant intervention humaine
- **Demandes conciergerie** : Transport, activités externes, recommandations
- **Notifications staff** : Alertes automatiques pour l'équipe hôtelière

### 📊 Gestion des Données Client
- **Profil complet** : Nom, chambre, statut (VIP), type de séjour
- **Préférences** : Cuisine, allergies, boissons, services favoris
- **Historique** : Services utilisés, satisfaction, réservations passées
- **Séjour actuel** : Détails de la réservation, services inclus

### 🔧 Outils et Services
- **Informations hôtel** : Services, horaires, tarifs, contact
- **Gestion des réservations** : Consultation et création de réservations
- **Actions backend** : Interface entre l'IA et les systèmes hôteliers

## 🛠️ Architecture Technique

### Technologies Utilisées
- **Framework IA** : LangChain avec Azure OpenAI
- **Interface utilisateur** : Streamlit pour les tests et démos
- **Backend** : FastAPI (prévu pour l'intégration)
- **Mémoire** : Système de mémoire conversationnelle persistante
- **Tests** : Pytest pour les tests unitaires

### Structure du Projet
```
bellAiLangchain/
├── src/
│   ├── core/
│   │   ├── agent.py              # Agent principal BellAI
│   │   ├── intention.py   # Système de détection d'intentions
│   │   └── memory.py     # Gestionnaire de mémoire conversationnelle
│   ├── tools/
│   │   ├── client.py            # Outils de gestion client
│   │   └── hotel.py             # Outils d'information hôtel
│   ├── streamlit_app.py         # Interface de test Streamlit
│   └── main.py                  # Point d'entrée principal
├── tests/                       # Tests unitaires
└── requirements.txt             # Dépendances Python
```

## 🚀 Installation et Configuration

### Prérequis
- Python 3.10+
- Compte Azure OpenAI
- Variables d'environnement configurées

### Installation
```bash
# Cloner le repository
git clone [URL_DU_REPO]
cd bellAiLangchain

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés Azure OpenAI
```

### Variables d'Environnement Requises
```bash
AZURE_OPENAI_API_KEY=votre_clé_api
AZURE_OPENAI_ENDPOINT=votre_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=nom_du_déploiement
AZURE_OPENAI_API_VERSION=2024-10-21
```

## 💻 Utilisation

### Interface de Test Streamlit
```bash
# Lancer l'interface de test
./.venv/bin/python3 -m streamlit run src/streamlit_app.py
```

### Utilisation Programmatique
```python
from src.core.agent import BellAIAgent
import asyncio

# Initialiser l'agent
agent = BellAIAgent()

# Traiter un message
async def main():
    response = await agent.process_message("Bonjour", "session_123")
    print(response["response"])
    
    # Vérifier les intentions détectées
    if response["intentions_detected"]:
        print(f"Actions détectées: {response['backend_actions']}")

asyncio.run(main())
```

## 📋 Exemples d'Utilisation

### Conversations Typiques

**Réservation Restaurant :**
```
Client: "J'ai faim, je voudrais manger"
BellAI: "Bonjour Adam ! Je vois que vous appréciez la cuisine française. 
        Notre restaurant Le Patio propose un excellent menu français ce soir. 
        Voulez-vous que j'ouvre l'interface de réservation ?"
```

**Demande Spa :**
```
Client: "Je voudrais un massage relaxant"
BellAI: "Parfait Adam ! Je vois que vous avez déjà apprécié nos services spa. 
        Notre spa est ouvert jusqu'à 23h. Souhaitez-vous réserver votre massage habituel ?"
```

**Escalade vers Humain :**
```
Client: "Je ne suis pas satisfait, je veux parler au responsable"
BellAI: "Je comprends votre préoccupation Adam. Je vais immédiatement 
        vous mettre en contact avec notre responsable. 
        Il vous contactera sous peu."
```

## 🧪 Tests

### Exécuter les Tests
```bash
# Tests complets
pytest tests/

# Tests spécifiques
pytest tests/test_intentions.py
pytest tests/test_agent.py
```

### Tests Disponibles
- **test_agent.py** : Tests de l'agent principal
- **test_intentions.py** : Tests de détection d'intentions
- **test_chat_memory.py** : Tests de la mémoire conversationnelle
- **salutations.py** : Tests des salutations
- **hotel_informations.py** : Tests des informations hôtel

## 🔄 Flux de Fonctionnement

1. **Initialisation** : Récupération du profil client et infos hôtel
2. **Analyse du message** : Traitement du langage naturel
3. **Détection d'intentions** : Identification des besoins client
4. **Personnalisation** : Adaptation selon préférences et historique
5. **Génération d'actions** : Création d'actions backend si nécessaire
6. **Réponse contextualisée** : Réponse personnalisée au client

## 🎯 Intentions Détectées

### Types d'Intentions
- **booking_restaurant** : Réservation restaurant
- **booking_spa** : Réservation spa
- **booking_room_service** : Commande room service
- **concierge_request** : Demande conciergerie
- **escalate_human** : Escalade vers humain
- **send_notification** : Notification équipe

### Actions Backend Générées
- **create_booking_[service]** : Ouverture interface de réservation
- **escalate_to_human** : Transfert vers agent humain
- **concierge_request** : Redirection conciergerie
- **send_notification** : Alerte équipe hôtelière

## 📊 Monitoring et Analytics

### Métriques Disponibles
- Nombre de conversations par session
- Intentions détectées par type
- Taux de satisfaction client
- Actions confirmées vs annulées
- Temps de réponse moyen

### Export de Données
- Historique conversationnel en JSON
- Logs d'actions backend
- Statistiques d'utilisation

## 🔒 Sécurité et Conformité

### Données Personnelles
- Respect du RGPD pour les données client
- Chiffrement des conversations sensibles
- Anonymisation pour les analytics

### Contrôles d'Accès
- Authentification requise pour les actions backend
- Logs d'audit complets
- Validation des entrées utilisateur

## 🚀 Roadmap

### Fonctionnalités Prévues
- [ ] Intégration API REST complète
- [ ] Support multilingue avancé
- [ ] Interface web responsive
- [ ] Analytics en temps réel
- [ ] Intégration systèmes PMS hôteliers

### Améliorations IA
- [ ] Modèles fine-tunés pour l'hôtellerie
- [ ] Reconnaissance vocale
- [ ] Sentiment analysis avancé
- [ ] Prédiction des besoins client

## 👥 Contribution

### Structure de Développement
- **Agent principal** : `/src/core/agent.py`
- **Système d'intentions** : `/src/core/intention_system.py`
- **Outils client** : `/src/tools/client.py`
- **Outils hôtel** : `/src/tools/hotel.py`

### Standards de Code
- Documentation complète des fonctions
- Tests unitaires obligatoires
- Respect des conventions Python PEP8
- Logging structuré

## 📞 Support

### Contact Technique
- **Développeur principal** : Adam YAHIA
- **Documentation** : README.md et commentaires inline
- **Tests** : Couverture > 80%

### Ressources
- Tests d'intégration disponibles
- Interface de debug Streamlit
- Logs détaillés pour troubleshooting

---

**BellAI** - Transforming Hotel Guest Experience with AI 🏨✨
