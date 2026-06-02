"""
TP 2.1 - Generadores Pseudoaleatorios
Simulación - UTN FRRO
"""

import math
import random
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats


# GENERADOR 1: Congruencial Lineal (GCL)
# Fórmula: X_{n+1} = (a * X_n + c) mod m

class GCL:
    """
    Generador Congruencial Lineal.
    Parámetros por defecto: los usados por glibc (C estándar).
    """
    def __init__(self, seed=None, a=1664525, c=1013904223, m=2**32):
        # Parámetros tomados de la biblioteca estándar de C (glibc).
        # Fueron elegidos porque cumplen el Teorema de Hull-Dobell,
        # garantizando período máximo de 2^32 números sin repetición.
        # Son constantes fijas del algoritmo, NO son la semilla.
        self.a = a
        self.c = c
        self.m = m

        # La semilla (X_0) es el estado inicial del generador.
        # Se fija en un valor constante para garantizar reproducibilidad:
        # la misma semilla siempre produce la misma secuencia, lo cual
        # es fundamental para verificar experimentos en simulación.
        # Si seed=None, se usa el reloj del sistema (varía en cada ejecución).
        self.estado = seed if seed is not None else int(time.time()) % m

    def siguiente_entero(self):
        self.estado = (self.a * self.estado + self.c) % self.m
        return self.estado

    def siguiente(self):
        """Devuelve un número en [0, 1)"""
        return self.siguiente_entero() / self.m

    def generar(self, n):
        """Genera una lista de n números en [0, 1)"""
        return [self.siguiente() for _ in range(n)]


# GENERADOR 2: Método de los Cuadrados Medios (von Neumann)
# Fórmula: tomar el cuadrado del número, extraer dígitos del medio

class CuadradosMedios:
    """
    Generador por el Método de los Cuadrados Medios (Middle Square).
    Necesita una semilla de d dígitos; se eleva al cuadrado y se
    extraen los d dígitos centrales como nuevo estado.
    Limitación conocida: puede degenerar a 0 o entrar en ciclos cortos.
    """
    def __init__(self, seed=6752, digitos=4):
        # La semilla debe tener exactamente 'd' dígitos para que el método
        # funcione correctamente. Se eligió 6752 como valor de prueba clásico
        # documentado en la literatura. Al igual que en el GCL, fijarla
        # garantiza reproducibilidad de los resultados.
        self.digitos = digitos
        self.estado = seed
        self._advertencia_ciclo = False

    def siguiente_entero(self):
        cuadrado = self.estado ** 2
        cuadrado_str = str(cuadrado).zfill(self.digitos * 2)
        inicio = len(cuadrado_str) // 2 - self.digitos // 2
        self.estado = int(cuadrado_str[inicio: inicio + self.digitos])
        return self.estado

    def siguiente(self):
        """Devuelve un número en [0, 1)"""
        return self.siguiente_entero() / (10 ** self.digitos)

    def generar(self, n):
        """Genera una lista de n números en [0, 1)"""
        numeros = []
        for _ in range(n):
            val = self.siguiente()
            if val == 0.0:
                break   # detuvo por degeneración
            numeros.append(val)
        return numeros

# GENERADOR 3: Python built-in (referencia)

class PythonRandom:
    """Envoltorio del generador Mersenne Twister de Python."""
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def siguiente(self):
        return self.rng.random()

    def generar(self, n):
        return [self.siguiente() for _ in range(n)]

# TESTS DE CALIDAD

def test_media(numeros, alpha=0.05):
    """
    Prueba de la Media.
    H0: la media de la muestra es 0.5 (distribución uniforme).
    Se usa un intervalo de confianza basado en la distribución normal.
    """
    n = len(numeros)
    media = np.mean(numeros)
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    limite = z_alpha * (1 / math.sqrt(12 * n))
    aprueba = abs(media - 0.5) < limite

    return {
        "test": "Media",
        "estadístico": round(media, 6),
        "esperado": 0.5,
        "límite_inferior": round(0.5 - limite, 6),
        "límite_superior": round(0.5 + limite, 6),
        "aprueba": aprueba,
        "resultado": "✓ PASA" if aprueba else "✗ FALLA"
    }


def test_varianza(numeros, alpha=0.05):
    """
    Prueba de la Varianza.
    H0: la varianza es 1/12 ≈ 0.0833 (distribución uniforme).
    Se usa la distribución chi-cuadrado con n-1 grados de libertad.
    """
    n = len(numeros)
    varianza = np.var(numeros, ddof=1)
    varianza_esperada = 1 / 12

    chi2_obs = (n - 1) * varianza / varianza_esperada
    chi2_lower = stats.chi2.ppf(alpha / 2, df=n - 1)
    chi2_upper = stats.chi2.ppf(1 - alpha / 2, df=n - 1)
    aprueba = chi2_lower < chi2_obs < chi2_upper

    return {
        "test": "Varianza",
        "estadístico": round(varianza, 6),
        "esperado": round(varianza_esperada, 6),
        "chi2_obs": round(chi2_obs, 4),
        "chi2_lower": round(chi2_lower, 4),
        "chi2_upper": round(chi2_upper, 4),
        "aprueba": aprueba,
        "resultado": "✓ PASA" if aprueba else "✗ FALLA"
    }


def test_chi_cuadrado(numeros, k=10, alpha=0.05):
    """
    Prueba de Chi-Cuadrado (Uniformidad).
    Divide [0,1) en k intervalos y compara frecuencias observadas
    con las esperadas para una distribución uniforme.
    """
    n = len(numeros)
    esperado = n / k
    observado, _ = np.histogram(numeros, bins=k, range=(0, 1))

    chi2_obs = sum((o - esperado) ** 2 / esperado for o in observado)
    chi2_critico = stats.chi2.ppf(1 - alpha, df=k - 1)
    p_valor = 1 - stats.chi2.cdf(chi2_obs, df=k - 1)
    aprueba = chi2_obs < chi2_critico

    return {
        "test": "Chi-Cuadrado (Uniformidad)",
        "chi2_obs": round(chi2_obs, 4),
        "chi2_critico": round(chi2_critico, 4),
        "p_valor": round(p_valor, 6),
        "grados_libertad": k - 1,
        "aprueba": aprueba,
        "resultado": "✓ PASA" if aprueba else "✗ FALLA"
    }


def test_runs(numeros, alpha=0.05):
    """
    Prueba de Rachas (Runs Test) - Independencia.
    Cuenta rachas ascendentes y descendentes y las compara con
    los valores esperados para una secuencia aleatoria.
    """
    n = len(numeros)
    # Construir secuencia de signos: + si sube, - si baja
    signos = [1 if numeros[i+1] > numeros[i] else 0 for i in range(n-1)]
    
    # Contar rachas
    rachas = 1
    for i in range(1, len(signos)):
        if signos[i] != signos[i-1]:
            rachas += 1

    # Media y varianza esperadas (fórmula estándar)
    media_r = (2*n - 1) / 3
    varianza_r = (16*n - 29) / 90

    z = (rachas - media_r) / math.sqrt(varianza_r)
    z_critico = stats.norm.ppf(1 - alpha / 2)
    p_valor = 2 * (1 - stats.norm.cdf(abs(z)))
    aprueba = abs(z) < z_critico

    return {
        "test": "Rachas (Independencia)",
        "rachas_obs": rachas,
        "media_esperada": round(media_r, 4),
        "z_obs": round(z, 4),
        "z_critico": round(z_critico, 4),
        "p_valor": round(p_valor, 6),
        "aprueba": aprueba,
        "resultado": "✓ PASA" if aprueba else "✗ FALLA"
    }


def test_series(numeros, e=5, alpha=0.05):
    """
    Prueba de las Series (Independencia Bidimensional).
    Forma pares (X_n, X_{n+1}) y divide el plano [0,1)x[0,1)
    en una cuadrícula de e×e celdas. Compara frecuencias observadas
    con las esperadas usando Chi-Cuadrado con e²-1 grados de libertad.
    """
    n = len(numeros)
    # Formar pares consecutivos
    pares = [(numeros[i], numeros[i+1]) for i in range(n - 1)]
    n_pares = len(pares)
    esperado = n_pares / (e * e)

    # Contar frecuencias en cada celda de la cuadrícula
    conteo = np.zeros((e, e), dtype=int)
    for x, y in pares:
        col = min(int(x * e), e - 1)
        fila = min(int(y * e), e - 1)
        conteo[fila][col] += 1

    chi2_obs = sum(
        (conteo[i][j] - esperado) ** 2 / esperado
        for i in range(e) for j in range(e)
    )
    gl = e * e - 1
    chi2_critico = stats.chi2.ppf(1 - alpha, df=gl)
    p_valor = 1 - stats.chi2.cdf(chi2_obs, df=gl)
    aprueba = chi2_obs < chi2_critico

    return {
        "test": "Series (Independencia Bidimensional)",
        "cuadrícula": f"{e}x{e}",
        "n_pares": n_pares,
        "frecuencia_esperada": round(esperado, 4),
        "chi2_obs": round(chi2_obs, 4),
        "chi2_critico": round(chi2_critico, 4),
        "p_valor": round(p_valor, 6),
        "grados_libertad": gl,
        "aprueba": aprueba,
        "resultado": "✓ PASA" if aprueba else "✗ FALLA"
    }


def test_poker(numeros, d=5, alpha=0.05):
    """
    Prueba de Póker (Independencia por Patrones).
    Agrupa los números en bloques de d dígitos decimales y
    clasifica cada bloque según la cantidad de dígitos distintos,
    comparando con las probabilidades teóricas del póker.
    """
    # Probabilidades teóricas para d=5 dígitos (0-9)
    # Categorías: todos distintos, un par, dos pares, pierna (three of a kind),
    #             full house, póker (four of a kind), quintilla (five of a kind)
    prob_teoricas = {
        "Todos distintos": 0.30240,
        "Un par":          0.50400,
        "Dos pares":       0.10800,
        "Pierna":          0.07200,
        "Full house":      0.00900,
        "Póker":           0.00450,
        "Quintilla":       0.00010,
    }

    def clasificar_mano(bloque):
        """Clasifica un bloque de d dígitos según patrones de póker."""
        digitos = [int(x * 10) % 10 for x in bloque]
        from collections import Counter
        conteos = sorted(Counter(digitos).values(), reverse=True)
        if conteos[0] == 5:   return "Quintilla"
        if conteos[0] == 4:   return "Póker"
        if conteos[0] == 3 and conteos[1] == 2: return "Full house"
        if conteos[0] == 3:   return "Pierna"
        if conteos[0] == 2 and conteos[1] == 2: return "Dos pares"
        if conteos[0] == 2:   return "Un par"
        return "Todos distintos"

    # Formar bloques de d números
    n = len(numeros)
    bloques = [numeros[i:i+d] for i in range(0, n - n % d, d)]
    n_bloques = len(bloques)

    # Contar frecuencias observadas
    from collections import Counter
    conteo_obs = Counter(clasificar_mano(b) for b in bloques)

    # Calcular Chi-Cuadrado
    chi2_obs = 0
    for categoria, prob in prob_teoricas.items():
        obs = conteo_obs.get(categoria, 0)
        esp = n_bloques * prob
        if esp > 0:
            chi2_obs += (obs - esp) ** 2 / esp

    gl = len(prob_teoricas) - 1
    chi2_critico = stats.chi2.ppf(1 - alpha, df=gl)
    p_valor = 1 - stats.chi2.cdf(chi2_obs, df=gl)
    aprueba = chi2_obs < chi2_critico

    # Tabla de resultados por categoría
    tabla = {}
    for cat, prob in prob_teoricas.items():
        obs = conteo_obs.get(cat, 0)
        esp = round(n_bloques * prob, 2)
        tabla[cat] = {"observado": obs, "esperado": esp}

    return {
        "test": "Póker (Independencia por Patrones)",
        "n_bloques": n_bloques,
        "chi2_obs": round(chi2_obs, 4),
        "chi2_critico": round(chi2_critico, 4),
        "p_valor": round(p_valor, 6),
        "grados_libertad": gl,
        "tabla_categorias": tabla,
        "aprueba": aprueba,
        "resultado": "✓ PASA" if aprueba else "✗ FALLA"
    }


def correr_todos_los_tests(numeros, nombre):
    """Corre los 6 tests y devuelve los resultados."""
    print(f"\n{'='*60}")
    print(f"  TESTS PARA: {nombre}  (n={len(numeros)})")
    print(f"{'='*60}")
    resultados = []
    for test_fn in [test_media, test_varianza, test_chi_cuadrado, test_runs, test_series, test_poker]:
        r = test_fn(numeros)
        resultados.append(r)
        print(f"\n[{r['test']}]  →  {r['resultado']}")
        for k, v in r.items():
            if k not in ("test", "resultado", "aprueba", "tabla_categorias"):
                print(f"    {k}: {v}")
        # Imprimir tabla de póker si existe
        if "tabla_categorias" in r:
            print("    Categorías:")
            for cat, vals in r["tabla_categorias"].items():
                print(f"      {cat:<20} obs={vals['observado']:>4}  esp={vals['esperado']:>7}")
    return resultados


# VISUALIZACIONES

def graficar_todo(generadores_data, nombre_archivo="graficas_tp.png"):
    """
    Genera una figura con 4 tipos de gráficas para cada generador:
    histograma, serie temporal, scatter plot y periodo.
    """
    nombres = list(generadores_data.keys())
    n_gen = len(nombres)

    fig = plt.figure(figsize=(18, 5 * n_gen))
    fig.suptitle("Análisis de Generadores Pseudoaleatorios", fontsize=16, fontweight='bold', y=1.01)
    gs = gridspec.GridSpec(n_gen, 4, figure=fig, hspace=0.5, wspace=0.4)

    colores = ['steelblue', 'darkorange', 'forestgreen']

    for i, nombre in enumerate(nombres):
        datos = generadores_data[nombre]
        color = colores[i % len(colores)]

        # 1. Histograma
        ax1 = fig.add_subplot(gs[i, 0])
        ax1.hist(datos, bins=20, color=color, edgecolor='white', alpha=0.85)
        ax1.axhline(len(datos)/20, color='red', linestyle='--', linewidth=1.2, label='Esperado')
        ax1.set_title(f"{nombre}\nHistograma", fontsize=10, fontweight='bold')
        ax1.set_xlabel("Valor")
        ax1.set_ylabel("Frecuencia")
        ax1.legend(fontsize=8)

        # 2. Serie temporal (primeros 200 valores)
        ax2 = fig.add_subplot(gs[i, 1])
        ax2.plot(datos[:200], color=color, linewidth=0.6, alpha=0.8)
        ax2.set_title(f"{nombre}\nSerie temporal (n=200)", fontsize=10, fontweight='bold')
        ax2.set_xlabel("Iteración")
        ax2.set_ylabel("Valor")

        # 3. Scatter plot (X_n vs X_{n+1})
        ax3 = fig.add_subplot(gs[i, 2])
        ax3.scatter(datos[:-1], datos[1:], s=1.5, color=color, alpha=0.4)
        ax3.set_title(f"{nombre}\nCorrelación $X_n$ vs $X_{{n+1}}$", fontsize=10, fontweight='bold')
        ax3.set_xlabel("$X_n$")
        ax3.set_ylabel("$X_{n+1}$")

        # 4. QQ-plot (vs uniforme)
        ax4 = fig.add_subplot(gs[i, 3])
        stats.probplot(datos, dist="uniform", plot=ax4)
        ax4.set_title(f"{nombre}\nQQ-Plot (vs Uniforme)", fontsize=10, fontweight='bold')
        ax4.get_lines()[0].set(markersize=1.5, color=color, alpha=0.5)
        ax4.get_lines()[1].set(color='red', linewidth=1.5)

    plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
    print(f"\n[INFO] Gráficas guardadas en '{nombre_archivo}'")
    plt.close()


def graficar_comparacion_periodo(nombre_archivo="comparacion_periodo.png"):
    """
    Muestra cómo el Método de Cuadrados Medios degenera
    en comparación con GCL y Python random.
    """
    N = 500
    gcl = GCL(seed=42)
    cm = CuadradosMedios(seed=6752)
    py = PythonRandom(seed=42)

    datos_gcl = gcl.generar(N)
    datos_cm_raw = cm.generar(N)       # puede ser < N si degenera
    datos_py = py.generar(N)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("Evolución de los generadores (n=500)", fontsize=13, fontweight='bold')

    for ax, datos, nombre, color in zip(
        axes,
        [datos_gcl, datos_cm_raw, datos_py],
        ["GCL", "Cuadrados Medios", "Python random"],
        ['steelblue', 'darkorange', 'forestgreen']
    ):
        ax.plot(datos, linewidth=0.7, color=color)
        ax.set_title(f"{nombre}\n(generó {len(datos)} valores)")
        ax.set_xlabel("Iteración")
        ax.set_ylabel("Valor")
        ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
    print(f"[INFO] Gráfica de comparación guardada en '{nombre_archivo}'")
    plt.close()


# TABLA RESUMEN

def imprimir_tabla_resumen(todos_resultados):
    """
    Imprime una tabla resumida estilo LaTeX para copiar al informe.
    """
    cols = ["Media", "Varianza", "Chi²", "Rachas", "Series", "Póker"]
    ancho = 88
    print("\n\n" + "="*ancho)
    print("  TABLA RESUMEN DE RESULTADOS (6 tests)")
    print("="*ancho)
    header = f"{'Generador':<22}" + "".join(f"{t:<11}" for t in cols)
    print(header)
    print("-"*ancho)

    for nombre, resultados in todos_resultados.items():
        fila = f"{nombre:<22}"
        for r in resultados:
            fila += f"{r['resultado']:<11}"
        print(fila)
    print("="*88)


# MAIN

def main():
    N = 1000
    SEED = 12345

    print("\n" + "="*60)
    print("  TP 2.1 - GENERADORES PSEUDOALEATORIOS")
    print("  Simulación - UTN FRRO")
    print("="*60)

    # --- Instanciar generadores ---
    gcl     = GCL(seed=SEED)
    cm      = CuadradosMedios(seed=6752, digitos=4)
    py_rand = PythonRandom(seed=SEED)

    # --- Generar secuencias ---
    datos_gcl = gcl.generar(N)
    datos_cm  = cm.generar(N)   # puede devolver menos de N si degenera
    datos_py  = py_rand.generar(N)

    print(f"\n[INFO] GCL generó         {len(datos_gcl)} números")
    print(f"[INFO] Cuadrados Medios generó {len(datos_cm)} números (puede degenerarse)")
    print(f"[INFO] Python random generó {len(datos_py)} números")

    # --- Correr tests ---
    todos_resultados = {}
    todos_resultados["GCL"]               = correr_todos_los_tests(datos_gcl, "GCL (Congruencial Lineal)")
    todos_resultados["Cuadrados Medios"]  = correr_todos_los_tests(datos_cm,  "Cuadrados Medios (von Neumann)")
    todos_resultados["Python random"]     = correr_todos_los_tests(datos_py,  "Python random (Mersenne Twister)")

    # --- Tabla resumen ---
    imprimir_tabla_resumen(todos_resultados)

    # --- Gráficas ---
    print("\n[INFO] Generando gráficas...")
    generadores_data = {
        "GCL":              datos_gcl,
        "Cuadrados Medios": datos_cm,
        "Python random":    datos_py,
    }
    graficar_todo(generadores_data, "graficas_tp.png")
    graficar_comparacion_periodo("comparacion_periodo.png")

    print("\n[✓] Proceso completado exitosamente.\n")


if __name__ == "__main__":
    main()