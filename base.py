import os
from mistralai import Mistral
from dotenv import load_dotenv

# Charger les variables depuis .env
load_dotenv()

# Récupérer la clé API
api_key = os.getenv("MISTRAL_API_KEY")

model = "mistral-large-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model= model,
    messages = [
        {
            "role": "user",
            "content": "What is the best French cheese?",
        },
    ]
)
print(chat_response.choices[0].message.content)