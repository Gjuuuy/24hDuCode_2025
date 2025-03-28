import os
import time
import sys
import re

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
            message.pretty_print()

    reponse = re.sub(r"\[\{.*?\}\]", "", reponse)

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
    """Get All Restaurants

    Exemple response body
        {
      "count": 3,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": 19,
          "name": "Le Maison Royale",
          "description": "Une expérience gastronomique raffinée mettant en vedette les saveurs de la cuisine française contemporaine",
          "capacity": 80,
          "opening_hours": "07:00-23:00",
          "location": "Rez-de-chaussée",
          "is_active": true
        },
        {
          "id": 20,
          "name": "Bistrot de la piscine",
          "description": "Une cuisine décontractée aux saveurs méditerranéennes",
          "capacity": 40,
          "opening_hours": "11:00-22:00",
          "location": "Terrasse de la piscine",
          "is_active": true
        },
        {
          "id": 21,
          "name": "Le Belvedere",
          "description": "Une table d'exception avec vue panoramique sur la ville",
          "capacity": 60,
          "opening_hours": "16:00-23:00",
          "location": "13ème étage",
          "is_active": true
        }
      ]
    }"""
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
    """Get All Spas

        Exemple Response body
        [
      {
        "id": 1,
        "name": "Relaxation Spa",
        "description": "Un spa dédié à la relaxation avec des massages professionnels et des bains chauds.",
        "location": "123 Wellness Street, Paris, France",
        "phone_number": "+33 1 23 45 67 89",
        "email": "contact@relaxationspa.fr",
        "opening_hours": "Lundi - Dimanche : 09:00 - 20:00",
        "created_at": "2024-12-08T15:32:43.062749+01:00",
        "updated_at": "2024-12-08T15:32:43.062754+01:00"
      },
      {
        "id": 2,
        "name": "Thermal Bliss Spa",
        "description": "Découvrez nos sources thermales naturelles et nos soins corporels personnalisés.",
        "location": "456 Thermal Avenue, Lyon, France",
        "phone_number": "+33 4 56 78 90 12",
        "email": "info@thermalblissspa.fr",
        "opening_hours": "Lundi - Vendredi : 10:00 - 18:00",
        "created_at": "2024-12-08T15:32:43.063120+01:00",
        "updated_at": "2024-12-08T15:32:43.063124+01:00"
      },
      {
        "id": 3,
        "name": "Luxury Escape Spa",
        "description": "Un spa haut de gamme offrant des soins de luxe et des expériences uniques.",
        "location": "789 Luxury Road, Nice, France",
        "phone_number": "+33 6 98 76 54 32",
        "email": "hello@luxuryescapespa.fr",
        "opening_hours": "Samedi - Dimanche : 11:00 - 23:00",
        "created_at": "2024-12-08T15:32:43.063471+01:00",
        "updated_at": "2024-12-08T15:32:43.063475+01:00"
      },
      {
        "id": 4,
        "name": "Relaxation Spa",
        "description": "Un spa dédié à la relaxation avec des massages professionnels et des bains chauds.",
        "location": "123 Wellness Street, Paris, France",
        "phone_number": "+33 1 23 45 67 89",
        "email": "contact@relaxationspa.fr",
        "opening_hours": "Lundi - Dimanche : 09:00 - 20:00",
        "created_at": "2024-12-08T15:33:20.203330+01:00",
        "updated_at": "2024-12-08T15:33:20.203334+01:00"
      },
      {
        "id": 5,
        "name": "Thermal Bliss Spa",
        "description": "Découvrez nos sources thermales naturelles et nos soins corporels personnalisés.",
        "location": "456 Thermal Avenue, Lyon, France",
        "phone_number": "+33 4 56 78 90 12",
        "email": "info@thermalblissspa.fr",
        "opening_hours": "Lundi - Vendredi : 10:00 - 18:00",
        "created_at": "2024-12-08T15:33:20.203794+01:00",
        "updated_at": "2024-12-08T15:33:20.203800+01:00"
      },
      {
        "id": 6,
        "name": "Luxury Escape Spa",
        "description": "Un spa haut de gamme offrant des soins de luxe et des expériences uniques.",
        "location": "789 Luxury Road, Nice, France",
        "phone_number": "+33 6 98 76 54 32",
        "email": "hello@luxuryescapespa.fr",
        "opening_hours": "Samedi - Dimanche : 11:00 - 23:00",
        "created_at": "2024-12-08T15:33:20.204194+01:00",
        "updated_at": "2024-12-08T15:33:20.204199+01:00"
      },
      {
        "id": 7,
        "name": "Relaxation Spa",
        "description": "Un spa dédié à la relaxation avec des massages professionnels et des bains chauds.",
        "location": "123 Wellness Street, Paris, France",
        "phone_number": "+33 1 23 45 67 89",
        "email": "contact@relaxationspa.fr",
        "opening_hours": "Lundi - Dimanche : 09:00 - 20:00",
        "created_at": "2025-03-21T17:57:54.064799+01:00",
        "updated_at": "2025-03-21T17:57:54.064803+01:00"
      },
      {
        "id": 8,
        "name": "Thermal Bliss Spa",
        "description": "Découvrez nos sources thermales naturelles et nos soins corporels personnalisés.",
        "location": "456 Thermal Avenue, Lyon, France",
        "phone_number": "+33 4 56 78 90 12",
        "email": "info@thermalblissspa.fr",
        "opening_hours": "Lundi - Vendredi : 10:00 - 18:00",
        "created_at": "2025-03-21T17:57:54.065438+01:00",
        "updated_at": "2025-03-21T17:57:54.065443+01:00"
      },
      {
        "id": 9,
        "name": "Luxury Escape Spa",
        "description": "Un spa haut de gamme offrant des soins de luxe et des expériences uniques.",
        "location": "789 Luxury Road, Nice, France",
        "phone_number": "+33 6 98 76 54 32",
        "email": "hello@luxuryescapespa.fr",
        "opening_hours": "Samedi - Dimanche : 11:00 - 23:00",
        "created_at": "2025-03-21T17:57:54.065791+01:00",
        "updated_at": "2025-03-21T17:57:54.065795+01:00"
      },
      {
        "id": 10,
        "name": "Relaxation Spa",
        "description": "Un spa dédié à la relaxation avec des massages professionnels et des bains chauds.",
        "location": "123 Wellness Street, Paris, France",
        "phone_number": "+33 1 23 45 67 89",
        "email": "contact@relaxationspa.fr",
        "opening_hours": "Lundi - Dimanche : 09:00 - 20:00",
        "created_at": "2025-03-22T11:05:30.080622+01:00",
        "updated_at": "2025-03-22T11:05:30.080639+01:00"
      },
      {
        "id": 11,
        "name": "Thermal Bliss Spa",
        "description": "Découvrez nos sources thermales naturelles et nos soins corporels personnalisés.",
        "location": "456 Thermal Avenue, Lyon, France",
        "phone_number": "+33 4 56 78 90 12",
        "email": "info@thermalblissspa.fr",
        "opening_hours": "Lundi - Vendredi : 10:00 - 18:00",
        "created_at": "2025-03-22T11:05:30.081172+01:00",
        "updated_at": "2025-03-22T11:05:30.081189+01:00"
      },
      {
        "id": 12,
        "name": "Luxury Escape Spa",
        "description": "Un spa haut de gamme offrant des soins de luxe et des expériences uniques.",
        "location": "789 Luxury Road, Nice, France",
        "phone_number": "+33 6 98 76 54 32",
        "email": "hello@luxuryescapespa.fr",
        "opening_hours": "Samedi - Dimanche : 11:00 - 23:00",
        "created_at": "2025-03-22T11:05:30.081624+01:00",
        "updated_at": "2025-03-22T11:05:30.081641+01:00"
      }
    ]
    """
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
    """Get All Meals

    Exemple response body
    {
      "count": 3,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": 19,
          "name": "Breakfast"
        },
        {
          "id": 20,
          "name": "Lunch"
        },
        {
          "id": 21,
          "name": "Dinner"
        }
      ]
    }"""
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
def put_reservation(id_reservation: int, id_client: int, id_restaurant: int, date: str, id_meal: str,
                    number_of_guests: int, special_requests: str):
    """
    Met à jour les informations d'une réservation existante dans la base de données de l'hôtel

    Args:
        id_reservation: Identifiant unique de la réservation à modifier
        id_client: Identifiant du client associé à la réservation
        id_restaurant: Identifiant du restaurant concerné
        date: Date de la réservation (format attendu: YYYY-MM-DD)
        id_meal: Identifiant du repas ou du service réservé
        number_of_guests: Nombre de personnes pour la réservation
        special_requests: Demandes particulières ou commentaires associés à la réservation

    Returns:
        Les données de la réservation mises à jour en cas de succès,
        ou un dictionnaire contenant les détails de l'erreur en cas d'échec
    """
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
    """
    Supprime une réservation de la base de données de l'hôtel

    Args:
        id_reservation: Identifiant unique de la réservation à supprimer

    Returns:
        Un dictionnaire avec un message de confirmation en cas de succès,
        ou un dictionnaire contenant les détails de l'erreur en cas d'échec
    """
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
def post_reservation(id_client: int, id_restaurant: int, date: str, id_meal: str, number_of_guests: int, special_requests: str):
    """Post a reservation into the database

    Args:
        id_client (int): L'ID du client.
        id_restaurant (int): L'ID du restaurant.
        date (str): Date de la réservation au format YYYY-MM-DD.
        id_meal (str): L'ID du repas.
        number_of_guests (int): Nombre de convives.
        special_requests (str, optional): Demandes spéciales. Par défaut "".

    Returns:
        dict | None: Les informations de la réservation ou None si erreur.
    """
    name: str = "api_post_reservation"
    description: str = "Post a reservation into the database"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/reservations/"
    json = {
        "client": id_client,
        "restaurant": id_restaurant,
        "date": date,
        "meal": id_meal,
        "number_of_guests": number_of_guests,
        "special_requests": special_requests
    }
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.post(api_url, json=json, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def get_reservation_by_id_reservation(id: int):
    """
    Récupère les informations d'une réservation spécifique à partir de son identifiant.

    Args:
        id (int): L'identifiant unique de la réservation.

    Returns:
        dict | None: Un dictionnaire contenant les détails de la réservation si la requête réussit (statut 200),
                     sinon `None` en cas d'erreur ou si la réservation n'existe pas.

    Exemples:
        >>> get_reservation_by_id_reservation(123)
        {
            "id": 123,
            "client": 45,
            "restaurant": 12,
            "date": "2025-03-23",
            "meal": 7,
            "number_of_guests": 2,
            "special_requests": "Table avec vue"
        }

    Remarque:
        - L'API requiert une authentification avec un token.
        - Si l'ID fourni ne correspond à aucune réservation, la fonction retournera `None`.
    """
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
    """
    Récupère les informations sur les réservations d'un client spécifique à partir de son identifiant.

    Args:
        id (int): L'identifiant unique du client.

    Returns:
        list[dict] | None: Une liste de dictionnaires contenant les détails des réservations du client si la requête réussit (statut 200),
                            sinon `None` en cas d'erreur ou si aucune réservation n'est trouvée.

    Exemples:
        >>> get_reservation_by_id_client(45)
        [
            {
                "id": 123,
                "client": 45,
                "restaurant": 12,
                "date": "2025-03-23",
                "meal": 7,
                "number_of_guests": 2,
                "special_requests": "Table avec vue"
            },
            {
                "id": 124,
                "client": 45,
                "restaurant": 15,
                "date": "2025-04-02",
                "meal": 3,
                "number_of_guests": 4,
                "special_requests": "Anniversaire"
            }
        ]

    Remarque:
        - L'API requiert une authentification avec un token.
        - Si l'ID fourni ne correspond à aucun client ayant des réservations, la fonction retournera `None`.
        - Cette requête peut retourner plusieurs réservations si le client en possède plusieurs.
    """
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
def put_client(id_client: int, name_client: str, phone_number: str, room_number: str, special_requests: str):
    """
    Met à jour les informations d'un client existant dans la base de données de l'hôtel

    Args:
        id_client: Identifiant unique du client à modifier
        name_client: Nom complet du client
        phone_number: Numéro de téléphone du client
        room_number: Numéro de chambre attribué au client
        special_requests: Demandes particulières ou commentaires associés au client

    Returns:
        Les données du client mises à jour en cas de succès, None en cas d'échec
    """
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
    """
    Supprime un client de la base de données de l'hôtel

    Args:
        id_client: Identifiant unique du client à supprimer

    Returns:
        Un dictionnaire avec un message de confirmation en cas de succès,
        ou un dictionnaire contenant les détails de l'erreur en cas d'échec
    """
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
def post_client(name_client: str, phone_number: str, room_number: str, special_requests: str):
    """
    Ajoute un nouveau client dans la base de données de l'hôtel.

    Args:
        name_client (str): Le nom complet du client.
        phone_number (str): Le numéro de téléphone du client.
        room_number (str): Le numéro de la chambre attribuée au client.
        special_requests (str): Toute demande spécifique formulée par le client.

    Returns:
        str | None: null si la requête réussit (statut 200),
                     sinon `None` en cas d'erreur.

    Exemples:
        >>> post_client("Jean Dupont", "+33612345678", "205", "Oreillers supplémentaires")
        {
            "id": 1,
            "name": "Jean Dupont",
            "phone_number": "+33612345678",
            "room_number": "205",
            "special_requests": "Oreillers supplémentaires"
        }

    Remarque:
        - L'API requiert une authentification avec un token.
        - Assurez-vous que les informations du client sont correctes avant d'envoyer la requête.
        - En cas d'échec de la requête (ex: problème réseau, données invalides), la fonction retournera `None`.
    """
    name: str = "api_post_client"
    description: str = "Post a client into the database"
    api_url = f"https://app-584240518682.europe-west9.run.app/api/clients/"
    json = {
        "name": name_client,
        "phone_number": phone_number,
        "room_number": room_number,
        "special_requests": special_requests
    }
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.post(api_url, json=json, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@tool
def get_client_by_id(id: int):
    """
    Récupère les informations d'un client à partir de son identifiant unique.

    Args:
        id (int): L'identifiant du client à rechercher.

    Returns:
        dict | None: Un dictionnaire contenant les informations du client si la requête réussit (statut 200),
                     sinon `None` en cas d'erreur.

    Exemples:
        >>> get_client_by_id(42)
        {
            "id": 42,
            "name": "Alice Martin",
            "phone_number": "+33698765432",
            "room_number": "302",
            "special_requests": "Vue sur la mer"
        }

    Remarque:
        - L'API requiert une authentification avec un token.
        - Assurez-vous que l'ID fourni est valide et existe dans la base de données.
        - En cas d'échec de la requête (ex: ID inexistant, problème réseau), la fonction retournera `None`.
    """
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
    """
    Récupère les informations d'un client à partir de spécificité comme le nom du client.

    Args:
        search (str): spécificité comme le nom du client à rechercher.

    Returns:
        dict | None: Un dictionnaire contenant les informations du client si la requête réussit (statut 200),
                     sinon `None` en cas d'erreur.

    Exemples:
        >>> get_client_by_search("George Dupont")
        {
          "id": 1535,
          "name": "Georges Dupont",
          "phone_number": "1234567890",
          "room_number": "101",
          "special_requests": "None"
        }

    Remarque:
        - L'API requiert une authentification avec un token.
        - Assurez-vous que l'ID fourni est valide et existe dans la base de données.
        - En cas d'échec de la requête (ex: ID inexistant, problème réseau), la fonction retournera `None`.
    """
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
    elif response.status_code == 202:
        print("Requête acceptée, en attente du traitement...")

        # Supposons que l'API nous donne une URL pour suivre le statut
        status_url = response.headers.get("Location", "http://api.duckduckgo.com/?q={search}&format=json")

        # Vérification périodique (Polling)
        for _ in range(5):  # On essaie 5 fois
            time.sleep(60)  # Attendre 5 secondes avant de vérifier
            statut_response = requests.get(status_url)

            if statut_response.status_code == 200:  # Si la tâche est terminée
                print("Traitement terminé :", statut_response.json())
                break

    print(f"erreur {response.status_code} with search : {search}")
    print(response.json())
    return "Erreur lors de la recherche."



tools = [get_restaurants, get_spas, get_meals, put_client, delete_client, post_client, get_client_by_id, get_client_by_search, put_reservation, delete_reservation, post_reservation, get_reservation_by_id_reservation, get_reservation_by_id_client, get_schema, search_duckduckgo]


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