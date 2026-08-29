import os
import threading
import discord
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
  return "Kael Bot está activo y funcionando."


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print(f"Conectado exitosamente como {client.user}")


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith("!kael"):
    user_query = message.content[6:].strip()
    await message.channel.send(
        f"Hola, recibí tu mensaje: '{user_query}'. ¡Kael está operativo!"
    )


def run_discord_bot():
  token = os.getenv("DISCORD_TOKEN")
  if token:
    client.run(token)
  else:
    print("Error: No se encontró la variable de entorno DISCORD_TOKEN.")


# Iniciar el hilo del bot de Discord para que corra junto con Flask/Gunicorn en Render
threading.Thread(target=run_discord_bot, daemon=True).start()

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)