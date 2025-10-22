import os
import discord
from discord.ext import commands
from flask import Flask
import threading
import asyncio
import yt_dlp
import requests

# === CONFIGURACIÓN DEL BOT ===
TOKEN = os.getenv("DISCORD_TOKEN")  # asegúrate de haberlo agregado en Render → Environment
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.voice_states = True

bot = commands.Bot(command_prefix="!", intents=INTENTS)

# === SERVIDOR WEB (para Render) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot activo y operativo en Render"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = threading.Thread(target=run_web)
    thread.start()

# === EVENTOS DEL BOT ===
@bot.event
async def on_ready():
    print(f"✅ Conectado como {bot.user}")
    await bot.change_presence(activity=discord.Game(name="🎵 ¡Listo para tocar música!"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("⚠️ Error al ejecutar el comando. Intenta nuevamente.")
        print(error)
    else:
        raise error

# === COMANDO: ENTRAR AL CANAL DE VOZ ===
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        try:
            await ctx.send(f"🎧 Conectando a {channel.name}...")
            await channel.connect(timeout=30.0, reconnect=True)
            await ctx.send("✅ Conectado al canal de voz.")
        except asyncio.TimeoutError:
            await ctx.send("⏱️ No pude conectarme al canal de voz. Intenta de nuevo en unos segundos.")
        except Exception as e:
            await ctx.send(f"❌ Error al conectar: {e}")
    else:
        await ctx.send("❌ Debes estar en un canal de voz primero.")

# === COMANDO: SALIR DEL CANAL DE VOZ ===
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Desconectado del canal de voz.")
    else:
        await ctx.send("❌ No estoy en ningún canal de voz.")

# === COMANDO: REPRODUCIR MÚSICA ===
@bot.command()
async def play(ctx, *, url: str):
    if not ctx.author.voice:
        await ctx.send("❌ Debes estar en un canal de voz primero.")
        return

    # Si el bot no está conectado, se conecta
    if not ctx.voice_client:
        try:
            await ctx.send("🎧 Conectando al canal...")
            await ctx.author.voice.channel.connect(timeout=30.0, reconnect=True)
        except asyncio.TimeoutError:
            await ctx.send("⏱️ No pude conectarme al canal. Intenta otra vez.")
            return
        except Exception as e:
            await ctx.send(f"❌ Error al conectar: {e}")
            return

    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()

    await ctx.send("🎵 Descargando audio...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extractaudio': True,
        'outtmpl': 'song.%(ext)s',
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        await ctx.send(f"❌ Error al descargar: {e}")
        return

    await ctx.send(f"▶️ Reproduciendo: {info.get('title', 'Desconocido')}")

    audio_source = discord.FFmpegPCMAudio(filename)
    voice_client.play(audio_source, after=lambda e: print(f"Reproducción terminada: {e}"))

# === COMANDO: DETENER MÚSICA ===
@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ Música detenida.")
    else:
        await ctx.send("❌ No se está reproduciendo música.")

# === INICIO DEL BOT ===
if __name__ == "__main__":
    keep_alive()  # Mantiene vivo el contenedor en Render
    bot.run(TOKEN)
