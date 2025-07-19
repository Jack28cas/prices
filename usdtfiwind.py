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

# Modo test - cambiar a False para enviar mensajes reales
MODO_TEST = False

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
ultimo_precio_compra_cotibot = None
ultimo_precio_venta_cotibot = None

# Función para obtener los precios desde la API de Fiwind
def obtener_precio_fiwind():
    try:
        url = "https://criptoya.com/api/fiwind/USDT/ARS/0.1"
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
        url = "https://criptoya.com/api/dolar"
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

# Función para obtener los precios del dólar blue desde Criptoya (incluye CCB)
def obtener_precio_blue_criptoya():
    try:
        url = "https://criptoya.com/api/dolar"
        response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            blue_data = data["blue"]
            ccb_data = data["cripto"]["ccb"]
            
            blue_compra = float(blue_data["bid"])
            blue_venta = float(blue_data["ask"])
            ccb_compra = float(ccb_data["bid"])
            ccb_venta = float(ccb_data["ask"])
            
            logging.info(f"Blue Criptoya - Compra: {blue_compra}, Venta: {blue_venta}")
            logging.info(f"CCB Criptoya - Compra: {ccb_compra}, Venta: {ccb_venta}")
            
            return blue_compra, blue_venta, ccb_compra, ccb_venta
        else:
            logging.error(f"Error en API Criptoya: Status {response.status_code}")
            return None, None, None, None
    except Exception as e:
        logging.error(f"Error al obtener precio Blue Criptoya: {str(e)}")
        return None, None, None, None

# Función para obtener los precios desde Bluelytics
def obtener_precio_bluelytics():
    try:
        url = "https://api.bluelytics.com.ar/v2/latest"
        response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            blue_compra = float(data["blue"]["value_buy"])
            blue_venta = float(data["blue"]["value_sell"])
            oficial_compra = float(data["oficial"]["value_buy"])
            oficial_venta = float(data["oficial"]["value_sell"])
            
            logging.info(f"Blue Bluelytics - Compra: {blue_compra}, Venta: {blue_venta}")
            logging.info(f"Oficial Bluelytics - Compra: {oficial_compra}, Venta: {oficial_venta}")
            
            return blue_compra, blue_venta, oficial_compra, oficial_venta
        else:
            logging.error(f"Error en API Bluelytics: Status {response.status_code}")
            return None, None, None, None
    except Exception as e:
        logging.error(f"Error al obtener precio Bluelytics: {str(e)}")
        return None, None, None, None

# Función para obtener los precios desde DolarAPI
def obtener_precio_dolarapi():
    try:
        url = "https://dolarapi.com/v1/dolares/blue"
        response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            compra = float(data["compra"])
            venta = float(data["venta"])
            logging.info(f"Blue DolarAPI - Compra: {compra}, Venta: {venta}")
            return compra, venta
        else:
            logging.error(f"Error en API DolarAPI: Status {response.status_code}")
            return None, None
    except Exception as e:
        logging.error(f"Error al obtener precio DolarAPI: {str(e)}")
        return None, None

# Función para redondear precios personalizado
def redondear_precio(precio):
    """
    Redondeo personalizado a múltiplos de 5:
    - 1301, 1302, 1303, 1304 → 1300
    - 1305 → 1305
    - 1306, 1307, 1308, 1309 → 1310
    - 1311, 1312, 1313, 1314 → 1310
    - 1315 → 1315
    - 1316, 1317, 1318, 1319 → 1320
    """
    # Redondear al múltiplo de 5 más cercano
    return round(precio / 5) * 5

# Función para calcular el DÓLAR BLUE COTIBOT
def calcular_dolar_blue_cotibot():
    try:
        # Obtener datos de todas las fuentes
        usdt_compra, usdt_venta = obtener_precio_fiwind()
        blue_criptoya_compra, blue_criptoya_venta, ccb_compra, ccb_venta = obtener_precio_blue_criptoya()
        blue_bluelytics_compra, blue_bluelytics_venta, oficial_bluelytics_compra, oficial_bluelytics_venta = obtener_precio_bluelytics()
        blue_dolarapi_compra, blue_dolarapi_venta = obtener_precio_dolarapi()
        
        # Verificar que tengamos todos los datos necesarios
        if not all([usdt_compra, usdt_venta, blue_criptoya_compra, blue_criptoya_venta, 
                   ccb_compra, ccb_venta, blue_bluelytics_compra, blue_bluelytics_venta,
                   oficial_bluelytics_compra, oficial_bluelytics_venta, 
                   blue_dolarapi_compra, blue_dolarapi_venta]):
            logging.error("No se pudieron obtener todos los datos necesarios para COTIBOT")
            return None, None
        
        # === 🧮 Promedio simple para COMPRA (4 fuentes) - BLUE + OFICIAL
        compra_blue = round(
            (blue_bluelytics_compra + blue_criptoya_compra + blue_dolarapi_compra + oficial_bluelytics_compra) / 4, 2
        )
        
        # === 🧮 Promedio ponderado para VENTA (90% de 3 fuentes + 10% del oficial Bluelytics) - BLUE + OFICIAL
        venta_blue = round(
            (blue_bluelytics_venta + blue_criptoya_venta + blue_dolarapi_venta) * 0.9 / 3 + oficial_bluelytics_venta * 0.1, 2
        )
        
        # === 🧮 Promedio USDT + CCB
        compra_usdt_ccb = round((usdt_compra + ccb_compra) / 2, 2)
        venta_usdt_ccb = round((usdt_venta + ccb_venta) / 2, 2)
        
        # === 🧮 BLUE + USDT + CCB (según AppScript)
        compra_blue_usdt_ccb = round((compra_blue + compra_usdt_ccb) / 2, 2)
        venta_blue_usdt_ccb = round((venta_blue + venta_usdt_ccb) / 2, 2)
        
        # === 🧮 Promedio final BLUE + USDT + CCB (DÓLAR BLUE COTIBOT)
        compra_cotibot = round((compra_blue + compra_blue_usdt_ccb) / 2, 2)
        venta_cotibot = round((venta_blue + venta_blue_usdt_ccb) / 2, 2)
        
        # Aplicar redondeo personalizado
        compra_cotibot = redondear_precio(compra_cotibot)
        venta_cotibot = redondear_precio(venta_cotibot)
        
        logging.info(f"DÓLAR BLUE COTIBOT - Compra: {compra_cotibot}, Venta: {venta_cotibot}")
        logging.info(f"Detalles - Blue+Oficial: {compra_blue}/{venta_blue}, Blue+USDT+CCB: {compra_blue_usdt_ccb}/{venta_blue_usdt_ccb}")
        
        return compra_cotibot, venta_cotibot
        
    except Exception as e:
        logging.error(f"Error al calcular DÓLAR BLUE COTIBOT: {str(e)}")
        return None, None

# Función para enviar el mensaje al canal
def enviar_mensaje(tipo, compra, venta, direccion):
    try:
        if MODO_TEST:
            if tipo == "USDT":
                mensaje = f"[TEST] USDT Precio - Fiwind\nCompra: {compra:.2f}  |  Venta: {venta:.2f}"
            else:
                mensaje = f"[TEST] Dólar Blue - Ámbito\nCompra: {compra:.2f}  |  Venta: {venta:.2f}"
            print(f"🔍 MODO TEST - Mensaje que se enviaría: {mensaje}")
            logging.info(f"[TEST] Mensaje que se enviaría: {mensaje}")
        else:
            if tipo == "USDT":
                mensaje = f"USDT Precio - Fiwind\nCompra: {compra:.2f}  |  Venta: {venta:.2f}"
            else:
                mensaje = f"Dólar Blue - Ámbito\nCompra: {compra:.2f}  |  Venta: {venta:.2f}"
            bot.send_message(CHAT_ID, mensaje)
            logging.info(f"Mensaje enviado: {mensaje}")
    except Exception as e:
        logging.error(f"Error al enviar mensaje: {str(e)}")

# Función para enviar mensaje del DÓLAR BLUE COTIBOT
def enviar_mensaje_cotibot(compra, venta, direccion):
    try:
        if MODO_TEST:
            mensaje = f"[TEST] 💱 DÓLAR BLUE COTIBOT\n\n"
            mensaje += f"Compra: ${compra:.2f}  |  Venta: ${venta:.2f}\n"
            mensaje += f"Dirección: {direccion}"
            print(f"🔍 MODO TEST - Mensaje COTIBOT que se enviaría: {mensaje}")
            logging.info(f"[TEST] Mensaje COTIBOT que se enviaría: {mensaje}")
        else:
            mensaje = f"💱 DÓLAR BLUE COTIBOT\n\n"
            mensaje += f"Compra: ${compra:.2f}  |  Venta: ${venta:.2f}\n"
            mensaje += f"Dirección: {direccion}"
            bot.send_message(CHAT_ID, mensaje)
            logging.info(f"Mensaje COTIBOT enviado: {mensaje}")
    except Exception as e:
        logging.error(f"Error al enviar mensaje COTIBOT: {str(e)}")

def monitorear_precios():
    global ultimo_precio_compra_usdt, ultimo_precio_venta_usdt
    global ultimo_precio_compra_blue, ultimo_precio_venta_blue
    global ultimo_precio_compra_cotibot, ultimo_precio_venta_cotibot
    
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

            # Monitorear DÓLAR BLUE COTIBOT
            compra_cotibot, venta_cotibot = calcular_dolar_blue_cotibot()
            if compra_cotibot and venta_cotibot:
                if ultimo_precio_compra_cotibot is not None and ultimo_precio_venta_cotibot is not None:
                    if compra_cotibot > ultimo_precio_compra_cotibot:
                        direccion = "🔺 SUBIÓ"
                    elif compra_cotibot < ultimo_precio_compra_cotibot:
                        direccion = "⬇️ BAJÓ"
                    else:
                        direccion = "➡️ ESTABLE"

                    if compra_cotibot != ultimo_precio_compra_cotibot or venta_cotibot != ultimo_precio_venta_cotibot:
                        enviar_mensaje_cotibot(compra_cotibot, venta_cotibot, direccion)

                ultimo_precio_compra_cotibot = compra_cotibot
                ultimo_precio_venta_cotibot = venta_cotibot
            
            time.sleep(tiempo_espera)
            tiempo_espera = 60  # Resetear tiempo de espera si todo va bien
            
        except Exception as e:
            logging.error(f"Error en el bucle principal: {str(e)}")
            tiempo_espera = 300  # Aumentar tiempo de espera a 5 minutos si hay error
            time.sleep(tiempo_espera)

# Iniciamos el monitoreo
if __name__ == "__main__":
    monitorear_precios()
