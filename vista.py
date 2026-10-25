"""
Interfaz de usuario de consola basada en Rich.

Este módulo se encarga de:

- Mostrar información meteorológica.
- Solicitar datos al usuario.
- Renderizar tablas y paneles.
- Mostrar mensajes de error y advertencia.
"""

from rich.console import Console
from rich.table import Table
from rich.prompt import IntPrompt, Prompt
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

consola = Console()

dias_semana = ["Lunes", "Martes", "Miércoles",
               "Jueves", "Viernes", "Sábado", "Domingo"]


def color_de_temperatura(temp):
    """
    Determina el color asociado a una temperatura.

    Args:
        temp: Temperatura en grados Celsius.

    Returns:
        str: Nombre del color para Rich.
    """

    if temp <= 0:
        return "bright_cyan"
    if temp <= 12:
        return "cyan"
    if temp <= 22:
        return "green"
    if temp <= 30:
        return "yellow"
    return "red"


def mostrar_bienvenida():
    """
    Muestra la pantalla de bienvenida de la aplicación.
    """

    titulo = Text("🌦️  CLIMA POR CONSOLA", style="bold white")
    sub = Text("Datos en vivo de Open-Meteo", style="dim")
    consola.print(Panel(Align.center(Text.assemble(
        titulo, "\n", sub)), border_style="blue", padding=(1, 4)))


def pedir_ciudad():
    """
    Solicita al usuario el nombre de una ciudad.

    Returns:
        str: Ciudad introducida por el usuario.
    """

    return Prompt.ask("\n[bold cyan]Ciudad[/] [dim](Enter vacío para salir)[/]", default="", show_default=False).strip()


def elegir_ciudad(ciudades):
    """
    Permite seleccionar una ciudad cuando existen varias coincidencias.

    Args:
        ciudades: Lista de ciudades encontradas.

    Returns:
        Ciudad: Ciudad seleccionada.
    """

    if len(ciudades) == 1:
        return ciudades[0]

    t = Table(title="Se encontró más de una ciudad", title_style="bold yellow")
    t.add_column("#", justify="right", style="bold cyan")
    t.add_column("Ubicación", style="white")
    t.add_column("Coordenadas", style="dim")

    for i, c in enumerate(ciudades, start=1):
        t.add_row(str(i), c.etiqueta, f"{c.latitud:.2f}, {c.longitud:.2f}")

    consola.print()
    consola.print(t)

    op = IntPrompt.ask("[bold cyan]Elegí una opción[/]", choices=[str(i)
                       for i in range(1, len(ciudades) + 1)], default=1)
    return ciudades[op - 1]


def indicador_carga(mensaje):
    return consola.status(f"[cyan]{mensaje}[/]", spinner="dots")




def mostrar_clima_actual(ciudad, clima):
    """
    Muestra el clima actual en formato enriquecido.

    Args:
        ciudad: Ciudad consultada.
        clima: Datos actuales del clima.
    """
    
    col = color_de_temperatura(clima.temperatura)

    g = Table.grid(padding=(0, 2))
    g.add_column(justify="right", style="dim")
    g.add_column(style="white")

    g.add_row("Temperatura", Text(
        f"{clima.temperatura:.1f} °C", style=f"bold {col}"))
    g.add_row("Sensación térmica", f"{clima.sensacion:.1f} °C")
    g.add_row("Humedad", f"{clima.humedad} %")
    g.add_row("Viento", f"{clima.viento:.1f} km/h")
    g.add_row("Cielo", f"{clima.emoji}  {clima.descripcion}")

    consola.print()
    consola.print(Panel(g, title=f"[bold]{ciudad.etiqueta}[/]",
                  subtitle="[dim]ahora mismo[/]", border_style=col, padding=(1, 3)))


def mostrar_pronostico(pronostico):
    """
    Muestra una tabla con el pronóstico de los próximos días.

    Args:
        pronostico: Lista de objetos DiaPronostico.
    """

    if not pronostico:
        return

    t = Table(title="Próximos días", title_style="bold white",
              border_style="blue", header_style="bold cyan")
    t.add_column("Día")
    t.add_column("Fecha", style="dim")
    t.add_column("Cielo")
    t.add_column("Mín.", justify="right")
    t.add_column("Máx.", justify="right")
    t.add_column("Lluvia", justify="right")

    for d in pronostico:
        mn = Text(f"{d.minima:.0f} °C", style=color_de_temperatura(d.minima))
        mx = Text(f"{d.maxima:.0f} °C", style=color_de_temperatura(d.maxima))
        t.add_row(dias_semana[d.fecha.weekday()], d.fecha.strftime(
            "%d/%m"), f"{d.emoji}  {d.descripcion}", mn, mx, f"{d.probabilidad_lluvia} %")

    consola.print()
    consola.print(t)


def mostrar_error(mensaje):
    consola.print(f"\n[bold red]✖ {mensaje}[/]")


def mostrar_aviso(mensaje):
    consola.print(f"\n[yellow]⚠ {mensaje}[/]")


def mostrar_despedida():
    consola.print("\n[bold blue]¡Hasta la próxima! 👋[/]\n")
