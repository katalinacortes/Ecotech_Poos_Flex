import getpass

from dominio.usuario import Usuario
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.usuario_dao import UsuarioDAO
from servicios.autenticacion import ServicioAutenticacion

_servicio = ServicioAutenticacion()


def iniciar_sesion() -> dict | None:
    nombre = input("Usuario: ").strip()
    clave = getpass.getpass("Contraseña: ")
    usuario = _servicio.iniciar_sesion(nombre, clave)
    if usuario is None:
        print("Usuario o contraseña incorrectos.")
        return None
    print(f"Sesión iniciada como {usuario.nombre_usuario}.")
    return {
        "id": usuario.id,
        "empleado_id": usuario.empleado_id,
        "nombre_usuario": usuario.nombre_usuario,
        "rol": usuario.rol,
    }


def crear_cuenta_usuario() -> dict | None:
    try:
        empleado_id = int(input("ID del empleado: ").strip())
    except ValueError:
        print("El ID del empleado debe ser un número.")
        return None

    if EmpleadoDAO.buscar_por_id(empleado_id) is None:
        print("No existe un empleado con ese ID.")
        return None

    nombre_usuario = input("Nuevo nombre de usuario: ").strip()
    clave = getpass.getpass("Nueva contraseña: ")

    try:
        nombre_normalizado = Usuario.normalizar_usuario(nombre_usuario)
        if UsuarioDAO.buscar_por_usuario(nombre_normalizado) is not None:
            print("Ese nombre de usuario ya existe.")
            return None

        password_hash = _servicio._hashear_password(clave)
        nuevo_usuario = Usuario(
            nombre_usuario=nombre_normalizado,
            password_hash=password_hash,
            empleado_id=empleado_id,
        )
        guardado = UsuarioDAO.insertar(nuevo_usuario)
        print(f"Usuario '{guardado.nombre_usuario}' creado correctamente.")
        return {
            "id": guardado.id,
            "empleado_id": guardado.empleado_id,
            "nombre_usuario": guardado.nombre_usuario,
        }
    except (TypeError, ValueError) as error:
        print(f"Error al crear usuario: {error}")
        return None


def solicitar_login() -> dict | None:
    while True:
        print("\n=== ACCESO ECOTECH ===")
        print("1. Iniciar sesión")
        print("2. Crear usuario")
        print("0. Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            sesion = iniciar_sesion()
            if sesion is not None:
                return sesion
        elif opcion == "2":
            sesion = crear_cuenta_usuario()
            if sesion is not None:
                return sesion
        elif opcion == "0":
            return None
        else:
            print("Opción no válida.")