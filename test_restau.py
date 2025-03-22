import os
import requests
from mistralai import Mistral
from dotenv import load_dotenv

# Charger les variables depuis .env
load_dotenv()

# Récupérer la clé API Mistral et le token API restaurant
mistral_api_key = os.getenv("MISTRAL_API_KEY")
restaurant_api_token = os.getenv("RESTAURANT_API_TOKEN")  # Assure-toi que ce token est dans ton fichier .env

# Initialiser le client Mistral
model = "mistral-large-latest"
client = Mistral(api_key=mistral_api_key)

# Fonction pour interroger l'API des restaurants avec le token
def get_restaurants(query):
    # Exemple d'URL d'API de restaurants (hypothétique)
    api_url = "https://app-584240518682.europe-west9.run.app/api/restaurants/"
    
    # Paramètres pour la requête (à ajuster selon l'API)
    params = {"query": query}
    
    # Ajouter le token dans les en-têtes de la requête
    headers = {
        "Authorization": f"Token 0luXztX1aBwLoefmkKx5xl6msvWCBmyw"  # Ajout du token ici
    }
    
    # Appeler l'API avec les en-têtes d'authentification
    response = requests.get(api_url, params=params, headers=headers)
    
    # Vérifier si la requête a réussi
    if response.status_code == 200:
        return response.json()  # Retourner la réponse sous forme de JSON
    else:
        return None

# Fonction pour répondre à l'utilisateur
def respond_to_user(user_message):
    # Si la question concerne des restaurants (exemple simple de détection)
    if "restaurant" in user_message.lower():
        restaurants = get_restaurants(user_message)
        if restaurants:
            # Formater la réponse basée sur les restaurants
            response_content = "Here are some restaurants I found:\n"
            for restaurant in restaurants['results']:
                response_content += f"- {restaurant['name']} ({restaurant['location']})\n"
        else:
            response_content = "Sorry, I couldn't find any restaurants at the moment."
    else:
        # Utiliser Mistral pour répondre autrement
        chat_response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": user_message}]
        )
        response_content = chat_response.choices[0].message.content
    
    return response_content

# Exemple de question
user_message = "Can you suggest some restaurants?"
response = respond_to_user(user_message)
print(response)
