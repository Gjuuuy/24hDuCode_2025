import os
from dotenv import load_dotenv

import requests

### MISTRAL EXAMPLE
from langchain_mistralai import ChatMistralAI


from langchain_core.messages import SystemMessage, ToolMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

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

tools = [get_restaurants]

# Define the graph

from langgraph.prebuilt import create_react_agent

graph = create_react_agent(model, tools=tools)

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {"messages": [("user", "combien il y a de restaurants ?")]}
print_stream(graph.stream(inputs, stream_mode="values"))