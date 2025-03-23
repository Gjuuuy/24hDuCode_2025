import os
import time
import sys
import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool

# Charger les variables depuis .env
load_dotenv(override=True)

# Récupérer les clés API
mistral_api_key = os.getenv("MISTRAL_API_KEY")
hotel_api_token = os.getenv("HOTEL_API_TOKEN")

# Configuration des mots-clés pour la détection des méthodes HTTP
HTTP_KEYWORDS = {
    'GET': ['obtenir', 'voir', 'afficher', 'consulter', 'rechercher', 'lister'],
    'POST': ['créer', 'ajouter', 'réserver', 'envoyer', 'demander', 'faire'],
    'PUT': ['modifier', 'mettre à jour', 'changer', 'éditer', 'actualiser'],
    'DELETE': ['supprimer', 'annuler', 'effacer', 'désactiver', 'retirer']
}

def detect_http_method(request_text: str) -> str:
    """Détection de la méthode HTTP basée sur le texte de la requête"""
    request_text = request_text.lower()
    
    for method, keywords in HTTP_KEYWORDS.items():
        if any(keyword in request_text for keyword in keywords):
            return method
    
    return 'GET'  # Méthode par défaut

def api_ask_agent(user_message: str, conversation_history=None, system_instruction=None):
    """Interroge l'agent avec l'historique de conversation pour maintenir le contexte"""
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
    response = ""
    success = False
    iteration = 0
    max_iteration = 5
    
    while (not success and iteration < max_iteration):
        try:
            response = print_stream(graph.stream(inputs, stream_mode="values"))
            success = True
        except Exception as e:
            iteration += 1
            time.sleep(1)
    
    return response

def print_stream(stream):
    """Fonction pour extraire la réponse d'un stream"""
    response = ""
    for s in stream:
        message: HumanMessage = s["messages"][-1]
        if isinstance(message, tuple):
            pass
        else:
            response = message.content
    return response

@tool
def get_restaurants():
    """Get All Restaurants"""
    name: str = "api_restaurants"
    description: str = "Get All Restaurants"
    api_url = "https://app-584240518682.europe-west9.run.app/api/restaurants/"
    headers = {"Authorization": f"Token {hotel_api_token}"}
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
    headers = {"Authorization": f"Token {hotel_api_token}"}
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
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def post_reservation(id_client: int, id_restaurant: int, date: str, id_meal: str, number_of_guests: int, special_requests: str):
    """Post a reservation into the database"""
    name: str = "api_post_reservation"
    description: str = "Post a reservation into the database"
    api_url = "https://app-584240518682.europe-west9.run.app/api/reservations/"
    json = {
        "client": id_client,
        "restaurant": id_restaurant,
        "date": date,
        "meal": id_meal,
        "number_of_guests": number_of_guests,
        "special_requests": special_requests
    }
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.post(api_url, json=json, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def put_reservation(id_reservation: int, id_client: int, id_restaurant: int, date: str, id_meal: str, number_of_guests: int, special_requests: str):
    """Put a reservation into the database"""
    name: str = "api_put_reservation"
    description: str = "Put a reservation into the database"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/reservations/{id_reservation}/"
    json_data = {
        "client": id_client,
        "restaurant": id_restaurant,
        "date": date,
        "meal": id_meal,
        "number_of_guests": number_of_guests,
        "special_requests": special_requests
    }
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.put(api_url, json=json_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to update reservation: {response.status_code}", "details": response.text}

@tool
def delete_reservation(id_reservation: int):
    """Supprime une réservation de la base de données de l'hôtel"""
    name: str = "api_delete_reservation"
    description: str = "Delete a reservation from the database"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/reservations/{id_reservation}/"
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.delete(api_url, headers=headers)
    
    if response.status_code == 204:
        return {"message": "Reservation successfully deleted"}
    else:
        return {"error": f"Failed to delete reservation: {response.status_code}", "details": response.text}


@tool
def get_reservation_by_id_reservation(id: int):
    """Récupère les informations d'une réservation spécifique à partir de son identifiant"""
    name: str = "api_reservation_reservation"
    description: str = "Get Informations on a reservation by id reservation"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/reservations/{id}/"
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def get_reservation_by_id_client(id: int):
    """Récupère les informations sur les réservations d'un client spécifique à partir de son identifiant"""
    name: str = "api_reservation_client"
    description: str = "Get Informations on a reservation by id client"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/reservations/?client={id}"
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def post_client(name_client: str, phone_number: str, room_number: str, special_requests: str):
    """Ajoute un nouveau client dans la base de données de l'hôtel"""
    name: str = "api_post_client"
    description: str = "Post a client into the database"
    api_url = "https://app-584240518682.europe-west9.run.app/api/clients/"
    json = {
        "name": name_client,
        "phone_number": phone_number,
        "room_number": room_number,
        "special_requests": special_requests
    }
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.post(api_url, json=json, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
@tool
def put_client(id_client: int, name_client: str, phone_number: str, room_number: str, special_requests: str):
    """Change un client dans la base de données de l'hôtel"""
    name: str = "api_put_client"
    description: str = "Put a client into the database"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/clients/{id_client}/"
    json = {
        "name": name_client,
        "phone_number": phone_number,
        "room_number": room_number,
        "special_requests": special_requests
    }
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.put(api_url, json=json, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def delete_client(id_client: int):
    """Supprime un client de la base de données de l'hôtel"""
    name: str = "api_delete_client"
    description: str = "Delete a client from the database"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/clients/{id_client}/"
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.delete(api_url, headers=headers)
    
    if response.status_code == 204:
        return {"message": "Client successfully deleted"}
    else:
        return {"error": f"Failed to delete client: {response.status_code}", "details": response.text}


@tool
def get_client_by_id(id: int):
    """Récupère les informations d'un client à partir de son identifiant unique"""
    name: str = "api_client_by_id"
    description: str = "Get Informations on a client by id client"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/clients/{id}/"
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def get_client_by_search(search: str):
    """Récupère les informations d'un client à partir de spécificité comme le nom du client"""
    name: str = "api_client_search"
    description: str = "Get Informations on a client by search"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/clients/?search={search}"
    headers = {"Authorization": f"Token {hotel_api_token}"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def get_schema():
    """Get OpenApi3 schema for this API"""
    name: str = "api_schema"
    description: str = "Get OpenApi3 schema for this API"
    api_url = "https://app-584240518682.europe-west9.run.app/api/clients/"
    headers = {"Authorization": f"Token {hotel_api_token}"}
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

tools = [get_restaurants, get_spas, get_meals, post_client, put_client, delete_client, get_client_by_id, get_client_by_search, post_reservation, put_reservation, delete_reservation, get_reservation_by_id_reservation, get_reservation_by_id_client, get_schema, search_duckduckgo]

# Définir le graphe
from langgraph.prebuilt import create_react_agent
graph = create_react_agent(model=ChatMistralAI(model="mistral-small-latest", temperature=0.7, max_retries=5), tools=tools)

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
    print(f"\nKimrau: {greeting_response}\n")
    
    # Ajouter le message système à l'historique (caché pour l'utilisateur)
    conversation_history.append(("system", system_instruction))
    conversation_history.append(("user", "Présente-toi en tant que responsable de l'hôtel et souhaite la bienvenue au client."))
    conversation_history.append(("assistant", greeting_response))
    
    # Boucle de conversation
    while True:
        user_input = input("Vous: ")
        
        if user_input.lower() in ["rien d'autre merci", "rien d'autre", "au revoir", "merci", "rien merci", "quit", "exit"]:
            farewell_response = api_ask_agent(user_input, conversation_history)
            print(f"\nKimrau: {farewell_response}\n")
            break
            
        print("\nKimrau réfléchit...", end="\r")
        try:
            response = api_ask_agent(user_input, conversation_history)
            print(" " * 30, end="\r")
            print(f"\nKimrau: {response}\n")
            conversation_history.append(("user", user_input))
            conversation_history.append(("assistant", response))
        except Exception as e:
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