import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class InfoDolarInspector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.base_url = "https://www.infodolar.com"
        
    def inspeccionar_pagina_principal(self):
        """
        Inspecciona la página principal de InfoDolar
        """
        print("🔍 Inspeccionando página principal de InfoDolar...")
        
        url = f"{self.base_url}/cotizacion-dolar-blue.aspx"
        
        try:
            response = self.session.get(url)
            if response.status_code != 200:
                print(f"❌ Error al cargar la página: {response.status_code}")
                return
                
            print(f"✅ Página cargada correctamente")
            
            # Analizar el HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar scripts con posibles llamadas AJAX
            self._buscar_scripts_ajax(soup)
            
            # Buscar formularios que puedan hacer POST
            self._buscar_formularios(soup)
            
            # Buscar elementos con data attributes
            self._buscar_data_attributes(soup)
            
            # Buscar patrones de ViewState (ASP.NET)
            self._buscar_viewstate(soup, response.text)
            
            # Intentar buscar endpoints comunes
            self._probar_endpoints_comunes()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def _buscar_scripts_ajax(self, soup):
        """
        Busca scripts que contengan llamadas AJAX
        """
        print("\n📜 Analizando scripts JavaScript...")
        
        scripts = soup.find_all('script')
        ajax_patterns = [
            r'\.ajax\s*\(\s*{[^}]*url\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'XMLHttpRequest.*open\s*\(\s*[\'"]([^\'"]++)[\'"],\s*[\'"]([^\'"]+)[\'"]',
            r'jQuery\.post\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'jQuery\.get\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'\$\.post\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'\$\.get\s*\(\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        found_urls = set()
        
        for script in scripts:
            if script.string:
                content = script.string
                
                for pattern in ajax_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        url = match if isinstance(match, str) else match[1]
                        if url and not url.startswith('javascript:'):
                            found_urls.add(url)
        
        if found_urls:
            print("🎯 URLs encontradas en scripts:")
            for url in sorted(found_urls):
                full_url = urljoin(self.base_url, url)
                print(f"   • {url} → {full_url}")
                self._probar_endpoint(full_url)
        else:
            print("❌ No se encontraron URLs AJAX en scripts")
    
    def _buscar_formularios(self, soup):
        """
        Busca formularios que puedan enviar datos
        """
        print("\n📝 Analizando formularios...")
        
        forms = soup.find_all('form')
        if forms:
            for i, form in enumerate(forms):
                action = form.get('action', '')
                method = form.get('method', 'GET').upper()
                
                print(f"   📋 Formulario {i+1}:")
                print(f"      Action: {action}")
                print(f"      Method: {method}")
                
                # Buscar campos hidden que puedan contener tokens
                hidden_inputs = form.find_all('input', {'type': 'hidden'})
                for hidden in hidden_inputs:
                    name = hidden.get('name', '')
                    if 'viewstate' in name.lower() or 'token' in name.lower():
                        print(f"      Hidden: {name}")
        else:
            print("❌ No se encontraron formularios")
    
    def _buscar_data_attributes(self, soup):
        """
        Busca elementos con atributos data-* que puedan contener URLs
        """
        print("\n🔍 Buscando atributos data-*...")
        
        elements = soup.find_all(attrs=lambda x: x and any(attr.startswith('data-') for attr in x.keys()))
        
        found = False
        for element in elements:
            for attr, value in element.attrs.items():
                if attr.startswith('data-') and ('url' in attr.lower() or 'api' in attr.lower() or 'endpoint' in attr.lower()):
                    print(f"   🎯 {attr}: {value}")
                    found = True
        
        if not found:
            print("❌ No se encontraron atributos data-* relevantes")
    
    def _buscar_viewstate(self, soup, html_content):
        """
        Busca ViewState de ASP.NET que puede contener información útil
        """
        print("\n🔐 Analizando ViewState (ASP.NET)...")
        
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        if viewstate:
            print("✅ Página usa ASP.NET ViewState")
            
            # Buscar UpdatePanels que usen AJAX
            update_panels = soup.find_all('div', {'id': re.compile(r'UpdatePanel')})
            if update_panels:
                print(f"   📦 Encontrados {len(update_panels)} UpdatePanels")
                for panel in update_panels:
                    panel_id = panel.get('id', '')
                    print(f"      • {panel_id}")
        else:
            print("❌ No es una página ASP.NET con ViewState")
    
    def _probar_endpoints_comunes(self):
        """
        Prueba endpoints comunes que suelen usar las páginas de cotizaciones
        """
        print("\n🧪 Probando endpoints comunes...")
        
        endpoints = [
            "/api/cotizaciones",
            "/api/dolar",
            "/api/blue",
            "/cotizaciones.aspx",
            "/ajax/cotizaciones.aspx",
            "/data/cotizaciones.aspx",
            "/services/cotizaciones.asmx",
            "/handlers/cotizaciones.ashx",
            "/api/infodolar",
            "/webservice/cotizaciones.asmx"
        ]
        
        for endpoint in endpoints:
            full_url = urljoin(self.base_url, endpoint)
            self._probar_endpoint(full_url)
    
    def _probar_endpoint(self, url):
        """
        Prueba un endpoint específico
        """
        try:
            print(f"   🌐 Probando: {url}")
            
            # Probar GET
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        print(f"      ✅ JSON válido encontrado!")
                        
                        # Buscar datos de cotización
                        json_str = json.dumps(data, indent=2)
                        if any(keyword in json_str.lower() for keyword in ['dolar', 'blue', 'cotiz', 'precio', 'compra', 'venta']):
                            print(f"      🎯 Contiene datos de cotización!")
                            print(f"      📄 Preview: {json_str[:300]}...")
                            
                            # Guardar la respuesta completa
                            with open('infodolar_response.json', 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            print(f"      💾 Respuesta guardada en 'infodolar_response.json'")
                            
                        return True
                        
                    except json.JSONDecodeError:
                        pass
                
                elif 'text/html' in content_type:
                    if len(response.text) < 1000:  # Respuesta corta, podría ser datos
                        print(f"      📄 HTML corto: {response.text[:100]}...")
                
                elif 'application/xml' in content_type or 'text/xml' in content_type:
                    print(f"      📄 XML encontrado: {response.text[:100]}...")
                    
            elif response.status_code == 404:
                print(f"      ❌ No encontrado (404)")
            elif response.status_code == 403:
                print(f"      🚫 Acceso denegado (403)")
            elif response.status_code == 500:
                print(f"      💥 Error del servidor (500)")
            else:
                print(f"      ❓ Status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"      ⏰ Timeout")
        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
        
        return False

def main():
    inspector = InfoDolarInspector()
    inspector.inspeccionar_pagina_principal()
    
    print(f"\n🔍 Inspección completada.")
    print(f"💡 Si no se encontraron APIs, puedes:")
    print(f"   1. Inspeccionar manualmente con F12 en el navegador")
    print(f"   2. Buscar llamadas AJAX mientras interactúas con la página")
    print(f"   3. Usar herramientas como Burp Suite o OWASP ZAP")

if __name__ == "__main__":
    main() 