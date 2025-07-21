import requests
import json
import time
from datetime import datetime

def test_infodolar_endpoints():
    """
    Prueba los endpoints específicos encontrados en el Network del navegador
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.infodolar.com/cotizacion-dolar-blue.aspx',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }
    
    # Endpoints base de InfoDolar
    base_endpoints = [
        "https://www.infodolar.com/",
        "https://www.infodolar.com/api/",
        "https://www.infodolar.com/data/",
        "https://www.infodolar.com/cotizacion/",
        "https://www.infodolar.com/ajax/",
        "https://www.infodolar.com/json/",
        "https://www.infodolar.com/ws/"
    ]
    
    # Endpoints específicos para dólar blue
    specific_endpoints = [
        "https://www.infodolar.com/api/cotizacion",
        "https://www.infodolar.com/api/dolar-blue",
        "https://www.infodolar.com/api/blue",
        "https://www.infodolar.com/data/cotizaciones",
        "https://www.infodolar.com/data/dolar",
        "https://www.infodolar.com/ajax/cotizaciones.php",
        "https://www.infodolar.com/ajax/dolar-blue.php",
        "https://www.infodolar.com/cotizacion-dolar-blue.aspx/GetData",
        "https://www.infodolar.com/cotizacion-dolar-blue.aspx/GetCotizaciones"
    ]
    
    # Posibles parámetros
    params_variations = [
        {},
        {"tipo": "blue"},
        {"moneda": "dolar"},
        {"cotizacion": "blue"},
        {"format": "json"},
        {"_": int(time.time() * 1000)}  # Timestamp para evitar cache
    ]
    
    print("🔍 Probando endpoints de InfoDolar...")
    print("=" * 60)
    
    resultados = []
    
    # Probar endpoints base
    for endpoint in base_endpoints + specific_endpoints:
        print(f"\n🌐 Probando: {endpoint}")
        
        for params in params_variations:
            try:
                response = requests.get(endpoint, headers=headers, params=params, timeout=10)
                
                status_info = f"Status: {response.status_code}"
                size_info = f"Size: {len(response.content)}B"
                content_type = response.headers.get('Content-Type', 'unknown')
                
                print(f"   📊 {status_info} | {size_info} | Type: {content_type}")
                
                if response.status_code == 200 and len(response.content) > 100:
                    # Intentar parsear como JSON
                    try:
                        data = response.json()
                        print(f"   ✅ JSON válido encontrado!")
                        print(f"   📄 Estructura: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        
                        # Buscar precios en el JSON
                        precios = _extraer_precios_json(data)
                        if precios:
                            print(f"   💰 PRECIOS ENCONTRADOS: {precios}")
                            resultados.append({
                                'endpoint': endpoint,
                                'params': params,
                                'precios': precios,
                                'data': data
                            })
                        
                    except json.JSONDecodeError:
                        # Si no es JSON, buscar precios en texto
                        text_content = response.text
                        if any(precio in text_content for precio in ['1.3', '1.2', '1300', '1200']):
                            print(f"   💰 Posibles precios encontrados en texto")
                            # Guardar para análisis manual
                            with open(f'infodolar_response_{int(time.time())}.txt', 'w', encoding='utf-8') as f:
                                f.write(f"Endpoint: {endpoint}\n")
                                f.write(f"Params: {params}\n")
                                f.write(f"Status: {response.status_code}\n")
                                f.write(f"Content-Type: {content_type}\n")
                                f.write("=" * 50 + "\n")
                                f.write(text_content)
                            print(f"   💾 Respuesta guardada para análisis")
                
                elif response.status_code == 204:
                    print(f"   ℹ️  Status 204 (No Content) - Posible API endpoint")
                
                elif response.status_code == 404:
                    print(f"   ❌ No encontrado")
                
                else:
                    print(f"   ⚠️  Respuesta inesperada")
                
                # Pausa para no sobrecargar
                time.sleep(0.5)
                
            except requests.RequestException as e:
                print(f"   ❌ Error: {str(e)}")
                continue
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS:")
    
    if resultados:
        print(f"✅ Encontrados {len(resultados)} endpoints con precios:")
        for i, resultado in enumerate(resultados, 1):
            print(f"\n{i}. {resultado['endpoint']}")
            print(f"   Params: {resultado['params']}")
            print(f"   Precios: {resultado['precios']}")
    else:
        print("❌ No se encontraron endpoints con precios válidos")
        print("\n💡 RECOMENDACIÓN:")
        print("   - Revisa los archivos guardados (.txt) para análisis manual")
        print("   - Considera usar herramientas más avanzadas como Selenium")
        print("   - O integra las APIs que sí funcionan (Criptoya, DolarAPI)")

def _extraer_precios_json(data):
    """
    Extrae precios de una estructura JSON
    """
    precios = {}
    
    def buscar_precios_recursivo(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                
                # Buscar claves que sugieran precios
                if any(palabra in key.lower() for palabra in ['precio', 'price', 'compra', 'venta', 'buy', 'sell', 'bid', 'ask', 'cotizacion']):
                    if isinstance(value, (int, float)) and 1000 <= value <= 2000:
                        precios[new_path] = value
                    elif isinstance(value, str):
                        try:
                            # Intentar extraer número de string
                            import re
                            precio_match = re.search(r'([1-2]\d{3}(?:\.\d{2})?)', value)
                            if precio_match:
                                precio_num = float(precio_match.group(1))
                                if 1000 <= precio_num <= 2000:
                                    precios[new_path] = precio_num
                        except:
                            pass
                
                # Continuar búsqueda recursiva
                buscar_precios_recursivo(value, new_path)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                buscar_precios_recursivo(item, f"{path}[{i}]")
    
    buscar_precios_recursivo(data)
    return precios

if __name__ == "__main__":
    test_infodolar_endpoints() 