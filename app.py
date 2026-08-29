import os
from flask import Flask, request, Response
import google.generativeai as genai
import requests

app = Flask(__name__)

# Credenciales (Configuradas mediante variables de entorno)
TOKEN_WHATSAPP = os.getenv("TOKEN_WHATSAPP", "EAAWfLGQU1BwBSRhy1RSpNjzv7qeVUbFq1ZBmRi6NZCYoeNNvbFvjrrqFwnIN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1281994055001514")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mi_token_secreto_kael_123")
GEMINI_API_KEY = os.getenv("AQ.Ab8RN6Lpe3_JEUe4Zl9SMRm-ElFaQlbffGWobIRAY9XOEW4TeA", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if token == VERIFY_TOKEN and challenge:
        return Response(response=str(challenge), status=200, mimetype="text/plain")
    
    return Response(response="Token invalido", status=403)

@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
    data = request.get_json()
    print("Mensaje recibido de Meta:", data)
    
    # Procesar mensajes entrantes si existen en la estructura de Meta
    try:
        entries = data.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                if messages:
                    msg = messages[0]
                    from_number = msg.get("from")
                    body = msg.get("text", {}).get("body", "")
                    
                    if body and GEMINI_API_KEY:
                        prompt = f"Eres Kael, un asistente virtual atento y conciso. Responde al usuario: {body}"
                        respuesta = model.generate_content(prompt)
                        enviar_whatsapp(from_number, respuesta.text)
    except Exception as e:
        print("Error procesando mensaje:", e)
        
    return "EVENT_RECEIVED", 200

def enviar_whatsapp(numero_destino, texto_respuesta):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN_WHATSAPP}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto_respuesta}
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)