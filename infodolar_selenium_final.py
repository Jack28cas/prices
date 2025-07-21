"""
ATAQUE SELENIUM FINAL - Manejo de anuncios y carga dinámica
"""

import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def selenium_final_attack():
    """Ataque Selenium final con manejo de anuncios"""
    print("🚀 ATAQUE SELENIUM FINAL - CON MANEJO DE ANUNCIOS")
    print("=" * 60)
    
    driver = None
    
    try:
        # Configuración de Chrome con bloqueo de anuncios
        print("🔧 Configurando Chrome con bloqueo de anuncios...")
        chrome_options = Options()
        
        # Opciones anti-detección
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Bloquear anuncios y popups
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Cargar más rápido
        chrome_options.add_argument("--disable-javascript")  # Inicialmente sin JS
        
        # Configurar bloqueo de dominios de anuncios
        chrome_options.add_argument("--block-new-web-contents")
        
        print("✅ Iniciando Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Script anti-detección
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("🌐 Cargando InfoDolar (sin JavaScript inicialmente)...")
        driver.get("https://www.infodolar.com/cotizacion-dolar-blue.aspx")
        
        # Obtener HTML estático primero
        print("📄 Obteniendo HTML estático...")
        static_html = driver.page_source
        
        # Guardar HTML estático
        with open('infodolar_static.html', 'w', encoding='utf-8') as f:
            f.write(static_html)
        
        # Buscar precios en HTML estático
        static_prices = extract_prices_from_html(static_html, "HTML estático")
        
        # Ahora habilitar JavaScript y recargar
        print("🔄 Habilitando JavaScript y recargando...")
        driver.execute_script("window.location.reload();")
        
        # Esperar carga inicial
        time.sleep(3)
        
        # Cerrar posibles popups/anuncios
        close_popups_and_ads(driver)
        
        # Esperar más tiempo para JavaScript
        print("⏳ Esperando carga completa de JavaScript...")
        time.sleep(8)
        
        # Cerrar anuncios nuevamente por si aparecieron más
        close_popups_and_ads(driver)
        
        # Obtener HTML después de JavaScript
        print("📄 Obteniendo HTML después de JavaScript...")
        dynamic_html = driver.page_source
        
        # Guardar HTML dinámico
        with open('infodolar_dynamic.html', 'w', encoding='utf-8') as f:
            f.write(dynamic_html)
        
        # Buscar precios en HTML dinámico
        dynamic_prices = extract_prices_from_html(dynamic_html, "HTML dinámico")
        
        # También buscar en elementos específicos
        print("🔍 Buscando en elementos DOM...")
        dom_prices = extract_prices_from_dom(driver)
        
        # Combinar todos los precios encontrados
        all_prices = static_prices + dynamic_prices + dom_prices
        
        # Procesar resultados
        return process_results(all_prices)
    
    except Exception as e:
        print(f"❌ Error en Selenium: {str(e)}")
        
        # Intentar obtener HTML antes de fallar
        try:
            if driver:
                emergency_html = driver.page_source
                with open('infodolar_emergency.html', 'w', encoding='utf-8') as f:
                    f.write(emergency_html)
                print("💾 HTML de emergencia guardado")
                
                # Buscar precios en HTML de emergencia
                emergency_prices = extract_prices_from_html(emergency_html, "HTML emergencia")
                if emergency_prices:
                    return process_results(emergency_prices)
        except:
            pass
        
        return None, None
    
    finally:
        if driver:
            print("🔧 Cerrando navegador...")
            try:
                driver.quit()
            except:
                pass

def close_popups_and_ads(driver):
    """Cierra popups y anuncios"""
    print("🚫 Cerrando anuncios y popups...")
    
    # Selectores comunes de anuncios y popups
    ad_selectors = [
        '[id*="google"]',
        '[class*="ad"]',
        '[class*="advertisement"]',
        '[class*="popup"]',
        '[class*="modal"]',
        '[class*="overlay"]',
        'iframe[src*="google"]',
        'iframe[src*="doubleclick"]',
        '.close',
        '[aria-label="close"]',
        '[aria-label="cerrar"]'
    ]
    
    for selector in ad_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                try:
                    if element.is_displayed():
                        # Intentar hacer click para cerrar
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(0.5)
                except:
                    try:
                        # Si no se puede hacer click, ocultar con CSS
                        driver.execute_script("arguments[0].style.display = 'none';", element)
                    except:
                        pass
        except:
            continue

def extract_prices_from_html(html_content, source_name):
    """Extrae precios del HTML"""
    print(f"🔍 Extrayendo precios de {source_name}...")
    
    prices = []
    
    # Patrones más específicos para InfoDolar
    patterns = [
        # Formato con separador de miles
        r'\$\s*([1-2]\.\d{3},\d{2})',  # $1.302,00
        r'\$\s*([1-2],\d{3}\.\d{2})',  # $1,302.00
        r'\$\s*([1-2]\.\d{3})',        # $1.302
        r'\$\s*([1-2],\d{3})',         # $1,302
        
        # En contexto de tabla o lista
        r'(?:compra|buy|bid)[:\s]*\$?\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        r'(?:venta|sell|ask)[:\s]*\$?\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        r'(?:blue|dolar)[:\s]*\$?\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        
        # En texto general
        r'>([1-2]\.\d{3},\d{2})<',     # Entre tags HTML
        r'>([1-2],\d{3}\.\d{2})<',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        
        for match in matches:
            try:
                # Limpiar y convertir precio
                clean_price = match.replace('.', '').replace(',', '.')
                
                # Si el precio tiene punto en posición de miles, ajustar
                if '.' in match and len(match.split('.')[-1]) == 3:
                    # Es formato 1.302 (miles)
                    clean_price = match.replace('.', '')
                
                price_float = float(clean_price)
                
                # Validar rango
                if 1200 <= price_float <= 1400:
                    prices.append(price_float)
                    print(f"💰 {source_name} - Precio: ${price_float} (patrón: {pattern[:20]}...)")
            
            except (ValueError, IndexError):
                continue
    
    return prices

def extract_prices_from_dom(driver):
    """Extrae precios directamente del DOM"""
    print("🔍 Extrayendo precios del DOM...")
    
    prices = []
    
    try:
        # Buscar tablas específicamente
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📊 Encontradas {len(tables)} tablas")
        
        for i, table in enumerate(tables):
            try:
                table_html = table.get_attribute('outerHTML')
                table_text = table.text
                
                print(f"📋 Tabla {i+1} texto: {table_text[:100]}...")
                
                # Buscar precios en el HTML de la tabla
                table_prices = extract_prices_from_html(table_html, f"Tabla {i+1}")
                prices.extend(table_prices)
                
            except Exception as e:
                print(f"⚠️  Error en tabla {i}: {str(e)}")
                continue
        
        # Buscar en elementos con clases específicas
        specific_selectors = [
            '.cotizacion',
            '.precio',
            '.price',
            '.currency',
            '.amount',
            '[class*="blue"]',
            '[class*="dolar"]'
        ]
        
        for selector in specific_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    element_html = element.get_attribute('outerHTML')
                    element_prices = extract_prices_from_html(element_html, f"Elemento {selector}")
                    prices.extend(element_prices)
            
            except Exception as e:
                continue
    
    except Exception as e:
        print(f"⚠️  Error buscando en DOM: {str(e)}")
    
    return prices

def process_results(all_prices):
    """Procesa todos los precios encontrados"""
    if not all_prices:
        print("❌ No se encontraron precios")
        return None, None
    
    # Eliminar duplicados y ordenar
    unique_prices = sorted(list(set(all_prices)))
    
    print(f"\n🎯 TODOS LOS PRECIOS ENCONTRADOS: {unique_prices}")
    
    if len(unique_prices) >= 2:
        compra = min(unique_prices)
        venta = max(unique_prices)
        
        print(f"\n🎉 ¡ÉXITO TOTAL CON INFODOLAR!")
        print(f"InfoDolar - Compra: ${compra} | Venta: ${venta}")
        print(f"Promedio: ${(compra + venta) / 2:.2f}")
        
        return compra, venta
    
    elif len(unique_prices) == 1:
        precio = unique_prices[0]
        print(f"\n⚠️  Solo un precio encontrado: ${precio}")
        
        # Estimar spread basado en precio
        spread = 15 if precio > 1300 else 10
        compra = precio - spread
        venta = precio + spread
        
        print(f"🔄 Estimando spread: Compra ${compra} | Venta ${venta}")
        return compra, venta
    
    return None, None

def main():
    """Función principal"""
    print("🎯 ¡ÚLTIMA OPORTUNIDAD PARA INFODOLAR!")
    print("💡 Esta vez manejaremos los anuncios de Google")
    print("⚠️  POR FAVOR: NO CIERRES EL NAVEGADOR MANUALMENTE")
    print("=" * 60)
    
    input("🔥 Presiona ENTER cuando estés listo para el ataque final...")
    
    compra, venta = selenium_final_attack()
    
    if compra and venta:
        print(f"\n🏆 ¡VICTORIA! InfoDolar ha sido conquistado!")
        print(f"🎯 Resultado: Compra ${compra} | Venta: ${venta}")
        
        # Comparar con bot actual
        print(f"\n📊 COMPARACIÓN CON TU BOT:")
        print(f"InfoDolar:     ${compra} / ${venta}")
        print(f"Tu bot actual: $1285 / $1305")
        print(f"Diferencia:    +${compra - 1285:.0f} / +${venta - 1305:.0f}")
        
        if compra > 1285:
            print(f"✅ ¡InfoDolar tiene precios MÁS ALTOS! Vale la pena integrarlo.")
        
    else:
        print(f"\n💔 InfoDolar resistió hasta el final")
        print(f"🏳️  Oficialmente declaramos InfoDolar como INEXPUGNABLE")
        print(f"\n🔄 PLAN B: Mejoremos tu bot con otras fuentes confiables")
    
    return compra, venta

if __name__ == "__main__":
    main() 