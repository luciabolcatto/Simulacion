import random
import matplotlib.pyplot as plt
import numpy as np
import sys

# --- FUNCIÓN PRINCIPAL ---
def simular(n_tiradas, n_corridas, elegido):
    # Valores teóricos para las líneas de referencia
    fr_esperada = 1/37
    vp_esperado = 18

    plt.figure(figsize=(10, 6))

    for i in range(n_corridas):
        resultados = []
        frecuencias = []
        exitos = 0

        for t in range(1, n_tiradas + 1):
            # 1. Simulamos el giro de la ruleta 
            tiro = random.randint(0, 36)
            resultados.append(tiro)
            
            # 2. Contamos si es el número que elegimos 
            if tiro == elegido:
                exitos += 1
            
            # 3. Guardamos la frecuencia relativa de este momento 
            frecuencias.append(exitos / t)

        # Graficamos la línea de esta corrida específica
        plt.plot(range(1, n_tiradas + 1), frecuencias, alpha=0.6)

    # Agregamos la línea roja teórica para comparar [cite: 131, 186]
    plt.axhline(y=fr_esperada, color='red', linestyle='--', label=f'Teórico: {fr_esperada:.3f}')
    
    plt.title(f"Simulación: {n_corridas} corridas de {n_tiradas} tiradas (Número: {elegido})")
    plt.xlabel("Número de tiradas (n)")
    plt.ylabel("Frecuencia Relativa (fr)")
    plt.legend()
    plt.grid(True)

    # ---  GUARDAR LAS GRÁFICAS ---
    # crea un archivo .png automáticamente 
    nombre_archivo = f"grafico_n{n_tiradas}_c{n_corridas}.png"
    plt.savefig(nombre_archivo)
    print(f"¡Listo! Gráfico guardado como: {nombre_archivo}")
    
    plt.show()

# --- BLOQUE PARA LEER PARÁMETROS DE CONSOLA ---
# ej: python Ruleta.py -n 1000 -c 5 -e 7 
if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Uso correcto: python Ruleta.py -n [tiradas] -c [corridas] -e [elegido]")
    else:
        # Extraemos los valores de la lista sys.argv
        # sys.argv[2] es el valor después de -n, y así sucesivamente
        tiradas = int(sys.argv[sys.argv.index('-n') + 1])
        corridas = int(sys.argv[sys.argv.index('-c') + 1])
        elegido = int(sys.argv[sys.argv.index('-e') + 1])
        
        simular(tiradas, corridas, elegido)