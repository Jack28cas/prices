"""
ATAQUE FINAL CON SELENIUM - Navegador Real
Este script usa Selenium para ejecutar JavaScript y capturar datos de InfoDolar
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

class InfoDolarSeleniumAttack:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Configura el driver de Chrome con opciones optimizadas"""
        print("🔧 Configurando navegador Chrome...")
        
        chrome_options = Options()
        
        # Opciones para parecer un navegador real
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--accept-lang=es-ES,es;q=0.9")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Habilitar logging de red para capturar requests
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_experimental_option("perfLoggingPrefs", {
            "enableNetwork": True,
            "enablePage": True
        })
        chrome_options.add_experimental_option("loggingPrefs", {
            "performance": "ALL",
            "browser": "ALL"
        })
        
        # Para debugging - comentar en producción
        # chrome_options.add_argument("--headless")  # Ejecutar sin ventana
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Ejecutar script para ocultar que es automatización
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Navegador configurado correctamente")
            
        except Exception as e:
            print(f"❌ Error configurando navegador: {str(e)}")
            print("💡 Asegúrate de tener ChromeDriver instalado")
            print("   Descarga desde: https://chromedriver.chromium.org/")
            raise

    def capture_network_requests(self):
        """Captura todas las requests de red mientras carga la página"""
        print("🌐 Cargando InfoDolar y capturando requests de red...")
        
        # Navegar a InfoDolar
        self.driver.get("https://www.infodolar.com/cotizacion-dolar-blue.aspx")
        
        # Esperar a que cargue completamente
        print("⏳ Esperando carga completa...")
        time.sleep(5)
        
        # Capturar logs de red
        logs = self.driver.get_log('performance')
        network_requests = []
        
        for log in logs:
            message = json.loads(log['message'])
            
            if message['message']['method'] in ['Network.responseReceived', 'Network.requestWillBeSent']:
                request_data = message['message']['params']
                
                if 'response' in request_data:
                    response = request_data['response']
                    url = response['url']
                    status = response.get('status', 0)
                    mime_type = response.get('mimeType', '')
                    
                    # Filtrar requests relevantes
                    if ('infodolar.com' in url and 
                        (mime_type == 'application/json' or 
                         'json' in url.lower() or 
                         'api' in url.lower() or
                         'ajax' in url.lower() or
                         'ws' in url.lower())):
                        
                        network_requests.append({
                            'url': url,
                            'status': status,
                            'mimeType': mime_type,
                            'method': request_data.get('request', {}).get('method', 'GET')
                        })
                        
                        print(f"📡 Request capturada: {url}")
                        print(f"   Status: {status} | Type: {mime_type}")
        
        return network_requests

    def extract_data_from_page(self):
        """Extrae datos directamente del DOM después de que JavaScript cargue"""
        print("🔍 Extrayendo datos del DOM...")
        
        try:
            # Esperar a que aparezcan elementos con precios
            wait = WebDriverWait(self.driver, 10)
            
            # Buscar diferentes selectores posibles para precios
            price_selectors = [
                '[class*="precio"]',
                '[class*="price"]',
                '[class*="cotizacion"]',
                '[class*="blue"]',
                'td:contains("$")',
                '.currency',
                '.amount'
            ]
            
            found_prices = {}
            
            for selector in price_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        text = element.text.strip()
                        
                        # Buscar precios en el texto
                        price_matches = re.findall(r'\$\s*([1-2]\d{3}(?:[,.]?\d{2})?)', text)
                        
                        for match in price_matches:
                            try:
                                price = float(match.replace(',', ''))
                                if 1200 <= price <= 1400:
                                    found_prices[f"{selector}_{len(found_prices)}"] = price
                                    print(f"💰 Precio encontrado: ${price} (selector: {selector})")
                            except ValueError:
                                continue
                                
                except Exception as e:
                    continue
            
            # También buscar en todo el texto de la página
            page_text = self.driver.page_source
            all_prices = re.findall(r'\$\s*([1-2]\d{3}(?:[,.]?\d{2})?)', page_text)
            
            for match in all_prices:
                try:
                    price = float(match.replace(',', ''))
                    if 1200 <= price <= 1400:
                        found_prices[f"page_text_{len(found_prices)}"] = price
                except ValueError:
                    continue
            
            # Eliminar duplicados y mostrar únicos
            unique_prices = list(set(found_prices.values()))
            
            if unique_prices:
                print(f"🎯 Precios únicos encontrados: {sorted(unique_prices)}")
                return unique_prices
            else:
                print("❌ No se encontraron precios en el DOM")
                return []
                
        except TimeoutException:
            print("⏰ Timeout esperando elementos de precios")
            return []

    def test_discovered_requests(self, network_requests):
        """Prueba las requests descubiertas con requests normales"""
        print("🧪 Probando requests descubiertas...")
        
        import requests
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.infodolar.com/cotizacion-dolar-blue.aspx'
        })
        
        # Copiar cookies del navegador Selenium
        selenium_cookies = self.driver.get_cookies()
        
        for cookie in selenium_cookies:
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
        
        successful_requests = []
        
        for request in network_requests:
            try:
                print(f"\n🌐 Probando: {request['url']}")
                
                response = session.get(request['url'], timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ JSON válido obtenido!")
                        
                        # Buscar precios en JSON
                        precios = self._buscar_precios_json(data)
                        
                        if precios:
                            print(f"💰 PRECIOS ENCONTRADOS: {precios}")
                            
                            # Guardar resultado exitoso
                            with open(f'infodolar_selenium_success.json', 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            
                            successful_requests.append({
                                'url': request['url'],
                                'data': data,
                                'precios': precios
                            })
                    
                    except json.JSONDecodeError:
                        print(f"⚠️  Respuesta no es JSON válido")
                
                else:
                    print(f"❌ Status: {response.status_code}")
            
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        return successful_requests

    def _buscar_precios_json(self, data):
        """Busca precios en estructura JSON"""
        precios = {}
        
        def buscar_recursivo(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    
                    # Buscar claves relacionadas con precios
                    precio_keys = ['precio', 'price', 'compra', 'venta', 'buy', 'sell', 'bid', 'ask', 'cotizacion', 'valor', 'value']
                    
                    if any(pk in key.lower() for pk in precio_keys):
                        if isinstance(value, (int, float)) and 1000 <= value <= 2000:
                            precios[new_path] = value
                        elif isinstance(value, str):
                            precio_match = re.search(r'([1-2]\d{3}(?:[.,]\d{2})?)', value)
                            if precio_match:
                                try:
                                    precio_num = float(precio_match.group(1).replace(',', '.'))
                                    if 1000 <= precio_num <= 2000:
                                        precios[new_path] = precio_num
                                except ValueError:
                                    pass
                    
                    buscar_recursivo(value, new_path)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    buscar_recursivo(item, f"{path}[{i}]")
        
        buscar_recursivo(data)
        return precios

    def execute_selenium_attack(self):
        """Ejecuta el ataque completo con Selenium"""
        print("🚀 INICIANDO ATAQUE SELENIUM CONTRA INFODOLAR")
        print("=" * 60)
        
        try:
            # Paso 1: Capturar requests de red
            network_requests = self.capture_network_requests()
            
            # Paso 2: Extraer datos del DOM
            dom_prices = self.extract_data_from_page()
            
            # Paso 3: Probar requests descubiertas
            successful_requests = self.test_discovered_requests(network_requests)
            
            # Resumen final
            print("\n" + "=" * 60)
            print("📊 RESUMEN SELENIUM ATTACK:")
            
            if network_requests:
                print(f"📡 Requests de red capturadas: {len(network_requests)}")
                for req in network_requests[:5]:  # Mostrar primeras 5
                    print(f"   🌐 {req['url']}")
            
            if dom_prices:
                print(f"💰 Precios encontrados en DOM: {dom_prices}")
                
                # Calcular promedio
                if len(dom_prices) >= 2:
                    compra = min(dom_prices)
                    venta = max(dom_prices)
                    print(f"🎯 RESULTADO: Compra ${compra} | Venta ${venta}")
                    return compra, venta
            
            if successful_requests:
                print(f"✅ Requests exitosas: {len(successful_requests)}")
                for req in successful_requests:
                    print(f"   🎯 {req['url']}")
                    print(f"      Precios: {req['precios']}")
                    
                    # Retornar primer resultado exitoso
                    if req['precios']:
                        precios_vals = list(req['precios'].values())
                        if len(precios_vals) >= 2:
                            compra = min(precios_vals)
                            venta = max(precios_vals)
                            return compra, venta
            
            if not network_requests and not dom_prices and not successful_requests:
                print("❌ Selenium tampoco pudo obtener datos de InfoDolar")
                print("💡 InfoDolar tiene las protecciones más avanzadas")
                print("   Recomiendo usar APIs alternativas confiables")
            
            return None, None
            
        except Exception as e:
            print(f"❌ Error en ataque Selenium: {str(e)}")
            return None, None
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔧 Navegador cerrado")

def main():
    """Función principal"""
    try:
        attacker = InfoDolarSeleniumAttack()
        compra, venta = attacker.execute_selenium_attack()
        
        if compra and venta:
            print(f"\n🎉 ¡ÉXITO TOTAL!")
            print(f"InfoDolar - Compra: ${compra} | Venta: ${venta}")
            print(f"Promedio: ${(compra + venta) / 2:.2f}")
        else:
            print(f"\n💔 No se pudieron obtener precios de InfoDolar")
            print(f"🔄 ¿Intentamos con APIs alternativas más confiables?")
        
        return compra, venta
        
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        return None, None

if __name__ == "__main__":
    main() 