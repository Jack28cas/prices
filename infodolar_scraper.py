import requests
from bs4 import BeautifulSoup
import re
import logging

def scrape_infodolar():
    """
    Hace web scraping directo de los precios de InfoDolar
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    try:
        print("🔍 Haciendo scraping de InfoDolar...")
        
        url = "https://www.infodolar.com/cotizacion-dolar-blue.aspx"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("✅ Página cargada correctamente")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar tabla de cotizaciones
            compra, venta = _extraer_precios_tabla(soup)
            
            if compra and venta:
                print(f"💰 InfoDolar - Compra: {compra}, Venta: {venta}")
                return float(compra), float(venta)
            else:
                print("❌ No se pudieron extraer los precios")
                return None, None
                
        else:
            print(f"❌ Error al cargar la página: Status {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error en scraping: {str(e)}")
        return None, None

def _extraer_precios_tabla(soup):
    """
    Extrae los precios de la tabla de cotizaciones
    """
    print("📊 Buscando tabla de cotizaciones...")
    
    # Estrategia 1: Buscar por texto "Dólar Blue"
    try:
        # Buscar elementos que contengan "Dólar Blue" o "Blue"
        blue_elements = soup.find_all(text=re.compile(r'(Dólar\s*Blue|Blue)', re.IGNORECASE))
        
        for element in blue_elements:
            print(f"🔍 Encontrado texto: {element.strip()}")
            
            # Buscar la fila padre
            parent = element.parent
            while parent and parent.name not in ['tr', 'div', 'table']:
                parent = parent.parent
                
            if parent:
                # Buscar números que parezcan precios (1000-2000 rango típico)
                precios = re.findall(r'\$?\s*([1-2]\d{3}(?:[,.]?\d{2})?)', str(parent))
                
                if len(precios) >= 2:
                    compra = precios[0].replace(',', '').replace('.', '')
                    venta = precios[1].replace(',', '').replace('.', '')
                    
                    # Convertir a float
                    try:
                        compra_float = float(compra) if len(compra) <= 4 else float(compra[:-2] + '.' + compra[-2:])
                        venta_float = float(venta) if len(venta) <= 4 else float(venta[:-2] + '.' + venta[-2:])
                        
                        print(f"✅ Precios extraídos: Compra: {compra_float}, Venta: {venta_float}")
                        return compra_float, venta_float
                        
                    except ValueError:
                        continue
    
    except Exception as e:
        print(f"❌ Error en estrategia 1: {str(e)}")
    
    # Estrategia 2: Buscar tabla con estructura típica
    try:
        print("🔍 Buscando tabla estructurada...")
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                # Buscar fila que contenga "blue"
                row_text = ' '.join([cell.get_text() for cell in cells]).lower()
                
                if 'blue' in row_text:
                    print(f"🎯 Fila con 'blue': {row_text}")
                    
                    # Extraer números
                    numeros = re.findall(r'([1-2]\d{3}(?:[,.]?\d{2})?)', row_text)
                    
                    if len(numeros) >= 2:
                        try:
                            compra = float(numeros[0].replace(',', ''))
                            venta = float(numeros[1].replace(',', ''))
                            
                            print(f"✅ Precios de tabla: Compra: {compra}, Venta: {venta}")
                            return compra, venta
                            
                        except ValueError:
                            continue
    
    except Exception as e:
        print(f"❌ Error en estrategia 2: {str(e)}")
    
    # Estrategia 3: Buscar cualquier precio en el rango típico
    try:
        print("🔍 Buscando precios en todo el HTML...")
        
        # Buscar todos los números que parezcan precios
        all_text = soup.get_text()
        precios = re.findall(r'\$?\s*([1-2]\d{3}(?:[,.]?\d{2})?)', all_text)
        
        # Filtrar precios únicos en rango típico del dólar
        precios_validos = []
        for precio in precios:
            try:
                precio_num = float(precio.replace(',', ''))
                if 1200 <= precio_num <= 1500:  # Rango típico del dólar blue
                    precios_validos.append(precio_num)
            except ValueError:
                continue
        
        # Eliminar duplicados y ordenar
        precios_unicos = sorted(list(set(precios_validos)))
        
        if len(precios_unicos) >= 2:
            compra = min(precios_unicos)  # Precio más bajo = compra
            venta = max(precios_unicos)   # Precio más alto = venta
            
            print(f"✅ Precios inferidos: Compra: {compra}, Venta: {venta}")
            return compra, venta
    
    except Exception as e:
        print(f"❌ Error en estrategia 3: {str(e)}")
    
    print("❌ No se pudieron extraer precios con ninguna estrategia")
    return None, None

def test_scraper():
    """
    Prueba el scraper
    """
    compra, venta = scrape_infodolar()
    
    if compra and venta:
        print(f"\n🎉 ÉXITO!")
        print(f"InfoDolar - Compra: ${compra} | Venta: ${venta}")
        print(f"Promedio: ${(compra + venta) / 2:.2f}")
    else:
        print(f"\n❌ No se pudieron obtener los precios de InfoDolar")

if __name__ == "__main__":
    test_scraper() 