import requests
from bs4 import BeautifulSoup
import re
import logging

def scrape_infodolar_table():
    """
    Hace scraping específico de la tabla de cotizaciones por provincia de InfoDolar
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    try:
        print("🔍 Haciendo scraping de tabla InfoDolar...")
        
        url = "https://www.infodolar.com/cotizacion-dolar-blue.aspx"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("✅ Página cargada correctamente")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Guardar HTML para debug
            with open('infodolar_debug.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("💾 HTML guardado en 'infodolar_debug.html' para análisis")
            
            # Estrategias de extracción
            resultados = []
            
            # Estrategia 1: Buscar tabla con precios típicos
            resultados.extend(_buscar_tabla_precios(soup))
            
            # Estrategia 2: Buscar por texto de provincias
            resultados.extend(_buscar_por_provincias(soup))
            
            # Estrategia 3: Buscar patrones de precios específicos
            resultados.extend(_buscar_patrones_precio(soup))
            
            if resultados:
                # Tomar el promedio de Capital Federal si está disponible
                capital_federal = next((r for r in resultados if 'capital' in r['provincia'].lower()), None)
                
                if capital_federal:
                    print(f"🎯 Usando datos de Capital Federal:")
                    print(f"   Compra: ${capital_federal['compra']}")
                    print(f"   Venta: ${capital_federal['venta']}")
                    return capital_federal['compra'], capital_federal['venta']
                
                # Si no hay Capital Federal, usar el primero
                primer_resultado = resultados[0]
                print(f"🎯 Usando datos de {primer_resultado['provincia']}:")
                print(f"   Compra: ${primer_resultado['compra']}")
                print(f"   Venta: ${primer_resultado['venta']}")
                return primer_resultado['compra'], primer_resultado['venta']
            
            else:
                print("❌ No se pudieron extraer precios")
                return None, None
                
        else:
            print(f"❌ Error al cargar la página: Status {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error en scraping: {str(e)}")
        return None, None

def _buscar_tabla_precios(soup):
    """
    Busca tabla con estructura de precios
    """
    print("📊 Estrategia 1: Buscando tabla con precios...")
    
    resultados = []
    
    try:
        # Buscar todas las tablas
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 3:  # Al menos 3 columnas (provincia, compra, venta)
                    texts = [cell.get_text().strip() for cell in cells]
                    
                    # Buscar patrones de precio ($1,XXX.XX)
                    precios = []
                    provincia = ""
                    
                    for i, text in enumerate(texts):
                        # Buscar nombres de provincias
                        if any(prov in text.lower() for prov in ['buenos aires', 'capital', 'córdoba', 'santa fe', 'mendoza']):
                            provincia = text
                        
                        # Buscar precios
                        precio_match = re.search(r'\$\s*([1-2]\d{3}(?:[,.]?\d{2})?)', text)
                        if precio_match:
                            precio_str = precio_match.group(1).replace(',', '')
                            try:
                                precio = float(precio_str)
                                if 1200 <= precio <= 1400:  # Rango válido
                                    precios.append(precio)
                            except ValueError:
                                continue
                    
                    # Si encontramos provincia y al menos 2 precios
                    if provincia and len(precios) >= 2:
                        compra = min(precios)  # Precio más bajo = compra
                        venta = max(precios)   # Precio más alto = venta
                        
                        resultado = {
                            'provincia': provincia,
                            'compra': compra,
                            'venta': venta
                        }
                        
                        resultados.append(resultado)
                        print(f"   ✅ {provincia}: Compra ${compra}, Venta ${venta}")
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    return resultados

def _buscar_por_provincias(soup):
    """
    Busca por nombres de provincias específicas
    """
    print("🗺️  Estrategia 2: Buscando por provincias...")
    
    resultados = []
    
    provincias = [
        'Buenos Aires', 'Capital Federal', 'Córdoba', 'Santa Fe', 
        'Mendoza', 'Chaco', 'Corrientes', 'Entre Ríos'
    ]
    
    try:
        for provincia in provincias:
            # Buscar elementos que contengan el nombre de la provincia
            elementos = soup.find_all(string=re.compile(provincia, re.IGNORECASE))
            
            for elemento in elementos:
                # Buscar el elemento padre que contenga los precios
                parent = elemento.parent
                
                # Expandir búsqueda a elementos hermanos
                for _ in range(3):  # Buscar en 3 niveles
                    if parent and parent.parent:
                        parent = parent.parent
                        
                        # Buscar precios en este nivel
                        parent_text = str(parent)
                        precios = re.findall(r'\$\s*([1-2]\d{3}(?:[,.]?\d{2})?)', parent_text)
                        
                        if len(precios) >= 2:
                            try:
                                precios_num = [float(p.replace(',', '')) for p in precios]
                                precios_validos = [p for p in precios_num if 1200 <= p <= 1400]
                                
                                if len(precios_validos) >= 2:
                                    compra = min(precios_validos)
                                    venta = max(precios_validos)
                                    
                                    resultado = {
                                        'provincia': provincia,
                                        'compra': compra,
                                        'venta': venta
                                    }
                                    
                                    resultados.append(resultado)
                                    print(f"   ✅ {provincia}: Compra ${compra}, Venta ${venta}")
                                    break
                                    
                            except ValueError:
                                continue
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    return resultados

def _buscar_patrones_precio(soup):
    """
    Busca patrones específicos de precios
    """
    print("🔍 Estrategia 3: Buscando patrones de precio...")
    
    resultados = []
    
    try:
        # Obtener todo el texto
        all_text = soup.get_text()
        
        # Buscar todos los precios en formato $1,XXX.XX
        precios_matches = re.findall(r'\$\s*([1-2]\d{3}(?:[,.]?\d{2})?)', all_text)
        
        precios_validos = []
        for precio_str in precios_matches:
            try:
                precio = float(precio_str.replace(',', ''))
                if 1200 <= precio <= 1400:
                    precios_validos.append(precio)
            except ValueError:
                continue
        
        # Eliminar duplicados y ordenar
        precios_unicos = sorted(list(set(precios_validos)))
        
        print(f"   🔍 Precios encontrados: {precios_unicos}")
        
        if len(precios_unicos) >= 2:
            # Agrupar precios similares (diferencia < 5)
            grupos = []
            for precio in precios_unicos:
                agregado = False
                for grupo in grupos:
                    if abs(precio - grupo[0]) <= 5:
                        grupo.append(precio)
                        agregado = True
                        break
                if not agregado:
                    grupos.append([precio])
            
            # Si hay al menos 2 grupos, usar el más bajo como compra y el más alto como venta
            if len(grupos) >= 2:
                compra = min(grupos[0])
                venta = max(grupos[-1])
                
                resultado = {
                    'provincia': 'General',
                    'compra': compra,
                    'venta': venta
                }
                
                resultados.append(resultado)
                print(f"   ✅ General: Compra ${compra}, Venta ${venta}")
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    return resultados

def test_table_scraper():
    """
    Prueba el scraper de tabla
    """
    compra, venta = scrape_infodolar_table()
    
    if compra and venta:
        print(f"\n🎉 ÉXITO!")
        print(f"InfoDolar - Compra: ${compra} | Venta: ${venta}")
        print(f"Promedio: ${(compra + venta) / 2:.2f}")
        
        # Comparar con APIs conocidas
        print(f"\n📊 COMPARACIÓN:")
        print(f"InfoDolar:    ${compra} / ${venta} (promedio: ${(compra + venta) / 2:.2f})")
        print(f"Tu bot actual: $1285 / $1305 (promedio: $1295)")
        print(f"Diferencia:   +${compra - 1285:.0f} / +${venta - 1305:.0f}")
        
    else:
        print(f"\n❌ No se pudieron obtener los precios de InfoDolar")
        print(f"💡 Revisa el archivo 'infodolar_debug.html' para ver la estructura")

if __name__ == "__main__":
    test_table_scraper() 