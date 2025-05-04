from flask import Flask, request, jsonify
from main import chatbot
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get('query', '')
    pending = data.get('pending', None)
    print("Query is ", query)
    response = chatbot(query, pending=pending)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=5000)