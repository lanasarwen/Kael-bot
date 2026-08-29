import os
import threading
import discord
from flask import Flask

# Inicializar Flask (necesario para mantener el servicio activo en Render)
app = Flask(__name__)


@app.route("/")
def home():
  return "Kael Bot está activo y funcionando en Discord y Render."


# Configurar los Intents de Discord (necesario para leer mensajes)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print(f"Conectado exitosamente como {client.user}")


@client.event
async def on_message(message):
  # Evitar que el bot se responda a sí mismo en bucle
  if message.author == client.user:
    return

  # Detectar cuando le hablas al bot
  if message.content.startswith("!kael"):
    user_query = message.content[6:].strip()

    # Respuesta de prueba para confirmar conexión
    respuesta_ia = f"Hola, recibí tu mensaje: '{user_query}'. ¡Kael está operativo!"

    await message.channel.send(respuesta_ia)


def run_discord_bot():
  token = os.getenv("DISCORD_TOKEN")
  if token:
    client.run(token)
  else:
    print("Error: No se encontró la variable de entorno DISCORD_TOKEN.")


if __name__ == "__main__":
  # Ejecutar el bot de Discord en un hilo secundario para que no bloquee a Flask
  discord_thread = threading.Thread(target=run_discord_bot)
  discord_thread.daemon = True
  discord_thread.start()

  # Ejecutar Flask en el puerto que exige Render
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)