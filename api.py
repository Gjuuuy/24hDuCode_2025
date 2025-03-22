from flask import Flask, request, jsonify
from test_langgraph import api_ask_agent
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message")
    response = api_ask_agent(user_message)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=52001, debug=True)