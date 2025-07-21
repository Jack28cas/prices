"""
SCRIPT DE PRUEBA - InfoDolar Córdoba Específico
Este script prueba la extracción específica de precios de Córdoba desde InfoDolar
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

# Configurar logging solo para consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def test_cordoba_extraction():
    """
    Prueba específica para extraer precios de Córdoba
    """
    driver = None
    try:
        print("🗺️ PRUEBA: Extracción específica de CÓRDOBA desde InfoDolar")
        print("=" * 60)
        
        # Configuración optimizada de Chrome
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
        print("🔍 Analizando HTML para encontrar Córdoba...")
        page_source = driver.page_source
        
        # Buscar específicamente Córdoba
        cordoba_compra, cordoba_venta, promedio_compra, promedio_venta = extraer_precios_cordoba_test(page_source)
        
        # Mostrar resultados
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DE LA EXTRACCIÓN:")
        
        if cordoba_compra and cordoba_venta:
            print(f"✅ CÓRDOBA ENCONTRADA:")
            print(f"   🗺️ Córdoba - Compra: ${cordoba_compra} | Venta: ${cordoba_venta}")
            print(f"   💰 Promedio Córdoba: ${(cordoba_compra + cordoba_venta) / 2:.2f}")
            
            # Comparar con bot actual
            print(f"\n📊 COMPARACIÓN CON BOT ACTUAL:")
            print(f"   Córdoba InfoDolar: ${cordoba_compra} / ${cordoba_venta}")
            print(f"   Bot actual:        $1285 / $1305")
            print(f"   Mejora potencial:  +${cordoba_compra - 1285:.0f} / +${cordoba_venta - 1305:.0f}")
            
            return cordoba_compra, cordoba_venta
        
        elif promedio_compra and promedio_venta:
            print(f"⚠️ CÓRDOBA NO ENCONTRADA, usando promedio:")
            print(f"   🔄 Promedio General - Compra: ${promedio_compra} | Venta: ${promedio_venta}")
            print(f"   💰 Promedio: ${(promedio_compra + promedio_venta) / 2:.2f}")
            
            return promedio_compra, promedio_venta
        
        else:
            print(f"❌ NO SE PUDIERON EXTRAER PRECIOS")
            print(f"   Ni Córdoba específica ni promedio general")
            return None, None
    
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        return None, None
    
    finally:
        if driver:
            try:
                driver.quit()
                print("🔧 Navegador cerrado")
            except:
                pass

def extraer_precios_cordoba_test(html_content):
    """
    Función de prueba para extraer precios de Córdoba (MEJORADA)
    """
    print("🔍 Buscando específicamente la fila de CÓRDOBA...")
    
    cordoba_compra = None
    cordoba_venta = None
    
    # === 🔍 ANÁLISIS DETALLADO DEL HTML ===
    print("📄 Analizando estructura HTML de InfoDolar...")
    
    # Buscar todas las menciones de Córdoba y sus contextos
    cordoba_contexts = []
    for match in re.finditer(r'.{0,200}Córdoba.{0,200}', html_content, re.IGNORECASE | re.DOTALL):
        context = match.group(0)
        cordoba_contexts.append(context)
        print(f"   📍 Contexto encontrado: {context[:100]}...")
    
    print(f"📊 Total contextos de Córdoba encontrados: {len(cordoba_contexts)}")
    
    # Patrones mejorados para encontrar Córdoba con AMBOS precios
    patterns_cordoba = [
        # Patrón 1: Córdoba seguido de dos precios diferentes
        r'Córdoba.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        
        # Patrón 2: En contexto de tabla HTML
        r'<td[^>]*>.*?Córdoba.*?</td>.*?<td[^>]*>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>.*?<td[^>]*>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>',
        
        # Patrón 3: Córdoba con números sin símbolo $
        r'Córdoba.*?([1-2]\.?\d{3}[,.]?\d{0,2}).*?([1-2]\.?\d{3}[,.]?\d{0,2})',
        
        # Patrón 4: Buscar en estructura de tabla más amplia
        r'(?i)córdoba.*?<td[^>]*>.*?([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>.*?<td[^>]*>.*?([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>',
        
        # Patrón 5: Con espacios y saltos de línea
        r'(?i)córdoba[\s\S]*?([1-2]\.?\d{3}[,.]?\d{0,2})[\s\S]*?([1-2]\.?\d{3}[,.]?\d{0,2})',
    ]
    
    # === 🎯 BÚSQUEDA ESPECÍFICA POR CONTEXTO ===
    for i, context in enumerate(cordoba_contexts, 1):
        print(f"\n🔍 Analizando contexto {i} de Córdoba:")
        print(f"   📄 Texto: {context[:150]}...")
        
        # Extraer todos los números que parecen precios del contexto
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
        
        # Eliminar duplicados y ordenar
        precios_en_contexto = sorted(list(set(precios_en_contexto)))
        print(f"   💰 Precios encontrados en contexto: {precios_en_contexto}")
        
        if len(precios_en_contexto) >= 2:
            cordoba_compra = min(precios_en_contexto)
            cordoba_venta = max(precios_en_contexto)
            print(f"   ✅ Córdoba extraída del contexto {i} - Compra: ${cordoba_compra}, Venta: ${cordoba_venta}")
            break
        elif len(precios_en_contexto) == 1:
            print(f"   ⚠️ Solo un precio encontrado en contexto {i}: ${precios_en_contexto[0]}")
    
    # === 🔄 MÉTODO ALTERNATIVO: PATRONES GLOBALES ===
    if not (cordoba_compra and cordoba_venta):
        print("\n🔄 Método de contexto falló, probando patrones globales...")
        
        for i, pattern in enumerate(patterns_cordoba, 1):
            print(f"   🔍 Probando patrón global {i} para Córdoba...")
            
            cordoba_match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            
            if cordoba_match:
                print(f"   ✅ Patrón {i} encontró coincidencia!")
                
                try:
                    precio1_str = cordoba_match.group(1)
                    precio2_str = cordoba_match.group(2)
                    
                    print(f"   📄 Precios extraídos: '{precio1_str}' y '{precio2_str}'")
                    
                    # Limpiar precios
                    precio1 = limpiar_precio_test(precio1_str)
                    precio2 = limpiar_precio_test(precio2_str)
                    
                    print(f"   🔢 Precios limpiados: {precio1} y {precio2}")
                    
                    if precio1 and precio2 and 1200 <= precio1 <= 1400 and 1200 <= precio2 <= 1400:
                        # Si son diferentes, asignar correctamente
                        if precio1 != precio2:
                            cordoba_compra = min(precio1, precio2)
                            cordoba_venta = max(precio1, precio2)
                            print(f"   🎯 Córdoba válida (diferentes) - Compra: ${cordoba_compra}, Venta: ${cordoba_venta}")
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
    
    # === 📊 GUARDAR HTML PARA ANÁLISIS ===
    if not (cordoba_compra and cordoba_venta):
        print("\n💾 Guardando HTML para análisis manual...")
        with open("infodolar_debug.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("   📄 HTML guardado en 'infodolar_debug.html'")
        
        # Mostrar fragmento con Córdoba
        for context in cordoba_contexts[:2]:  # Mostrar solo los primeros 2
            print(f"\n📋 FRAGMENTO DE CÓRDOBA PARA DEBUG:")
            print(f"   {context[:200]}...")
    
    # Si no encontramos Córdoba, extraer promedio general
    if not (cordoba_compra and cordoba_venta):
        print("🔄 Córdoba no encontrada, extrayendo promedio general...")
        todos_los_precios = extraer_todos_precios_test(html_content)
        
        if len(todos_los_precios) >= 2:
            promedio_compra = min(todos_los_precios)
            promedio_venta = max(todos_los_precios)
            print(f"   📊 Promedio calculado de {len(todos_los_precios)} precios")
            return None, None, promedio_compra, promedio_venta
    
    return cordoba_compra, cordoba_venta, None, None

def limpiar_precio_test(precio_str):
    """
    Función de prueba para limpiar precios
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
    print("🧪 PRUEBA ESPECÍFICA DE CÓRDOBA")
    print("🗺️ Verificando extracción de precios de Córdoba desde InfoDolar")
    print("🔒 Esta prueba NO envía mensajes a Telegram")
    print()
    
    compra, venta = test_cordoba_extraction()
    
    if compra and venta:
        print(f"\n🎉 ¡PRUEBA EXITOSA!")
        print(f"🗺️ Córdoba será integrada en AMBAS partes del COTIBOT:")
        print(f"   📊 BLUE + OFICIAL: Incluirá precios de Córdoba")
        print(f"   📊 BLUE + USDT/CCB: También incluirá precios de Córdoba")
        print(f"   💰 Resultado final será más preciso")
        
    else:
        print(f"\n💔 PRUEBA FALLÓ")
        print(f"❌ No se pudieron obtener precios de Córdoba")
        print(f"🔄 El bot usará promedio general o funcionará sin InfoDolar")
    
    print(f"\n🔒 CONFIRMACIÓN: Ningún mensaje enviado a Telegram")
    print(f"✅ Prueba de Córdoba completada")

if __name__ == "__main__":
    main() 