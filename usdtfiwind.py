import os
from dotenv import load_dotenv
import requests
import time
import telebot
import logging
from datetime import datetime
import socket

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Cargar variables de entorno
load_dotenv()

# Configurar el bot con tu token
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Configuración de requests
session = requests.Session()
session.mount('https://', requests.adapters.HTTPAdapter(
    max_retries=3,
    pool_connections=10,
    pool_maxsize=10
))

bot = telebot.TeleBot(TOKEN)

# Guardamos los últimos valores para comparar cambios
ultimo_precio_compra_usdt = None
ultimo_precio_venta_usdt = None
ultimo_precio_compra_blue = None
ultimo_precio_venta_blue = None

# Función para obtener los precios desde la API de Fiwind
def obtener_precio_fiwind():
    try:
        # Forzar IPv4
        session.headers.update({'Host': 'criptoya.com'})
        url = "http://168.181.186.118/api/fiwind/USDT/ARS/0.1"  # IP directa de criptoya.com
        
        response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            compra = float(data["bid"])
            venta = float(data["ask"])
            logging.info(f"USDT Fiwind - Compra: {compra}, Venta: {venta}")
            return compra, venta
        else:
            logging.error(f"Error en API Fiwind: Status {response.status_code}")
            return None, None
    except Exception as e:
        logging.error(f"Error al obtener precio Fiwind: {str(e)}")
        time.sleep(30)  # Esperar 30 segundos antes de reintentar
        return None, None

# Función para obtener los precios del dólar blue
def obtener_precio_blue():
    try:
        # Forzar IPv4
        session.headers.update({'Host': 'criptoya.com'})
        url = "http://168.181.186.118/api/dolar"  # IP directa de criptoya.com
        
        response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            blue_data = data["blue"]
            compra = float(blue_data["bid"])
            venta = float(blue_data["ask"])
            logging.info(f"Dólar Blue - Compra: {compra}, Venta: {venta}")
            return compra, venta
        else:
            logging.error(f"Error en API Dólar: Status {response.status_code}")
            return None, None
    except Exception as e:
        logging.error(f"Error al obtener precio Blue: {str(e)}")
        time.sleep(30)  # Esperar 30 segundos antes de reintentar
        return None, None

# Función para enviar el mensaje al canal
def enviar_mensaje(tipo, compra, venta, direccion):
    try:
        if tipo == "USDT":
            mensaje = f"USDT Precio - Fiwind\nCompra: {compra:.2f}  |  Venta: {venta:.2f}"
        else:
            mensaje = f"Dólar Blue - Ámbito\nCompra: {compra:.2f}  |  Venta: {venta:.2f}"
        bot.send_message(CHAT_ID, mensaje)
        logging.info(f"Mensaje enviado: {mensaje}")
    except Exception as e:
        logging.error(f"Error al enviar mensaje: {str(e)}")

def monitorear_precios():
    global ultimo_precio_compra_usdt, ultimo_precio_venta_usdt
    global ultimo_precio_compra_blue, ultimo_precio_venta_blue
    
    logging.info("Bot iniciado")
    tiempo_espera = 60  # Tiempo inicial de espera
    
    while True:
        try:
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
            
            time.sleep(tiempo_espera)
            tiempo_espera = 60  # Resetear tiempo de espera si todo va bien
            
        except Exception as e:
            logging.error(f"Error en el bucle principal: {str(e)}")
            tiempo_espera = 300  # Aumentar tiempo de espera a 5 minutos si hay error
            time.sleep(tiempo_espera)

# Iniciamos el monitoreo
if __name__ == "__main__":
    monitorear_precios()
