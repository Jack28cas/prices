import requests
import re
from bs4 import BeautifulSoup
import json

def inspeccionar_infodolar():
    """
    Inspecciona la página de InfoDolar para buscar llamadas AJAX/API
    """
    url = "https://www.infodolar.com/cotizacion-dolar-blue.aspx"
    
    # Headers para simular un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("🔍 Inspeccionando InfoDolar...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Página cargada correctamente (Status: {response.status_code})")
            
            # Buscar en el HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar scripts que puedan contener llamadas AJAX
            scripts = soup.find_all('script')
            
            print(f"\n📜 Analizando {len(scripts)} scripts...")
            
            # Patrones para buscar URLs de API
            api_patterns = [
                r'ajax\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'XMLHttpRequest.*open\s*\(\s*[\'"][^\'"]++[\'"],\s*[\'"]([^\'"]+)[\'"]',
                r'\.get\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'\.post\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'api[/\w]*\.aspx',
                r'[\'"]([^\'"]*api[^\'"]*\.aspx?[^\'"]*)[\'"]',
                r'[\'"]([^\'"]*ajax[^\'"]*\.aspx?[^\'"]*)[\'"]',
                r'[\'"]([^\'"]*data[^\'"]*\.aspx?[^\'"]*)[\'"]'
            ]
            
            found_urls = set()
            
            for script in scripts:
                if script.string:
                    script_content = script.string
                    
                    # Buscar patrones de API
                    for pattern in api_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        for match in matches:
                            if 'infodolar' in match or match.startswith('/') or match.startswith('http'):
                                found_urls.add(match)
            
            # Buscar en atributos de elementos
            print("\n🔍 Buscando en atributos de elementos...")
            
            # Buscar data-* attributes
            elements_with_data = soup.find_all(attrs={'data-url': True})
            elements_with_data += soup.find_all(attrs={'data-api': True})
            elements_with_data += soup.find_all(attrs={'data-endpoint': True})
            
            for element in elements_with_data:
                for attr, value in element.attrs.items():
                    if 'url' in attr.lower() or 'api' in attr.lower():
                        found_urls.add(value)
            
            # Mostrar URLs encontradas
            if found_urls:
                print(f"\n🎯 URLs potenciales encontradas:")
                for url in sorted(found_urls):
                    print(f"   • {url}")
                    
                # Probar las URLs encontradas
                print(f"\n🧪 Probando URLs encontradas...")
                for url in found_urls:
                    probar_url(url, headers)
            else:
                print("\n❌ No se encontraron URLs de API evidentes")
                
            # Buscar patrones específicos de InfoDolar
            print(f"\n🔍 Buscando patrones específicos...")
            
            # Buscar referencias a cotizaciones
            cotiz_pattern = r'cotiz[a-z]*[\'"]?\s*:\s*[\'"]?([^\'"]+)[\'"]?'
            cotiz_matches = re.findall(cotiz_pattern, response.text, re.IGNORECASE)
            
            if cotiz_matches:
                print("💰 Referencias a cotizaciones encontradas:")
                for match in cotiz_matches[:5]:  # Mostrar solo las primeras 5
                    print(f"   • {match}")
                    
        else:
            print(f"❌ Error al cargar la página (Status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def probar_url(url, headers):
    """
    Prueba una URL para ver si devuelve JSON
    """
    try:
        # Construir URL completa si es relativa
        if url.startswith('/'):
            url = 'https://www.infodolar.com' + url
        elif not url.startswith('http'):
            url = 'https://www.infodolar.com/' + url
            
        print(f"   🌐 Probando: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                # Intentar parsear como JSON
                data = response.json()
                print(f"   ✅ JSON encontrado! Claves: {list(data.keys()) if isinstance(data, dict) else 'Lista'}")
                
                # Mostrar un preview del JSON
                json_preview = json.dumps(data, indent=2)[:200] + "..."
                print(f"   📄 Preview: {json_preview}")
                
            except json.JSONDecodeError:
                # No es JSON, pero ver si contiene datos útiles
                content = response.text[:200]
                if any(keyword in content.lower() for keyword in ['dolar', 'blue', 'cotiz', 'precio']):
                    print(f"   📄 Contenido relevante encontrado: {content}...")
                else:
                    print(f"   ⚠️  Respuesta no JSON")
        else:
            print(f"   ❌ Status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    inspeccionar_infodolar() 