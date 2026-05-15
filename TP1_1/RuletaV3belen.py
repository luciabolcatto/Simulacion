import random
import sys
import statistics
import matplotlib.pyplot as plt

# ingresar por consola
if len(sys.argv) != 7 or sys.argv[1] != "-c" or sys.argv[3] != "-n" or sys.argv[5] != "-e":
    print("Uso: python ruleta.py -c <corridas> -n <tiradas> -e <numero_elegido>")
    sys.exit(1)

try:
    corridas = int(sys.argv[2])
    tiradas = int(sys.argv[4])
    numero_elegido = int(sys.argv[6])
except ValueError:
    print("Error: argumentos inválidos.")
    sys.exit(1)

if not (0 <= numero_elegido <= 37):
    print("El número elegido debe estar entre 0 y 37.")
    sys.exit(1)

frecuencia_esperada = 1 / 38
promedio_esperado = tiradas * frecuencia_esperada
desvio_esperado = (tiradas * frecuencia_esperada * (1 - frecuencia_esperada))**0.5
varianza_esperada = desvio_esperado**2

# sim
simulaciones = 10
resultados_todas = []
frecuencias_promedio = []

for _ in range(simulaciones):
    resultados_sim = []
    frecuencias_sim = []
    for _ in range(corridas):
        tiradas_corrida = [random.randint(0, 37) for _ in range(tiradas)]
        ocurrencias = tiradas_corrida.count(numero_elegido)
        resultados_sim.append(ocurrencias)
        frecuencias_sim.append(ocurrencias / tiradas)
    resultados_todas.append(resultados_sim)
    frecuencias_promedio.append(statistics.mean(frecuencias_sim))

# ultima sim
ultimos_resultados = resultados_todas[-1]
frecuencia_relativa = [r / tiradas for r in ultimos_resultados]
promedios = [statistics.mean(ultimos_resultados[:i+1]) for i in range(corridas)]
desvios = [statistics.stdev(ultimos_resultados[:i+1]) if i > 0 else 0 for i in range(corridas)]
varianzas = [statistics.variance(ultimos_resultados[:i+1]) if i > 0 else 0 for i in range(corridas)]


print(f"\nNúmero elegido: {numero_elegido}")
print(f"Corridas: {corridas}, Tiradas por corrida: {tiradas}")
print(f"Promedio final de ocurrencias: {promedios[-1]:.2f}")
print(f"Desvío estándar final: {desvios[-1]:.2f}")

# graficos
fig, axs = plt.subplots(4, 2, figsize=(14, 12))

# frec rel
axs[0, 0].plot(frecuencia_relativa, color='orange', label='frn')
axs[0, 0].axhline(frecuencia_esperada, color='blue', linestyle='--', label='fre')
axs[0, 0].set_title('Frecuencia Relativa (última simulación)')
axs[0, 0].set_xlabel('Corrida')
axs[0, 0].set_ylabel('fr')
axs[0, 0].legend()

# promedio
axs[0, 1].plot(promedios, color='orange', label='vpn')
axs[0, 1].axhline(promedio_esperado, color='blue', linestyle='--', label='vpe')
axs[0, 1].set_title('Promedio de ocurrencias')
axs[0, 1].set_xlabel('Corrida')
axs[0, 1].set_ylabel('vp')
axs[0, 1].legend()

# desv estandar
axs[1, 0].plot(desvios, color='orange', label='vd')
axs[1, 0].axhline(desvio_esperado, color='blue', linestyle='--', label='vde')
axs[1, 0].set_title('Desvío estándar')
axs[1, 0].set_xlabel('Corrida')
axs[1, 0].set_ylabel('vd')
axs[1, 0].legend()

# varianza
axs[1, 1].plot(varianzas, color='orange', label='vvn')
axs[1, 1].axhline(varianza_esperada, color='blue', linestyle='--', label='vve')
axs[1, 1].set_title('Varianza')
axs[1, 1].set_xlabel('Corrida')
axs[1, 1].set_ylabel('vv')
axs[1, 1].legend()

# histograma ocurrencias
axs[2, 0].hist(ultimos_resultados, bins=range(min(ultimos_resultados), max(ultimos_resultados)+2), color='skyblue', edgecolor='black')
axs[2, 0].set_title('Histograma de ocurrencias (última simulación)')
axs[2, 0].set_xlabel('Veces que salió el número')
axs[2, 0].set_ylabel('Frecuencia')

# ecolucion de simu
for sim in resultados_todas:
    axs[2, 1].plot(sim, alpha=0.5)
axs[2, 1].axhline(promedio_esperado, color='black', linestyle='--', label='Esperado')
axs[2, 1].set_title('Evolución de ocurrencias por simulación')
axs[2, 1].set_xlabel('Corrida')
axs[2, 1].set_ylabel('Ocurrencias')
axs[2, 1].legend()

# boxplot
axs[3, 0].boxplot(resultados_todas)
axs[3, 0].set_title('Boxplot de ocurrencias por simulación')
axs[3, 0].set_xlabel('Simulación')
axs[3, 0].set_ylabel('Cantidad')

# hist de frec rel promedio
axs[3, 1].hist(frecuencias_promedio, bins=10, color='lightgreen', edgecolor='black')
axs[3, 1].axvline(frecuencia_esperada, color='red', linestyle='--', label='Esperada')
axs[3, 1].set_title('Histograma de frecuencias relativas (promedio por simulación)')
axs[3, 1].set_xlabel('Frecuencia relativa promedio')
axs[3, 1].set_ylabel('Frecuencia')
axs[3, 1].legend()

plt.tight_layout()
plt.show()