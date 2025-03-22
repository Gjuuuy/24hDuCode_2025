import os
import time

import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
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
    temperature=0,
    max_retries=5
)


def print_stream(stream):
    reponse = ""
    for s in stream:
        message: HumanMessage = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            reponse = message.content
            message.pretty_print()
    return reponse

def api_ask_agent(user_message: str):
    inputs = {"messages":["user",user_message]}
    reponse = ""
    reussi = False
    iteration = 0
    max_iteration = 5
    while (not reussi and iteration < max_iteration):
        try:
            reponse = print_stream(graph.stream(inputs, stream_mode="values"))
            reussi = True
        except:
            print("tentative raté")
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

if __name__ == "__main__":
    inputs = {"messages": [("user", "Quels sont les menus proposés ?")]}
    reussi = False
    iteration = 0
    max_iteration = 5
    while(not reussi and iteration < max_iteration):
        try:
            print_stream(graph.stream(inputs, stream_mode="values"))
            reussi = True
        except:
            print("tentative raté")
            iteration += 1
            time.sleep(1)


