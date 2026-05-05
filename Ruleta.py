import random 
import matplotlib.pyplot as plt # Para graficar resultados
import numpy as np #promedio y varianza

# 1. Configurar parámetros (puedes usar input o sys.argv)
# n = tiradas, c = corridas, e = número elegido
def simular_ruleta(n, c, numero_elegido):
    plt.figure(figsize=(12, 8))
    
    for i in range(c):
        resultados = []
        frecuencias_relativas = []
        promedios = []
        
        exitos = 0
        for t in range(1, n + 1):
            tirada = random.randint(0, 36) # Ruleta Europea [cite: 22, 29]
            resultados.append(tirada)
            
            if tirada == numero_elegido:
                exitos += 1
            
            # Cálculos acumulados [cite: 30, 31, 32]
            frecuencias_relativas.append(exitos / t)
            promedios.append(np.mean(resultados))
        
        # Graficar frecuencia relativa de cada corrida [cite: 56]
        plt.plot(range(1, n + 1), frecuencias_relativas)
    
    # Línea de valor esperado teórico (1/37) [cite: 23, 36]
    plt.axhline(y=1/37, color='r', linestyle='--', label='Esperado (1/37)')
    plt.title(f"Frecuencia Relativa del número {numero_elegido}")
    plt.xlabel("Número de tiradas (n)")
    plt.ylabel("fr")
    plt.legend()
    plt.show()