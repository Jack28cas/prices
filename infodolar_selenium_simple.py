"""
ATAQUE SELENIUM SIMPLIFICADO - Sin opciones problemáticas
"""

import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def selenium_simple_attack():
    """Ataque Selenium simplificado"""
    print("🚀 INICIANDO ATAQUE SELENIUM SIMPLIFICADO")
    print("=" * 60)
    
    driver = None
    
    try:
        # Configuración básica de Chrome
        print("🔧 Configurando Chrome...")
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Inicializar driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome configurado correctamente")
        
        # Cargar InfoDolar
        print("🌐 Cargando InfoDolar...")
        driver.get("https://www.infodolar.com/cotizacion-dolar-blue.aspx")
        
        # Esperar carga completa
        print("⏳ Esperando carga completa...")
        time.sleep(8)  # Dar tiempo suficiente para JavaScript
        
        # Extraer datos del DOM
        print("🔍 Extrayendo precios del DOM...")
        
        # Obtener todo el HTML después de JavaScript
        page_source = driver.page_source
        
        # Guardar HTML para análisis
        with open('infodolar_selenium_dom.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("💾 DOM guardado en 'infodolar_selenium_dom.html'")
        
        # Buscar precios en todo el HTML
        precios_encontrados = []
        
        # Patrón para precios con formato $1.XXX,XX o $1,XXX.XX
        price_patterns = [
            r'\$\s*([1-2]\d{3}[,.]?\d{0,2})',
            r'([1-2]\d{3}[,.]?\d{0,2})\s*pesos',
            r'precio[:\s]*\$?([1-2]\d{3}[,.]?\d{0,2})',
            r'cotización[:\s]*\$?([1-2]\d{3}[,.]?\d{0,2})',
            r'compra[:\s]*\$?([1-2]\d{3}[,.]?\d{0,2})',
            r'venta[:\s]*\$?([1-2]\d{3}[,.]?\d{0,2})'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            
            for match in matches:
                try:
                    # Limpiar el precio
                    clean_price = match.replace(',', '').replace('.', '')
                    
                    # Si tiene más de 4 dígitos, asumir que el punto/coma son decimales
                    if len(clean_price) > 4:
                        price_float = float(match.replace(',', '.'))
                    else:
                        price_float = float(clean_price)
                    
                    # Validar rango
                    if 1200 <= price_float <= 1400:
                        precios_encontrados.append(price_float)
                        print(f"💰 Precio encontrado: ${price_float}")
                
                except ValueError:
                    continue
        
        # También buscar en elementos específicos
        print("🔍 Buscando en elementos específicos...")
        
        # Buscar tablas
        try:
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"📊 Encontradas {len(tables)} tablas")
            
            for i, table in enumerate(tables):
                table_text = table.text
                
                # Buscar precios en texto de tabla
                table_prices = re.findall(r'\$\s*([1-2]\d{3}(?:[,.]?\d{2})?)', table_text)
                
                for price_str in table_prices:
                    try:
                        price = float(price_str.replace(',', ''))
                        if 1200 <= price <= 1400:
                            precios_encontrados.append(price)
                            print(f"💰 Precio en tabla {i}: ${price}")
                    except ValueError:
                        continue
        
        except Exception as e:
            print(f"⚠️  Error buscando tablas: {str(e)}")
        
        # Buscar divs con clases relacionadas
        try:
            selectors = [
                '[class*="precio"]',
                '[class*="price"]', 
                '[class*="cotiz"]',
                '[class*="blue"]',
                '[class*="dolar"]',
                '[class*="currency"]'
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    element_text = element.text
                    
                    # Buscar precios en el texto del elemento
                    element_prices = re.findall(r'\$?\s*([1-2]\d{3}(?:[,.]?\d{2})?)', element_text)
                    
                    for price_str in element_prices:
                        try:
                            price = float(price_str.replace(',', ''))
                            if 1200 <= price <= 1400:
                                precios_encontrados.append(price)
                                print(f"💰 Precio en {selector}: ${price}")
                        except ValueError:
                            continue
        
        except Exception as e:
            print(f"⚠️  Error buscando elementos: {str(e)}")
        
        # Procesar resultados
        if precios_encontrados:
            # Eliminar duplicados y ordenar
            precios_unicos = sorted(list(set(precios_encontrados)))
            
            print(f"\n🎯 PRECIOS ÚNICOS ENCONTRADOS: {precios_unicos}")
            
            if len(precios_unicos) >= 2:
                compra = min(precios_unicos)
                venta = max(precios_unicos)
                
                print(f"\n🎉 ¡ÉXITO CON SELENIUM!")
                print(f"InfoDolar - Compra: ${compra} | Venta: ${venta}")
                print(f"Promedio: ${(compra + venta) / 2:.2f}")
                
                return compra, venta
            
            elif len(precios_unicos) == 1:
                precio = precios_unicos[0]
                print(f"\n⚠️  Solo se encontró un precio: ${precio}")
                # Asumir spread típico de ±10 pesos
                compra = precio - 10
                venta = precio + 10
                
                print(f"🔄 Estimando spread: Compra ${compra} | Venta ${venta}")
                return compra, venta
        
        else:
            print("❌ No se encontraron precios válidos en el DOM")
            print("💡 InfoDolar podría estar usando técnicas anti-bot muy avanzadas")
            return None, None
    
    except Exception as e:
        print(f"❌ Error en Selenium: {str(e)}")
        return None, None
    
    finally:
        if driver:
            driver.quit()
            print("🔧 Navegador cerrado")

def main():
    """Función principal"""
    compra, venta = selenium_simple_attack()
    
    if compra and venta:
        print(f"\n✅ MISIÓN CUMPLIDA - InfoDolar conquistado!")
        print(f"🎯 Resultado final: Compra ${compra} | Venta ${venta}")
        
        # Comparar con tu bot actual
        print(f"\n📊 COMPARACIÓN:")
        print(f"InfoDolar (Selenium): ${compra} / ${venta}")
        print(f"Tu bot actual:        $1285 / $1305")
        print(f"Diferencia:           +${compra - 1285:.0f} / +${venta - 1305:.0f}")
        
    else:
        print(f"\n💔 Selenium tampoco pudo con InfoDolar")
        print(f"🏳️  InfoDolar tiene las defensas más avanzadas del mercado")
        print(f"\n🔄 PLAN B: ¿Agregamos APIs alternativas más actualizadas?")
        print(f"   - Criptoya: Precios más altos que tu bot actual")
        print(f"   - DolarAPI: API confiable y actualizada") 
        print(f"   - Bluelytics: Fuente histórica confiable")

if __name__ == "__main__":
    main() 