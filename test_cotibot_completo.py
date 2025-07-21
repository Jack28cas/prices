"""
SCRIPT DE PRUEBA COMPLETA - DÓLAR BLUE COTIBOT con Córdoba
Este script prueba el cálculo completo del COTIBOT con la nueva integración de Córdoba
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from usdtfiwind import (
    obtener_precio_fiwind,
    obtener_precio_blue_criptoya, 
    obtener_precio_bluelytics,
    obtener_precio_dolarapi,
    obtener_precio_infodolar,
    redondear_precio
)
import logging

# Configurar logging para la prueba
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def test_cotibot_completo():
    """
    Prueba completa del cálculo COTIBOT con Córdoba integrada
    """
    print("🔥 PRUEBA COMPLETA: DÓLAR BLUE COTIBOT CON CÓRDOBA")
    print("=" * 70)
    
    try:
        # === 📊 OBTENER DATOS DE TODAS LAS FUENTES ===
        print("\n📡 Obteniendo datos de todas las fuentes...")
        
        print("   🔍 USDT Fiwind...")
        usdt_compra, usdt_venta = obtener_precio_fiwind()
        
        print("   🔍 Blue Criptoya + CCB...")
        blue_criptoya_compra, blue_criptoya_venta, ccb_compra, ccb_venta = obtener_precio_blue_criptoya()
        
        print("   🔍 Bluelytics (Blue + Oficial)...")
        blue_bluelytics_compra, blue_bluelytics_venta, oficial_bluelytics_compra, oficial_bluelytics_venta = obtener_precio_bluelytics()
        
        print("   🔍 DolarAPI...")
        blue_dolarapi_compra, blue_dolarapi_venta = obtener_precio_dolarapi()
        
        print("   🔍 InfoDolar Córdoba + Blue General...")
        infodolar_cordoba_compra, infodolar_cordoba_venta, infodolar_blue_general_compra, infodolar_blue_general_venta = obtener_precio_infodolar()
        
        # === 📊 MOSTRAR DATOS OBTENIDOS ===
        print("\n" + "=" * 70)
        print("📊 DATOS OBTENIDOS:")
        print(f"   💰 USDT Fiwind:      ${usdt_compra} / ${usdt_venta}")
        print(f"   🔵 Blue Criptoya:    ${blue_criptoya_compra} / ${blue_criptoya_venta}")
        print(f"   💎 CCB Criptoya:     ${ccb_compra} / ${ccb_venta}")
        print(f"   📈 Blue Bluelytics:  ${blue_bluelytics_compra} / ${blue_bluelytics_venta}")
        print(f"   🏛️ Oficial Bluelytics: ${oficial_bluelytics_compra} / ${oficial_bluelytics_venta}")
        print(f"   📊 Blue DolarAPI:    ${blue_dolarapi_compra} / ${blue_dolarapi_venta}")
        print(f"   🗺️ InfoDolar Córdoba: ${infodolar_cordoba_compra} / ${infodolar_cordoba_venta}")
        print(f"   💙 InfoDolar Blue General: ${infodolar_blue_general_compra} / ${infodolar_blue_general_venta}")
        
        # Verificar datos esenciales
        if not all([usdt_compra, usdt_venta, blue_criptoya_compra, blue_criptoya_venta, 
                   ccb_compra, ccb_venta, blue_bluelytics_compra, blue_bluelytics_venta,
                   oficial_bluelytics_compra, oficial_bluelytics_venta, 
                   blue_dolarapi_compra, blue_dolarapi_venta]):
            print("❌ No se pudieron obtener todos los datos esenciales")
            return None, None
        
        # === 🧮 CÁLCULO PASO A PASO ===
        print("\n" + "=" * 70)
        print("🧮 CÁLCULO PASO A PASO DEL COTIBOT:")
        
        # Fuentes para BLUE + OFICIAL
        blue_sources_compra = [blue_bluelytics_compra, blue_criptoya_compra, blue_dolarapi_compra]
        blue_sources_venta = [blue_bluelytics_venta, blue_criptoya_venta, blue_dolarapi_venta]
        
        if infodolar_cordoba_compra and infodolar_cordoba_venta:
            blue_sources_compra.append(infodolar_cordoba_compra)
            blue_sources_venta.append(infodolar_cordoba_venta)
            print(f"   ✅ InfoDolar Córdoba INCLUIDA en BLUE+OFICIAL")
        else:
            print(f"   ⚠️ InfoDolar Córdoba NO disponible para BLUE+OFICIAL")
        
        if infodolar_blue_general_compra and infodolar_blue_general_venta:
            blue_sources_compra.append(infodolar_blue_general_compra)
            blue_sources_venta.append(infodolar_blue_general_venta)
            print(f"   ✅ InfoDolar Blue General INCLUIDA en BLUE+OFICIAL")
        else:
            print(f"   ⚠️ InfoDolar Blue General NO disponible para BLUE+OFICIAL")
        
        # Promedio BLUE + OFICIAL
        num_sources = len(blue_sources_compra)
        compra_blue = round(
            (sum(blue_sources_compra) + oficial_bluelytics_compra) / (num_sources + 1), 2
        )
        venta_blue = round(
            sum(blue_sources_venta) * 0.9 / num_sources + oficial_bluelytics_venta * 0.1, 2
        )
        
        print(f"   📊 BLUE + OFICIAL:")
        print(f"      Fuentes Blue: {blue_sources_compra}")
        print(f"      + Oficial: {oficial_bluelytics_compra} / {oficial_bluelytics_venta}")
        print(f"      = Promedio: ${compra_blue} / ${venta_blue}")
        
        # Fuentes para USDT + CCB + Blues + InfoDolar
        usdt_ccb_sources_compra = [usdt_compra, ccb_compra]
        usdt_ccb_sources_venta = [usdt_venta, ccb_venta]
        
        # Agregar los 3 blues principales
        usdt_ccb_sources_compra.extend([blue_bluelytics_compra, blue_criptoya_compra, blue_dolarapi_compra])
        usdt_ccb_sources_venta.extend([blue_bluelytics_venta, blue_criptoya_venta, blue_dolarapi_venta])
        print(f"   📊 Blues principales INCLUIDOS en USDT+CCB")
        
        if infodolar_cordoba_compra and infodolar_cordoba_venta:
            usdt_ccb_sources_compra.append(infodolar_cordoba_compra)
            usdt_ccb_sources_venta.append(infodolar_cordoba_venta)
            print(f"   ✅ InfoDolar Córdoba INCLUIDA en USDT+CCB")
        else:
            print(f"   ⚠️ InfoDolar Córdoba NO disponible para USDT+CCB")
        
        if infodolar_blue_general_compra and infodolar_blue_general_venta:
            usdt_ccb_sources_compra.append(infodolar_blue_general_compra)
            usdt_ccb_sources_venta.append(infodolar_blue_general_venta)
            print(f"   ✅ InfoDolar Blue General INCLUIDA en USDT+CCB")
        else:
            print(f"   ⚠️ InfoDolar Blue General NO disponible para USDT+CCB")
        
        compra_usdt_ccb = round(sum(usdt_ccb_sources_compra) / len(usdt_ccb_sources_compra), 2)
        venta_usdt_ccb = round(sum(usdt_ccb_sources_venta) / len(usdt_ccb_sources_venta), 2)
        
        print(f"   💎 USDT + CCB + Blues + InfoDolar:")
        print(f"      Fuentes: {usdt_ccb_sources_compra}")
        print(f"      = Promedio: ${compra_usdt_ccb} / ${venta_usdt_ccb}")
        
        # BLUE + USDT + CCB
        compra_blue_usdt_ccb = round((compra_blue + compra_usdt_ccb) / 2, 2)
        venta_blue_usdt_ccb = round((venta_blue + venta_usdt_ccb) / 2, 2)
        
        print(f"   🔗 BLUE + USDT + CCB:")
        print(f"      (${compra_blue} + ${compra_usdt_ccb}) / 2 = ${compra_blue_usdt_ccb}")
        print(f"      (${venta_blue} + ${venta_usdt_ccb}) / 2 = ${venta_blue_usdt_ccb}")
        
        # Promedio final COTIBOT
        compra_cotibot = round((compra_blue + compra_blue_usdt_ccb) / 2, 2)
        venta_cotibot = round((venta_blue + venta_blue_usdt_ccb) / 2, 2)
        
        print(f"   🎯 PROMEDIO FINAL COTIBOT:")
        print(f"      (${compra_blue} + ${compra_blue_usdt_ccb}) / 2 = ${compra_cotibot}")
        print(f"      (${venta_blue} + ${venta_blue_usdt_ccb}) / 2 = ${venta_cotibot}")
        
        # Aplicar redondeo personalizado
        compra_cotibot_redondeado = redondear_precio(compra_cotibot)
        venta_cotibot_redondeado = redondear_precio(venta_cotibot)
        
        print(f"   ✨ REDONDEO PERSONALIZADO:")
        print(f"      ${compra_cotibot} → ${compra_cotibot_redondeado}")
        print(f"      ${venta_cotibot} → ${venta_cotibot_redondeado}")
        
        # === 🎉 RESULTADO FINAL ===
        print("\n" + "=" * 70)
        print("🎉 RESULTADO FINAL - DÓLAR BLUE COTIBOT:")
        print(f"   💰 COMPRA: ${compra_cotibot_redondeado}")
        print(f"   💰 VENTA:  ${venta_cotibot_redondeado}")
        print(f"   📊 Fuentes Blue+Oficial: {num_sources} {'+ Córdoba ✅' if infodolar_cordoba_compra else ''} {'+ Blue General ✅' if infodolar_blue_general_compra else ''}")
        print(f"   📊 Fuentes USDT+CCB: {len(usdt_ccb_sources_compra)} (incluye Blues + InfoDolar {'Córdoba ✅' if infodolar_cordoba_compra else ''} {'Blue General ✅' if infodolar_blue_general_compra else ''})")
        
        # Comparación con bot actual
        print(f"\n📈 COMPARACIÓN CON BOT ACTUAL:")
        print(f"   Bot actual:    $1285 / $1305")
        print(f"   COTIBOT nuevo: ${compra_cotibot_redondeado} / ${venta_cotibot_redondeado}")
        print(f"   Diferencia:    +${compra_cotibot_redondeado - 1285:.0f} / +${venta_cotibot_redondeado - 1305:.0f}")
        
        return compra_cotibot_redondeado, venta_cotibot_redondeado
        
    except Exception as e:
        print(f"❌ Error en cálculo COTIBOT: {str(e)}")
        return None, None

def main():
    """
    Función principal de prueba
    """
    print("🧪 PRUEBA COMPLETA DEL COTIBOT CON CÓRDOBA")
    print("🔒 Esta prueba NO envía mensajes a Telegram")
    print()
    
    compra, venta = test_cotibot_completo()
    
    if compra and venta:
        print(f"\n🎊 ¡PRUEBA EXITOSA!")
        print(f"🔥 DÓLAR BLUE COTIBOT funcionando correctamente")
        print(f"🗺️ InfoDolar completo integrado en AMBAS partes del cálculo")
        print(f"💎 Resultado más preciso y actualizado")
        
    else:
        print(f"\n💔 PRUEBA FALLÓ")
        print(f"❌ No se pudo calcular el COTIBOT")
    
    print(f"\n🔒 CONFIRMACIÓN: Ningún mensaje enviado a Telegram")
    print(f"✅ Prueba completa terminada")

if __name__ == "__main__":
    main() 