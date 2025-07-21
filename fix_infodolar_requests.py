import requests
import re
import time
from bs4 import BeautifulSoup

def obtener_precio_infodolar_requests():
    """
    InfoDolar con requests - SIN Selenium
    """
    try:
        print("🌐 Conectando a InfoDolar con requests...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        start_time = time.time()
        response = session.get('https://www.infodolar.com/cotizacion-dolar-blue.aspx', timeout=30)
        load_time = time.time() - start_time
        
        print(f"✅ InfoDolar respondió en {load_time:.2f} segundos")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            print(f"📊 Tamaño HTML: {len(html_content)} caracteres")
            
            # Guardar HTML para análisis
            with open('/tmp/infodolar_requests.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Extraer precios usando múltiples métodos
            cordoba_compra, cordoba_venta = extraer_precios_cordoba(html_content)
            blue_general_compra, blue_general_venta = extraer_precios_blue_general(html_content)
            
            print("📊 RESULTADOS:")
            print(f"🗺️ Córdoba: ${cordoba_compra} / ${cordoba_venta}")
            print(f"💙 Blue General: ${blue_general_compra} / ${blue_general_venta}")
            
            return cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return None, None, None, None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None, None, None, None

def extraer_precios_cordoba(html_content):
    """Extrae precios específicos de Córdoba"""
    print("🔍 Buscando precios de Córdoba...")
    
    # Patrones específicos para Córdoba
    patterns_cordoba = [
        r'Córdoba.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        r'<td[^>]*>.*?Córdoba.*?</td>.*?<td[^>]*>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>.*?<td[^>]*>.*?\$\s*([1-2]\.?\d{3}[,.]?\d{0,2}).*?</td>',
        r'(?i)córdoba[^$]*\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})[^$]*\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
    ]
    
    for i, pattern in enumerate(patterns_cordoba, 1):
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            try:
                precio1_str = match.group(1)
                precio2_str = match.group(2)
                
                precio1 = limpiar_precio(precio1_str)
                precio2 = limpiar_precio(precio2_str)
                
                if precio1 and precio2 and 1200 <= precio1 <= 1400 and 1200 <= precio2 <= 1400:
                    if precio1 != precio2:
                        compra = min(precio1, precio2)
                        venta = max(precio1, precio2)
                        print(f"✅ Córdoba encontrada (patrón {i}): ${compra} / ${venta}")
                        return compra, venta
            except:
                continue
    
    print("⚠️ Córdoba no encontrada")
    return None, None

def extraer_precios_blue_general(html_content):
    """Extrae precio general de InfoDolar"""
    print("🔍 Buscando precio Blue general...")
    
    # Buscar todos los precios válidos
    all_patterns = [
        r'\$\s*([1-2]\.?\d{3}[,.]?\d{0,2})',
        r'([1-2]\.?\d{3}[,.]?\d{0,2})',
        r'>([1-2]\.?\d{3}[,.]?\d{0,2})<',
    ]
    
    precios = []
    for pattern in all_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            precio = limpiar_precio(match)
            if precio and 1200 <= precio <= 1400:
                precios.append(precio)
    
    precios_unicos = sorted(list(set(precios)))
    print(f"💰 Precios encontrados: {precios_unicos}")
    
    if len(precios_unicos) >= 2:
        compra = min(precios_unicos)
        venta = max(precios_unicos)
        print(f"✅ Blue general: ${compra} / ${venta}")
        return compra, venta
    
    print("⚠️ Blue general no encontrado")
    return None, None

def limpiar_precio(precio_str):
    """Limpia y convierte precio a float"""
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
    except:
        return None

if __name__ == "__main__":
    print("🚀 PROBANDO INFODOLAR CON REQUESTS")
    print("=" * 50)
    
    cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta = obtener_precio_infodolar_requests()
    
    print("\n" + "=" * 50)
    if (cordoba_compra and cordoba_venta) or (blue_general_compra and blue_general_venta):
        print("🎉 ¡InfoDolar FUNCIONANDO con requests!")
    else:
        print("❌ InfoDolar necesita más análisis")
        print("🔍 Revisa /tmp/infodolar_requests.html para debug")
