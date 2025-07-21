"""
SCRIPT DE PRUEBA - InfoDolar COMPLETO (Córdoba + Blue General)
Este script prueba la extracción de AMBOS precios de InfoDolar
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

# Configurar logging solo para consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def test_infodolar_completo():
    """
    Prueba extracción completa de InfoDolar: Córdoba + Blue General
    """
    driver = None
    try:
        print("🔥 PRUEBA COMPLETA: InfoDolar Córdoba + Blue General")
        print("=" * 70)
        
        # Configuración Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-images")
        
        # Inicializar driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Cargar InfoDolar
        print("📄 Cargando InfoDolar...")
        driver.get("https://www.infodolar.com/cotizacion-dolar-blue.aspx")
        time.sleep(3)
        
        # Recargar con JavaScript
        print("🔄 Recargando con JavaScript...")
        driver.execute_script("window.location.reload();")
        time.sleep(5)
        
        # Obtener HTML
        print("🔍 Analizando HTML para extraer AMBOS precios...")
        page_source = driver.page_source
        
        # Extraer ambos precios
        cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta, promedio_compra, promedio_venta = extraer_precios_completos_test(page_source)
        
        # Mostrar resultados
        print("\n" + "=" * 70)
        print("📊 RESULTADOS DE LA EXTRACCIÓN COMPLETA:")
        
        # Córdoba específica
        if cordoba_compra and cordoba_venta:
            print(f"✅ CÓRDOBA ESPECÍFICA:")
            print(f"   🗺️ Compra: ${cordoba_compra} | Venta: ${cordoba_venta}")
            print(f"   📊 Spread: ${cordoba_venta - cordoba_compra}")
        else:
            print(f"❌ CÓRDOBA ESPECÍFICA: No encontrada")
        
        # Blue General
        if blue_general_compra and blue_general_venta:
            print(f"✅ DÓLAR BLUE INFODOLAR GENERAL:")
            print(f"   💙 Compra: ${blue_general_compra} | Venta: ${blue_general_venta}")
            print(f"   📊 Spread: ${blue_general_venta - blue_general_compra}")
        else:
            print(f"❌ DÓLAR BLUE INFODOLAR GENERAL: No encontrado")
        
        # Promedio backup
        if promedio_compra and promedio_venta:
            print(f"🔄 PROMEDIO BACKUP:")
            print(f"   📊 Compra: ${promedio_compra} | Venta: ${promedio_venta}")
        
        # Comparación con lo que viste
        print(f"\n📋 COMPARACIÓN CON LO QUE VISTE:")
        print(f"   Córdoba esperada:     $1,309 / $1,339")
        print(f"   Blue General esperado: $1,305 / $1,325")
        
        if cordoba_compra and cordoba_venta:
            print(f"   Córdoba extraída:     ${cordoba_compra} / ${cordoba_venta} {'✅' if cordoba_compra == 1309.0 else '⚠️'}")
        
        if blue_general_compra and blue_general_venta:
            print(f"   Blue General extraído: ${blue_general_compra} / ${blue_general_venta} {'✅' if blue_general_compra == 1305.0 else '⚠️'}")
        
        return cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta
    
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        return None, None, None, None
    
    finally:
        if driver:
            try:
                driver.quit()
                print("🔧 Navegador cerrado")
            except:
                pass

def extraer_precios_completos_test(html_content):
    """
    Función de prueba para extraer AMBOS precios de InfoDolar
    """
    print("🔍 Buscando Córdoba específica Y Dólar Blue InfoDolar general...")
    
    cordoba_compra = None
    cordoba_venta = None
    blue_general_compra = None
    blue_general_venta = None
    
    # === 🗺️ EXTRAER CÓRDOBA ESPECÍFICA ===
    print("\n🗺️ EXTRAYENDO CÓRDOBA ESPECÍFICA:")
    
    cordoba_contexts = []
    for match in re.finditer(r'.{0,200}Córdoba.{0,200}', html_content, re.IGNORECASE | re.DOTALL):
        context = match.group(0)
        cordoba_contexts.append(context)
    
    print(f"   📍 Contextos de Córdoba encontrados: {len(cordoba_contexts)}")
    
    # Buscar en contextos
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
                precio = limpiar_precio_test(match)
                if precio and 1200 <= precio <= 1400:
                    precios_en_contexto.append(precio)
        
        precios_en_contexto = sorted(list(set(precios_en_contexto)))
        
        if len(precios_en_contexto) >= 2:
            cordoba_compra = min(precios_en_contexto)
            cordoba_venta = max(precios_en_contexto)
            print(f"   ✅ Córdoba encontrada en contexto {i} - ${cordoba_compra} / ${cordoba_venta}")
            break
        elif len(precios_en_contexto) == 1:
            print(f"   ⚠️ Solo un precio en contexto {i}: ${precios_en_contexto[0]}")
    
    # Si no encontramos por contexto, usar patrones globales
    if not (cordoba_compra and cordoba_venta):
        print("   🔄 Buscando Córdoba con patrones globales...")
        
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
                    
                    precio1 = limpiar_precio_test(precio1_str)
                    precio2 = limpiar_precio_test(precio2_str)
                    
                    if precio1 and precio2 and 1200 <= precio1 <= 1400 and 1200 <= precio2 <= 1400:
                        if precio1 != precio2:
                            cordoba_compra = min(precio1, precio2)
                            cordoba_venta = max(precio1, precio2)
                            print(f"   ✅ Córdoba extraída con patrón global {i} - ${cordoba_compra} / ${cordoba_venta}")
                            break
                
                except (ValueError, AttributeError):
                    continue
    
    # === 💙 EXTRAER DÓLAR BLUE INFODOLAR GENERAL ===
    print("\n💙 EXTRAYENDO DÓLAR BLUE INFODOLAR GENERAL:")
    
    blue_general_patterns = [
        # Buscar "Dólar Blue InfoDolar" específicamente
        r'Dólar Blue InfoDolar.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        
        # Buscar en tabla con "InfoDolar"
        r'<td[^>]*>.*?InfoDolar.*?</td>.*?<td[^>]*>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>.*?<td[^>]*>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>',
        
        # Buscar contexto más general con InfoDolar
        r'InfoDolar.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        
        # Buscar en títulos o headers
        r'(?i)<h[1-6][^>]*>.*?blue.*?infodolar.*?</h[1-6]>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        
        # Buscar más general
        r'(?i)blue.*?infodolar.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
    ]
    
    for i, pattern in enumerate(blue_general_patterns, 1):
        print(f"   🔍 Probando patrón Blue General {i}...")
        
        blue_match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        if blue_match:
            try:
                precio1_str = blue_match.group(1)
                precio2_str = blue_match.group(2)
                
                print(f"   📄 Precios extraídos: '{precio1_str}' y '{precio2_str}'")
                
                precio1 = limpiar_precio_test(precio1_str)
                precio2 = limpiar_precio_test(precio2_str)
                
                print(f"   🔢 Precios limpiados: {precio1} y {precio2}")
                
                if precio1 and precio2 and 1200 <= precio1 <= 1400 and 1200 <= precio2 <= 1400:
                    if precio1 != precio2:
                        blue_general_compra = min(precio1, precio2)
                        blue_general_venta = max(precio1, precio2)
                        print(f"   ✅ Blue General extraído con patrón {i} - ${blue_general_compra} / ${blue_general_venta}")
                        break
                    else:
                        print(f"   ⚠️ Precios iguales encontrados: ${precio1}")
                else:
                    print(f"   ❌ Precios fuera de rango válido")
            
            except (ValueError, AttributeError) as e:
                print(f"   ❌ Error procesando precios: {str(e)}")
                continue
        else:
            print(f"   ❌ Patrón {i} no encontró coincidencias")
    
    # === 📊 EXTRAER PROMEDIO COMO BACKUP ===
    todos_los_precios = extraer_todos_precios_test(html_content)
    
    promedio_compra = None
    promedio_venta = None
    
    if len(todos_los_precios) >= 2:
        promedio_compra = min(todos_los_precios)
        promedio_venta = max(todos_los_precios)
        print(f"\n📊 Promedio backup calculado de {len(todos_los_precios)} precios: ${promedio_compra} / ${promedio_venta}")
    
    return cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta, promedio_compra, promedio_venta

def limpiar_precio_test(precio_str):
    """
    Función para limpiar precios
    """
    try:
        if '.' in precio_str and ',' in precio_str:
            clean_price = precio_str.replace('.', '').replace(',', '.')
        elif ',' in precio_str and len(precio_str.split(',')[-1]) == 2:
            clean_price = precio_str.replace(',', '.')
        else:
            clean_price = precio_str.replace('.', '').replace(',', '')
        
        return float(clean_price)
    
    except (ValueError, AttributeError):
        return None

def extraer_todos_precios_test(html_content):
    """
    Extrae todos los precios como backup
    """
    precios = []
    
    patterns = [
        r'\$\s*([1-2]\.\d{3},\d{2})',
        r'\$\s*([1-2],\d{3}\.\d{2})',
        r'\$\s*([1-2]\.\d{3})',
        r'\$\s*([1-2],\d{3})',
        r'>([1-2]\.\d{3},\d{2})<',
        r'>([1-2],\d{3}\.\d{2})<',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        
        for match in matches:
            precio = limpiar_precio_test(match)
            if precio and 1200 <= precio <= 1400:
                precios.append(precio)
    
    return list(set(precios))

def main():
    """
    Función principal de prueba
    """
    print("🧪 PRUEBA COMPLETA DE INFODOLAR")
    print("🗺️ Extrayendo Córdoba específica Y Dólar Blue InfoDolar general")
    print("🔒 Esta prueba NO envía mensajes a Telegram")
    print()
    
    cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta = test_infodolar_completo()
    
    print(f"\n" + "=" * 70)
    print("🎯 RESUMEN FINAL:")
    
    total_extraidos = 0
    
    if cordoba_compra and cordoba_venta:
        print(f"✅ Córdoba específica: ${cordoba_compra} / ${cordoba_venta}")
        total_extraidos += 1
    else:
        print(f"❌ Córdoba específica: No extraída")
    
    if blue_general_compra and blue_general_venta:
        print(f"✅ Blue General: ${blue_general_compra} / ${blue_general_venta}")
        total_extraidos += 1
    else:
        print(f"❌ Blue General: No extraído")
    
    print(f"\n📊 TOTAL PRECIOS EXTRAÍDOS: {total_extraidos}/2")
    
    if total_extraidos >= 1:
        print(f"🎉 ¡ÉXITO! InfoDolar integrado correctamente")
        print(f"💎 El COTIBOT tendrá más fuentes de datos")
    else:
        print(f"💔 FALLO: No se pudieron extraer precios de InfoDolar")
    
    print(f"\n🔒 CONFIRMACIÓN: Ningún mensaje enviado a Telegram")
    print(f"✅ Prueba completa terminada")

if __name__ == "__main__":
    main() 