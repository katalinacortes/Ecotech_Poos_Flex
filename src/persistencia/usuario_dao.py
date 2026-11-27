from dominio.usuario import Usuario
from persistencia.conexion import abrir_conexion, obtener_motor


class UsuarioDAO:
    @staticmethod
    def _marcador() -> str:
        return "?" if obtener_motor() == "sqlite" else "%s"

    @classmethod
    def _fila_a_usuario(cls, fila: tuple) -> Usuario:
        id_usuario, nombre_usuario, password_hash, empleado_id, rol = fila
        return Usuario(
            nombre_usuario=nombre_usuario,
            password_hash=password_hash,
            empleado_id=empleado_id,
            rol=rol or "empleado",
            id=id_usuario,
        )

    @classmethod
    def insertar(cls, usuario: Usuario) -> Usuario:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"""
                INSERT INTO usuario (nombre_usuario, password_hash, empleado_id, rol)
                VALUES ({m}, {m}, {m}, {m})
            """
            cursor.execute(
                sql,
                (
                    usuario.nombre_usuario,
                    usuario.password_hash,
                    usuario.empleado_id,
                    usuario.rol,
                ),
            )
            usuario.id = cursor.lastrowid
            conexion.commit()
            return usuario
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_por_usuario(cls, nombre_usuario: str) -> Usuario | None:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            usuario_limpio = Usuario.normalizar_usuario(nombre_usuario)
            m = cls._marcador()
            sql = f"""
                SELECT id, nombre_usuario, password_hash, empleado_id, rol
                FROM usuario
                WHERE nombre_usuario = {m}
            """
            cursor.execute(sql, (usuario_limpio,))
            fila = cursor.fetchone()
            if fila is None:
                return None
            return cls._fila_a_usuario(fila)
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_por_empleado_id(cls, empleado_id: int) -> Usuario | None:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"""
                SELECT id, nombre_usuario, password_hash, empleado_id, rol
                FROM usuario
                WHERE empleado_id = {m}
            """
            cursor.execute(sql, (empleado_id,))
            fila = cursor.fetchone()
            if fila is None:
                return None
            return cls._fila_a_usuario(fila)
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def listar(cls) -> list[Usuario]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            sql = """
                SELECT id, nombre_usuario, password_hash, empleado_id, rol
                FROM usuario
                ORDER BY id
            """
            cursor.execute(sql)
            filas = cursor.fetchall()
            return [cls._fila_a_usuario(fila) for fila in filas]
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar_hash(cls, id_usuario: int, nuevo_hash: str) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"UPDATE usuario SET password_hash = {m} WHERE id = {m}"
            cursor.execute(sql, (nuevo_hash, id_usuario))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def eliminar(cls, id_usuario: int) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"DELETE FROM usuario WHERE id = {m}"
            cursor.execute(sql, (id_usuario,))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()