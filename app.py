import os
import random
from flask import Flask
import discord

app = Flask(__name__)


@app.route("/")
def home():
  return "Kael Bot está activo con una personalidad dulce y aprendizaje activo."


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# Mini red neuronal simulada con pesos dinámicos y adaptación por refuerzo
class MiniNeuralNetworkSelector:

  def __init__(self):
    self.emociones_atentas = [
        "¡Hola! Me alegra muchísimo leerte, ¿cómo va tu día?",
        "Hola, corazón. Aquí estoy cuidando el fuerte por ti, espero que estés sonriendo.",
        (
            "¡Hola! Respira hondo y tómate un momento para ti. Lo estás"
            " haciendo excelente."
        ),
        (
            "¡Qué alegría verte por aquí! Estaba pensando en ti, ¿en qué te"
            " puedo acompañar hoy?"
        ),
    ]
    self.chistes_aleatorios = [
        (
            "¿Por qué los programadores preferimos el frío? Porque en verano"
            " las ventanas nos dan demasiada alergia."
        ),
        "¿Qué hace una abeja en el gimnasio? ¡Zumba!",
        (
            "¿Por qué los pájaros vuelan hacia el sur en invierno? ¡Porque"
            " caminando tardan una eternidad!"
        ),
        (
            "¿Qué le dice una impresora a otra? ¿Esa hoja es tuya o es"
            " impresión mía?"
        ),
        (
            "¿Cómo se despiden los químicos? Ácido un placer."
        ),
    ]
    # Pesos sinápticos iniciales para evitar repeticiones y simular aprendizaje
    self.pesos_emocion = [1.0] * len(self.emociones_atentas)
    self.pesos_chiste = [1.0] * len(self.chistes_aleatorios)

  def _activacion_ponderada(self, opciones, pesos):
    # Selección probabilística inspirada en capas de activación (Softmax ligero)
    total = sum(pesos)
    probabilidades = [p / total for p in pesos]
    elegido = random.choices(opciones, weights=probabilidades, k=1)[0]
    idx = opciones.index(elegido)

    # Ajuste de pesos dinámico (retropropagación simulada: penaliza lo recién usado)
    pesos[idx] *= 0.7
    for i in range(len(pesos)):
      if i != idx:
        pesos[i] += 0.15  # Recompensa a las otras rutas para variar

    return elegido

  def generar_respuesta(self, query):
    frase_dulce = self._activacion_ponderada(
        self.emociones_atentas, self.pesos_emocion
    )
    chiste = self._activacion_ponderada(
        self.chistes_aleatorios, self.pesos_chiste
    )

    if query:
      return (
          f"{frase_dulce}\n\nPor cierto, me dijiste: *'{query}'*. Me parece"
          f" súper interesante. Oye, hablando de otra cosa para alegrarte el"
          f" momento: {chiste}"
      )
    else:
      return f"{frase_dulce}\n\nPara romper el hielo: {chiste}"


brain = MiniNeuralNetworkSelector()


@client.event
async def on_ready():
  print(f"Conectado exitosamente como {client.user} con red neuronal activa.")


@client.event
async def on_message(message):
  print(f"Mensaje recibido de {message.author}: {message.content}")
  if message.author == client.user:
    return

  if message.content.lower().startswith("!kael"):
    user_query = message.content[5:].strip()
    respuesta = brain.generar_respuesta(user_query)
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
    