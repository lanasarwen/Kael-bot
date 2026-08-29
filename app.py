import os
from flask import Flask
import discord

app = Flask(__name__)


@app.route("/")
def home():
  return "Kael Bot está activo y operando."


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# Función para darle una personalidad característica a Kael
def estilizar_respuesta(user_query):
  # Puedes cambiar este texto o agregarle muletillas, tono sarcástico, técnico o ciberpunk
  estilo_prefijo = (
      "[Kael v1.0]: Análisis completado. Analicé tus palabras y..."
  )
  if not user_query:
    return f"{estilo_prefijo} ¿Venías a decir algo o solo querías hacer parpadear el cursor?"
  return f"{estilo_prefijo} Me dijiste: '{user_query}'. Interesante, anótalo en los registros."


@client.event
async def on_ready():
  print(f"Conectado exitosamente como {client.user}")


@client.event
async def on_message(message):
  print(f"Mensaje recibido de {message.author}: {message.content}")
  if message.author == client.user:
    return

  if message.content.lower().startswith("!kael"):
    user_query = message.content[5:].strip()
    respuesta = estilizar_respuesta(user_query)
    await message.channel.send(respuesta)


if __name__ == "__main__":
  import threading

  def run_flask():
    app.run(host="0.0.0.0", port=10000)

  t = threading.Thread(target=run_flask)
  t.start()

  TOKEN = os.getenv("DISCORD_TOKEN")
  if not TOKEN:
    print("Error: No se encontró la variable de entorno DISCORD_TOKEN.")
  else:
    client.run(TOKEN)