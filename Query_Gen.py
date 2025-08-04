from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("OPENROUTER_API_KEY") 
print("DEBUG: API Key loaded:", "FOUND" if API_KEY else "MISSING") 
MODEL = "anthropic/claude-3-haiku"
URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter(sentence):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""You are a helpful assistant that generates all follow-up questions.
Sentence: "{sentence}"
"""

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.7
    }

    response = requests.post(URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        reply = result['choices'][0]['message']['content']
        return reply.strip()
    else:
        return f"Error: {response.status_code} - {response.text}"

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    data = request.get_json()
    if not data or 'sentence' not in data:
        return jsonify({"error": "Please provide 'sentence' in JSON body."}), 400

    sentence = data['sentence']
    questions = call_openrouter(sentence)

    if questions.startswith("Error:"):
        return jsonify({"error": questions}), 500

    return jsonify({"questions": questions})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)

