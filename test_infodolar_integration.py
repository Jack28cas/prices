"""
SCRIPT DE PRUEBA - InfoDolar Integration
Este script prueba SOLO la función de InfoDolar sin riesgo de enviar mensajes a Telegram
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

# Configurar logging solo para consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def obtener_precio_infodolar_test():
    """
    Versión de prueba de la función InfoDolar (SIN conexión a Telegram)
    """
    driver = None
    try:
        print("🔥 PRUEBA: Obteniendo precios de InfoDolar...")
        
        # Configuración optimizada de Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Sin ventana
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-images")  # Más rápido
        
        # Inicializar driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Cargar InfoDolar
        print("📄 Cargando InfoDolar...")
        driver.get("https://www.infodolar.com/cotizacion-dolar-blue.aspx")
        time.sleep(3)  # Espera inicial
        
        # Recargar con JavaScript habilitado
        print("🔄 Recargando con JavaScript...")
        driver.execute_script("window.location.reload();")
        time.sleep(5)  # Esperar carga de JavaScript
        
        # Obtener HTML y buscar precios
        print("🔍 Extrayendo precios...")
        page_source = driver.page_source
        precios = extraer_precios_infodolar_test(page_source)
        
        if len(precios) >= 2:
            compra = min(precios)
            venta = max(precios)
            
            print(f"✅ InfoDolar - Compra: ${compra}, Venta: ${venta}")
            print(f"📊 Todos los precios encontrados: {sorted(precios)}")
            return compra, venta
        
        else:
            print("❌ InfoDolar: No se pudieron obtener suficientes precios")
            print(f"⚠️  Precios encontrados: {precios}")
            return None, None
    
    except Exception as e:
        print(f"❌ Error en InfoDolar: {str(e)}")
        return None, None
    
    finally:
        if driver:
            try:
                driver.quit()
                print("🔧 Navegador cerrado")
            except:
                pass

def extraer_precios_infodolar_test(html_content):
    """
    Versión de prueba para extraer precios del HTML
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
    
    print("🔍 Aplicando patrones de búsqueda...")
    
    for i, pattern in enumerate(patterns, 1):
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        
        if matches:
            print(f"   Patrón {i}: {len(matches)} coincidencias")
        
        for match in matches:
            try:
                # Limpiar y convertir precio
                if '.' in match and ',' in match:
                    # Formato 1.302,00 -> 1302.00
                    clean_price = match.replace('.', '').replace(',', '.')
                elif ',' in match and len(match.split(',')[-1]) == 2:
                    # Formato 1302,00 -> 1302.00
                    clean_price = match.replace(',', '.')
                else:
                    # Formato simple
                    clean_price = match.replace('.', '').replace(',', '')
                
                price_float = float(clean_price)
                
                # Validar rango
                if 1200 <= price_float <= 1400:
                    precios.append(price_float)
                    print(f"   💰 Precio válido: ${price_float}")
            
            except (ValueError, IndexError):
                continue
    
    # Eliminar duplicados
    precios_unicos = list(set(precios))
    print(f"📊 Precios únicos encontrados: {len(precios_unicos)}")
    
    return precios_unicos

def main():
    """
    Función principal de prueba
    """
    print("🧪 PRUEBA DE INTEGRACIÓN INFODOLAR")
    print("=" * 50)
    print("⚠️  Esta prueba NO envía mensajes a Telegram")
    print("🔒 Es completamente segura para testing")
    print("=" * 50)
    
    # Ejecutar prueba
    compra, venta = obtener_precio_infodolar_test()
    
    if compra and venta:
        print(f"\n🎉 ¡PRUEBA EXITOSA!")
        print(f"🎯 InfoDolar - Compra: ${compra} | Venta: ${venta}")
        print(f"💰 Promedio: ${(compra + venta) / 2:.2f}")
        
        # Simular comparación con precios actuales del bot
        print(f"\n📊 COMPARACIÓN SIMULADA:")
        print(f"InfoDolar (nuevo): ${compra} / ${venta}")
        print(f"Bot actual:        $1285 / $1305")
        print(f"Mejora potencial:  +${compra - 1285:.0f} / +${venta - 1305:.0f}")
        
        if compra > 1285:
            print("✅ InfoDolar mejorará los precios del bot!")
        
    else:
        print(f"\n💔 PRUEBA FALLÓ")
        print(f"❌ No se pudieron obtener precios de InfoDolar")
        print(f"🔄 El bot funcionará sin InfoDolar usando otras fuentes")
    
    print(f"\n🔒 CONFIRMACIÓN: Ningún mensaje fue enviado a Telegram")
    print(f"✅ Prueba completada de forma segura")

if __name__ == "__main__":
    main() 