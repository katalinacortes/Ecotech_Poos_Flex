from persistencia.crear_bd import crear_tablas
from presentacion.menu_consola import MenuConsola


def main() -> None:
    crear_tablas()
    menu = MenuConsola()
    menu.ejecutar()


if __name__ == "__main__":
    main()