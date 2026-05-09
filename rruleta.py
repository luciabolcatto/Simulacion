"""
TP 1.1 - Simulación de una Ruleta
Universidad Tecnológica Nacional - FRRO
Uso: python ruleta.py -c <corridas> -n <tiradas> -e <numero_elegido>
Ejemplo: python ruleta.py -c 5 -n 1000 -e 7
"""

import argparse
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


# ──────────────────────────────────────────────
# Parámetros de la ruleta europea (0..36)
# ──────────────────────────────────────────────
TOTAL_NUMEROS = 37          # 0 a 36
PROB_ESPERADA = 1 / TOTAL_NUMEROS
VALOR_ESPERADO = sum(range(TOTAL_NUMEROS)) / TOTAL_NUMEROS   # 18.0
VARIANZA_ESPERADA = sum((x - VALOR_ESPERADO) ** 2 for x in range(TOTAL_NUMEROS)) / TOTAL_NUMEROS


def simular_corrida(n_tiradas: int, numero_elegido: int, seed=None):
    """
    Simula n_tiradas de ruleta y devuelve arrays acumulados de:
    - frecuencia relativa del número elegido
    - valor promedio de las tiradas
    - desvío estándar acumulado
    - varianza acumulada
    """
    if seed is not None:
        random.seed(seed)

    resultados = [random.randint(0, 36) for _ in range(n_tiradas)]

    frn   = []   # frecuencia relativa del número elegido
    vpn   = []   # valor promedio acumulado
    vdn   = []   # desvío estándar acumulado
    vvn   = []   # varianza acumulada

    aciertos = 0
    suma     = 0
    suma_cuad = 0

    for i, r in enumerate(resultados, start=1):
        if r == numero_elegido:
            aciertos += 1
        suma      += r
        suma_cuad += r ** 2

        media = suma / i
        var   = suma_cuad / i - media ** 2  # varianza muestral online
        var   = max(var, 0)                  # evita -0 por punto flotante

        frn.append(aciertos / i)
        vpn.append(media)
        vdn.append(var ** 0.5)
        vvn.append(var)

    return frn, vpn, vdn, vvn


def graficar_corrida_individual(frn, vpn, vdn, vvn, n_tiradas, numero_elegido, corrida_num):
    """4 gráficas para una sola corrida."""
    eje_n = range(1, n_tiradas + 1)

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.suptitle(
        f"Corrida {corrida_num} — Número elegido: {numero_elegido} — Tiradas: {n_tiradas}",
        fontsize=14, fontweight="bold"
    )

    # ── 1. Frecuencia relativa ──
    ax = axes[0, 0]
    ax.plot(eje_n, frn, color="red", linewidth=0.8, label=f"frn (simulada)")
    ax.axhline(PROB_ESPERADA, color="blue", linewidth=1.5, linestyle="--",
               label=f"fre = 1/37 ≈ {PROB_ESPERADA:.4f}")
    ax.set_title("Frecuencia Relativa del número elegido")
    ax.set_xlabel("n (número de tiradas)")
    ax.set_ylabel("fr")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── 2. Valor promedio ──
    ax = axes[0, 1]
    ax.plot(eje_n, vpn, color="red", linewidth=0.8, label="vpn (simulado)")
    ax.axhline(VALOR_ESPERADO, color="blue", linewidth=1.5, linestyle="--",
               label=f"vpe = {VALOR_ESPERADO:.2f}")
    ax.set_title("Valor Promedio de las tiradas")
    ax.set_xlabel("n (número de tiradas)")
    ax.set_ylabel("vp")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── 3. Desvío estándar ──
    desvio_esperado = VARIANZA_ESPERADA ** 0.5
    ax = axes[1, 0]
    ax.plot(eje_n, vdn, color="red", linewidth=0.8, label="vd (simulado)")
    ax.axhline(desvio_esperado, color="blue", linewidth=1.5, linestyle="--",
               label=f"vde = {desvio_esperado:.4f}")
    ax.set_title("Desvío Estándar acumulado")
    ax.set_xlabel("n (número de tiradas)")
    ax.set_ylabel("vd")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── 4. Varianza ──
    ax = axes[1, 1]
    ax.plot(eje_n, vvn, color="red", linewidth=0.8, label="vvn (simulada)")
    ax.axhline(VARIANZA_ESPERADA, color="blue", linewidth=1.5, linestyle="--",
               label=f"vve = {VARIANZA_ESPERADA:.4f}")
    ax.set_title("Varianza acumulada")
    ax.set_xlabel("n (número de tiradas)")
    ax.set_ylabel("vv")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fname = f"corrida_{corrida_num:02d}.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    print(f"  → Guardado: {fname}")
    plt.close()


def graficar_multiples_corridas(todas_frn, todas_vpn, todas_vdn, todas_vvn,
                                n_tiradas, numero_elegido, n_corridas):
    """4 gráficas con todas las corridas superpuestas."""
    eje_n  = range(1, n_tiradas + 1)
    colors = plt.cm.tab10.colors

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(
        f"Comparación de {n_corridas} corridas — Número elegido: {numero_elegido} — "
        f"Tiradas por corrida: {n_tiradas}",
        fontsize=13, fontweight="bold"
    )

    datasets = [
        (todas_frn, axes[0, 0], "Frecuencia Relativa", "fr",
         PROB_ESPERADA, f"fre = 1/37 ≈ {PROB_ESPERADA:.4f}"),
        (todas_vpn, axes[0, 1], "Valor Promedio", "vp",
         VALOR_ESPERADO, f"vpe = {VALOR_ESPERADO:.2f}"),
        (todas_vdn, axes[1, 0], "Desvío Estándar", "vd",
         VARIANZA_ESPERADA ** 0.5, f"vde = {VARIANZA_ESPERADA**0.5:.4f}"),
        (todas_vvn, axes[1, 1], "Varianza", "vv",
         VARIANZA_ESPERADA, f"vve = {VARIANZA_ESPERADA:.4f}"),
    ]

    for datos, ax, titulo, ylabel, esperado, label_esp in datasets:
        for i, serie in enumerate(datos):
            ax.plot(eje_n, serie, color=colors[i % 10], linewidth=0.7,
                    alpha=0.8, label=f"Corrida {i+1}")
        ax.axhline(esperado, color="black", linewidth=2, linestyle="--", label=label_esp)
        ax.set_title(titulo)
        ax.set_xlabel("n (número de tiradas)")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=7, ncol=2)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fname = "multiples_corridas.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    print(f"  → Guardado: {fname}")
    plt.close()


def graficar_histograma_finales(todas_frn, n_corridas, numero_elegido):
    """Histograma de los valores finales de la frecuencia relativa."""
    finales = [frn[-1] for frn in todas_frn]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(finales, bins=max(5, n_corridas // 2), color="steelblue",
            edgecolor="white", alpha=0.85)
    ax.axvline(PROB_ESPERADA, color="red", linewidth=2, linestyle="--",
               label=f"fre = {PROB_ESPERADA:.4f}")
    ax.set_title(f"Histograma de frecuencias relativas finales\n"
                 f"({n_corridas} corridas, número elegido: {numero_elegido})")
    ax.set_xlabel("Frecuencia relativa final")
    ax.set_ylabel("Cantidad de corridas")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fname = "histograma_finales.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    print(f"  → Guardado: {fname}")
    plt.close()


def imprimir_resumen(todas_frn, todas_vpn, todas_vvn, n_corridas, n_tiradas, numero_elegido):
    print("\n" + "=" * 55)
    print("  RESUMEN ESTADÍSTICO FINAL")
    print("=" * 55)
    print(f"  Ruleta europea: 0 a 36  ({TOTAL_NUMEROS} números)")
    print(f"  Número elegido   : {numero_elegido}")
    print(f"  Corridas         : {n_corridas}")
    print(f"  Tiradas/corrida  : {n_tiradas}")
    print("-" * 55)
    print(f"  {'':30s} {'Simulado':>10s}  {'Esperado':>10s}")
    print("-" * 55)

    fr_fin  = [s[-1] for s in todas_frn]
    vp_fin  = [s[-1] for s in todas_vpn]
    vv_fin  = [s[-1] for s in todas_vvn]

    print(f"  {'Frec. relativa promedio':30s} {np.mean(fr_fin):>10.4f}  {PROB_ESPERADA:>10.4f}")
    print(f"  {'Valor promedio':30s} {np.mean(vp_fin):>10.4f}  {VALOR_ESPERADO:>10.4f}")
    print(f"  {'Varianza promedio':30s} {np.mean(vv_fin):>10.4f}  {VARIANZA_ESPERADA:>10.4f}")
    print(f"  {'Desvío estándar promedio':30s} {np.mean(vv_fin)**0.5:>10.4f}  {VARIANZA_ESPERADA**0.5:>10.4f}")
    print("=" * 55)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="TP1.1 - Simulación de Ruleta Europea"
    )
    parser.add_argument("-c", "--corridas", type=int, default=5,
                        help="Cantidad de corridas del experimento (default: 5)")
    parser.add_argument("-n", "--tiradas", type=int, default=1000,
                        help="Cantidad de tiradas por corrida (default: 1000)")
    parser.add_argument("-e", "--elegido", type=int, default=7,
                        help="Número elegido (0-36) (default: 7)")
    args = parser.parse_args()

    n_corridas     = args.corridas
    n_tiradas      = args.tiradas
    numero_elegido = args.elegido

    # Validaciones
    if not (0 <= numero_elegido <= 36):
        print("ERROR: El número elegido debe estar entre 0 y 36.")
        return
    if n_tiradas < 10:
        print("ERROR: Se necesitan al menos 10 tiradas.")
        return
    if n_corridas < 1:
        print("ERROR: Se necesita al menos 1 corrida.")
        return

    print(f"\n{'='*55}")
    print(f"  TP 1.1 - Simulación de Ruleta Europea")
    print(f"  Corridas: {n_corridas} | Tiradas: {n_tiradas} | Número: {numero_elegido}")
    print(f"{'='*55}\n")

    todas_frn, todas_vpn, todas_vdn, todas_vvn = [], [], [], []

    for c in range(1, n_corridas + 1):
        print(f"Simulando corrida {c}/{n_corridas}...")
        frn, vpn, vdn, vvn = simular_corrida(n_tiradas, numero_elegido, seed=c * 42)
        todas_frn.append(frn)
        todas_vpn.append(vpn)
        todas_vdn.append(vdn)
        todas_vvn.append(vvn)
        graficar_corrida_individual(frn, vpn, vdn, vvn, n_tiradas, numero_elegido, c)

    print("\nGenerando gráfica comparativa de todas las corridas...")
    graficar_multiples_corridas(todas_frn, todas_vpn, todas_vdn, todas_vvn,
                                n_tiradas, numero_elegido, n_corridas)

    print("Generando histograma de frecuencias relativas finales...")
    graficar_histograma_finales(todas_frn, n_corridas, numero_elegido)

    imprimir_resumen(todas_frn, todas_vpn, todas_vvn, n_corridas, n_tiradas, numero_elegido)
    print("\n¡Simulación finalizada! Revisá las imágenes generadas.\n")


if __name__ == "__main__":
    main()