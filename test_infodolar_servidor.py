#!/usr/bin/env python3
"""
Script de diagnóstico para InfoDolar en servidor Linux
Ejecutar: python test_infodolar_servidor.py
"""

import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def test_chrome_installation():
    """Verificar instalación de Chrome y ChromeDriver"""
    logging.info("🔍 Verificando instalación de Chrome...")
    
    try:
        # Verificar ChromeDriver
        import subprocess
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True, timeout=10)
        logging.info(f"✅ ChromeDriver: {result.stdout.strip()}")
    except Exception as e:
        logging.error(f"❌ ChromeDriver no encontrado: {e}")
        return False
    
    try:
        # Verificar Google Chrome
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True, timeout=10)
        logging.info(f"✅ Google Chrome: {result.stdout.strip()}")
    except Exception as e:
        logging.error(f"❌ Google Chrome no encontrado: {e}")
        return False
    
    return True

def test_selenium_basic():
    """Prueba básica de Selenium"""
    logging.info("🔍 Probando Selenium básico...")
    
    driver = None
    try:
        # Configuración mínima para servidor
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(15)
        
        # Probar con una página simple
        driver.get("https://httpbin.org/html")
        title = driver.title
        logging.info(f"✅ Selenium funciona - Título: {title}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error en Selenium básico: {e}")
        return False
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def test_infodolar_connection():
    """Probar conexión específica a InfoDolar"""
    logging.info("🔍 Probando conexión a InfoDolar...")
    
    driver = None
    try:
        # Configuración optimizada para InfoDolar
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(20)  # Timeout más generoso para prueba
        driver.implicitly_wait(5)
        
        logging.info("🌐 Conectando a InfoDolar...")
        start_time = time.time()
        
        driver.get("https://www.infodolar.com/cotizacion-dolar-blue.aspx")
        
        load_time = time.time() - start_time
        logging.info(f"✅ InfoDolar cargado en {load_time:.2f} segundos")
        
        # Obtener información básica
        title = driver.title
        logging.info(f"📄 Título: {title}")
        
        # Obtener HTML y buscar precios
        page_source = driver.page_source
        html_size = len(page_source)
        logging.info(f"📊 Tamaño HTML: {html_size} caracteres")
        
        # Buscar patrones de precios
        price_patterns = [
            r'\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
            r'([1-2]\.?\d{3}[,.]?\d{0,2})',
        ]
        
        total_prices = 0
        for pattern in price_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            valid_prices = []
            
            for match in matches:
                try:
                    clean_price = match.replace('.', '').replace(',', '')
                    price = float(clean_price)
                    if 1200 <= price <= 1400:
                        valid_prices.append(price)
                except:
                    continue
            
            total_prices += len(set(valid_prices))
        
        logging.info(f"💰 Precios encontrados: {total_prices}")
        
        # Buscar términos específicos
        cordoba_found = "córdoba" in page_source.lower()
        blue_found = "blue" in page_source.lower()
        infodolar_found = "infodolar" in page_source.lower()
        
        logging.info(f"🗺️ 'Córdoba' encontrado: {cordoba_found}")
        logging.info(f"💙 'Blue' encontrado: {blue_found}")
        logging.info(f"🏢 'InfoDolar' encontrado: {infodolar_found}")
        
        if total_prices > 0:
            logging.info("✅ InfoDolar parece estar funcionando")
            return True
        else:
            logging.warning("⚠️ InfoDolar cargó pero no se encontraron precios")
            return False
        
    except Exception as e:
        logging.error(f"❌ Error conectando a InfoDolar: {e}")
        return False
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    """Ejecutar todos los tests de diagnóstico"""
    logging.info("🚀 INICIANDO DIAGNÓSTICO DE INFODOLAR EN SERVIDOR")
    logging.info("=" * 60)
    
    # Test 1: Instalaciones
    logging.info("\n📋 TEST 1: Verificar instalaciones")
    chrome_ok = test_chrome_installation()
    
    if not chrome_ok:
        logging.error("❌ Chrome/ChromeDriver no están correctamente instalados")
        return False
    
    # Test 2: Selenium básico
    logging.info("\n📋 TEST 2: Selenium básico")
    selenium_ok = test_selenium_basic()
    
    if not selenium_ok:
        logging.error("❌ Selenium no funciona correctamente")
        return False
    
    # Test 3: InfoDolar específico
    logging.info("\n📋 TEST 3: Conexión InfoDolar")
    infodolar_ok = test_infodolar_connection()
    
    # Resumen
    logging.info("\n" + "=" * 60)
    logging.info("📊 RESUMEN DEL DIAGNÓSTICO:")
    logging.info(f"   Chrome/ChromeDriver: {'✅' if chrome_ok else '❌'}")
    logging.info(f"   Selenium básico: {'✅' if selenium_ok else '❌'}")
    logging.info(f"   InfoDolar: {'✅' if infodolar_ok else '❌'}")
    
    if infodolar_ok:
        logging.info("\n🎉 ¡InfoDolar debería funcionar en el bot!")
    else:
        logging.info("\n⚠️ InfoDolar necesita ajustes adicionales")
    
    return infodolar_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 