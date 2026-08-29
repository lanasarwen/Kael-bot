import os
import random
from flask import Flask
import discord

app = Flask(__name__)


@app.route("/")
def home():
  return "Kael Bot está activo y operando."


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def estilizar_respuesta(user_query):
  q = user_query.lower()

  if "hola" in q:
    return "¡Qué onda! ¿Qué andamos maquinando hoy?"
  elif "chiste" in q:
    return (
        "¿Cómo se despiden los químicos? Ácido un placer... lo sé, un clásico"
        " terrible."
    )
  elif "bien" in q or "genial" in q or "excelente" in q:
    return "¡Eso me gusta! Con toda la energía."
  elif not q:
    return "¿Me llamaste y te quedaste en blanco? Jaja, dime."

  frases_casuales = [
      f"A ver, sobre eso de '{user_query}'... me suena interesante, cuéntame más.",
      f"Interesante punto con lo de '{user_query}'. ¿Por dónde quieres que lo veamos?",
      f"Leído. Analizando '{user_query}'... Bueno, fuera de bromas, ¿qué más planeas hacer con eso?",
  ]
  return random.choice(frases_casuales)


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