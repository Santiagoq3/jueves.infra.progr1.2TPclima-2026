## 👥 Integrantes

- 
- Agustin Maldonado
- Thiago Di Gianni
- Santiago Quipildor

# 🌦️ Clima por consola

Programa de consola que muestra el **clima actual** y el **pronóstico de los
próximos 4 días** de cualquier ciudad del mundo, con tablas y colores en la
terminal.

Los datos se piden en vivo a la API pública de
[Open-Meteo](https://open-meteo.com), que es **gratuita y no necesita API key**.

## ✨ Qué hace

- Busca la ciudad por nombre y, si hay varias coincidencias (por ejemplo
  "Rosario" en Argentina, Filipinas o Colombia), muestra una tabla para elegir.
- Muestra temperatura, sensación térmica, humedad, viento y estado del cielo.
- Muestra una tabla con el pronóstico de los próximos días: mínima, máxima y
  probabilidad de lluvia.
- Colorea las temperaturas según lo frías o calurosas que sean.
- Permite consultar varias ciudades seguidas hasta que el usuario decide salir.

```text
┌───────────────── Rosario, Provincia de Santa Fe, Argentina ─────────────────┐
│         Temperatura  21.1 °C                                                │
│   Sensación térmica  21.6 °C                                                │
│             Humedad  72 %                                                   │
│              Viento  9.8 km/h                                               │
│               Cielo  ⛅  Parcialmente nublado                               │
└──────────────────────────────── ahora mismo ────────────────────────────────┘

                           Próximos días
┌─────────┬───────┬───────────────────────┬───────┬───────┬────────┐
│ Día     │ Fecha │ Cielo                 │  Mín. │  Máx. │ Lluvia │
├─────────┼───────┼───────────────────────┼───────┼───────┼────────┤
│ Viernes │ 23/10 │ 🌦️  Chubascos ligeros │ 17 °C │ 22 °C │   59 % │
│ Sábado  │ 24/10 │ ☁️  Nublado           │ 13 °C │ 18 °C │    9 % │
└─────────┴───────┴───────────────────────┴───────┴───────┴────────┘
```

## 📦 Librerías de terceros

| Librería | Para qué se usa |
|----------|-----------------|
| [`requests`](https://pypi.org/project/requests/) | Hacer las consultas HTTP a la API de Open-Meteo. |
| [`rich`](https://pypi.org/project/rich/) | Dibujar los paneles, las tablas, los colores y el spinner de carga. |

## 📁 Estructura

```text
entregable/
├── .venv/              ← entorno virtual (no se sube a Git)
├── .gitignore
├── README.md
├── requirements.txt
├── main.py             ← punto de entrada: coordina y maneja los errores
├── clima.py            ← módulo propio: consulta la API y arma los datos
└── vista.py            ← módulo propio: todo lo que se muestra en pantalla
```

La idea es separar responsabilidades: `clima.py` **no imprime nada** y
`vista.py` **no consulta nada**. `main.py` los une.

## 🚀 Instalación

Hace falta **Python 3.10 o superior**.

```bash
# 1. Clonar el repositorio y entrar a la carpeta
git clone <URL-DEL-REPOSITORIO>
cd entregable

# 2. Crear el entorno virtual
python -m venv .venv

# 3. Activarlo
.venv\Scripts\activate         # Windows
source .venv/bin/activate      # Linux / Mac

# 4. Instalar las dependencias
pip install -r requirements.txt
```

> ⚠️ **Windows / PowerShell:** si no deja activar el entorno, ejecutar una vez:
> `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

## ▶️ Cómo se ejecuta

```bash
python main.py
```

Después se escribe el nombre de una ciudad y se presiona Enter. Para salir,
se deja la respuesta **vacía** y se presiona Enter (o `Ctrl+C`).

## 🛡️ Manejo de errores

El programa no se cae: todos los casos problemáticos se capturan con
`try / except` y se muestran como un mensaje en rojo.

| Situación | Qué pasa |
|-----------|----------|
| No hay internet | "No hay conexión a internet o el servicio no responde." |
| El servidor tarda demasiado | Corta a los 10 segundos y avisa. |
| El servidor responde con error HTTP | Muestra el código (404, 500, etc.). |
| La ciudad no existe | "No se encontró ninguna ciudad llamada '...'." |
| Nombre de ciudad vacío | Sale del programa de forma ordenada. |
| `Ctrl+C` | Se despide sin mostrar el traceback. |


