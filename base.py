import os
import time
import sys

import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
# MISTRAL EXAMPLE
from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool

# Charger les variables depuis .env
load_dotenv(override=True)

# Récupérer les clés API
mistral_api_key = os.getenv("MISTRAL_API_KEY")
hotel_api_token = os.getenv("HOTEL_API_TOKEN")

# LLM Configuration
model = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0.7,
    max_retries=5
)


def print_stream(stream):
    reponse = ""
    for s in stream:
        message: HumanMessage = s["messages"][-1]
        if isinstance(message, tuple):
            # Ne pas afficher les messages de traitement
            pass
        else:
            reponse = message.content
            # Ne pas afficher les messages avec pretty_print
    return reponse

def api_ask_agent(user_message: str, conversation_history=None, system_instruction=None):
    """
    Interroge l'agent avec l'historique de conversation pour maintenir le contexte
    
    Args:
        user_message: Le message de l'utilisateur
        conversation_history: Liste de tuples (role, contenu) représentant l'historique
        system_instruction: Instruction système optionnelle pour guider le comportement de l'agent
    
    Returns:
        La réponse de l'agent
    """
    # Si pas d'historique fourni, initialiser avec une liste vide
    if conversation_history is None:
        conversation_history = []
    
    # Préparation des messages avec l'historique complet
    messages = conversation_history.copy()
    
    # Ajouter l'instruction système si elle est fournie
    if system_instruction:
        if not any(role == "system" for role, _ in messages):
            messages.insert(0, ("system", system_instruction))
    
    # Ajouter le message de l'utilisateur
    messages.append(("user", user_message))
    
    inputs = {"messages": messages}
    reponse = ""
    reussi = False
    iteration = 0
    max_iteration = 5
    while (not reussi and iteration < max_iteration):
        try:
            reponse = print_stream(graph.stream(inputs, stream_mode="values"))
            reussi = True
        except Exception as e:
            # Ne pas afficher les messages d'erreur de tentative
            iteration += 1
            time.sleep(1)
    return reponse

@tool
def get_restaurants():
    """Get All Restaurants"""
    name: str = "api_restaurants"
    description: str = "Get All Restaurants"
    api_url = "https://app-584240518682.europe-west9.run.app/api/restaurants/"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None


@tool
def get_spas():
    """Get All Spas"""
    name: str = "api_spas"
    description: str = "Get All Spas"
    api_url = "https://app-584240518682.europe-west9.run.app/api/spas/"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()

    else:
        return None

@tool
def get_meals():
    """Get All Meals"""
    name: str = "api_meals"
    description: str = "Get All Meals"
    api_url = "https://app-584240518682.europe-west9.run.app/api/meals/"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()

    else:
        return None

@tool
def get_reservation_by_id_reservation(id: int):
    """Get Informations on a reservation by id reservation"""
    name: str = "api_reservation_reservation"
    description: str = "Get Informations on a reservation by id reservation"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/reservations/{id}/"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def get_reservation_by_id_client(id: int):
    """Get Informations on a reservation by id client"""
    name: str = "api_reservation_client"
    description: str = "Get Informations on a reservation by id client"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/reservations/?client={id}"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def get_client_by_id(id: int):
    """Get Informations on a client by id client"""
    name: str = "api_client_by_id"
    description: str = "Get Informations on a client by id client"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/clients/{id}/"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def get_client_by_search(search: str):
    """Get Informations on a client by search"""
    name: str = "api_client_search"
    description: str = "Get Informations on a client by search"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/clients/?search={search}"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def get_schema():
    """Get OpenApi3 schema for this API of https://app-584240518682.europe-west9.run.app/api/"""
    name: str = "api_schema"
    description: str = "Get OpenApi3 schema for this API of https://app-584240518682.europe-west9.run.app/api/"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/clients/{id}/"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def search_duckduckgo(search: str):
    """Search on the Web"""
    name: str = "api_duckduckgo"
    description: str = "Search on the web"
    api_url = f"http://api.duckduckgo.com/?q={search}&format=json"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data.get("AbstractText", "Aucune information trouvée.")
    return "Erreur lors de la recherche."

tools = [get_restaurants, get_spas, get_meals, get_client_by_id, get_client_by_search, get_reservation_by_id_reservation, get_reservation_by_id_client, get_schema, search_duckduckgo]


# Définir le graphe
from langgraph.prebuilt import create_react_agent

graph = create_react_agent(model, tools=tools)

def run_interactive_agent():
    """Fonction pour exécuter l'agent en mode interactif avec uniquement les messages essentiels"""
    # Initialiser l'historique de conversation
    conversation_history = []
    
    # Définir le comportement de l'agent via une instruction système
    system_instruction = """
    Tu es Kimrau, le responsable temporaire de l'Hôtel California, un établissement luxueux et prestigieux.
    Tu dois accueillir les clients avec courtoisie et professionnalisme, répondre à leurs questions et les aider.
    Pour le premier message, présente-toi et souhaite la bienvenue au client à l'Hôtel California.
    Après chaque réponse à une question, demande poliment s'il y a autre chose que tu peux faire pour aider le client.
    Si le client indique qu'il n'a plus besoin d'aide (en disant par exemple "rien d'autre merci"), remercie-le et dis au revoir poliment.
    Utilise un langage formel mais chaleureux, adapté à un établissement hôtelier de luxe.
    """
    
    # Demander à l'agent de générer le message d'accueil
    greeting_response = api_ask_agent("Présente-toi en tant que responsable de l'hôtel et souhaite la bienvenue au client.", [], system_instruction)
    
    # Afficher uniquement la réponse de l'agent
    print(f"\nKimrau: {greeting_response}\n")
    
    # Ajouter le message système à l'historique (caché pour l'utilisateur)
    conversation_history.append(("system", system_instruction))
    
    # Ajouter le message de demande de présentation (caché pour l'utilisateur)
    conversation_history.append(("user", "Présente-toi en tant que responsable de l'hôtel et souhaite la bienvenue au client."))
    
    # Ajouter la réponse de bienvenue à l'historique
    conversation_history.append(("assistant", greeting_response))
    
    # Boucle de conversation
    while True:
        # Obtenir la demande de l'utilisateur avec un préfixe simple
        user_input = input("Vous: ")
        
        # Vérifier si l'utilisateur souhaite terminer la conversation
        if user_input.lower() in ["rien d'autre merci", "rien d'autre", "au revoir", "merci", "rien merci", "quit", "exit"]:
            # Demander à l'agent de générer un message d'au revoir personnalisé
            farewell_response = api_ask_agent(user_input, conversation_history)
            
            # Afficher uniquement la réponse finale
            print(f"\nKimrau: {farewell_response}\n")
            break
        
        # Indication discrète que la requête est en cours de traitement
        print("\nKimrau réfléchit...", end="\r")
        
        try:
            # Passer l'historique de conversation pour maintenir le contexte
            response = api_ask_agent(user_input, conversation_history)
            
            # Effacer la ligne "réfléchit"
            print(" " * 30, end="\r")
            
            # Afficher uniquement la réponse de l'agent
            print(f"\nKimrau: {response}\n")
            
            # Ajouter la demande de l'utilisateur à l'historique
            conversation_history.append(("user", user_input))
            
            # Ajouter la réponse de l'agent à l'historique
            conversation_history.append(("assistant", response))
            
        except Exception as e:
            # En cas d'erreur, afficher un message simple
            print(f"\nKimrau: Je suis désolé, j'ai eu un problème technique. Pourriez-vous reformuler votre demande?\n")

def save_conversation(conversation_history, filename="conversation_log.txt"):
    """Sauvegarde l'historique de conversation dans un fichier"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=== HISTORIQUE DE CONVERSATION AVEC L'AGENT HÔTEL CALIFORNIA ===\n\n")
        for role, content in conversation_history:
            if role != "system":  # Ne pas inclure les instructions système
                f.write(f"{role.upper()}: {content}\n\n")
    print(f"Conversation sauvegardée dans {filename}")

if __name__ == "__main__":
    # Effacer le terminal au démarrage pour une expérience plus propre
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/MacOS
        os.system('clear')
        
    run_interactive_agent()