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

# Síntomas que se pueden registrar
SINTOMAS = ["ninguno", "dolor de cabeza", "cansancio", "falta de concentración", "otro"]

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
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
        return pd.DataFrame(columns=COLUMNAS)
    return _limpiar(df)


def _limpiar(df):
    """Corrige los tipos de las columnas y descarta las filas incompletas o dañadas.

    Así, si alguien edita el CSV a mano y deja una celda vacía o con letras donde
    va un número, la aplicación no se rompe: simplemente ignora esa fila.
    """
    df = df.reindex(columns=COLUMNAS)
    for columna in ["intensidad", "sueno", "comidas", "agua"]:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")
    df = df.dropna(subset=["fecha", "sintoma", "sueno", "comidas", "agua"])

    df = df.assign(
        intensidad=df["intensidad"].fillna(0).astype(int),
        comidas=df["comidas"].astype(int),
        agua=df["agua"].astype(int),
        ejercicio=df["ejercicio"].where(df["ejercicio"].isin(["si", "no"]), "no"),
        ejemplo=df["ejemplo"].where(df["ejemplo"].isin(["si", "no"]), "no"),
    )
    return df.reset_index(drop=True)


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


def eliminar_registro(fecha):
    """Elimina el registro de una fecha. Regresa cuántos registros se eliminaron."""
    df = leer_registros()
    restantes = df[df["fecha"] != fecha]
    guardar_registros(restantes)
    return len(df) - len(restantes)


def borrar_ejemplos():
    """Elimina todos los registros de ejemplo. Regresa cuántos se eliminaron."""
    df = leer_registros()
    restantes = df[df["ejemplo"] != "si"]
    guardar_registros(restantes)
    return len(df) - len(restantes)


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
