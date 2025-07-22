import os
from dotenv import load_dotenv
import requests
import time
import telebot
import logging
from datetime import datetime
import socket

# === 🔥 NUEVAS IMPORTACIONES PARA INFODOLAR ===
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import brotli

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

# === 🔥 NUEVA FUNCIÓN: INFODOLAR CON SELENIUM (CÓRDOBA + BLUE GENERAL) ===
def obtener_precio_infodolar():
    """
    Obtiene precios de InfoDolar: Córdoba específica Y Dólar Blue general
    VERSIÓN FINAL CON BROTLI QUE FUNCIONA EN SERVIDOR
    """
    try:
        logging.info("🔥 Obteniendo precios de InfoDolar (Córdoba + Blue General)...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        session_infodolar = requests.Session()
        session_infodolar.headers.update(headers)
        
        response = session_infodolar.get('https://www.infodolar.com/cotizacion-dolar-blue.aspx', timeout=30)
        
        if response.status_code == 200:
            # Manejar compresión Brotli
            content_encoding = response.headers.get('Content-Encoding', '').lower()
            
            if 'br' in content_encoding:
                try:
                    html_content = brotli.decompress(response.content).decode('utf-8')
                except:
                    html_content = response.text
            else:
                html_content = response.text
            
            # Verificar contenido legible
            if not ('html' in html_content.lower()[:100] and 'infodolar' in html_content.lower()):
                logging.warning("⚠️ HTML InfoDolar no legible")
                return None, None, None, None
            
            # Extraer precios usando BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # === 🗺️ EXTRAER CÓRDOBA ESPECÍFICA ===
            cordoba_compra, cordoba_venta = _extraer_precios_cordoba_final(soup, html_content)
            
            # === 💙 EXTRAER DÓLAR BLUE INFODOLAR GENERAL ===
            blue_general_compra, blue_general_venta = _extraer_precios_blue_general_final(soup, html_content)
            
            logging.info(f"🗺️ InfoDolar Córdoba: ${cordoba_compra}/{cordoba_venta} {'✅' if cordoba_compra else '❌'}")
            logging.info(f"💙 InfoDolar Blue General: ${blue_general_compra}/{blue_general_venta} {'✅' if blue_general_compra else '❌'}")
            
            return cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta
        
        else:
            logging.error(f"❌ Error HTTP InfoDolar: {response.status_code}")
            return None, None, None, None
    
    except Exception as e:
        logging.error(f"❌ Error al obtener precios InfoDolar: {str(e)}")
        logging.info("🔄 InfoDolar no disponible - Bot continúa con otras 11 fuentes")
        return None, None, None, None

def _extraer_precios_completos_infodolar(html_content):
    """
    Extrae AMBOS precios de InfoDolar: Córdoba específica Y Dólar Blue general
    """
    cordoba_compra = None
    cordoba_venta = None
    blue_general_compra = None
    blue_general_venta = None
    
    try:
        logging.info("🔍 Buscando Córdoba específica Y Dólar Blue InfoDolar general...")
        
        # === 🗺️ EXTRAER CÓRDOBA ESPECÍFICA ===
        cordoba_contexts = []
        for match in re.finditer(r'.{0,200}Córdoba.{0,200}', html_content, re.IGNORECASE | re.DOTALL):
            context = match.group(0)
            cordoba_contexts.append(context)
        
        logging.info(f"🗺️ Contextos de Córdoba encontrados: {len(cordoba_contexts)}")
        
        # Buscar precios en contextos de Córdoba
        for i, context in enumerate(cordoba_contexts, 1):
            precios_en_contexto = []
            
            price_patterns = [
                r'\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
                r'([1-2]\.?\d{3}[,.]?\d{0,2})',
                r'>([1-2]\.?\d{3}[,.]?\d{0,2})<',
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, context, re.IGNORECASE)
                for match in matches:
                    precio = _limpiar_precio_infodolar(match)
                    if precio and 1200 <= precio <= 1400:
                        precios_en_contexto.append(precio)
            
            precios_en_contexto = sorted(list(set(precios_en_contexto)))
            
            if len(precios_en_contexto) >= 2:
                cordoba_compra = min(precios_en_contexto)
                cordoba_venta = max(precios_en_contexto)
                logging.info(f"🗺️ Córdoba encontrada - Compra: ${cordoba_compra}, Venta: ${cordoba_venta}")
                break
        
        # Si no encontramos Córdoba por contexto, usar patrones globales
        if not (cordoba_compra and cordoba_venta):
            patterns_cordoba = [
                r'<td[^>]*>.*?Córdoba.*?</td>.*?<td[^>]*>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>.*?<td[^>]*>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>',
                r'Córdoba.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
            ]
            
            for i, pattern in enumerate(patterns_cordoba, 1):
                cordoba_match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
                
                if cordoba_match:
                    try:
                        precio1_str = cordoba_match.group(1)
                        precio2_str = cordoba_match.group(2)
                        
                        precio1 = _limpiar_precio_infodolar(precio1_str)
                        precio2 = _limpiar_precio_infodolar(precio2_str)
                        
                        if precio1 and precio2 and 1200 <= precio1 <= 1400 and 1200 <= precio2 <= 1400:
                            if precio1 != precio2:
                                cordoba_compra = min(precio1, precio2)
                                cordoba_venta = max(precio1, precio2)
                                logging.info(f"🗺️ Córdoba extraída con patrón {i} - Compra: ${cordoba_compra}, Venta: ${cordoba_venta}")
                                break
                    
                    except (ValueError, AttributeError) as e:
                        continue
        
        # === 💙 EXTRAER DÓLAR BLUE INFODOLAR GENERAL ===
        logging.info("💙 Buscando Dólar Blue InfoDolar general...")
        
        # Patrones para encontrar el precio general de InfoDolar
        blue_general_patterns = [
            # Buscar "Dólar Blue InfoDolar" específicamente
            r'Dólar Blue InfoDolar.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
            
            # Buscar en tabla con "InfoDolar"
            r'<td[^>]*>.*?InfoDolar.*?</td>.*?<td[^>]*>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>.*?<td[^>]*>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>',
            
            # Buscar contexto más general con InfoDolar
            r'InfoDolar.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
            
            # Buscar en títulos o headers
            r'(?i)<h[1-6][^>]*>.*?blue.*?infodolar.*?</h[1-6]>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        ]
        
        for i, pattern in enumerate(blue_general_patterns, 1):
            blue_match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            
            if blue_match:
                try:
                    precio1_str = blue_match.group(1)
                    precio2_str = blue_match.group(2)
                    
                    precio1 = _limpiar_precio_infodolar(precio1_str)
                    precio2 = _limpiar_precio_infodolar(precio2_str)
                    
                    if precio1 and precio2 and 1200 <= precio1 <= 1400 and 1200 <= precio2 <= 1400:
                        if precio1 != precio2:
                            blue_general_compra = min(precio1, precio2)
                            blue_general_venta = max(precio1, precio2)
                            logging.info(f"💙 Blue InfoDolar general extraído con patrón {i} - Compra: ${blue_general_compra}, Venta: ${blue_general_venta}")
                            break
                        else:
                            logging.warning(f"Patrón Blue {i} encontró precios iguales: ${precio1}")
                
                except (ValueError, AttributeError) as e:
                    logging.warning(f"Error procesando Blue general con patrón {i}: {str(e)}")
                    continue
        
        # === 📊 EXTRAER PROMEDIO GENERAL COMO BACKUP ===
        todos_los_precios = _extraer_todos_precios_infodolar(html_content)
        
        promedio_compra = None
        promedio_venta = None
        
        if len(todos_los_precios) >= 2:
            promedio_compra = min(todos_los_precios)
            promedio_venta = max(todos_los_precios)
        
        # === 📋 RESUMEN DE EXTRACCIÓN ===
        logging.info("📋 RESUMEN InfoDolar:")
        logging.info(f"   🗺️ Córdoba: ${cordoba_compra}/{cordoba_venta} {'✅' if cordoba_compra else '❌'}")
        logging.info(f"   💙 Blue General: ${blue_general_compra}/{blue_general_venta} {'✅' if blue_general_compra else '❌'}")
        logging.info(f"   📊 Promedio Backup: ${promedio_compra}/{promedio_venta} {'✅' if promedio_compra else '❌'}")
        
        return cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta, promedio_compra, promedio_venta
    
    except Exception as e:
        logging.error(f"Error extrayendo precios completos de InfoDolar: {str(e)}")
        return None, None, None, None, None, None

def _limpiar_precio_infodolar(precio_str):
    """
    Limpia y convierte string de precio a float
    """
    try:
        if '.' in precio_str and ',' in precio_str:
            # Formato 1.302,00 -> 1302.00
            clean_price = precio_str.replace('.', '').replace(',', '.')
        elif ',' in precio_str and len(precio_str.split(',')[-1]) == 2:
            # Formato 1302,00 -> 1302.00
            clean_price = precio_str.replace(',', '.')
        else:
            # Formato simple
            clean_price = precio_str.replace('.', '').replace(',', '')
        
        return float(clean_price)
    
    except (ValueError, AttributeError):
        return None

def _extraer_todos_precios_infodolar(html_content):
    """
    Extrae todos los precios como backup
    """
    precios = []
    
    # Patrones específicos para InfoDolar
    patterns = [
        r'\$\s*([1-2]\.\d{3},\d{2})',  # $1.302,00
        r'\$\s*([1-2],\d{3}\.\d{2})',  # $1,302.00
        r'\$\s*([1-2]\.\d{3})',        # $1.302
        r'\$\s*([1-2],\d{3})',         # $1,302
        r'>([1-2]\.\d{3},\d{2})<',     # Entre tags HTML
        r'>([1-2],\d{3}\.\d{2})<',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        
        for match in matches:
            precio = _limpiar_precio_infodolar(match)
            if precio and 1200 <= precio <= 1400:
                precios.append(precio)
    
    # Eliminar duplicados
    return list(set(precios))

# Función para redondear precios personalizado

def _extraer_precios_cordoba_final(soup, html_content):
    """Extraer precios específicos de Córdoba"""
    try:
        # Buscar en filas de tabla que contengan Córdoba
        rows = soup.find_all('tr')
        
        for row in rows:
            row_text = row.get_text()
            
            if 'córdoba' in row_text.lower():
                cells = row.find_all(['td', 'th'])
                precios = []
                
                for cell in cells:
                    cell_text = cell.get_text()
                    # Buscar precios en formato $ 1.XXX,XX
                    price_matches = re.findall(r'\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})', cell_text)
                    
                    for match in price_matches:
                        precio = _limpiar_precio_infodolar_final(match)
                        if precio and 1200 <= precio <= 1400:
                            precios.append(precio)
                
                if len(precios) >= 2:
                    precios = sorted(list(set(precios)))
                    return min(precios), max(precios)
        
        # Fallback: buscar en HTML completo
        cordoba_patterns = [
            r'Córdoba.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        ]
        
        for pattern in cordoba_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                precio1 = _limpiar_precio_infodolar_final(match.group(1))
                precio2 = _limpiar_precio_infodolar_final(match.group(2))
                
                if precio1 and precio2 and 1200 <= precio1 <= 1400 and 1200 <= precio2 <= 1400:
                    return min(precio1, precio2), max(precio1, precio2)
        
        return None, None
        
    except Exception as e:
        logging.error(f"Error extrayendo Córdoba: {e}")
        return None, None

def _extraer_precios_blue_general_final(soup, html_content):
    """Extraer precio Blue General InfoDolar (primera fila)"""
    try:
        # Buscar específicamente "Dólar Blue InfoDolar" en filas
        rows = soup.find_all('tr')
        
        for row in rows:
            # Buscar span con clase "nombre" que contenga "Dólar Blue InfoDolar"
            nombre_span = row.find('span', class_='nombre')
            
            if nombre_span and 'dólar blue infodolar' in nombre_span.get_text().lower():
                # Esta es la fila correcta, extraer precios de las celdas
                cells = row.find_all(['td', 'th'])
                precios = []
                
                for cell in cells:
                    cell_text = cell.get_text()
                    # Buscar precios en formato $ 1.XXX,XX
                    price_matches = re.findall(r'\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})', cell_text)
                    
                    for match in price_matches:
                        precio = _limpiar_precio_infodolar_final(match)
                        if precio and 1200 <= precio <= 1400:
                            precios.append(precio)
                
                if len(precios) >= 2:
                    precios = sorted(list(set(precios)))
                    return min(precios), max(precios)
        
        # Fallback: buscar en HTML completo
        blue_patterns = [
            r'Dólar\s+Blue\s+InfoDolar.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        ]
        
        for pattern in blue_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                precio1 = _limpiar_precio_infodolar_final(match.group(1))
                precio2 = _limpiar_precio_infodolar_final(match.group(2))
                
                if precio1 and precio2 and 1200 <= precio1 <= 1400 and 1200 <= precio2 <= 1400:
                    return min(precio1, precio2), max(precio1, precio2)
        
        return None, None
        
    except Exception as e:
        logging.error(f"Error extrayendo Blue General: {e}")
        return None, None

def _limpiar_precio_infodolar_final(precio_str):
    """Limpiar y convertir precio a float"""
    try:
        if '.' in precio_str and ',' in precio_str:
            # Formato 1.300,00 -> 1300.00
            clean_price = precio_str.replace('.', '').replace(',', '.')
        elif ',' in precio_str and len(precio_str.split(',')[-1]) == 2:
            # Formato 1300,00 -> 1300.00
            clean_price = precio_str.replace(',', '.')
        else:
            # Formato simple
            clean_price = precio_str.replace('.', '').replace(',', '')
        
        return float(clean_price)
    except:
        return None

def redondear_precio(precio):
    """
    Redondeo personalizado según fórmula de spreadsheet:
    =SI(F18>=REDONDEAR.MENOS(F18/10,0)*10+7, REDONDEAR.MENOS(F18/10,0)*10+10, 
       SI(F18>=REDONDEAR.MENOS(F18/10,0)*10+3.5, REDONDEAR.MENOS(F18/10,0)*10+5, 
          REDONDEAR.MENOS(F18/10,0)*10))
    
    Traducido:
    - Si precio >= (base_decena + 7) → redondear a (base_decena + 10)
    - Si precio >= (base_decena + 3.5) → redondear a (base_decena + 5)  
    - Sino → redondear a base_decena
    
    Ejemplos:
    - 1297 → 1300 (porque 1297 >= 1290+7)
    - 1294 → 1295 (porque 1294 >= 1290+3.5)
    - 1292 → 1290
    """
    import math
    
    # Obtener la base de la decena (equivalente a REDONDEAR.MENOS(precio/10,0)*10)
    base_decena = math.floor(precio / 10) * 10
    
    # Aplicar la lógica de la fórmula
    if precio >= (base_decena + 7):
        return base_decena + 10
    elif precio >= (base_decena + 3.5):
        return base_decena + 5
    else:
        return base_decena

# Función para calcular el DÓLAR BLUE COTIBOT
def calcular_dolar_blue_cotibot():
    try:
        # Obtener datos de todas las fuentes (incluyendo InfoDolar Córdoba)
        usdt_compra, usdt_venta = obtener_precio_fiwind()
        blue_criptoya_compra, blue_criptoya_venta, ccb_compra, ccb_venta = obtener_precio_blue_criptoya()
        blue_bluelytics_compra, blue_bluelytics_venta, oficial_bluelytics_compra, oficial_bluelytics_venta = obtener_precio_bluelytics()
        blue_dolarapi_compra, blue_dolarapi_venta = obtener_precio_dolarapi()
        
        # === 🔥 NUEVA FUENTE: INFODOLAR CÓRDOBA ===
        infodolar_cordoba_compra, infodolar_cordoba_venta, infodolar_blue_general_compra, infodolar_blue_general_venta = obtener_precio_infodolar()
        
        # Verificar que tengamos los datos esenciales (sin InfoDolar como requisito)
        if not all([usdt_compra, usdt_venta, blue_criptoya_compra, blue_criptoya_venta, 
                   ccb_compra, ccb_venta, blue_bluelytics_compra, blue_bluelytics_venta,
                   oficial_bluelytics_compra, oficial_bluelytics_venta, 
                   blue_dolarapi_compra, blue_dolarapi_venta]):
            logging.error("No se pudieron obtener todos los datos esenciales para COTIBOT")
            return None, None
        
        # === 🧮 CÁLCULO CON INFODOLAR CÓRDOBA INTEGRADO EN AMBAS PARTES ===
        
        # Fuentes para BLUE + OFICIAL (incluye InfoDolar Córdoba si está disponible)
        blue_sources_compra = [blue_bluelytics_compra, blue_criptoya_compra, blue_dolarapi_compra]
        blue_sources_venta = [blue_bluelytics_venta, blue_criptoya_venta, blue_dolarapi_venta]
        
        if infodolar_cordoba_compra and infodolar_cordoba_venta:
            blue_sources_compra.append(infodolar_cordoba_compra)
            blue_sources_venta.append(infodolar_cordoba_venta)
            logging.info(f"🗺️ InfoDolar Córdoba integrado en BLUE+OFICIAL - Compra: {infodolar_cordoba_compra}, Venta: {infodolar_cordoba_venta}")
        else:
            logging.warning("⚠️ InfoDolar Córdoba no disponible para BLUE+OFICIAL")
        
        if infodolar_blue_general_compra and infodolar_blue_general_venta:
            blue_sources_compra.append(infodolar_blue_general_compra)
            blue_sources_venta.append(infodolar_blue_general_venta)
            logging.info(f"💙 InfoDolar Blue General integrado en BLUE+OFICIAL - Compra: {infodolar_blue_general_compra}, Venta: {infodolar_blue_general_venta}")
        else:
            logging.warning("⚠️ InfoDolar Blue General no disponible para BLUE+OFICIAL")
        
        # Promedio BLUE + OFICIAL (con o sin InfoDolar Córdoba)
        num_sources = len(blue_sources_compra)
        compra_blue = round(
            (sum(blue_sources_compra) + oficial_bluelytics_compra) / (num_sources + 1), 2
        )
        
        # Promedio ponderado VENTA (90% blues + 10% oficial)
        venta_blue = round(
            sum(blue_sources_venta) * 0.9 / num_sources + oficial_bluelytics_venta * 0.1, 2
        )
        
        # === 🧮 PROMEDIO USDT + CCB (CON AMBOS INFODOLAR + BLUES) ===
        # Fuentes para USDT + CCB + InfoDolar + Blues principales
        usdt_ccb_sources_compra = [usdt_compra, ccb_compra]
        usdt_ccb_sources_venta = [usdt_venta, ccb_venta]
        
        # Agregar los 3 blues principales
        usdt_ccb_sources_compra.extend([blue_bluelytics_compra, blue_criptoya_compra, blue_dolarapi_compra])
        usdt_ccb_sources_venta.extend([blue_bluelytics_venta, blue_criptoya_venta, blue_dolarapi_venta])
        logging.info(f"📊 Blues principales agregados a USDT+CCB")
        
        if infodolar_cordoba_compra and infodolar_cordoba_venta:
            usdt_ccb_sources_compra.append(infodolar_cordoba_compra)
            usdt_ccb_sources_venta.append(infodolar_cordoba_venta)
            logging.info(f"🗺️ InfoDolar Córdoba integrado en USDT+CCB - Compra: {infodolar_cordoba_compra}, Venta: {infodolar_cordoba_venta}")
        else:
            logging.warning("⚠️ InfoDolar Córdoba no disponible para USDT+CCB")
        
        if infodolar_blue_general_compra and infodolar_blue_general_venta:
            usdt_ccb_sources_compra.append(infodolar_blue_general_compra)
            usdt_ccb_sources_venta.append(infodolar_blue_general_venta)
            logging.info(f"💙 InfoDolar Blue General integrado en USDT+CCB - Compra: {infodolar_blue_general_compra}, Venta: {infodolar_blue_general_venta}")
        else:
            logging.warning("⚠️ InfoDolar Blue General no disponible para USDT+CCB")
        
        compra_usdt_ccb = round(sum(usdt_ccb_sources_compra) / len(usdt_ccb_sources_compra), 2)
        venta_usdt_ccb = round(sum(usdt_ccb_sources_venta) / len(usdt_ccb_sources_venta), 2)
        
        # === 🧮 RESTO DEL CÁLCULO IGUAL ===
        # BLUE + USDT + CCB (según AppScript)
        compra_blue_usdt_ccb = round((compra_blue + compra_usdt_ccb) / 2, 2)
        venta_blue_usdt_ccb = round((venta_blue + venta_usdt_ccb) / 2, 2)
        
        # Promedio final BLUE + USDT + CCB (DÓLAR BLUE COTIBOT)
        compra_cotibot = round((compra_blue + compra_blue_usdt_ccb) / 2, 2)
        venta_cotibot = round((venta_blue + venta_blue_usdt_ccb) / 2, 2)
        
        # Aplicar redondeo personalizado
        compra_cotibot = redondear_precio(compra_cotibot)
        venta_cotibot = redondear_precio(venta_cotibot)
        
        logging.info(f"🔥 DÓLAR BLUE COTIBOT (con InfoDolar completo) - Compra: {compra_cotibot}, Venta: {venta_cotibot}")
        logging.info(f"🗺️ InfoDolar Córdoba: {'✅' if infodolar_cordoba_compra else '❌'} | 💙 Blue General: {'✅' if infodolar_blue_general_compra else '❌'}")
        logging.info(f"📊 Blue+Oficial fuentes: {num_sources}, USDT+CCB fuentes: {len(usdt_ccb_sources_compra)}")
        
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
        # Determinar emoji y texto de tendencia según dirección
        if "SUBIÓ" in direccion:
            emoji_tendencia = "📈"
            texto_tendencia = "Subió ⬆️"
        elif "BAJÓ" in direccion:
            emoji_tendencia = "📉"
            texto_tendencia = "Bajó ⬇️"
        else:  # ESTABLE
            emoji_tendencia = "📊"
            texto_tendencia = "Estable ➡️"
        
        # Formato nuevo profesional
        mensaje = f"📊 COTIZACIÓN DÓLAR BLUE - COTIBOT\n\n"
        mensaje += f"🟢 Compra: ${compra:.2f}\n"
        mensaje += f"🔴 Venta: ${venta:.2f}\n"
        mensaje += f"{emoji_tendencia} Tendencia: {texto_tendencia}"
        
        if MODO_TEST:
            print(f"🔍 MODO TEST - Mensaje COTIBOT que se enviaría:\n{mensaje}")
            logging.info(f"[TEST] Mensaje COTIBOT que se enviaría: {mensaje}")
        else:
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
                    # Solo enviar mensaje si hay cambio real después del redondeo
                    if compra_cotibot != ultimo_precio_compra_cotibot or venta_cotibot != ultimo_precio_venta_cotibot:
                        if compra_cotibot > ultimo_precio_compra_cotibot:
                            direccion = "🔺 SUBIÓ"
                        elif compra_cotibot < ultimo_precio_compra_cotibot:
                            direccion = "⬇️ BAJÓ"
                        else:
                            direccion = "➡️ ESTABLE"

                        enviar_mensaje_cotibot(compra_cotibot, venta_cotibot, direccion)
                        logging.info(f"📤 COTIBOT mensaje enviado: ${compra_cotibot}/${venta_cotibot} - {direccion}")
                    else:
                        logging.info(f"🔄 COTIBOT sin cambios: ${compra_cotibot}/${venta_cotibot} (no enviar mensaje)")

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
