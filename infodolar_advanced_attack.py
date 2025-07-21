import requests
import json
import re
import time
from bs4 import BeautifulSoup
import base64
from urllib.parse import urljoin, urlparse, parse_qs

class InfoDolarAdvancedAttack:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.infodolar.com"
        self.main_page = "https://www.infodolar.com/cotizacion-dolar-blue.aspx"
        
        # Headers más realistas
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })

    def step1_load_main_page(self):
        """
        Paso 1: Cargar la página principal y extraer cookies/tokens
        """
        print("🔥 PASO 1: Cargando página principal...")
        
        try:
            response = self.session.get(self.main_page, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Página cargada: {len(response.content)} bytes")
                
                # Guardar HTML para análisis
                with open('infodolar_main_page.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # Extraer información importante
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 1. Buscar ViewState (ASP.NET)
                viewstate = self._extract_viewstate(soup)
                
                # 2. Buscar tokens/keys en JavaScript
                js_tokens = self._extract_js_tokens(response.text)
                
                # 3. Buscar formularios ocultos
                hidden_inputs = self._extract_hidden_inputs(soup)
                
                # 4. Buscar llamadas AJAX en JavaScript
                ajax_calls = self._extract_ajax_calls(response.text)
                
                # 5. Analizar cookies recibidas
                cookies_info = self._analyze_cookies()
                
                print(f"📊 ViewState encontrado: {'✅' if viewstate else '❌'}")
                print(f"📊 Tokens JS encontrados: {len(js_tokens)}")
                print(f"📊 Inputs ocultos: {len(hidden_inputs)}")
                print(f"📊 Llamadas AJAX: {len(ajax_calls)}")
                print(f"📊 Cookies recibidas: {len(self.session.cookies)}")
                
                return {
                    'viewstate': viewstate,
                    'js_tokens': js_tokens,
                    'hidden_inputs': hidden_inputs,
                    'ajax_calls': ajax_calls,
                    'cookies': cookies_info
                }
                
            else:
                print(f"❌ Error al cargar página: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error en paso 1: {str(e)}")
            return None

    def step2_test_discovered_endpoints(self, page_data):
        """
        Paso 2: Probar todos los endpoints descubiertos
        """
        print("\n🔥 PASO 2: Probando endpoints descubiertos...")
        
        if not page_data:
            print("❌ No hay datos de la página principal")
            return []
        
        successful_endpoints = []
        
        # Probar llamadas AJAX encontradas
        for ajax_call in page_data['ajax_calls']:
            print(f"\n🌐 Probando AJAX: {ajax_call}")
            result = self._test_ajax_endpoint(ajax_call, page_data)
            if result:
                successful_endpoints.append(result)
        
        # Probar endpoints comunes con tokens
        common_endpoints = [
            '/json/',
            '/api/cotizaciones',
            '/ws/dolar',
            '/ajax/precios',
            '/data/blue'
        ]
        
        for endpoint in common_endpoints:
            print(f"\n🌐 Probando con tokens: {endpoint}")
            result = self._test_endpoint_with_tokens(endpoint, page_data)
            if result:
                successful_endpoints.append(result)
        
        return successful_endpoints

    def step3_simulate_browser_behavior(self, page_data):
        """
        Paso 3: Simular comportamiento completo del navegador
        """
        print("\n🔥 PASO 3: Simulando comportamiento del navegador...")
        
        # Simular carga de recursos estáticos
        self._load_static_resources()
        
        # Simular JavaScript execution delays
        time.sleep(2)
        
        # Intentar POST con ViewState si existe
        if page_data and page_data['viewstate']:
            return self._try_postback_with_viewstate(page_data)
        
        return None

    def _extract_viewstate(self, soup):
        """Extrae ViewState de ASP.NET"""
        viewstate_input = soup.find('input', {'name': '__VIEWSTATE'})
        if viewstate_input:
            return viewstate_input.get('value')
        return None

    def _extract_js_tokens(self, html_content):
        """Extrae tokens/keys de JavaScript"""
        tokens = []
        
        # Patrones comunes de tokens
        patterns = [
            r'apiKey["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'key["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'auth["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'session["\']?\s*[:=]\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            tokens.extend(matches)
        
        return list(set(tokens))  # Eliminar duplicados

    def _extract_hidden_inputs(self, soup):
        """Extrae inputs ocultos de formularios"""
        hidden_inputs = {}
        
        for input_tag in soup.find_all('input', type='hidden'):
            name = input_tag.get('name')
            value = input_tag.get('value')
            if name and value:
                hidden_inputs[name] = value
        
        return hidden_inputs

    def _extract_ajax_calls(self, html_content):
        """Extrae llamadas AJAX del JavaScript"""
        ajax_calls = []
        
        # Patrones para diferentes tipos de llamadas AJAX
        patterns = [
            r'ajax\s*\(\s*[{\'"]\s*url\s*[:\'"]\s*[\'"]([^\'\"]+)[\'"]',
            r'fetch\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            r'XMLHttpRequest.*open\s*\(\s*[\'"]GET[\'"],\s*[\'"]([^\'\"]+)[\'"]',
            r'\.get\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            r'\.post\s*\(\s*[\'"]([^\'\"]+)[\'"]'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if not match.startswith('http') and not match.startswith('//'):
                    ajax_calls.append(urljoin(self.base_url, match))
                else:
                    ajax_calls.append(match)
        
        return list(set(ajax_calls))

    def _analyze_cookies(self):
        """Analiza las cookies recibidas"""
        cookies_info = {}
        
        for cookie in self.session.cookies:
            cookies_info[cookie.name] = {
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure
            }
        
        return cookies_info

    def _test_ajax_endpoint(self, url, page_data):
        """Prueba un endpoint AJAX con todos los datos disponibles"""
        try:
            # Headers para AJAX
            ajax_headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': self.main_page
            }
            
            # Probar GET
            response = self.session.get(url, headers=ajax_headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ ÉXITO AJAX GET: {url}")
                    print(f"📄 Datos JSON: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                    
                    # Buscar precios
                    precios = self._buscar_precios_en_json(data)
                    if precios:
                        print(f"💰 PRECIOS ENCONTRADOS: {precios}")
                        
                        # Guardar resultado exitoso
                        with open(f'infodolar_success_ajax.json', 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        
                        return {
                            'url': url,
                            'method': 'GET',
                            'data': data,
                            'precios': precios
                        }
                
                except json.JSONDecodeError:
                    pass
            
            # Si GET no funciona, probar POST con datos del formulario
            if page_data['hidden_inputs']:
                response = self.session.post(url, data=page_data['hidden_inputs'], headers=ajax_headers, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ ÉXITO AJAX POST: {url}")
                        precios = self._buscar_precios_en_json(data)
                        if precios:
                            print(f"💰 PRECIOS ENCONTRADOS: {precios}")
                            return {
                                'url': url,
                                'method': 'POST',
                                'data': data,
                                'precios': precios
                            }
                    except json.JSONDecodeError:
                        pass
        
        except Exception as e:
            pass
        
        return None

    def _test_endpoint_with_tokens(self, endpoint, page_data):
        """Prueba endpoint con todos los tokens disponibles"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            # Probar con diferentes combinaciones de parámetros
            param_combinations = [
                {},
                {'format': 'json'},
                {'type': 'blue'},
                {'_': int(time.time() * 1000)}
            ]
            
            # Agregar tokens como parámetros
            for token in page_data['js_tokens']:
                param_combinations.append({'token': token})
                param_combinations.append({'key': token})
                param_combinations.append({'auth': token})
            
            for params in param_combinations:
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        precios = self._buscar_precios_en_json(data)
                        if precios:
                            print(f"✅ ÉXITO con tokens: {url}")
                            print(f"💰 PRECIOS: {precios}")
                            return {
                                'url': url,
                                'params': params,
                                'data': data,
                                'precios': precios
                            }
                    except json.JSONDecodeError:
                        pass
        
        except Exception as e:
            pass
        
        return None

    def _load_static_resources(self):
        """Simula carga de recursos estáticos para parecer más real"""
        static_resources = [
            '/css/bootstrap.min.css',
            '/js/jquery.min.js',
            '/js/bootstrap.min.js'
        ]
        
        for resource in static_resources:
            try:
                self.session.get(urljoin(self.base_url, resource), timeout=5)
                time.sleep(0.1)
            except:
                pass

    def _try_postback_with_viewstate(self, page_data):
        """Intenta hacer postback con ViewState"""
        try:
            postback_data = page_data['hidden_inputs'].copy()
            
            # Agregar datos típicos de postback
            postback_data.update({
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__ASYNCPOST': 'true'
            })
            
            response = self.session.post(self.main_page, data=postback_data, timeout=30)
            
            if response.status_code == 200:
                # Buscar JSON en la respuesta
                json_matches = re.findall(r'\{[^{}]*"[^"]*"[^{}]*\}', response.text)
                
                for json_str in json_matches:
                    try:
                        data = json.loads(json_str)
                        precios = self._buscar_precios_en_json(data)
                        if precios:
                            print(f"✅ ÉXITO PostBack ViewState!")
                            print(f"💰 PRECIOS: {precios}")
                            return {
                                'method': 'PostBack',
                                'data': data,
                                'precios': precios
                            }
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            pass
        
        return None

    def _buscar_precios_en_json(self, data):
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
                            # Extraer números de strings
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

    def execute_full_attack(self):
        """Ejecuta el ataque completo"""
        print("🚀 INICIANDO ATAQUE AVANZADO CONTRA INFODOLAR")
        print("=" * 60)
        
        # Paso 1: Cargar página principal
        page_data = self.step1_load_main_page()
        
        # Paso 2: Probar endpoints descubiertos
        successful_endpoints = self.step2_test_discovered_endpoints(page_data)
        
        # Paso 3: Simular comportamiento del navegador
        browser_result = self.step3_simulate_browser_behavior(page_data)
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN DEL ATAQUE:")
        
        if successful_endpoints:
            print(f"✅ Endpoints exitosos encontrados: {len(successful_endpoints)}")
            for endpoint in successful_endpoints:
                print(f"   🎯 {endpoint['url']}")
                print(f"      Precios: {endpoint['precios']}")
        
        if browser_result:
            print(f"✅ Simulación de navegador exitosa:")
            print(f"   Precios: {browser_result['precios']}")
        
        if not successful_endpoints and not browser_result:
            print("❌ No se pudieron obtener datos de InfoDolar")
            print("💡 InfoDolar tiene protecciones muy avanzadas")
            print("   Considera usar Selenium o APIs alternativas")
        
        return successful_endpoints, browser_result

def main():
    attacker = InfoDolarAdvancedAttack()
    return attacker.execute_full_attack()

if __name__ == "__main__":
    main() 