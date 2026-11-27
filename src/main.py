import os

from persistencia.crear_bd import crear_tablas
from presentacion.menu_consola import MenuConsola


def limpiar_pantalla() -> None:
    if os.name == "nt":
        os.system("")  # Activa las secuencias ANSI en la consola de Windows
    # \033[H = cursor al inicio, \033[2J = borra la pantalla, \033[3J = borra el historial (scroll)
    print("\033[H\033[2J\033[3J", end="", flush=True)


def main() -> None:
    limpiar_pantalla()
    crear_tablas()
    menu = MenuConsola()
    try:
        menu.ejecutar()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma finalizado.")


if __name__ == "__main__":
    main()
