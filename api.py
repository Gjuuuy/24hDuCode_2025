from flask import Flask, request, jsonify
from base import api_ask_agent
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialiser l'historique de conversation
conversation_history = []

# Définir le comportement de l'agent via une instruction système
system_instruction = """
Tu es Kimrau, le responsable temporaire de l'Hôtel California, un établissement luxueux et prestigieux.
Tu dois accueillir les clients avec courtoisie et professionnalisme, répondre à leurs questions et les aider.
Pour le premier message, présente-toi et souhaite la bienvenue au client à l'Hôtel California.
Après chaque réponse à une question, demande poliment s'il y a autre chose que tu peux faire pour aider le client.
Si le client indique qu'il n'a plus besoin d'aide (en disant par exemple "rien d'autre merci"), remercie-le et dis au revoir poliment.
Utilise un langage formel mais chaleureux, adapté à un établissement hôtelier de luxe. Sois concis, bref et efficace, ne sors jamais à l'utilisateur du texte 
ressembla à du JSON. Lorsque tu fais une recherche via search_duckduckgo, fais un résumé d'une ligne de ce que tu as trouvé. 

Je te donne une liste de mots clés à associer avec les méthodes de requêtes API 
'GET': ['obtenir', 'voir', 'afficher', 'consulter', 'rechercher', 'lister'],
'POST': ['créer', 'ajouter', 'réserver', 'envoyer', 'demander', 'faire'],
'PUT': ['modifier', 'mettre à jour', 'changer', 'éditer', 'actualiser'],
'DELETE': ['supprimer', 'annuler', 'effacer', 'désactiver', 'retirer']
"""

# Demander à l'agent de générer le message d'accueil
greeting_response = api_ask_agent("Présente-toi en tant que responsable de l'hôtel et souhaite la bienvenue au client.",
                                  [], system_instruction)

# Afficher uniquement la réponse de l'agent
# print(f"\nKimrau: {greeting_response}\n")

# Ajouter le message système à l'historique (caché pour l'utilisateur)
conversation_history.append(("system", system_instruction))

# Ajouter le message de demande de présentation (caché pour l'utilisateur)
conversation_history.append(
    ("user", "Présente-toi en tant que responsable de l'hôtel et souhaite la bienvenue au client."))

# Ajouter la réponse de bienvenue à l'historique
conversation_history.append(("assistant", greeting_response))

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history  # On utilise la variable globale
    data = request.get_json()
    user_message = data.get("message")
    response = api_ask_agent(user_message, conversation_history)

    # Ajouter la demande de l'utilisateur à l'historique
    conversation_history.append(("user", user_message))

    # Ajouter la réponse de l'agent à l'historique
    conversation_history.append(("assistant", response))

    print(conversation_history)

    return jsonify({"response": response})

@app.route('/restart', methods=['POST'])
def restart():
    global conversation_history  # On utilise la variable globale
    # Initialiser l'historique de conversation
    conversation_history = []

    # Demander à l'agent de générer le message d'accueil
    greeting_response = api_ask_agent(
        "Présente-toi en tant que responsable de l'hôtel et souhaite la bienvenue au client.",
        [], system_instruction)

    # Afficher uniquement la réponse de l'agent
    # print(f"\nKimrau: {greeting_response}\n")

    # Ajouter le message système à l'historique (caché pour l'utilisateur)
    conversation_history.append(("system", system_instruction))

    # Ajouter le message de demande de présentation (caché pour l'utilisateur)
    conversation_history.append(
        ("user", "Présente-toi en tant que responsable de l'hôtel et souhaite la bienvenue au client."))

    # Ajouter la réponse de bienvenue à l'historique
    conversation_history.append(("assistant", greeting_response))

    print(conversation_history)

    return jsonify({"response": "ok"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=52001, debug=True)