import os
from click import prompt
import requests
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.llms.base import LLM
from mistralai import Mistral
#from langchain.utilities import PythonREPL




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
            return response.split("Final Answer:")[1].strip()
        elif "Action:" in response:
            action_part = response.split("Action:")[1]
            action_input_part = action_part.split("Action Input:")[1]
            return f"Action:{action_part.split('Action Input:')[0].strip()}\nAction Input:{action_input_part.strip()}"
        else:
            return response
    
    def _call(self, prompt: str, stop=None) -> str:
        try:
            # Instructions claires pour Mistral
            prompt_with_instructions = f"""
            {prompt}
            
            IMPORTANT: When you respond, follow this EXACT format:
            Thought: (reflect on what you need to do)
            Action: (choose ONE tool from the available tools, nothing else)
            Action Input: (provide the input for the chosen tool)
            
            After receiving an Observation, continue with:
            Thought: (reflect on the observation)
            
            Only use 'Final Answer:' when you're ready to provide the complete, final response.
            """
            
            chat_response = client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt_with_instructions}],
                max_tokens=1000,
                temperature=0.1  # Réduire la température pour des réponses plus déterministes
            )
            response_text = chat_response.choices[0].message.content

            # Nettoyage post-traitement si nécessaire
            if "For troubleshooting" in response_text:
                response_text = response_text.split("For troubleshooting")[0].strip() 
            return self._clean_response(response_text)

            
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
    #max_iterations=5,  # Limite cruciale
    early_stopping_method="generate",
    verbose=True,
    handle_parsing_errors=True
)

# Fonction d'interaction avec l'utilisateur
def interact_with_user(user_message: str):
    response = agent.invoke({"input": user_message})
    return response

# Exemple d'interaction
user_message = "Combien de spas y a-t-il ?"
response = interact_with_user(user_message)
print(response)
