import os
import discord
from discord.ext import commands
import asyncio
from keep_alive import keep_alive
import yt_dlp

# -------- CONFIGURACIÓN -------- #
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ No se encontró el token. Configura 'DISCORD_TOKEN' en Railway.")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# -------- EVENTOS -------- #

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Ese comando no existe. Usa `!p`, `!salir` o `!decir`.")
    else:
        raise error

# -------- COMANDOS -------- #

@bot.command()
async def entrar(ctx):
    """El bot entra al canal de voz."""
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
    """Convierte texto a voz y lo reproduce."""
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("❌ Primero entra a un canal de voz.")
            return

    from gtts import gTTS
    tts = gTTS(texto, lang='es')
    tts.save("voz.mp3")

    source = discord.FFmpegPCMAudio("voz.mp3")
    ctx.voice_client.play(source)
    await ctx.send(f"🗣️ Diciendo: {texto}")

    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)

    os.remove("voz.mp3")

@bot.command(name="p")
async def play(ctx, *, query: str):
    """Reproduce música desde YouTube."""
    if not ctx.author.voice:
        await ctx.send("❌ Debes estar en un canal de voz.")
        return

    voice_client = ctx.voice_client
    if not voice_client:
        voice_client = await ctx.author.voice.channel.connect()

    await ctx.send(f"🎶 Buscando: {query}")

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "extract_flat": "in_playlist",
        "outtmpl": "song.%(ext)s",
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        url = info["entries"][0]["url"]
        title = info.get("title", "desconocido")

    source = await discord.FFmpegOpusAudio.from_probe(url)
    voice_client.play(source)
    await ctx.send(f"▶️ Reproduciendo: **{title}**")

# -------- KEEP ALIVE + EJECUCIÓN -------- #
keep_alive()
bot.run(TOKEN)
