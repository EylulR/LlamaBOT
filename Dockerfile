# Usa Python 3.10 (puedes cambiar a 3.11 si prefieres)
FROM python:3.10-slim

# Crea un directorio de trabajo
WORKDIR /app

# Copia todos los archivos
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expón el puerto si usas Flask o keep_alive
EXPOSE 8080

# Comando para ejecutar el bot
CMD ["python", "main.py"]
