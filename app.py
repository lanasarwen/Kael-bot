import os
import threading
import discord
import google.generativeai as genai
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
  return "Kael Bot potenciado por IA está activo."


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Configurar la API de Gemini con su personalidad base (System Instruction)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
  genai.configure(api_key=GEMINI_API_KEY)
  # Aquí defines cómo quieres que hable, su tono y su estilo
  system_prompt = (
      "Eres Kael, un asistente virtual con una personalidad casual, amigable,"
      " un toque tecnológico/ciberpunk y muy fluido. Respondes de forma"
      " natural, concisa y conversacional en los chats de Discord, evitando"
      " sonar como un robot corporativo aburrido."
  )
  generation_config = {"temperature": 0.8}
  model = genai.GenerativeModel(
      model_name="gemini-2.5-flash",
      system_instruction=system_prompt,
      generation_config=generation_config,
  )
else:
  model = None


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

    try:
      # Enviar la consulta a la IA y obtener la respuesta fluida
      response = model.generate_content(user_query)
      await message.channel.send(response.text)
    except Exception as e:
      await message.channel.send(
          "Uf, tuve un pequeño cortocircuito procesando eso en la red."
      )
      print(f"Error generando contenido: {e}")


if __name__ == "__main__":

  def run_flask():
    app.run(host="0.0.0.0", port=10000)

  threading.Thread(target=run_flask, daemon=True).start()

  TOKEN = os.getenv("DISCORD_TOKEN")
  if TOKEN:
    client.run(TOKEN)
  else:
    print("Error: No se encontró la variable DISCORD_TOKEN.")