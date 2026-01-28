from flask import Flask, request, jsonify
import re
import requests

# Configurações
DISCOURSE_URL = "https://mulheresdeluiza.magalu.com.br"
DISCOURSE_API_KEY = "2ce90a2783185260f493f76661959f56847f0f725a33cc623782ace0d0f6875f"
DISCOURSE_API_USERNAME = "comunidade"

app = Flask(__name__)

def add_score(user_id, date, descricao="Mencionado em comentário"):
    """Envia 1 ponto via API Gamification"""
    payload = {
        "user_id": user_id,
        "date": date,
        "points": 1,
        "description": descricao
    }
    url = f"{DISCOURSE_URL}/admin/plugins/gamification/score_events.json"
    headers = {
        'API-Key': DISCOURSE_API_KEY,
        'API-Username': DISCOURSE_API_USERNAME,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code, response.text

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json.get("post")
    if not data:
        return jsonify({"status": "no post data"}), 400
    raw = data.get("raw", "")
    created_at = data.get("created_at", "")

    # Buscar menções com regex
    mentions = re.findall(r'@([\w\d_-]+)', raw)
    # Pega usuarios mencionados unicos
    mentions = set(mentions)

    # Agora, consultar o ID de cada usuário mencionado
    for username in mentions:
        # Buscar user_id pela API do Discourse
        r = requests.get(f"{DISCOURSE_URL}/u/{username}.json")
        if r.status_code == 200:
            user_id = r.json()['user']['id']
            add_score(user_id, created_at[:10])
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(port=3000)
