from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

def test_infodolar_optimizado():
    driver = None
    try:
        print("🔧 Configurando Chrome para InfoDolar...")
        
        # Configuración ESPECÍFICA para InfoDolar
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # PERMITIR JavaScript para InfoDolar (necesario)
        # chrome_options.add_argument("--disable-javascript")  # COMENTADO
        
        # Optimizaciones de red
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Inicializar driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)  # Timeout más generoso
        driver.implicitly_wait(15)  # Esperar elementos
        
        print("🌐 Conectando a InfoDolar con JavaScript habilitado...")
        start_time = time.time()
        
        # Cargar página
        driver.get("https://www.infodolar.com/cotizacion-dolar-blue.aspx")
        
        print("⏳ Esperando que cargue el contenido JavaScript...")
        time.sleep(10)  # Esperar carga de JavaScript
        
        load_time = time.time() - start_time
        print(f"✅ InfoDolar cargado en {load_time:.2f} segundos")
        
        # Obtener HTML después de JavaScript
        page_source = driver.page_source
        
        print(f"📊 Tamaño HTML: {len(page_source)} caracteres")
        
        # Buscar contenido específico
        cordoba_found = "córdoba" in page_source.lower()
        blue_found = "blue" in page_source.lower()
        infodolar_found = "infodolar" in page_source.lower()
        
        print(f"🗺️ 'Córdoba' encontrado: {cordoba_found}")
        print(f"💙 'Blue' encontrado: {blue_found}")
        print(f"🏢 'InfoDolar' encontrado: {infodolar_found}")
        
        # Buscar precios con patrones específicos
        price_patterns = [
            r'\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
            r'([1-2]\.?\d{3}[,.]?\d{0,2})',
        ]
        
        precios_encontrados = []
        for pattern in price_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            for match in matches:
                try:
                    # Limpiar precio
                    clean_price = match.replace('.', '').replace(',', '')
                    precio = float(clean_price)
                    if 1200 <= precio <= 1400:
                        precios_encontrados.append(precio)
                except:
                    continue
        
        precios_unicos = list(set(precios_encontrados))
        print(f"💰 Precios válidos encontrados: {len(precios_unicos)}")
        print(f"💰 Precios: {sorted(precios_unicos)}")
        
        if len(precios_unicos) >= 2:
            print("✅ InfoDolar funcionando - precios extraídos correctamente")
            return True
        else:
            print("⚠️ InfoDolar carga pero faltan precios")
            # Guardar HTML para debug
            with open('/tmp/infodolar_debug.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("🔍 HTML guardado en /tmp/infodolar_debug.html para debug")
            return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    print("🚀 PROBANDO INFODOLAR OPTIMIZADO PARA SERVIDOR")
    print("=" * 60)
    success = test_infodolar_optimizado()
    print("=" * 60)
    print(f"Resultado: {'✅ ÉXITO' if success else '❌ NECESITA MÁS AJUSTES'}")
