# Leer archivo actual
with open('usdtfiwind.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar la función obtener_precio_infodolar con la configuración que funciona
new_function = '''def obtener_precio_infodolar():
    """
    Obtiene precios de InfoDolar: Córdoba específica Y Dólar Blue general
    CONFIGURACIÓN QUE FUNCIONA EN LOCAL
    """
    driver = None
    try:
        logging.info("🔥 Obteniendo precios de InfoDolar (Córdoba + Blue General)...")
        
        # Configuración que FUNCIONA en local
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-images")  # Más rápido
        chrome_options.add_argument("--disable-javascript")  # Inicialmente sin JS
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Inicializar driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)  # Timeout más generoso
        driver.implicitly_wait(10)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logging.info("🌐 Cargando InfoDolar (sin JavaScript inicialmente)...")
        driver.get("https://www.infodolar.com/cotizacion-dolar-blue.aspx")
        
        # Obtener HTML estático primero
        static_html = driver.page_source
        
        # Buscar precios en HTML estático
        cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta, _, _ = _extraer_precios_completos_infodolar(static_html)
        
        # Si no encontramos precios, habilitar JavaScript
        if not (cordoba_compra and cordoba_venta and blue_general_compra and blue_general_venta):
            logging.info("🔄 Habilitando JavaScript y recargando...")
            driver.execute_script("window.location.reload();")
            time.sleep(5)  # Esperar carga JavaScript
            
            # Obtener HTML después de JavaScript
            dynamic_html = driver.page_source
            cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta, _, _ = _extraer_precios_completos_infodolar(dynamic_html)
        
        return cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta
    
    except Exception as e:
        logging.error(f"❌ Error al obtener precios InfoDolar: {str(e)}")
        logging.info("🔄 InfoDolar no disponible - Bot continúa con otras 11 fuentes")
        return None, None, None, None
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass'''

# Buscar y reemplazar la función
import re
pattern = r'def obtener_precio_infodolar\(\):.*?(?=\n\ndef|\nclass|\n# ===|\Z)'
new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)

# Escribir archivo actualizado
with open('usdtfiwind.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Configuración InfoDolar actualizada con la versión que funciona en local")
