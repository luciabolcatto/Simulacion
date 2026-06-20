import random
import numpy as np
import matplotlib.pyplot as plt

def simular_inventario(S, s, costo_orden_fijo, costo_mantenimiento_unidad, costo_faltante_unidad, dias_simulacion):
    stock_actual = S
    pedido_en_camino = False
    tiempo_llegada_pedido = 0
    
    costo_total_orden = 0.0
    costo_total_mantenimiento = 0.0
    costo_total_faltante = 0.0

    # Historial diario para graficar una corrida típica en el informe
    historial_stock = []

    for dia in range(1, dias_simulacion + 1):
        # 1. Verificar si llega el pedido programado del proveedor
        if pedido_en_camino and dia == tiempo_llegada_pedido:
            stock_actual = S  # Rellenamos el stock al máximo S
            pedido_en_camino = False
        
        # 2. Generar demanda diaria estocástica (Entre 0 y 15 unidades)
        demanda = random.randint(0, 15)
        
        # 3. Satisfacer la demanda
        stock_actual -= demanda
        historial_stock.append(stock_actual)
        
        # 4. Calcular costos del día según el estado del stock
        if stock_actual >= 0:
            costo_total_mantenimiento += stock_actual * costo_mantenimiento_unidad
        else:
            costo_total_faltante += abs(stock_actual) * costo_faltante_unidad
            
        # 5. Revisión de política (s, S) al cierre del día
        if stock_actual < s and not pedido_en_camino:
            costo_total_orden += costo_orden_fijo
            pedido_en_camino = True
            # El proveedor demora entre 1 y 3 días en entregar (Lead Time)
            tiempo_llegada_pedido = dia + random.randint(1, 3)

    return costo_total_orden, costo_total_mantenimiento, costo_total_faltante, historial_stock

if __name__ == "__main__":
    # Parámetros base justificados para la UTN
    INV_MAX = 100           # S
    PUNTO_REPOSICION = 20   # s
    C_ORDEN = 50.0          # Costo fijo por pedido
    C_MANT = 1.0            # Costo por unidad retenida al día
    C_FALT = 10.0           # Penalización por unidad faltante al día
    DIAS = 365              # 1 año de operación
    CORRIDAS = 10           # Mínimo exigido por el enunciado
    
    print("=" * 70)
    print(" INICIANDO EXPERIMENTOS DE INVENTARIO - POLÍTICA (s, S)")
    print("=" * 70)
    
    ordenes, mantenimientos, faltantes, totales = [], [], [], []
    ultimo_historial = []
    
    for i in range(CORRIDAS):
        co, cm, cf, hist = simular_inventario(INV_MAX, PUNTO_REPOSICION, C_ORDEN, C_MANT, C_FALT, DIAS)
        ct = co + cm + cf
        
        ordenes.append(co)
        mantenimientos.append(cm)
        faltantes.append(cf)
        totales.append(ct)
        ultimo_historial = hist  # Guardamos el perfil de la última corrida para graficar
        
    print(f"Resultados medios de {CORRIDAS} corridas independientes:")
    print(f"  - Costo Promedio de Orden:        ${np.mean(ordenes):.2f}")
    print(f"  - Costo Promedio de Mantenimiento: ${np.mean(mantenimientos):.2f}")
    print(f"  - Costo Promedio de Faltante:     ${np.mean(faltantes):.2f}")
    print(f"  - COSTO TOTAL LOGÍSTICO MEDIO:    ${np.mean(totales):.2f}")
    print("=" * 70)
    
    # --- GENERAR Y GUARDAR EL GRÁFICO DEL COMPORTAMIENTO DEL STOCK ---
    print("\n[INFO] Guardando y abriendo el gráfico de evolución de inventario...")
    plt.figure(figsize=(10, 4))
    plt.plot(range(1, DIAS + 1), ultimo_historial, color='teal', label='Nivel de Stock Diario')
    plt.axhline(y=INV_MAX, color='g', linestyle='--', label='Inventario Máximo (S = 100)')
    plt.axhline(y=PUNTO_REPOSICION, color='r', linestyle='--', label='Punto de Reposición (s = 20)')
    plt.axhline(y=0, color='black', linewidth=0.8, linestyle='-')
    plt.title('Perfil de Evolución Dinámica del Inventario - Política (s, S)')
    plt.xlabel('Tiempo (Días)')
    plt.ylabel('Unidades Disponibles')
    plt.grid(True, alpha=0.5)
    plt.legend(loc='upper right')
    plt.tight_layout()
    
    # Guarda la imagen automáticamente en tu carpeta
    plt.savefig('grafico_inventario.png', dpi=300)
    plt.show()
    print("[OK] Imagen guardada con éxito como 'grafico_inventario.png'.")