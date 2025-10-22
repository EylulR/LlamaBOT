import os
import discord
from discord.ext import commands
import asyncio
from keep_alive import keep_alive

# Inicializar bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Obtener el token desde las variables de entorno de Railway
TOKEN = os.getenv("DISCORD_TOKEN")

# Verificar que el token exista
if not TOKEN:
    raise ValueError("❌ No se encontró el token. Asegúrate de configurarlo en Railway como 'DISCORD_TOKEN'.")

# -------- COMANDOS -------- #

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command()
async def entrar(ctx):
    """El bot entra al canal de voz del usuario."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("🎤 Me uní al canal de voz.")
    else:
        await ctx.send("❌ Primero entra a un canal de voz.")

@bot.command()
async def salir(ctx):
    """El bot sale del canal de voz."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Me salí del canal de voz.")
    else:
        await ctx.send("❌ No estoy en ningún canal de voz.")

@bot.command()
async def decir(ctx, *, texto: str):
    """Convierte texto a voz y lo reproduce en el canal."""
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("❌ Primero entra a un canal de voz.")
            return

    # Guardar el texto en un archivo de audio usando gTTS
    from gtts import gTTS
    tts = gTTS(texto, lang='es')
    tts.save("voz.mp3")

    # Reproducir el archivo de audio con FFmpeg
    source = discord.FFmpegPCMAudio("voz.mp3")
    ctx.voice_client.play(source)
    await ctx.send(f"🗣️ Diciendo: {texto}")

    # Esperar a que termine
    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)

    os.remove("voz.mp3")

# -------- INICIAR SERVIDOR KEEP-ALIVE -------- #
keep_alive()

# -------- EJECUTAR BOT -------- #
bot.run(TOKEN)
