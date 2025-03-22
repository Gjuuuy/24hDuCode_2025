import os
import requests
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from mistralai import Mistral

# Charger les variables depuis .env
load_dotenv()

# Récupérer les clés API
mistral_api_key = os.getenv("MISTRAL_API_KEY")
hotel_api_token = os.getenv("HOTEL_API_TOKEN")

# Initialiser le client Mistral
client = Mistral(api_key=mistral_api_key)

# Fonction pour interroger Mistral
def ask_mistral(query):
    chat_response = client.chat.complete(
        model="mistral-large-latest",  # On spécifie ici le modèle Mistral
        messages=[{"role": "user", "content": query}]
    )
    return chat_response.choices[0].message.content

# Fonction pour interroger l'API des restaurants avec le token
def get_restaurants(query):
    api_url = "https://app-584240518682.europe-west9.run.app/api/restaurants/?param1=value1&param2=value2"
    params = {"query": query}
    
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    
    response = requests.get(api_url, params=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Retourner la réponse sous forme de JSON
    else:
        return None

# Créer un outil LangChain pour Mistral
mistral_tool = Tool(
    name="Mistral Model",
    func=ask_mistral,
    description="Interacts with Mistral to get a response based on a user query"
)

# Créer un outil LangChain pour l'API des restaurants
restaurant_tool = Tool(
    name="Restaurant API",
    func=get_restaurants,
    description="Call the restaurant API to get a list of restaurants based on a query"
)

# Initialiser l'agent LangChain avec les outils
tools = [mistral_tool, restaurant_tool]

# Spécifier que l'argument 'llm' est 'None' puisque nous utilisons un outil personnalisé
agent = initialize_agent(tools, llm=None, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# Fonction d'interaction avec l'utilisateur
def interact_with_user(user_message):
    response = agent.run(user_message)
    return response

# Exemple d'interaction avec un utilisateur
user_message = "Can you suggest some restaurants?"
response = interact_with_user(user_message)
print(response)
