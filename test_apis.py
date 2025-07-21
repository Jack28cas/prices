import requests
import json
from datetime import datetime

def probar_apis_dolar():
    """
    Prueba diferentes APIs de cotización del dólar blue para comparar precios
    """
    
    apis = {
        "DolarAPI.com": "https://dolarapi.com/v1/dolares/blue",
        "API Dolar Argentina": "https://api-dolar-argentina.herokuapp.com/api/dolarblue", 
        "Criptoya": "https://criptoya.com/api/dolar",
        "Bluelytics": "https://api.bluelytics.com.ar/v2/latest"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"🔍 Probando APIs de cotización del dólar blue...")
    print(f"⏰ Hora actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    resultados = {}
    
    for nombre, url in apis.items():
        try:
            print(f"🌐 Probando {nombre}...")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraer precios según la estructura de cada API
                if nombre == "DolarAPI.com":
                    compra = data.get("compra", 0)
                    venta = data.get("venta", 0)
                    fecha = data.get("fechaActualizacion", "")
                    
                elif nombre == "API Dolar Argentina":
                    compra = float(data.get("compra", "0").replace(",", "."))
                    venta = float(data.get("venta", "0").replace(",", "."))
                    fecha = data.get("fecha", "")
                    
                elif nombre == "Criptoya":
                    blue_data = data.get("blue", {})
                    compra = blue_data.get("bid", 0)
                    venta = blue_data.get("ask", 0)
                    fecha = "Tiempo real"
                    
                elif nombre == "Bluelytics":
                    blue_data = data.get("blue", {})
                    compra = blue_data.get("value_buy", 0)
                    venta = blue_data.get("value_sell", 0)
                    fecha = data.get("last_update", "")
                
                resultados[nombre] = {
                    "compra": compra,
                    "venta": venta,
                    "fecha": fecha,
                    "promedio": (compra + venta) / 2
                }
                
                print(f"   ✅ Compra: ${compra} | Venta: ${venta} | Promedio: ${(compra + venta) / 2:.2f}")
                print(f"   📅 Fecha: {fecha}")
                
            else:
                print(f"   ❌ Error: Status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
    
    # Mostrar resumen
    if resultados:
        print("📊 RESUMEN DE PRECIOS:")
        print("-" * 60)
        
        # Ordenar por precio promedio
        ordenados = sorted(resultados.items(), key=lambda x: x[1]['promedio'], reverse=True)
        
        for nombre, datos in ordenados:
            print(f"{nombre:20} | Compra: ${datos['compra']:7.2f} | Venta: ${datos['venta']:7.2f} | Promedio: ${datos['promedio']:7.2f}")
        
        # Calcular promedio general
        precios_compra = [datos['compra'] for datos in resultados.values()]
        precios_venta = [datos['venta'] for datos in resultados.values()]
        
        promedio_compra = sum(precios_compra) / len(precios_compra)
        promedio_venta = sum(precios_venta) / len(precios_venta)
        
        print("-" * 60)
        print(f"{'PROMEDIO GENERAL':20} | Compra: ${promedio_compra:7.2f} | Venta: ${promedio_venta:7.2f} | Promedio: ${(promedio_compra + promedio_venta) / 2:7.2f}")
        
        # Mostrar diferencias
        print("\n🔍 ANÁLISIS:")
        max_compra = max(precios_compra)
        min_compra = min(precios_compra)
        diferencia_compra = max_compra - min_compra
        
        print(f"Diferencia máxima en compra: ${diferencia_compra:.2f} ({((diferencia_compra/min_compra)*100):.1f}%)")
        
        # Recomendar fuentes más actualizadas
        print(f"\n💡 RECOMENDACIÓN:")
        print(f"Las fuentes con precios más altos (más actualizados) son:")
        for i, (nombre, datos) in enumerate(ordenados[:2]):
            print(f"{i+1}. {nombre}: ${datos['promedio']:.2f}")

if __name__ == "__main__":
    probar_apis_dolar() 