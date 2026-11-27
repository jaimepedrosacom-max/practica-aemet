"""
Práctica #2 - Requests + AEMET
Obtiene la climatología diaria de octubre de 2019 en la estación
"MADRID, CIUDAD UNIVERSITARIA" usando la API de AEMET OpenData.
"""

import json
import os
import sys

import requests

BASE_URL = "https://opendata.aemet.es/opendata/api"
ESTACION_BUSCADA = "MADRID, CIUDAD UNIVERSITARIA"
FECHA_INI = "2019-10-01T00:00:00UTC"
FECHA_FIN = "2019-10-30T23:59:59UTC"


def leer_api_key():
    """Lee la API key de la variable de entorno AEMET_API_KEY o del fichero .env"""
    api_key = os.environ.get("AEMET_API_KEY")
    if api_key:
        return api_key.strip()

    ruta_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(ruta_env):
        with open(ruta_env, encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if linea.startswith("AEMET_API_KEY="):
                    return linea.split("=", 1)[1].strip().strip('"').strip("'")

    sys.exit(
        "ERROR: no se encuentra la API key.\n"
        "Define la variable de entorno AEMET_API_KEY o créa un fichero .env con:\n"
        "AEMET_API_KEY=tu_api_key"
    )


def pedir_datos(url, api_key):
    """
    La API de AEMET responde en dos pasos:
      1) La petición al endpoint devuelve un JSON con el campo 'datos' (una URL).
      2) Esa URL contiene los datos reales.
    Esta función hace los dos pasos y devuelve los datos ya parseados.
    """
    # Paso 1: petición al endpoint pasando la API key como query string
    respuesta = requests.get(url, params={"api_key": api_key}, timeout=30)
    print(f"  GET {url} -> {respuesta.status_code}")
    respuesta.raise_for_status()

    cuerpo = respuesta.json()
    if cuerpo.get("estado") != 200:
        sys.exit(f"ERROR de la API: {cuerpo.get('estado')} - {cuerpo.get('descripcion')}")

    url_datos = cuerpo["datos"]
    print(f"  Link a los datos: {url_datos}")

    # Paso 2: descarga del fichero de datos
    respuesta_datos = requests.get(url_datos, timeout=60)
    print(f"  GET datos -> {respuesta_datos.status_code}")
    respuesta_datos.raise_for_status()

    # AEMET sirve los ficheros en ISO-8859-15, no en UTF-8
    respuesta_datos.encoding = "ISO-8859-15"
    return json.loads(respuesta_datos.text)


def buscar_idema(estaciones, nombre):
    """Busca el 'indicativo' (idema) de una estación por su nombre."""
    for estacion in estaciones:
        if estacion.get("nombre", "").strip().upper() == nombre:
            return estacion["indicativo"], estacion
    sys.exit(f"ERROR: no se ha encontrado la estación '{nombre}'")


def main():
    api_key = leer_api_key()

    # ----- Paso 1: inventario de estaciones -----
    print("\n[1] Inventario de estaciones")
    url_inventario = f"{BASE_URL}/valores/climatologicos/inventarioestaciones/todasestaciones"
    estaciones = pedir_datos(url_inventario, api_key)
    print(f"  Estaciones recibidas: {len(estaciones)}")

    # ----- Paso 2: localizar MADRID, CIUDAD UNIVERSITARIA -----
    print(f"\n[2] Buscando la estación '{ESTACION_BUSCADA}'")
    idema, estacion = buscar_idema(estaciones, ESTACION_BUSCADA)
    print(f"  indicativo (idema): {idema}")
    print(f"  provincia: {estacion.get('provincia')} | altitud: {estacion.get('altitud')} m")

    # ----- Paso 3: climatologías diarias de octubre de 2019 -----
    print(f"\n[3] Climatologías diarias {FECHA_INI} -> {FECHA_FIN}")
    url_clima = (
        f"{BASE_URL}/valores/climatologicos/diarios/datos"
        f"/fechaini/{FECHA_INI}/fechafin/{FECHA_FIN}/estacion/{idema}"
    )
    climatologia = pedir_datos(url_clima, api_key)
    print(f"  Días recibidos: {len(climatologia)}")

    # ----- Resultados -----
    print("\n[4] Resumen (fecha | tmed | tmin | tmax | prec)")
    print("-" * 52)
    for dia in climatologia:
        print(
            f"  {dia.get('fecha')} | "
            f"{dia.get('tmed', '-'):>5} | "
            f"{dia.get('tmin', '-'):>5} | "
            f"{dia.get('tmax', '-'):>5} | "
            f"{dia.get('prec', '-'):>5}"
        )

    salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "climatologia_octubre_2019.json")
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(climatologia, f, ensure_ascii=False, indent=2)
    print(f"\nDatos guardados en: {salida}")


if __name__ == "__main__":
    main()
