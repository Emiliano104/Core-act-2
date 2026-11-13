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


def filtrar_por_sintoma(df, sintoma):
    """Regresa solo los días con ese síntoma. Con "Todos" regresa todos los días."""
    if sintoma == "Todos":
        return df
    return df[df["sintoma"] == sintoma]


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
