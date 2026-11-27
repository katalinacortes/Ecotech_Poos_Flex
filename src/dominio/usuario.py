# En dominio/usuario.py
class Usuario:
    ROLES_VALIDOS = ("admin", "empleado")

    def __init__(
        self,
        nombre_usuario: str,
        password_hash: str,
        empleado_id: int,
        rol: str = "empleado",
        id: int | None = None,
    ):
        self.id = id
        self.nombre_usuario = self.normalizar_usuario(nombre_usuario)
        self.password_hash = password_hash
        self.empleado_id = empleado_id
        self.rol = self.validar_rol(rol)

    @classmethod
    def validar_rol(cls, rol: str) -> str:
        if not isinstance(rol, str):
            raise ValueError("El rol debe ser un texto.")
        limpio = rol.strip().lower()
        if limpio not in cls.ROLES_VALIDOS:
            raise ValueError(f"Rol no válido '{rol}'. Usa 'admin' o 'empleado'.")
        return limpio

    @staticmethod
    def normalizar_usuario(nombre_usuario: str) -> str:
        if not isinstance(nombre_usuario, str):
            raise ValueError("El nombre de usuario debe ser un texto.")
        limpio = nombre_usuario.strip().lower()
        if len(limpio) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres.")
        return limpio

    @staticmethod
    def validar_clave(clave_plana: str) -> str:
        if not isinstance(clave_plana, str) or len(clave_plana) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres.")
        return clave_plana
