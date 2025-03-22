import os
import time
import functools
from click import prompt
import requests
from dotenv import load_dotenv
from langchain.agents import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import chain
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langchain_mistralai import MistralChat
from typing import TypedDict, List, Dict, Any

# Charger les variables depuis .env
load_dotenv(override=True)

# Récupérer les clés API
mistral_api_key = os.getenv("MISTRAL_API_KEY")
hotel_api_token = os.getenv("HOTEL_API_TOKEN")

print(f"Mistral API Key: {mistral_api_key}")

# Définir l'état du graphe
class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    agent_outcome: Any
    steps: List[List[str]]

# Fonctions pour interroger les APIs
def get_restaurants(query: str):
    api_url = "https://app-584240518682.europe-west9.run.app/api/restaurants/"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
    }
    response = requests.get(api_url, params={"query": query}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_spas(query: str):
    api_url = "https://app-584240518682.europe-west9.run.app/api/spas/"
    headers = {
        "Authorization": f"Token {hotel_api_token}"
        }
    response = requests.get(api_url, params={"search": query}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Définir les outils
class RestaurantTool(BaseTool):
    name = "Restaurant API"
    description = "Utilisez cet outil pour rechercher des restaurants."

    def _run(self, query: str) -> str:
        return str(get_restaurants(query))

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("This tool does not support async execution")

class SpaTool(BaseTool):
    name = "Spa API"
    description = "Utilisez cet outil pour rechercher des spas."

    def _run(self, query: str) -> str:
        return str(get_spas(query))

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("This tool does not support async execution")

tools = [RestaurantTool(), SpaTool()]

# Initialiser le modèle Mistral avec Langchain
llm = MistralChat(mistral_api_key=mistral_api_key, model_name="mistral-large-latest")

# Créer le prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un agent qui peut accéder à des outils.  Réponds de manière concise."),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Fonction pour formater les outils pour l'agent
def format_tools(tools):
    tool_strings = []
    for tool in tools:
        tool_strings.append(f"{tool.name}: {tool.description}")
    return "\n".join(tool_strings)

def format_tool_invocation(tool_name, tool_input):
    return f"Action: {tool_name}\nAction Input: {tool_input}"

# Chaîne LLM
llm_with_tools = prompt | llm.bind_tools(tools)

# Définir la fonction de décision pour l'agent
def agent_decision(state: AgentState):
    messages = state['messages']
    response = llm_with_tools.invoke({
        "messages": messages,
        "tools": format_tools(tools),
        "agent_scratchpad": ""  # Initialement vide
    })
    return {"agent_outcome": response, "messages": messages + [response]}

# Fonction pour exécuter l'outil
def perform_action(state: AgentState):
    messages = state['messages']
    agent_outcome = state['agent_outcome']

    # Extraire l'action et l'entrée de l'action
    action = None
    action_input = None
    if hasattr(agent_outcome, 'tool') and agent_outcome.tool is not None:
        action = agent_outcome.tool
    if hasattr(agent_outcome, 'tool_input') and agent_outcome.tool_input is not None:
        action_input = agent_outcome.tool_input

    if action is not None and action_input is not None:
        tool = next((tool for tool in tools if tool.name == action), None)
        if tool:
            # Exécuter l'outil et ajouter le résultat aux messages
            tool_result = tool.run(action_input)
            messages.append(AIMessage(content=format_tool_invocation(action, action_input)))
            messages.append(HumanMessage(content=str(tool_result)))
        else:
            messages.append(AIMessage(content="Outil non trouvé."))
    else:
        messages.append(AIMessage(content="Pas d'outil à utiliser."))

    return {"messages": messages, "agent_outcome": None}

# Configurer le graphe
builder = StateGraph(AgentState)
builder.add_node("agent", agent_decision)
builder.add_node("action", perform_action)

# Définir les arêtes
builder.set_entry_point("agent")
builder.add_edge("agent", "action")
builder.add_conditional_edges(
    "action",
    lambda state: "agent" if state["agent_outcome"] is None else END,
    {
        "agent": "agent",
        END: END
    }
)

# Créer le graphe
graph = builder.compile()

# Fonction d'interaction avec l'utilisateur
def interact_with_user(user_message: str):
    inputs = {"messages": [HumanMessage(content=user_message)], "agent_outcome": None, "steps": []}
    for output in graph.stream(inputs):
        for key, value in output.items():
            print(f"--- {key}:")
            print(value)
    return output

# Exemple d'interaction
user_message_1 = "Combien de restaurants y a-t-il ?"
response_1 = interact_with_user(user_message_1)
print(response_1)
