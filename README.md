# Práctica #2 - Requests + AEMET

Operación de Modelos (MUIAAP) · Comillas ICAI

Obtiene la **climatología diaria de octubre de 2019** en la estación
*MADRID, CIUDAD UNIVERSITARIA* usando la API de [AEMET OpenData](https://opendata.aemet.es)
con la librería `requests`.

## Qué hace

La API de AEMET responde en **dos pasos**: la petición al endpoint devuelve un JSON con un
campo `datos` que contiene una URL, y es esa URL la que sirve los datos reales. El script
encadena los dos pasos en las dos llamadas que pide el enunciado:

1. **Inventario de estaciones** (`/valores/climatologicos/inventarioestaciones/todasestaciones`)
   para localizar el `indicativo` (idema) de la estación → **3194U**.
2. **Climatologías diarias** (`/valores/climatologicos/diarios/datos/...`) entre
   `2019-10-01T00:00:00UTC` y `2019-10-30T23:59:59UTC` para esa estación → **30 días**.

La API key se pasa como *query string* con la clave `api_key`, como indica la documentación.

Detalle a tener en cuenta: AEMET sirve los ficheros de datos en **ISO-8859-15**, no en UTF-8,
así que hay que fijar el encoding antes de parsear el JSON o los nombres con acentos fallan.

## Uso

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip3 install requests

cp .env.example .env        # y pega dentro tu API key
python aemet.py
```

La API key se lee de la variable de entorno `AEMET_API_KEY` o, si no está definida, del
fichero `.env`. Nunca se escribe en el código: `.env` está en el `.gitignore`.

Puedes pedir tu propia key en
<https://opendata.aemet.es/centrodedescargas/obtencionAPIKey>.

## Ficheros

| Fichero | Contenido |
|---|---|
| `aemet.py` | El script de la práctica |
| `resultados.txt` | Salida completa de la ejecución (las dos llamadas, el idema y los 30 días) |
| `climatologia_octubre_2019.json` | Datos descargados de la AEMET |

## Resultado

Estación `3194U` — MADRID, CIUDAD UNIVERSITARIA (provincia de Madrid, 664 m).
30 días de octubre de 2019, con temperatura media, mínima, máxima y precipitación.
El día más lluvioso fue el **19 de octubre, con 15,0 mm**; la máxima más alta, **29,8 °C el día 8**.
