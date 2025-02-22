import os
from dotenv import load_dotenv
import requests
import time
import telebot

# Cargar variables de entorno
load_dotenv()

# Configurar el bot con tu token
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

# Guardamos los últimos valores para comparar cambios
ultimo_precio_compra_usdt = None
ultimo_precio_venta_usdt = None
ultimo_precio_compra_blue = None
ultimo_precio_venta_blue = None

# Función para obtener los precios desde la API de Fiwind
def obtener_precio_fiwind():
    url = "https://criptoya.com/api/fiwind/USDT/ARS/0.1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        compra = float(data["bid"])   # Precio de compra (bid)
        venta = float(data["ask"])   # Precio de venta (ask)
        return compra, venta
    else:
        return None, None

# Función para obtener los precios del dólar blue
def obtener_precio_blue():
    url = "https://criptoya.com/api/dolar"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        blue_data = data["blue"]
        compra = float(blue_data["bid"])
        venta = float(blue_data["ask"])
        return compra, venta
    else:
        return None, None

# Función para enviar el mensaje al canal
def enviar_mensaje(tipo, compra, venta, direccion):
    if tipo == "USDT":
        mensaje = f"USDT Precio - Fiwind\nCompra: {compra:.2f} {direccion}  |  Venta: {venta:.2f} {direccion}"
    else:
        mensaje = f"Dólar Blue - Ámbito\nCompra: {compra:.2f} {direccion}  |  Venta: {venta:.2f} {direccion}"
    bot.send_message(CHAT_ID, mensaje)

def monitorear_precios():
    global ultimo_precio_compra_usdt, ultimo_precio_venta_usdt
    global ultimo_precio_compra_blue, ultimo_precio_venta_blue
    
    while True:
        # Monitorear USDT Fiwind
        compra_usdt, venta_usdt = obtener_precio_fiwind()
        if compra_usdt and venta_usdt:
            if ultimo_precio_compra_usdt is not None and ultimo_precio_venta_usdt is not None:
                if compra_usdt > ultimo_precio_compra_usdt:
                    direccion = "🔺"
                elif compra_usdt < ultimo_precio_compra_usdt:
                    direccion = "⬇️"
                else:
                    direccion = "➡️"

                if compra_usdt != ultimo_precio_compra_usdt or venta_usdt != ultimo_precio_venta_usdt:
                    enviar_mensaje("USDT", compra_usdt, venta_usdt, direccion)

            ultimo_precio_compra_usdt = compra_usdt
            ultimo_precio_venta_usdt = venta_usdt

        # Monitorear Dólar Blue
        compra_blue, venta_blue = obtener_precio_blue()
        if compra_blue and venta_blue:
            if ultimo_precio_compra_blue is not None and ultimo_precio_venta_blue is not None:
                if compra_blue > ultimo_precio_compra_blue:
                    direccion = "🔺"
                elif compra_blue < ultimo_precio_compra_blue:
                    direccion = "⬇️"
                else:
                    direccion = "➡️"

                if compra_blue != ultimo_precio_compra_blue or venta_blue != ultimo_precio_venta_blue:
                    enviar_mensaje("BLUE", compra_blue, venta_blue, direccion)

            ultimo_precio_compra_blue = compra_blue
            ultimo_precio_venta_blue = venta_blue
        
        time.sleep(60)  # Consulta cada 60 segundos

# Iniciamos el monitoreo
if __name__ == "__main__":
    monitorear_precios()
