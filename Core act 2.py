"""Rastreador de síntomas - Fase 2 (programa principal)

Menú de terminal para registrar síntomas y hábitos diarios, ver el historial,
detectar patrones simples y recibir recomendaciones básicas de hábitos.

Para ejecutarlo:  python main.py
"""

from datetime import date

import almacenamiento
import analisis
import recomendaciones

# Opciones de síntoma que se muestran en el menú de registro
SINTOMAS = {
    "1": "ninguno",
    "2": "dolor de cabeza",
    "3": "cansancio",
    "4": "falta de concentración",
    "5": "otro",
}

AVISO = (
    "Esta app no sustituye a un médico. Si tus síntomas son fuertes\n"
    "o no se van, consulta a un profesional."
)


# ---------------------------------------------------------------------------
# Funciones para pedir datos al usuario (cada una repite hasta que sea válido)
# ---------------------------------------------------------------------------

def pedir_fecha():
    """Pide la fecha. Si el usuario solo da Enter, usa la de hoy."""
    hoy = date.today().isoformat()
    while True:
        texto = input(f"Fecha (AAAA-MM-DD) [Enter para hoy, {hoy}]: ").strip()
        if texto == "":
            return hoy
        try:
            return date.fromisoformat(texto).isoformat()
        except ValueError:
            print("Fecha no válida. Usa el formato AAAA-MM-DD, por ejemplo 2026-10-16.")


def pedir_sintoma():
    """Muestra las opciones de síntoma y regresa la elegida."""
    print("\n¿Qué sentiste hoy?")
    for numero, nombre in SINTOMAS.items():
        print(f"  {numero}. {nombre}")
    while True:
        opcion = input("Elige una opción (1-5): ").strip()
        if opcion in SINTOMAS:
            return SINTOMAS[opcion]
        print("Opción no válida. Escribe un número del 1 al 5.")


def pedir_numero(pregunta, minimo, maximo, tipo=float):
    """Pide un número dentro de un rango y repite hasta que sea válido."""
    while True:
        texto = input(pregunta).strip().replace(",", ".")
        try:
            valor = tipo(texto)
        except ValueError:
            print("Escribe un número.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"El número debe estar entre {minimo} y {maximo}.")


def pedir_si_no(pregunta):
    """Pide una respuesta de sí o no y regresa True o False."""
    while True:
        texto = input(pregunta + " (s/n): ").strip().lower()
        if texto in ("s", "si", "sí"):
            return True
        if texto in ("n", "no"):
            return False
        print("Responde con s o n.")


# ---------------------------------------------------------------------------
# Funciones de cada opción del menú
# ---------------------------------------------------------------------------

def registrar_dia():
    """Opción 1: pide los datos del día y los guarda en el CSV."""
    print("\n--- Registro diario ---")

    fecha = pedir_fecha()
    sintoma = pedir_sintoma()

    # Si no sintió nada, la intensidad es 0 y no se pregunta
    if sintoma == "ninguno":
        intensidad = 0
    else:
        intensidad = pedir_numero("Intensidad del 1 (leve) al 5 (muy fuerte): ", 1, 5, int)

    print("\nHábitos del día")
    sueno = pedir_numero("Horas de sueño (por ejemplo 6.5): ", 0, 24, float)
    comidas = pedir_numero("Comidas al día: ", 0, 8, int)
    agua = pedir_numero("Vasos de agua: ", 0, 30, int)
    ejercicio = "si" if pedir_si_no("¿Hiciste ejercicio?") else "no"

    registro = {
        "fecha": fecha,
        "sintoma": sintoma,
        "intensidad": intensidad,
        "sueno": sueno,
        "comidas": comidas,
        "agua": agua,
        "ejercicio": ejercicio,
        "ejemplo": "no",
    }

    if almacenamiento.agregar_registro(registro):
        print("\nActualizamos tu registro de esa fecha.")
    else:
        print("\nRegistro guardado. ¡Gracias por llevar tu seguimiento!")


def ver_historial():
    """Opción 2: muestra todos los registros (del más reciente al más antiguo) y un resumen."""
    df = almacenamiento.leer_registros()
    if df.empty:
        print("\nAún no tienes registros. Registra tu primer día con la opción 1.")
        return

    df = df.sort_values("fecha", ascending=False)

    print("\n--- Historial ---")
    print(f"{'Fecha':<12}{'Síntoma':<24}{'Intens.':<9}{'Sueño':<9}{'Comidas':<9}{'Agua':<6}{'Ejercicio'}")
    print("-" * 78)
    for _, r in df.iterrows():
        intensidad = str(int(r["intensidad"])) if r["intensidad"] > 0 else "-"
        sueno = f"{r['sueno']} h"
        print(f"{r['fecha']:<12}{r['sintoma']:<24}{intensidad:<9}{sueno:<9}"
              f"{int(r['comidas']):<9}{int(r['agua']):<6}{r['ejercicio']}")

    # Resumen general calculado con pandas
    datos = analisis.resumen(df)
    print("\nResumen")
    print(f"  Días registrados: {datos['dias']} (con síntomas: {datos['dias_con_sintoma']})")
    print(f"  Promedio de sueño: {datos['sueno_promedio']} h")
    print(f"  Promedio de comidas: {datos['comidas_promedio']} al día")
    print(f"  Promedio de agua: {datos['agua_promedio']} vasos")
    print(f"  Días con ejercicio: {datos['dias_ejercicio']}")


def hay_suficientes_datos(df, para):
    """Revisa que haya registros suficientes; si no, avisa. Regresa True o False."""
    if len(df) >= analisis.MIN_REGISTROS:
        return True
    print(f"\nNecesitas al menos {analisis.MIN_REGISTROS} registros para {para}. Tienes {len(df)}.")
    print("Registra más días o carga datos de ejemplo desde el menú.")
    return False


def ver_patrones():
    """Opción 3: compara los días según tus hábitos y muestra los patrones."""
    df = almacenamiento.leer_registros()
    if not hay_suficientes_datos(df, "detectar patrones"):
        return

    resultados = analisis.detectar_patrones(df)

    print("\n--- Patrones detectados ---")
    if not resultados:
        print("Todavía no hay suficientes días comparables en tus hábitos.")
        print("Sigue registrando para que haya más variedad.")
        return

    for r in resultados:
        print(f"\nCuando {r['cumple']}: tuviste síntomas el {r['p_cumple']}% de los días ({r['n_cumple']} días).")
        print(f"Cuando {r['no_cumple']}: tuviste síntomas el {r['p_no_cumple']}% de los días ({r['n_no_cumple']} días).")
        if r["es_patron"]:
            extra = f", sobre todo {r['sintoma_comun']}" if r["sintoma_comun"] else ""
            print(f"  >> Posible patrón: los síntomas aparecen más cuando {r['cumple']}{extra}.")

    print("\nSon patrones simples basados en tus registros, no son un diagnóstico.")


def ver_recomendaciones():
    """Opción 4: da recomendaciones básicas de hábitos según los patrones."""
    df = almacenamiento.leer_registros()
    if not hay_suficientes_datos(df, "dar recomendaciones"):
        return

    consejos = recomendaciones.generar_recomendaciones(analisis.detectar_patrones(df))

    print("\n--- Recomendaciones ---")
    if not consejos:
        print("Por ahora no se ve ningún patrón claro en tus registros.")
        print("Sigue registrando tus días y vuelve a revisar en unos días.")
    else:
        print("Según tus registros, estos hábitos podrían ayudarte:")
        for numero, (situacion, consejo) in enumerate(consejos, start=1):
            print(f"\n{numero}. Cuando {situacion} aparecen más síntomas.")
            print(f"   {consejo}")

    print("\nSon sugerencias generales de hábitos, no un diagnóstico.")
    print("Si tus síntomas son fuertes, frecuentes o no se van, consulta a un profesional de la salud.")


def cargar_ejemplo():
    """Opción 5: agrega 14 días de datos simulados para probar la app."""
    print("\nEsto agregará 14 días de datos de ejemplo a tu historial.")
    print("Si ya tenías un registro en alguna de esas fechas, se conserva el tuyo.")
    if not pedir_si_no("¿Quieres continuar?"):
        print("No se cargó nada.")
        return

    agregados = almacenamiento.cargar_ejemplo()
    print(f"Listo, se agregaron {agregados} días de ejemplo.")
    print(f"Para borrarlos, elimina las filas con ejemplo = si en {almacenamiento.ARCHIVO_CSV.name}.")


# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------

def main():
    """Muestra el menú en un ciclo hasta que el usuario elige salir."""
    print("=== Rastreador de síntomas ===")
    print(AVISO)

    while True:
        total = len(almacenamiento.leer_registros())
        print(f"\nRegistros guardados: {total}")
        print("1. Registrar mi día")
        print("2. Ver mi historial")
        print("3. Ver mis patrones")
        print("4. Ver recomendaciones")
        print("5. Cargar datos de ejemplo")
        print("6. Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            registrar_dia()
        elif opcion == "2":
            ver_historial()
        elif opcion == "3":
            ver_patrones()
        elif opcion == "4":
            ver_recomendaciones()
        elif opcion == "5":
            cargar_ejemplo()
        elif opcion == "6":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
"""Manejo de archivos: lee y escribe los registros en un archivo CSV.

Todo lo que tiene que ver con guardar o cargar datos está en este módulo,
así el resto del programa no necesita saber cómo se guardan.
"""

from datetime import date, timedelta
from pathlib import Path

import pandas as pd  # Librería externa: se usa para leer y escribir el CSV

# La ruta se calcula a partir de la ubicación de este archivo, así funciona
# sin importar desde qué carpeta abras o ejecutes el programa en VS Code.
CARPETA_DATOS = Path(__file__).resolve().parent / "datos"
ARCHIVO_CSV = CARPETA_DATOS / "registros.csv"

# Columnas del CSV (una fila por día registrado)
COLUMNAS = ["fecha", "sintoma", "intensidad", "sueno", "comidas", "agua", "ejercicio", "ejemplo"]

# Datos simulados: (sueño, comidas, agua, ejercicio, síntoma, intensidad)
DATOS_EJEMPLO = [
    (5.0, 2, 3, "no", "dolor de cabeza", 4),
    (7.5, 3, 6, "si", "ninguno", 0),
    (8.0, 3, 5, "si", "ninguno", 0),
    (5.5, 2, 4, "no", "dolor de cabeza", 3),
    (6.5, 3, 6, "no", "ninguno", 0),
    (4.5, 2, 2, "no", "cansancio", 4),
    (7.0, 3, 7, "si", "ninguno", 0),
    (5.0, 3, 3, "no", "dolor de cabeza", 5),
    (8.0, 3, 6, "si", "ninguno", 0),
    (6.0, 3, 5, "si", "ninguno", 0),
    (5.5, 2, 4, "no", "falta de concentración", 3),
    (7.0, 3, 6, "no", "ninguno", 0),
    (7.5, 3, 5, "si", "cansancio", 2),
    (6.5, 3, 4, "si", "ninguno", 0),
]


def leer_registros():
    """Lee el CSV y regresa un DataFrame. Si no existe o está vacío, regresa uno vacío."""
    if not ARCHIVO_CSV.exists():
        return pd.DataFrame(columns=COLUMNAS)
    try:
        df = pd.read_csv(ARCHIVO_CSV, dtype={"fecha": str}, encoding="utf-8-sig")
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=COLUMNAS)
    return df.reindex(columns=COLUMNAS)


def guardar_registros(df):
    """Escribe el DataFrame completo en el CSV (crea la carpeta si hace falta)."""
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    # utf-8-sig hace que Excel muestre bien los acentos
    df.to_csv(ARCHIVO_CSV, index=False, encoding="utf-8-sig")


def _juntar(df, filas):
    """Agrega filas (lista de diccionarios) a un DataFrame."""
    nuevas = pd.DataFrame(filas, columns=COLUMNAS)
    if df.empty:
        return nuevas
    return pd.concat([df, nuevas], ignore_index=True)


def agregar_registro(registro):
    """Guarda un registro. Si ya había uno con esa fecha, lo reemplaza.

    Regresa True si reemplazó uno existente, False si era nuevo.
    """
    df = leer_registros()
    reemplazo = registro["fecha"] in df["fecha"].values
    df = df[df["fecha"] != registro["fecha"]]
    df = _juntar(df, [registro])
    guardar_registros(df)
    return reemplazo


def cargar_ejemplo():
    """Agrega 14 días de datos simulados. Regresa cuántos días agregó."""
    df = leer_registros()

    # Se quitan ejemplos anteriores para no duplicarlos
    df = df[df["ejemplo"] != "si"]
    fechas_usadas = set(df["fecha"])

    hoy = date.today()
    filas = []
    for i, (sueno, comidas, agua, ejercicio, sintoma, intensidad) in enumerate(DATOS_EJEMPLO):
        fecha = (hoy - timedelta(days=len(DATOS_EJEMPLO) - i)).isoformat()
        if fecha in fechas_usadas:
            continue  # se conserva el registro real de esa fecha
        filas.append({
            "fecha": fecha,
            "sintoma": sintoma,
            "intensidad": intensidad,
            "sueno": sueno,
            "comidas": comidas,
            "agua": agua,
            "ejercicio": ejercicio,
            "ejemplo": "si",
        })

    if filas:
        df = _juntar(df, filas)
    guardar_registros(df)
    return len(filas)

"""Análisis de los registros con pandas: resumen y detección de patrones simples."""

# Para detectar patrones se necesitan al menos este número de días en cada grupo
MIN_DIAS = 3
# Total mínimo de registros para intentar comparar
MIN_REGISTROS = MIN_DIAS * 2
# Diferencia (en puntos de porcentaje) para considerar que hay un posible patrón
DIFERENCIA_PATRON = 20

# Cada condición: (texto si se cumple, texto si no se cumple, función que
# recibe el DataFrame y regresa True/False por cada día)
CONDICIONES = [
    ("duermes menos de 6 horas", "duermes 6 horas o más", lambda df: df["sueno"] < 6),
    ("tomas menos de 4 vasos de agua", "tomas 4 vasos o más", lambda df: df["agua"] < 4),
    ("comes menos de 3 veces al día", "comes 3 veces o más", lambda df: df["comidas"] < 3),
    ("no haces ejercicio", "haces ejercicio", lambda df: df["ejercicio"] == "no"),
]


def porcentaje_con_sintoma(df):
    """Porcentaje de días (del DataFrame dado) en los que hubo algún síntoma."""
    if df.empty:
        return 0
    return round((df["sintoma"] != "ninguno").mean() * 100)


def sintoma_mas_comun(df):
    """Síntoma que más se repite en esos días, o None si no hubo ninguno."""
    con_sintoma = df[df["sintoma"] != "ninguno"]["sintoma"]
    if con_sintoma.empty:
        return None
    return con_sintoma.mode().iloc[0]


def resumen(df):
    """Promedios generales de los registros (regresa un diccionario)."""
    return {
        "dias": len(df),
        "dias_con_sintoma": int((df["sintoma"] != "ninguno").sum()),
        "sueno_promedio": round(df["sueno"].mean(), 1),
        "comidas_promedio": round(df["comidas"].mean(), 1),
        "agua_promedio": round(df["agua"].mean(), 1),
        "dias_ejercicio": int((df["ejercicio"] == "si").sum()),
    }


def detectar_patrones(df):
    """Compara los días que cumplen cada condición contra los que no.

    Regresa una lista de diccionarios (uno por condición con datos suficientes).
    """
    resultados = []
    for texto_cumple, texto_no_cumple, condicion in CONDICIONES:
        mascara = condicion(df)       # True en los días que cumplen la condición
        cumplen = df[mascara]
        no_cumplen = df[~mascara]

        # Si hay muy pocos días en algún grupo, no se puede comparar
        if len(cumplen) < MIN_DIAS or len(no_cumplen) < MIN_DIAS:
            continue

        p_cumple = porcentaje_con_sintoma(cumplen)
        p_no_cumple = porcentaje_con_sintoma(no_cumplen)

        resultados.append({
            "cumple": texto_cumple,
            "no_cumple": texto_no_cumple,
            "n_cumple": len(cumplen),
            "n_no_cumple": len(no_cumplen),
            "p_cumple": p_cumple,
            "p_no_cumple": p_no_cumple,
            "sintoma_comun": sintoma_mas_comun(cumplen),
            "es_patron": (p_cumple - p_no_cumple) >= DIFERENCIA_PATRON,
        })
    return resultados

"""Recomendaciones básicas de hábitos según los patrones detectados.

Son sugerencias generales, nunca diagnósticos.
"""

# Una recomendación para cada condición definida en analisis.CONDICIONES
RECOMENDACIONES = {
    "duermes menos de 6 horas": (
        "Intenta dormir al menos 7 horas esta semana. Fija una hora para acostarte "
        "y evita las pantallas un rato antes de dormir."
    ),
    "tomas menos de 4 vasos de agua": (
        "Intenta tomar agua a lo largo del día. Tener una botella cerca mientras "
        "estudias ayuda a no olvidarlo."
    ),
    "comes menos de 3 veces al día": (
        "Intenta no saltarte comidas. Aunque sea algo ligero, comer a tus horas "
        "puede ayudarte a sentirte mejor."
    ),
    "no haces ejercicio": (
        "Intenta moverte un poco cada día, aunque sea una caminata corta o "
        "estirarte entre sesiones de estudio."
    ),
}


def generar_recomendaciones(patrones):
    """Recibe la lista de patrones y regresa una lista de (situación, consejo).

    Solo usa los patrones claros, empezando por el que más diferencia muestra.
    """
    claros = [p for p in patrones if p["es_patron"]]
    claros.sort(key=lambda p: p["p_cumple"] - p["p_no_cumple"], reverse=True)
    return [(p["cumple"], RECOMENDACIONES[p["cumple"]]) for p in claros]
