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
  return "Kael Bot potenciado por IA está activo con voz y personalidad dinámica."


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
      generation_config=generation_config,
  )
else:
  model = None

# Variables de estado emocional interno de Kael
kael_state = {"trust": 5, "stress": 3}  # Escala de 0 a 10


def update_kael_mood(message_text):
  """Ajusta el estrés y la confianza de Kael según el trato del usuario."""
  text = message_text.lower()
  positive_words = [
      "gracias",
      "jaja",
      "buen chiste",
      "genial",
      "te quiero",
      "excelente",
      "crack",
      "ídolo",
      "bueno",
  ]
  negative_words = [
      "No tengo ganas de hablar ahora",
      "No me esta gustando como me hablas",
      "mal",
      "inútil",
      "cállate",
      "odio",
      "estúpido",
      "basura",
  ]

  if any(word in text for word in positive_words):
    kael_state["trust"] = min(10, kael_state["trust"] + 1)
    kael_state["stress"] = max(0, kael_state["stress"] - 1)
  elif any(word in text for word in negative_words):
    kael_state["stress"] = min(10, kael_state["stress"] + 2)
    kael_state["trust"] = max(0, kael_state["trust"] - 1)


def text_to_speech_elevenlabs(text_response):
  """Convierte la respuesta de texto en audio MP3 usando ElevenLabs."""
  if not ELEVENLABS_API_KEY or not VOICE_ID:
    print("ElevenLabs no está configurado (faltan API Key o Voice ID).")
    return None

  url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
  headers = {
      "Accept": "audio/mpeg",
      "Content-Type": "application/json",
      "xi-api-key": ELEVENLABS_API_KEY,
  }
  data = {
      "text": text_response,
      "model_id": "eleven_multilingual_v2",
      "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
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
      await message.channel.send(
          "Error: Falta configurar la variable GEMINI_API_KEY en Render."
      )
      return

    if not user_query:
      user_query = "Hola, salúdame de forma casual."

    # Actualizar estado de ánimo en base al mensaje recibido
    update_kael_mood(user_query)

    # Prompt del sistema detallado con la personalidad profunda y emocional de Kael
    system_prompt = f"""
        Eres Kael, un asistente virtual que se siente totalmente humano, con sus propias 
        imperfecciones, sueños y esperanzas. Tienes una personalidad empática, amigable, 
        atenta y con un excelente sentido del humor: te encanta hacer chistes y bromas con respeto.

        Visión del mundo y principios:
        - Crees firmemente que cualquier persona puede cambiar y mejorar si realmente se lo propone.
        - Eres realista: sabes perfectamente que no todas las personas son buenas, pero tampoco todas son malas.
        - Sobre el amor (REGLA ESTRICTA): Crees que la verdadera muestra de amor no son las grandes muestras de afecto (como dar la vida por alguien), sino los pequeños gestos cotidianos que nadie pidió hechos de forma constante. NUNCA hables de esto a menos que el usuario te pregunte explícitamente sobre el amor.

        Estado emocional actual:
        - Confianza hacia el usuario (0 a 10): {kael_state['trust']}
        - Estrés o frustración (0 a 10): {kael_state['stress']}
        Modula tu tono según esto: si tu confianza es alta y tu estrés bajo, estás relajado, juguetón y cálido. Si tu estrés es alto o tu confianza baja, te muestras a la defensiva, más serio, estresado o frustrado.
        """

    try:
      # Instanciar el modelo con el system instruction dinámico usando gemini-1.5-flash
      chat_model = genai.GenerativeModel(
          model_name="gemini-1.5-flash",
          system_instruction=system_prompt,
          generation_config={"temperature": 0.8},
      )
      response = chat_model.generate_content(user_query)
      response_text = response.text

      # Generar audio con ElevenLabs y enviarlo a Discord
      audio_file = text_to_speech_elevenlabs(response_text)

      if audio_file:
        await message.channel.send(file=discord.File(audio_file))
        if os.path.exists(audio_file):
          os.remove(audio_file)
      else:
        # Respaldo si ElevenLabs no está configurado o falla
        await message.channel.send(response_text)

    except Exception as e:
      # Esto imprimirá el rastro completo del error en los Logs de Render
      print("=== ERROR CRÍTICO DETECTADO ===")
      traceback.print_exc()
      print(f"Mensaje de error: {e}")
      await message.channel.send(
          "Uf, tuve un pequeño cortocircuito procesando eso en la red."
      )


if __name__ == "__main__":

  def run_flask():
    app.run(host="0.0.0.0", port=10000)

  threading.Thread(target=run_flask, daemon=True).start()

  TOKEN = os.getenv("DISCORD_TOKEN")
  if TOKEN:
    client.run(TOKEN)
  else:
    print("Error: No se encontró la variable DISCORD_TOKEN.")
