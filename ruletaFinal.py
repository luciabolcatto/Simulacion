"""
TP 1.1 - Simulación de una Ruleta Europea
Universidad Tecnológica Nacional - FRRO

Uso:
    python ruleta_final.py -c <corridas> -n <tiradas> -e <numero_elegido>

Ejemplo:
    python ruleta_final.py -c 5 -n 1000 -e 7

Descripción:
    Simula el plato de una ruleta europea (0 a 36, 37 números).
    Para cada corrida registra la evolución acumulada de:
      - frn : frecuencia relativa del número elegido
      - vpn : valor promedio de las tiradas
      - vdn : desvío estándar acumulado
      - vvn : varianza acumulada
    Genera 8 gráficas (mínimo requerido por el enunciado):
      - Fig. 1: 4 subgráficas de UNA corrida (convergencia individual)
      - Fig. 2: 4 subgráficas con TODAS las corridas superpuestas
    Y adicionalmente:
      - Histograma de frecuencias relativas finales
      - Resumen estadístico impreso en consola
"""

import argparse
import random
import math
import matplotlib.pyplot as plt


# ─────────────────────────────────────────────────────────────
#  CONSTANTES TEÓRICAS — Ruleta europea 0..36 (37 números)
# ─────────────────────────────────────────────────────────────

TOTAL_NUMEROS = 37                                          # 0 a 36 inclusive
PROB_ESPERADA = 1.0 / TOTAL_NUMEROS                         # ≈ 0.02703
VALOR_ESPERADO = sum(range(TOTAL_NUMEROS)) / TOTAL_NUMEROS  # = 18.0

# Varianza poblacional de la distribución uniforme discreta {0,1,...,36}
# Fórmula: (N² - 1) / 12, con N = TOTAL_NUMEROS
VARIANZA_ESPERADA = (TOTAL_NUMEROS ** 2 - 1) / 12          # ≈ 114.0
DESVIO_ESPERADO = math.sqrt(VARIANZA_ESPERADA)              # ≈ 10.677


# ─────────────────────────────────────────────────────────────
#  SIMULACIÓN
# ─────────────────────────────────────────────────────────────

def simular_corrida(n_tiradas: int, numero_elegido: int) -> tuple:
    """
    Simula n_tiradas de ruleta y devuelve cuatro listas con la
    evolución ACUMULADA de los estadísticos tras cada tirada:

        frn[i]  — frecuencia relativa del número elegido tras i+1 tiradas
        vpn[i]  — valor promedio de las tiradas 1..i+1
        vdn[i]  — desvío estándar acumulado
        vvn[i]  — varianza acumulada

    Se usan acumuladores online (O(n) en tiempo y O(1) en memoria
    auxiliar) para evitar recalcular desde cero en cada paso.
    La fórmula de varianza usada es la identidad de König:
        Var = E[X²] - (E[X])²
    con un clamp a 0 para evitar valores negativos por error de
    punto flotante.
    """
    aciertos = 0
    suma = 0
    suma_cuad = 0

    frn, vpn, vdn, vvn = [], [], [], []

    for i in range(1, n_tiradas + 1):
        tirada = random.randint(0, 36)          # ruleta europea: 0..36

        if tirada == numero_elegido:
            aciertos += 1
        suma += tirada
        suma_cuad += tirada ** 2

        media = suma / i
        varianza = max(suma_cuad / i - media ** 2, 0.0)     # clamp >= 0

        frn.append(aciertos / i)
        vpn.append(media)
        vvn.append(varianza)
        vdn.append(math.sqrt(varianza))

    return frn, vpn, vdn, vvn


# ─────────────────────────────────────────────────────────────
#  GRAFICADO
# ─────────────────────────────────────────────────────────────

def _configurar_subgrafica(ax, datos, eje_x, valor_esperado,
                            titulo, xlabel, ylabel, label_sim, label_esp,
                            color_sim='red', alpha=1.0):
    """Helper interno: plotea una serie y su valor teórico de referencia."""
    ax.plot(eje_x, datos, color=color_sim, linewidth=0.8,
            alpha=alpha, label=label_sim)
    ax.axhline(valor_esperado, color='blue', linewidth=1.5,
               linestyle='--', label=label_esp)
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)


def graficar_corrida_individual(frn, vpn, vdn, vvn,
                                 n_tiradas, numero_elegido, corrida_num):
    """
    Figura 1 (mínimo requerido): 4 subgráficas para UNA corrida.
    Muestra la convergencia de cada estadístico hacia su valor teórico
    a medida que aumenta n (Ley de los Grandes Números).
    """
    eje_x = range(1, n_tiradas + 1)
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.suptitle(
        f"Corrida {corrida_num} — Número elegido: {numero_elegido} "
        f"— Tiradas: {n_tiradas}",
        fontsize=14, fontweight='bold'
    )

    datos = [
        (frn,  axes[0, 0], 'Frecuencia Relativa del número elegido',
         'fr',  PROB_ESPERADA,    f'fre = 1/37 ≈ {PROB_ESPERADA:.4f}', 'frn (simulada)'),
        (vpn,  axes[0, 1], 'Valor Promedio de las tiradas',
         'vp',  VALOR_ESPERADO,   f'vpe = {VALOR_ESPERADO:.2f}',        'vpn (simulado)'),
        (vdn,  axes[1, 0], 'Desvío Estándar acumulado',
         'vd',  DESVIO_ESPERADO,  f'vde = {DESVIO_ESPERADO:.4f}',       'vdn (simulado)'),
        (vvn,  axes[1, 1], 'Varianza acumulada',
         'vv',  VARIANZA_ESPERADA,f'vve = {VARIANZA_ESPERADA:.4f}',     'vvn (simulada)'),
    ]

    for serie, ax, titulo, ylabel, esperado, label_esp, label_sim in datos:
        _configurar_subgrafica(
            ax, serie, eje_x, esperado,
            titulo, 'n (número de tiradas)', ylabel,
            label_sim, label_esp
        )

    plt.tight_layout()

    # Guardar con nombre descriptivo (idea de Ruleta.py)
    fname = f"corrida_{corrida_num:02d}_n{n_tiradas}_e{numero_elegido}.png"
    plt.savefig(fname, dpi=150, bbox_inches='tight')
    print(f"  → Guardado: {fname}")
    plt.close()


def graficar_multiples_corridas(todas_frn, todas_vpn, todas_vdn, todas_vvn,
                                 n_tiradas, numero_elegido, n_corridas):
    """
    Figura 2 (mínimo requerido): 4 subgráficas con TODAS las corridas
    superpuestas. Permite apreciar la dispersión entre corridas y la
    convergencia global al valor teórico (Teorema Central del Límite).
    """
    eje_x = range(1, n_tiradas + 1)
    colors = plt.cm.tab10.colors

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(
        f"Comparación de {n_corridas} corridas — "
        f"Número elegido: {numero_elegido} — Tiradas/corrida: {n_tiradas}",
        fontsize=13, fontweight='bold'
    )

    grupos = [
        (todas_frn, axes[0, 0], 'Frecuencias Relativas',       'fr',
         PROB_ESPERADA,    f'fre = 1/37 ≈ {PROB_ESPERADA:.4f}'),
        (todas_vpn, axes[0, 1], 'Valores Promedio',             'vp',
         VALOR_ESPERADO,   f'vpe = {VALOR_ESPERADO:.2f}'),
        (todas_vdn, axes[1, 0], 'Desvíos Estándar',             'vd',
         DESVIO_ESPERADO,  f'vde = {DESVIO_ESPERADO:.4f}'),
        (todas_vvn, axes[1, 1], 'Varianzas',                    'vv',
         VARIANZA_ESPERADA,f'vve = {VARIANZA_ESPERADA:.4f}'),
    ]

    for todas_series, ax, titulo, ylabel, esperado, label_esp in grupos:
        for i, serie in enumerate(todas_series):
            ax.plot(eje_x, serie, color=colors[i % 10],
                    linewidth=0.7, alpha=0.75, label=f'Corrida {i+1}')
        ax.axhline(esperado, color='black', linewidth=2,
                   linestyle='--', label=label_esp)
        ax.set_title(titulo)
        ax.set_xlabel('n (número de tiradas)')
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=7, ncol=2)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fname = f"multiples_corridas_n{n_tiradas}_e{numero_elegido}.png"
    plt.savefig(fname, dpi=150, bbox_inches='tight')
    print(f"  → Guardado: {fname}")
    plt.close()


def graficar_histograma_finales(todas_frn, n_corridas, numero_elegido):
    """
    Histograma de los valores FINALES de la frecuencia relativa
    (uno por corrida). Permite visualizar la distribución de los
    resultados y verificar que se centran en torno al valor teórico.
    Vinculado al Teorema Central del Límite: con suficientes corridas,
    esta distribución tiende a la normal.
    """
    finales = [frn[-1] for frn in todas_frn]

    fig, ax = plt.subplots(figsize=(8, 5))
    n_bins = max(5, n_corridas // 2)
    ax.hist(finales, bins=n_bins, color='steelblue',
            edgecolor='white', alpha=0.85)
    ax.axvline(PROB_ESPERADA, color='red', linewidth=2,
               linestyle='--', label=f'fre = {PROB_ESPERADA:.4f}')
    ax.set_title(
        f"Histograma de frecuencias relativas finales\n"
        f"({n_corridas} corridas, número elegido: {numero_elegido})"
    )
    ax.set_xlabel('Frecuencia relativa final')
    ax.set_ylabel('Cantidad de corridas')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    fname = f"histograma_finales_n{numero_elegido}.png"
    plt.savefig(fname, dpi=150, bbox_inches='tight')
    print(f"  → Guardado: {fname}")
    plt.close()


# ─────────────────────────────────────────────────────────────
#  RESUMEN EN CONSOLA
# ─────────────────────────────────────────────────────────────

def imprimir_resumen(todas_frn, todas_vpn, todas_vdn, todas_vvn,
                      n_corridas, n_tiradas, numero_elegido):
    """
    Imprime una tabla comparativa de valores simulados (promedio de los
    valores finales de cada corrida) versus valores teóricos esperados.
    """
    def promedio(listas):
        return sum(s[-1] for s in listas) / len(listas)

    fr_prom = promedio(todas_frn)
    vp_prom = promedio(todas_vpn)
    vd_prom = promedio(todas_vdn)
    vv_prom = promedio(todas_vvn)

    sep = '=' * 58
    print(f"\n{sep}")
    print("  RESUMEN ESTADÍSTICO FINAL")
    print(sep)
    print(f"  Ruleta europea: 0 a 36  ({TOTAL_NUMEROS} números)")
    print(f"  Número elegido : {numero_elegido}")
    print(f"  Corridas       : {n_corridas}")
    print(f"  Tiradas/corrida: {n_tiradas}")
    print('-' * 58)
    print(f"  {'Estadístico':<28} {'Simulado':>10}  {'Esperado':>10}")
    print('-' * 58)
    filas = [
        ('Frec. relativa promedio', fr_prom, PROB_ESPERADA),
        ('Valor promedio',          vp_prom, VALOR_ESPERADO),
        ('Varianza promedio',       vv_prom, VARIANZA_ESPERADA),
        ('Desvío estándar promedio',vd_prom, DESVIO_ESPERADO),
    ]
    for nombre, sim, esp in filas:
        print(f"  {nombre:<28} {sim:>10.4f}  {esp:>10.4f}")
    print(sep)


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='TP1.1 — Simulación de Ruleta Europea (UTN-FRRO)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-c', '--corridas', type=int, default=5,
                        help='Cantidad de corridas del experimento')
    parser.add_argument('-n', '--tiradas', type=int, default=1000,
                        help='Cantidad de tiradas por corrida')
    parser.add_argument('-e', '--elegido', type=int, default=7,
                        help='Número apostado (0-36)')
    args = parser.parse_args()

    n_corridas = args.corridas
    n_tiradas = args.tiradas
    numero_elegido = args.elegido

    # Validaciones
    if not (0 <= numero_elegido <= 36):
        parser.error("El número elegido debe estar entre 0 y 36.")
    if n_tiradas < 10:
        parser.error("Se necesitan al menos 10 tiradas por corrida.")
    if n_corridas < 1:
        parser.error("Se necesita al menos 1 corrida.")

    print(f"\n{'='*58}")
    print("  TP 1.1 — Simulación de Ruleta Europea — UTN FRRO")
    print(f"  Corridas: {n_corridas} | Tiradas: {n_tiradas} | Número: {numero_elegido}")
    print(f"{'='*58}\n")

    todas_frn, todas_vpn, todas_vdn, todas_vvn = [], [], [], []

    # Corridas individuales
    for c in range(1, n_corridas + 1):
        print(f"Simulando corrida {c}/{n_corridas}...")
        frn, vpn, vdn, vvn = simular_corrida(n_tiradas, numero_elegido)
        todas_frn.append(frn)
        todas_vpn.append(vpn)
        todas_vdn.append(vdn)
        todas_vvn.append(vvn)
        graficar_corrida_individual(frn, vpn, vdn, vvn,
                                    n_tiradas, numero_elegido, c)

    # Gráfica comparativa de todas las corridas
    print("\nGenerando gráfica comparativa de todas las corridas...")
    graficar_multiples_corridas(todas_frn, todas_vpn, todas_vdn, todas_vvn,
                                 n_tiradas, numero_elegido, n_corridas)

    # Histograma de valores finales
    print("Generando histograma de frecuencias relativas finales...")
    graficar_histograma_finales(todas_frn, n_corridas, numero_elegido)

    # Resumen en consola
    imprimir_resumen(todas_frn, todas_vpn, todas_vdn, todas_vvn,
                     n_corridas, n_tiradas, numero_elegido)

    print("\n¡Simulación finalizada! Revisá las imágenes generadas.\n")


if __name__ == '__main__':
    main()