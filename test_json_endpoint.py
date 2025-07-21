import requests
import json

def test_json_endpoint():
    """
    Prueba específica del endpoint /json/ que devolvió 403 Forbidden
    """
    
    base_url = "https://www.infodolar.com/json/"
    
    # Diferentes variaciones de headers
    headers_variations = [
        # Headers básicos
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        },
        # Headers completos simulando navegador
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.infodolar.com/cotizacion-dolar-blue.aspx',
            'Origin': 'https://www.infodolar.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        },
        # Headers con token/session simulado
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.infodolar.com/cotizacion-dolar-blue.aspx',
            'X-Requested-With': 'XMLHttpRequest'
        }
    ]
    
    # Diferentes endpoints JSON posibles
    json_endpoints = [
        "",  # /json/ base
        "cotizaciones",
        "dolar-blue",
        "blue", 
        "precios",
        "data",
        "api",
        "cotizaciones.json",
        "dolar.json",
        "blue.json"
    ]
    
    # Métodos HTTP
    methods = ['GET', 'POST']
    
    print("🔍 Probando endpoint JSON de InfoDolar...")
    print("=" * 60)
    
    for endpoint in json_endpoints:
        url = base_url + endpoint if endpoint else base_url
        print(f"\n🌐 Probando: {url}")
        
        for i, headers in enumerate(headers_variations, 1):
            print(f"   📋 Headers set {i}:")
            
            for method in methods:
                try:
                    if method == 'GET':
                        response = requests.get(url, headers=headers, timeout=10)
                    else:
                        response = requests.post(url, headers=headers, timeout=10)
                    
                    status = response.status_code
                    size = len(response.content)
                    content_type = response.headers.get('Content-Type', 'unknown')
                    
                    print(f"      {method}: Status {status} | Size {size}B | Type: {content_type}")
                    
                    if status == 200:
                        print("      ✅ ÉXITO! Analizando contenido...")
                        
                        # Intentar parsear JSON
                        try:
                            data = response.json()
                            print(f"      🎉 JSON VÁLIDO ENCONTRADO!")
                            print(f"      📄 Estructura: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                            
                            # Guardar respuesta exitosa
                            with open(f'infodolar_json_success.json', 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            print(f"      💾 JSON guardado en 'infodolar_json_success.json'")
                            
                            return data  # Retornar si encontramos algo
                            
                        except json.JSONDecodeError:
                            print("      ⚠️  Respuesta no es JSON válido")
                            # Guardar contenido para análisis
                            with open(f'infodolar_response_200.txt', 'w', encoding='utf-8') as f:
                                f.write(f"URL: {url}\n")
                                f.write(f"Method: {method}\n") 
                                f.write(f"Headers: {headers}\n")
                                f.write("=" * 50 + "\n")
                                f.write(response.text)
                            print(f"      💾 Respuesta guardada para análisis")
                    
                    elif status == 403:
                        print("      🚫 Forbidden - Endpoint existe pero requiere autenticación")
                    
                    elif status == 404:
                        print("      ❌ No encontrado")
                    
                    elif status == 405:
                        print("      ⚠️  Método no permitido")
                    
                    else:
                        print(f"      ⚠️  Status inesperado: {status}")
                
                except requests.RequestException as e:
                    print(f"      ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("❌ No se pudo acceder al endpoint JSON")
    print("\n💡 CONCLUSIÓN:")
    print("   InfoDolar usa protecciones avanzadas contra scraping")
    print("   Recomiendo usar APIs alternativas que sí funcionan")

if __name__ == "__main__":
    test_json_endpoint() 