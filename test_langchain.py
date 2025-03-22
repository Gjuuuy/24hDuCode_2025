import os
import time
from click import prompt
import requests
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.llms.base import LLM
from mistralai import Mistral


# Charger les variables depuis .env
load_dotenv(override=True)

# Récupérer les clés API
mistral_api_key = os.getenv("MISTRAL_API_KEY")
hotel_api_token = os.getenv("HOTEL_API_TOKEN")

print(f"Mistral API Key: {mistral_api_key}")

# Initialiser le client Mistral
client = Mistral(api_key=mistral_api_key)

# Création d'un LLM personnalisé pour Mistral
class MistralLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "mistral"

    def _clean_response(self, response: str) -> str:
        if "Final Answer:" in response:
            return "Final Answer:" + response.split("Final Answer:")[1].strip()
        elif "Action:" in response:
            return "Action:" + response.split("Action:")[1].strip()
        else:
            return response
    
    def _call(self, prompt: str, stop=None) -> str:
        try:
            # Instructions claires pour Mistral
            prompt_with_instructions = f"""
            {prompt}
            
            INSTRUCTIONS STRICTES :
            1. Choisissez UNE SEULE option :
            - Soit une Action avec son Action Input
            - Soit une Final Answer
            2. N'incluez JAMAIS les deux dans la même réponse
            3. Utilisez le format exact :
            Thought: votre raisonnement
            Action: nom de l'action
            Action Input: entrée de l'action
            OU
            Thought: votre raisonnement 
            Final Answer: votre réponse définitive

            Exemple valide 1 :
            Thought: Je dois obtenir plus d'informations
            Action: Spa API
            Action Input: "liste des spas"

            Exemple valide 2 :
            Thought: J'ai toutes les informations nécessaires
            Final Answer: Il y a 3 spas.
            """
            
            time.sleep(1) 
            chat_response = client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt_with_instructions}],
                max_tokens=1000,
                temperature=0.3  # Réduire la température pour des réponses plus déterministes
            )
            response_text = chat_response.choices[0].message.content

            # Nettoyage post-traitement si nécessaire
            if "For troubleshooting" in response_text:
                response_text = response_text.split("For troubleshooting")[0].strip() 
            cleaned_response = self._clean_response(response_text)
            if not ("Final Answer:" in cleaned_response or "Action:" in cleaned_response):
                return "Final Answer: Désolé, je n'ai pas pu formater ma réponse correctement."
            return cleaned_response
            
        except Exception as e:
            print(f"Erreur lors de l'appel à Mistral API: {e}")
            return f"Error: {str(e)}"
    

    async def _acall(self, prompt: str, stop=None) -> str:
        # Pour cet exemple, on ne supporte pas l'appel asynchrone
        raise NotImplementedError("MistralLLM does not support async calls.")

# Créer une instance du LLM personnalisé
mistral_llm = MistralLLM()

# Fonction pour interroger l'API des restaurants avec le token
def get_restaurants(query: str):
    api_url = "https://app-584240518682.europe-west9.run.app/api/restaurants/"
    params = {"query": query}
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, params=params, headers=headers)
    if response.status_code == 200:
        # On attend un JSON contenant une clé 'data'
        return response.json()  
    else:
        return None

def get_spas(query: str):
    api_url = "https://app-584240518682.europe-west9.run.app/api/spas/"
    params = {"search": query}
    headers = {
        "Authorization": f"Token {hotel_api_token}"
        }
    response = requests.get(api_url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json() 
    
    else:
        return None

# Outil LangChain pour interroger Mistral (on peut l'utiliser en complément ou pour d'autres usages)
def ask_mistral(query: str) -> str:
    return mistral_llm._call(query)

mistral_tool = Tool(
    name="Mistral Model",
    func=ask_mistral,
    description="Interacts with Mistral to get a response based on a user query"
)

restaurant_tool = Tool(
    name="Restaurant API",
    func=get_restaurants,
    description="Calls the restaurant API to get a list of restaurants based on a query"
)

spa_tool = Tool(
    name="Spa API",
    func=get_spas,
    description="Recherche des centres de spa"
) 



# Initialiser l'agent LangChain avec les outils et le modèle Mistral
tools = [mistral_tool, restaurant_tool, spa_tool]
agent = initialize_agent(
    tools, 
    llm=mistral_llm, 
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    max_iterations=5,  # Limite cruciale
    early_stopping_method="generate",
    verbose=True,
    handle_parsing_errors=True
)

# Fonction d'interaction avec l'utilisateur
def interact_with_user(user_message: str):
    response = agent.invoke({"input": user_message})
    return response

# Exemple d'interaction
user_message = "Donne moi les noms des restaurants qui sont ouverts à 12:00"
response = interact_with_user(user_message)
print(response)

#user_message_1 = "Combien de restaurants y a-t-il ?"
#response_1 = interact_with_user(user_message_1)
#print(response_1)