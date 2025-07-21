import sys
sys.path.append('.')

# Importar la función actualizada
from usdtfiwind import obtener_precio_infodolar

print("🚀 PROBANDO NUEVA CONFIGURACIÓN INFODOLAR")
print("=" * 50)

try:
    cordoba_compra, cordoba_venta, blue_general_compra, blue_general_venta = obtener_precio_infodolar()
    
    print("📊 RESULTADOS:")
    print(f"🗺️ Córdoba: ${cordoba_compra} / ${cordoba_venta}")
    print(f"💙 Blue General: ${blue_general_compra} / ${blue_general_venta}")
    
    if cordoba_compra and cordoba_venta:
        print("✅ ¡InfoDolar Córdoba FUNCIONANDO!")
    
    if blue_general_compra and blue_general_venta:
        print("✅ ¡InfoDolar Blue General FUNCIONANDO!")
        
    if (cordoba_compra and cordoba_venta) or (blue_general_compra and blue_general_venta):
        print("🎉 ¡InfoDolar está funcionando en el servidor!")
    else:
        print("❌ InfoDolar aún no funciona")

except Exception as e:
    print(f"❌ Error: {str(e)}")
