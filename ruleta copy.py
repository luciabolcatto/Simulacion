import random
import argparse
import math
import matplotlib.pyplot as plt

def main():
    # 1. Ingreso por consola de parámetros
    parser = argparse.ArgumentParser(description='Simulación de una Ruleta (TP 1.1)')
    parser.add_argument('-c', '--corridas', type=int, required=True, help='Cantidad de corridas')
    parser.add_argument('-n', '--tiradas', type=int, required=True, help='Cantidad de tiradas por corrida')
    parser.add_argument('-e', '--elegido', type=int, required=True, help='Número elegido para la apuesta (0-36)')
    
    #Correrlo:
    # python ruleta copy.py -c (corridas) -n (tiradas) -e (numero elegido)
    #"Ejemplo:
    # python ruleta copy.py -c 5 -n 1000 -e 17"

    args = parser.parse_args()
    c = args.corridas
    n = args.tiradas
    elegido = args.elegido

    if not (0 <= elegido <= 36):
        print("Error: La ruleta europea solo tiene números del 0 al 36.")
        return

    # 2. Cálculos Teóricos (Valores Esperados)
    # Frecuencia relativa: 1 sobre los 37 números posibles
    esp_fr = 1.0 / 37.0 
    
    # Promedio esperado: suma de todos los números (0+1+2...+36) / 37 = 18
    esp_vp = 18.0       
    
    # Varianza esperada: (n^2 - 1) / 12 -> (37^2 - 1)/12 = 114
    esp_vv = 114.0      
    
    # Desvío esperado: raíz cuadrada de la varianza
    esp_vd = math.sqrt(esp_vv) 

    # Estructuras (listas) para almacenar los resultados de TODAS las corridas
    historico_fr =[]
    historico_vp = []
    historico_vd = []
    historico_vv =[]

    print(f"Iniciando simulación: {c} corridas de {n} tiradas (Número elegido: {elegido})...")

    # 3. Ciclo FOR principal (corridas)
    for corrida in range(c):
        # Listas para almacenar el avance paso a paso de la corrida actual
        fr_corrida =[]
        vp_corrida = []
        vd_corrida = []
        vv_corrida =[]

        # Variables acumuladoras
        count_elegido = 0
        suma_valores = 0
        suma_cuadrados = 0

        # Ciclo FOR interno (tiradas)
        for i in range(1, n + 1):
            # Generación del valor aleatorio (0 al 36 inclusive)
            tirada = random.randint(0, 36)

            # Actualizamos la suma y los contadores
            if tirada == elegido:
                count_elegido += 1
            
            suma_valores += tirada
            suma_cuadrados += (tirada ** 2)

            # 4. Empleo de funciones estadísticas (fórmulas paso a paso)
            fr = count_elegido / i
            vp = suma_valores / i
            
            # Cálculo de la Varianza (Media de los cuadrados menos el cuadrado de la media)
            vv = (suma_cuadrados / i) - (vp ** 2)
            
            # Cálculo del desvío estándar
            vd = math.sqrt(vv) if vv > 0 else 0.0

            # Guardamos los resultados iterando las listas
            fr_corrida.append(fr)
            vp_corrida.append(vp)
            vv_corrida.append(vv)
            vd_corrida.append(vd)

        # Agregamos la corrida actual al registro histórico
        historico_fr.append(fr_corrida)
        historico_vp.append(vp_corrida)
        historico_vv.append(vv_corrida)
        historico_vd.append(vd_corrida)

    print("Simulación terminada. Generando gráficos...")

    # 5. Exposición de los resultados mediante el paquete Matplotlib
    tiradas_eje_x = list(range(1, n + 1))

    # --- FIGURA 1: Análisis de UNA SOLA corrida (4 gráficas) ---
    # Sirve para analizar la convergencia de una tira en particular, como en el boceto del PDF.
    fig1, axs1 = plt.subplots(2, 2, figsize=(12, 8))
    fig1.canvas.manager.set_window_title('Análisis de una sola corrida')
    fig1.suptitle(f'Primera corrida - {n} tiradas (Número {elegido})', fontsize=14, fontweight='bold')

    axs1[0, 0].plot(tiradas_eje_x, historico_fr[0], color='blue')
    axs1[0, 0].axhline(esp_fr, color='red', linestyle='--', label=f'Esperada ({esp_fr:.4f})')
    axs1[0, 0].set_title('fr (Frecuencia Relativa)')
    axs1[0, 0].set_xlabel('n (Tiradas)')
    axs1[0, 0].legend()

    axs1[0, 1].plot(tiradas_eje_x, historico_vp[0], color='green')
    axs1[0, 1].axhline(esp_vp, color='red', linestyle='--', label=f'Esperado ({esp_vp})')
    axs1[0, 1].set_title('vp (Valor Promedio)')
    axs1[0, 1].set_xlabel('n (Tiradas)')
    axs1[0, 1].legend()

    axs1[1, 0].plot(tiradas_eje_x, historico_vd[0], color='purple')
    axs1[1, 0].axhline(esp_vd, color='red', linestyle='--', label=f'Esperado ({esp_vd:.2f})')
    axs1[1, 0].set_title('vd (Desvío Estándar)')
    axs1[1, 0].set_xlabel('n (Tiradas)')
    axs1[1, 0].legend()

    axs1[1, 1].plot(tiradas_eje_x, historico_vv[0], color='orange')
    axs1[1, 1].axhline(esp_vv, color='red', linestyle='--', label=f'Esperado ({esp_vv})')
    axs1[1, 1].set_title('vv (Varianza)')
    axs1[1, 1].set_xlabel('n (Tiradas)')
    axs1[1, 1].legend()

    plt.tight_layout()

    # --- FIGURA 2: Análisis de TODAS las corridas superpuestas (4 gráficas) ---
    # Este es el extra que te piden para sumar 8 gráficas totales y justificar teóricamente.
    fig2, axs2 = plt.subplots(2, 2, figsize=(12, 8))
    fig2.canvas.manager.set_window_title('Análisis Múltiples Corridas')
    fig2.suptitle(f'Múltiples corridas ({c} en total) - {n} tiradas (Número {elegido})', fontsize=14, fontweight='bold')

    for i in range(c):
        axs2[0, 0].plot(tiradas_eje_x, historico_fr[i], alpha=0.6)
        axs2[0, 1].plot(tiradas_eje_x, historico_vp[i], alpha=0.6)
        axs2[1, 0].plot(tiradas_eje_x, historico_vd[i], alpha=0.6)
        axs2[1, 1].plot(tiradas_eje_x, historico_vv[i], alpha=0.6)

    # Líneas esperadas (Teóricas) por encima de las múltiples líneas de las corridas
    axs2[0, 0].axhline(esp_fr, color='black', linestyle='--', linewidth=2, label='Esperada')
    axs2[0, 0].set_title('Frecuencias Relativas')
    axs2[0, 0].set_xlabel('n (Tiradas)')
    axs2[0, 0].legend()

    axs2[0, 1].axhline(esp_vp, color='black', linestyle='--', linewidth=2, label='Esperado')
    axs2[0, 1].set_title('Valores Promedio')
    axs2[0, 1].set_xlabel('n (Tiradas)')
    axs2[0, 1].legend()

    axs2[1, 0].axhline(esp_vd, color='black', linestyle='--', linewidth=2, label='Esperado')
    axs2[1, 0].set_title('Desvíos Estándar')
    axs2[1, 0].set_xlabel('n (Tiradas)')
    axs2[1, 0].legend()

    axs2[1, 1].axhline(esp_vv, color='black', linestyle='--', linewidth=2, label='Esperado')
    axs2[1, 1].set_title('Varianzas')
    axs2[1, 1].set_xlabel('n (Tiradas)')
    axs2[1, 1].legend()

    plt.tight_layout()
    
    # Mostramos todo en pantalla
    plt.show()

if __name__ == '__main__':
    main()  