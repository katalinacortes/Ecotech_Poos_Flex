import sys


def leer_password(mensaje: str = "Contraseña: ") -> str:
    """Lee una contraseña mostrando un asterisco (*) por cada carácter escrito."""
    return _leer_linea(mensaje, inicial="", ocultar=True)


def leer_con_valor(mensaje: str, valor_actual: str) -> str:
    """Lee un texto que aparece ya escrito con el valor actual, para editarlo en la misma línea.

    Con la tecla de retroceso se borra y se escribe el nuevo valor; con Enter se confirma.
    """
    return _leer_linea(mensaje, inicial=valor_actual or "", ocultar=False).strip()


def _leer_linea(mensaje: str, inicial: str, ocultar: bool) -> str:
    print(mensaje, end="", flush=True)

    # Si la entrada no es una terminal (por ejemplo, redirigida), se lee normal.
    # Una línea vacía conserva el valor inicial.
    if not sys.stdin.isatty():
        if inicial:
            print(inicial, end="", flush=True)
        linea = sys.stdin.readline().rstrip("\r\n")
        print()
        return linea or inicial

    caracteres = list(inicial)
    print(("*" * len(caracteres)) if ocultar else inicial, end="", flush=True)

    try:
        import msvcrt  # Windows
    except ImportError:
        return _leer_linea_posix(caracteres, ocultar)

    while True:
        tecla = msvcrt.getwch()
        if tecla in ("\r", "\n"):  # Enter
            print()
            return "".join(caracteres)
        if tecla == "\x03":  # Ctrl+C
            print()
            raise KeyboardInterrupt
        if tecla == "\b":  # Retroceso: borra el último carácter
            if caracteres:
                caracteres.pop()
                print("\b \b", end="", flush=True)
        elif tecla in ("\x00", "\xe0"):  # Teclas especiales (flechas, F1...): se ignoran
            msvcrt.getwch()
        else:
            caracteres.append(tecla)
            print("*" if ocultar else tecla, end="", flush=True)


def _leer_linea_posix(caracteres: list[str], ocultar: bool) -> str:
    import termios
    import tty

    descriptor = sys.stdin.fileno()
    configuracion_original = termios.tcgetattr(descriptor)
    try:
        tty.setraw(descriptor)
        while True:
            tecla = sys.stdin.read(1)
            if tecla in ("\r", "\n"):
                break
            if tecla == "\x03":
                raise KeyboardInterrupt
            if tecla in ("\x7f", "\b"):
                if caracteres:
                    caracteres.pop()
                    sys.stdout.write("\b \b")
            elif tecla == "\x1b":  # Secuencias de flechas: se ignoran
                sys.stdin.read(2)
            else:
                caracteres.append(tecla)
                sys.stdout.write("*" if ocultar else tecla)
            sys.stdout.flush()
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, configuracion_original)
        print()
    return "".join(caracteres)
