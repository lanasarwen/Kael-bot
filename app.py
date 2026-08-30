import os
import threading
import traceback
import requests
import discord
import google.generativeai as genai
from flask import Flask

# Inicializar Flask para mantener el bot activo en Render
app = Flask(__name__)

@app.route("/")
def home():
    return "Kael Bot potenciado por IA está activo con voz."

# Configuración de Discord Intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Configurar claves de API desde variables de entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    generation_config = {"temperature": 0.8}
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config
    )
else:
    model = None

def text_to_speech_elevenlabs(text_response):
    if not ELEVENLABS_API_KEY or not VOICE_ID:
        print("ElevenLabs no está configurado (faltan API Key o Voice ID).")
        return None
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text_response,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            audio_path = "respuesta_kael.mp3"
            with open(audio_path, "wb") as f:
                f.write(response.content)
            return audio_path
        else:
            print(f"Error en ElevenLabs (Código {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Excepción conectando con ElevenLabs: {e}")
    return None

@client.event
async def on_ready():
    print(f"Conectado exitosamente como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith("!kael"):
        user_query = message.content[5:].strip()
        
        if not model:
            await message.channel.send("Error: Falta configurar la variable GEMINI_API_KEY en Render.")
            return

        if not user_query:
            user_query = "Hola, salúdame de forma casual."

        system_prompt = """
        Eres Kael, un asistente virtual amigable, atento, relajado y con un excelente sentido del humor.
        Responde de manera natural, cercana y respetuosa.
        """

        try:
            chat_model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_prompt,
                generation_config={"temperature": 0.8}
            )
            response = chat_model.generate_content(user_query)
            response_text = response.text

            audio_file = text_to_speech_elevenlabs(response_text)

            if audio_file:
                await message.channel.send(file=discord.File(audio_file))
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            else:
                await message.channel.send(response_text)

        except Exception as e:
            print("=== ERROR CRÍTICO DETECTADO ===")
            traceback.print_exc()
            print(f"Mensaje de error: {e}")
            await message.channel.send("Uf, tuve un pequeño cortocircuito procesando eso en la red.")

if __name__ == "__main__":
    def run_flask():
        app.run(host="0.0.0.0", port=10000)
    threading.Thread(target=run_flask, daemon=True).start()

    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        client.run(TOKEN)
    else:
        print("Error: No se encontró la variable DISCORD_TOKEN.")
