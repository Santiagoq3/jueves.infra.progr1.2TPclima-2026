from clima import ErrorClima, buscar_ciudades, obtener_clima, obtener_pronostico
import vista

dias_de_pronostico = 4


def consultar_y_mostrar(ciudad):
    with vista.indicador_carga(f"Consultando el clima de {ciudad.nombre}..."):
        clima_actual = obtener_clima(ciudad)
        pronostico = obtener_pronostico(ciudad, dias_de_pronostico)

    vista.mostrar_clima_actual(ciudad, clima_actual)
    vista.mostrar_pronostico(pronostico)


def procesar_busqueda(texto):
    with vista.indicador_carga(f"Buscando '{texto}'..."):
        ciudades = buscar_ciudades(texto)

    if not ciudades:
        vista.mostrar_aviso(
            f"No se encontró ninguna ciudad llamada '{texto}'.")
        return

    c = vista.elegir_ciudad(ciudades)
    consultar_y_mostrar(c)


def main():
    vista.mostrar_bienvenida()

    while True:
        try:
            texto = vista.pedir_ciudad()
            if not texto:
                break
            procesar_busqueda(texto)
        except ErrorClima as error:
            vista.mostrar_error(str(error))
        except (KeyboardInterrupt, EOFError):
            break

    vista.mostrar_despedida()


if __name__ == "__main__":
    main()
