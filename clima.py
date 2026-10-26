"""
Funciones y modelos para consultar información meteorológica utilizando
la API pública de Open-Meteo.

Este módulo permite:

- Buscar ciudades mediante geocodificación.
- Obtener el clima actual.
- Obtener el pronóstico diario.
- Traducir códigos meteorológicos WMO a descripciones legibles.
- Gestionar errores de comunicación con los servicios externos.
"""

from dataclasses import dataclass
import requests
from datetime import date

url_geocoding = "https://geocoding-api.open-meteo.com/v1/search"
url_pronostico = "https://api.open-meteo.com/v1/forecast"
segundos_de_espera = 10

# codigo WMO -> (descripcion, emoji)
codigos_wmo = {
    0: ("Despejado", "☀️"),
    1: ("Mayormente despejado", "🌤️"),
    2: ("Parcialmente nublado", "⛅"),
    3: ("Nublado", "☁️"),
    45: ("Niebla", "🌫️"),
    48: ("Niebla con escarcha", "🌫️"),
    51: ("Llovizna ligera", "🌦️"),
    53: ("Llovizna moderada", "🌦️"),
    55: ("Llovizna intensa", "🌧️"),
    56: ("Llovizna helada ligera", "🌧️"),
    57: ("Llovizna helada intensa", "🌧️"),
    61: ("Lluvia ligera", "🌦️"),
    63: ("Lluvia moderada", "🌧️"),
    65: ("Lluvia fuerte", "🌧️"),
    66: ("Lluvia helada ligera", "🌧️"),
    67: ("Lluvia helada fuerte", "🌧️"),
    71: ("Nevada ligera", "🌨️"),
    73: ("Nevada moderada", "🌨️"),
    75: ("Nevada intensa", "❄️"),
    77: ("Granos de nieve", "❄️"),
    80: ("Chubascos ligeros", "🌦️"),
    81: ("Chubascos moderados", "🌧️"),
    82: ("Chubascos violentos", "⛈️"),
    85: ("Chubascos de nieve ligeros", "🌨️"),
    86: ("Chubascos de nieve fuertes", "❄️"),
    95: ("Tormenta eléctrica", "⛈️"),
    96: ("Tormenta con granizo", "⛈️"),
    99: ("Tormenta con granizo fuerte", "⛈️"),
}


class ErrorClima(Exception):
    """Excepción personalizada para errores relacionados con el clima."""
    pass


@dataclass
class Ciudad:
    """
    Representa una ciudad obtenida desde el servicio de geocodificación.

    Attributes:
        nombre: Nombre de la ciudad.
        pais: País al que pertenece.
        region: Provincia, estado o región administrativa.
        latitud: Latitud geográfica.
        longitud: Longitud geográfica.
    """

    nombre: str
    pais: str
    region: str
    latitud: float
    longitud: float

    @property
    def etiqueta(self):
        """
        Devuelve una representación legible de la ubicación.

        Returns:
            str: Cadena formada por ciudad, región y país.
        """

        partes = [self.nombre, self.region, self.pais]
        return ", ".join(p for p in partes if p)


@dataclass
class ClimaActual:
    """
    Información meteorológica actual de una ciudad.

    Attributes:
        temperatura: Temperatura actual en °C.
        sensacion: Sensación térmica en °C.
        humedad: Humedad relativa (%).
        viento: Velocidad del viento (km/h).
        codigo: Código meteorológico WMO.
        es_de_dia: Indica si es de día.
    """

    temperatura: float
    sensacion: float
    humedad: int
    viento: float
    codigo: int
    es_de_dia: bool

    @property
    def descripcion(self):
        return describir_codigo(self.codigo)

    @property
    def emoji(self):
        if self.codigo in (0, 1) and not self.es_de_dia:
            return "🌙"
        return emoji_de_codigo(self.codigo)


@dataclass
class DiaPronostico:
    """
    Representa el pronóstico meteorológico de un día.

    Attributes:
        fecha: Fecha del pronóstico.
        minima: Temperatura mínima prevista.
        maxima: Temperatura máxima prevista.
        probabilidad_lluvia: Probabilidad máxima de precipitaciones.
        codigo: Código meteorológico WMO.
    """

    fecha: date
    minima: float
    maxima: float
    probabilidad_lluvia: int
    codigo: int

    @property
    def descripcion(self):
        return describir_codigo(self.codigo)

    @property
    def emoji(self):
        return emoji_de_codigo(self.codigo)


def describir_codigo(codigo: int) -> str:
    """
    Convierte un código WMO en una descripción legible.

    Args:
        codigo: Código meteorológico WMO.

    Returns:
        str: Descripción asociada al código.
    """
    d, _ = codigos_wmo.get(codigo, ("Desconocido", "❓"))
    return d


def emoji_de_codigo(codigo: int) -> str:
    """
    Convierte un código WMO en un emoji representativo.

    Args:
        codigo: Código meteorológico WMO.

    Returns:
        str: Emoji asociado al código.
    """
    _, e = codigos_wmo.get(codigo, ("Desconocido", "❓"))
    return e


def _pedir_json(url: str, parametros: dict) -> dict:
    """
    Realiza una petición HTTP y devuelve la respuesta JSON.

    Args:
        url: URL del servicio.
        parametros: Parámetros enviados en la petición.

    Returns:
        dict: Respuesta JSON del servicio.

    Raises:
        ErrorClima: Si ocurre un problema de conexión,
            tiempo de espera o formato de respuesta.
    """
    try:
        r = requests.get(url, params=parametros, timeout=segundos_de_espera)
        r.raise_for_status()
        return r.json()
    except requests.Timeout as error:
        raise ErrorClima(
            "El servidor tardó demasiado en responder.") from error
    except requests.ConnectionError as error:
        raise ErrorClima(
            "No hay conexión a internet o el servicio no responde.") from error
    except requests.HTTPError as error:
        resp = error.response
        cod = resp.status_code if resp is not None else "?"
        raise ErrorClima(
            f"El servicio respondió con un error HTTP {cod}.") from error
    except requests.RequestException as error:
        raise ErrorClima(f"Falló la consulta al servicio: {error}") from error
    except ValueError as error:
        raise ErrorClima(
            "La respuesta del servicio no tenía un formato válido.") from error


def buscar_ciudades(nombre: str, cantidad: int = 5) -> list['Ciudad']:
    """
    Busca ciudades por nombre utilizando la API de Open-Meteo.

    Args:
        nombre: Nombre de la ciudad a buscar.
        cantidad: Cantidad máxima de resultados.

    Returns:
        list[Ciudad]: Lista de ciudades encontradas.

    Raises:
        ErrorClima: Si el nombre está vacío o falla la consulta.
    """
    
    nombre = nombre.strip()
    if not nombre:
        raise ErrorClima("Tenés que escribir el nombre de una ciudad.")

    datos = _pedir_json(url_geocoding, {
                        "name": nombre, "count": cantidad, "language": "es", "format": "json"})

    lista = []
    for res in datos.get("results", []):
        lista.append(Ciudad(
            nombre=res.get("name", nombre),
            pais=res.get("country", ""),
            region=res.get("admin1", ""),
            latitud=float(res["latitude"]),
            longitud=float(res["longitude"]),
        ))
    return lista


def obtener_clima(ciudad: 'Ciudad') -> 'ClimaActual':
    """
    Obtiene el clima actual para una ciudad.

    Args:
        ciudad: Instancia de Ciudad.

    Returns:
        ClimaActual: Datos meteorológicos actuales.

    Raises:
        ErrorClima: Si la respuesta del servicio es inválida.
    """
    
    datos = _pedir_json(url_pronostico, {
        "latitude": ciudad.latitud,
        "longitude": ciudad.longitud,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code,is_day",
        "timezone": "auto",
    })

    try:
        a = datos["current"]
        return ClimaActual(
            temperatura=float(a["temperature_2m"]),
            sensacion=float(a["apparent_temperature"]),
            humedad=int(a["relative_humidity_2m"]),
            viento=float(a["wind_speed_10m"]),
            codigo=int(a["weather_code"]),
            es_de_dia=bool(a["is_day"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ErrorClima(
            "La respuesta del servicio no trae el clima actual.") from error


def obtener_pronostico(ciudad: 'Ciudad', dias: int = 4) -> list['DiaPronostico']:
    """
    Obtiene el pronóstico diario de una ciudad.

    Args:
        ciudad: Ciudad a consultar.
        dias: Cantidad de días de pronóstico.

    Returns:
        list[DiaPronostico]: Pronóstico diario.

    Raises:
        ErrorClima: Si los datos recibidos son inválidos.
    """
    
    dias = max(1, min(dias, 16))
    datos = _pedir_json(url_pronostico, {
        "latitude": ciudad.latitud,
        "longitude": ciudad.longitud,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": dias,
        "timezone": "auto",
    })

    try:
        diario = datos["daily"]
        lista = []
        for i, texto_fecha in enumerate(diario["time"]):
            prob = diario["precipitation_probability_max"][i]
            lista.append(DiaPronostico(
                fecha=date.fromisoformat(texto_fecha),
                minima=float(diario["temperature_2m_min"][i]),
                maxima=float(diario["temperature_2m_max"][i]),
                probabilidad_lluvia=int(prob or 0),
                codigo=int(diario["weather_code"][i]),
            ))
        return lista
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise ErrorClima(
            "La respuesta del servicio no trae el pronóstico diario.") from error
