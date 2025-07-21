import requests
import re
import time
from bs4 import BeautifulSoup
import gzip
import io

def obtener_precio_infodolar_final():
    """
    InfoDolar con requests - Manejo correcto de compresión
    """
    try:
        print("🌐 Conectando a InfoDolar con decodificación correcta...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',  # Aceptar compresión
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        start_time = time.time()
        response = session.get('https://www.infodolar.com/cotizacion-dolar-blue.aspx', timeout=30)
        load_time = time.time() - start_time
        
        print(f"✅ InfoDolar respondió en {load_time:.2f} segundos")
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Encoding: {response.encoding}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # El texto ya debería estar decodificado por requests
            html_content = response.text
            print(f"📊 Tamaño HTML decodificado: {len(html_content)} caracteres")
            
            # Verificar si el contenido está legible
            if 'html' in html_content.lower()[:100]:
                print("✅ HTML decodificado correctamente")
            else:
                print("⚠️ HTML podría estar mal decodificado")
                # Intentar decodificación manual
                try:
                    html_content = response.content.decode('utf-8')
                    print("✅ Decodificación UTF-8 manual exitosa")
                except:
                    html_content = response.content.decode('latin-1')
                    print("✅ Decodificación latin-1 manual exitosa")
            
            # Guardar HTML legible
            with open('/tmp/infodolar_legible.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("💾 HTML legible guardado en /tmp/infodolar_legible.html")
            
            # Buscar contenido específico
            print("\n🔍 ANÁLISIS DEL CONTENIDO:")
            cordoba_found = html_content.lower().count('córdoba') + html_content.lower().count('cordoba')
            blue_found = html_content.lower().count('blue')
            dolar_found = html_content.lower().count('dolar') + html_content.lower().count('dólar')
            
            print(f"🗺️ 'Córdoba/Cordoba': {cordoba_found} veces")
            print(f"💙 'Blue': {blue_found} veces")
            print(f"💰 'Dolar/Dólar': {dolar_found} veces")
            
            # Buscar precios
            precios = buscar_precios_en_html(html_content)
            
            # Extraer precios específicos
            cordoba_compra, cordoba_venta = extraer_precios_cordoba(html_content)
            blue_general_compra, blue_general_venta = extraer_precios_blue_general(html_content, precios)
            
            print("\n📊 RESULTADOS FINALES:")
            print(f"🗺️ Córdoba: ${cordoba_compra} / ${cordoba_venta}")
            print(f"💙 Blue General: ${blue_general_compra} / ${blue_general_venta}")
            
            return cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return None, None, None, None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None, None, None, None

def buscar_precios_en_html(html_content):
    """Busca todos los precios posibles en el HTML"""
    print("🔍 Buscando todos los precios...")
    
    # Patrones más amplios
    patterns = [
        r'\$\s*([1-2][\d,\.]{3,6})',  # $1234, $1.234, $1,234
        r'([1-2][\d,\.]{3,6})',       # 1234, 1.234, 1,234
        r'>([1-2][\d,\.]{3,6})<',     # Entre tags HTML
        r'"([1-2][\d,\.]{3,6})"',     # Entre comillas
    ]
    
    precios = []
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            precio = limpiar_precio(match)
            if precio and 1200 <= precio <= 1500:  # Rango más amplio
                precios.append(precio)
    
    precios_unicos = sorted(list(set(precios)))
    print(f"💰 Precios válidos encontrados: {precios_unicos}")
    
    return precios_unicos

def extraer_precios_cordoba(html_content):
    """Extrae precios específicos de Córdoba"""
    print("🔍 Buscando precios de Córdoba...")
    
    # Buscar contexto de Córdoba
    cordoba_patterns = [
        r'(?i)córdoba[^<>]{0,100}?([1-2][\d,\.]{3,6})[^<>]{0,50}?([1-2][\d,\.]{3,6})',
        r'(?i)cordoba[^<>]{0,100}?([1-2][\d,\.]{3,6})[^<>]{0,50}?([1-2][\d,\.]{3,6})',
        r'<td[^>]*>[^<]*(?i:córdoba|cordoba)[^<]*</td>[^<>]*<td[^>]*>[^<]*([1-2][\d,\.]{3,6})[^<]*</td>[^<>]*<td[^>]*>[^<]*([1-2][\d,\.]{3,6})[^<]*</td>',
    ]
    
    for i, pattern in enumerate(cordoba_patterns, 1):
        matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            try:
                precio1 = limpiar_precio(match[0])
                precio2 = limpiar_precio(match[1])
                
                if precio1 and precio2 and 1200 <= precio1 <= 1500 and 1200 <= precio2 <= 1500:
                    if precio1 != precio2:
                        compra = min(precio1, precio2)
                        venta = max(precio1, precio2)
                        print(f"✅ Córdoba encontrada (patrón {i}): ${compra} / ${venta}")
                        return compra, venta
            except:
                continue
    
    print("⚠️ Córdoba no encontrada con patrones específicos")
    return None, None

def extraer_precios_blue_general(html_content, precios_disponibles):
    """Extrae precio general de Blue"""
    print("🔍 Estimando precio Blue general...")
    
    if len(precios_disponibles) >= 2:
        # Usar los precios más comunes o extremos
        compra = min(precios_disponibles)
        venta = max(precios_disponibles)
        print(f"✅ Blue general estimado: ${compra} / ${venta}")
        return compra, venta
    elif len(precios_disponibles) == 1:
        precio = precios_disponibles[0]
        spread = 20  # Spread estimado
        compra = precio - spread
        venta = precio + spread
        print(f"✅ Blue general con spread: ${compra} / ${venta}")
        return compra, venta
    
    print("⚠️ Blue general no disponible")
    return None, None

def limpiar_precio(precio_str):
    """Limpia y convierte precio a float"""
    try:
        # Remover caracteres no numéricos excepto . y ,
        clean = re.sub(r'[^\d,\.]', '', precio_str)
        
        if '.' in clean and ',' in clean:
            # Formato 1.234,56 -> 1234.56
            clean = clean.replace('.', '').replace(',', '.')
        elif ',' in clean and len(clean.split(',')[-1]) <= 2:
            # Formato 1234,56 -> 1234.56
            clean = clean.replace(',', '.')
        else:
            # Formato simple, remover separadores de miles
            clean = clean.replace('.', '').replace(',', '')
        
        return float(clean)
    except:
        return None

if __name__ == "__main__":
    print("🚀 INFODOLAR - VERSIÓN FINAL CON DECODIFICACIÓN")
    print("=" * 60)
    
    cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta = obtener_precio_infodolar_final()
    
    print("\n" + "=" * 60)
    if (cordoba_compra and cordoba_venta) or (blue_general_compra and blue_general_venta):
        print("🎉 ¡InfoDolar FUNCIONANDO!")
        print("✅ Listo para integrar al bot principal")
    else:
        print("❌ InfoDolar necesita análisis manual del HTML")
        print("🔍 Revisa /tmp/infodolar_legible.html")
