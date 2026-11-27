import bcrypt

from dominio.empleado import Empleado
from dominio.usuario import Usuario
from persistencia.conexion import abrir_conexion, marcador_parametro
from persistencia.empleado_dao import EmpleadoDAO


class ServicioAutenticacion:
    ROLES_VALIDOS = {"empleado", "admin"}

    @staticmethod
    def _hashear_password(password: str) -> str:
        if not password or len(password) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres.")
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _verificar_password(password: str, password_hash: str) -> bool:
        if not password or not password_hash:
            return False
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except Exception:
            return password == password_hash

    def _obtener_o_crear_empleado(self, correo: str, rol: str, empleado_id: int | None = None) -> Empleado:
        if empleado_id is not None:
            emp_por_id = EmpleadoDAO.buscar_por_id(empleado_id)
            if emp_por_id is not None:
                return emp_por_id

        emp_por_correo = EmpleadoDAO.buscar_por_correo(correo)
        if emp_por_correo is not None:
            return emp_por_correo

        prefijo = correo.split("@")[0] if "@" in correo else correo
        etiqueta = "Administrador" if rol == "admin" else "Empleado"
        nuevo_emp = Empleado(
            nombre=f"{etiqueta} {prefijo}",
            correo=correo,
            salario=500000.0,
        )
        return EmpleadoDAO.insertar(nuevo_emp)

    def registrar_por_correo(
        self,
        correo: str,
        password: str,
        rol: str = "empleado",
        empleado_id: int | None = None,
    ) -> Usuario:
        correo_limpio = correo.strip().lower()
        rol_limpio = (rol or "empleado").strip().lower()

        if rol_limpio not in self.ROLES_VALIDOS:
            rol_limpio = "empleado"

        if not correo_limpio or "@" not in correo_limpio or "." not in correo_limpio.split("@")[-1]:
            raise ValueError("Ingresa un correo electrónico válido.")

        password_hash = self._hashear_password(password)
        empleado = self._obtener_o_crear_empleado(correo_limpio, rol_limpio, empleado_id)

        p = marcador_parametro()
        conexion = abrir_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                f"SELECT id FROM usuario WHERE LOWER(nombre_usuario) = {p};",
                (correo_limpio,),
            )
            if cursor.fetchone():
                raise ValueError("Ya existe una cuenta registrada con ese correo.")

            cursor.execute(
                f"""
                INSERT INTO usuario (nombre_usuario, password_hash, rol, empleado_id)
                VALUES ({p}, {p}, {p}, {p});
                """,
                (correo_limpio, password_hash, rol_limpio, empleado.id),
            )
            usuario_id = cursor.lastrowid
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()

        return Usuario(
            id=usuario_id,
            nombre_usuario=correo_limpio,
            password_hash=password_hash,
            rol=rol_limpio,
            empleado_id=empleado.id,
        )

    # Alias por si alguna parte llama a registrar(...) o registrar_usuario(...)
    def registrar(
        self,
        correo_o_usuario: str,
        password: str,
        empleado_id_o_rol: int | str | None = None,
        rol: str = "empleado",
    ) -> Usuario:
        if isinstance(empleado_id_o_rol, int):
            return self.registrar_por_correo(
                correo=correo_o_usuario,
                password=password,
                rol=rol,
                empleado_id=empleado_id_o_rol,
            )
        if isinstance(empleado_id_o_rol, str):
            return self.registrar_por_correo(
                correo=correo_o_usuario,
                password=password,
                rol=empleado_id_o_rol,
            )
        return self.registrar_por_correo(
            correo=correo_o_usuario,
            password=password,
            rol=rol,
        )

    def registrar_usuario(
        self,
        correo_o_usuario: str,
        password: str,
        empleado_id_o_rol: int | str | None = None,
        rol: str = "empleado",
    ) -> Usuario:
        return self.registrar(correo_o_usuario, password, empleado_id_o_rol, rol)

    def iniciar_sesion_con_id(self, correo: str, id_ingresado: int, password: str) -> Usuario | None:
        correo_limpio = correo.strip().lower()
        p = marcador_parametro()
        conexion = abrir_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            f"""
            SELECT u.id, u.nombre_usuario, u.password_hash, u.rol, u.empleado_id
            FROM usuario u
            LEFT JOIN empleado e ON u.empleado_id = e.id
            WHERE LOWER(u.nombre_usuario) = {p} OR LOWER(e.correo) = {p}
            LIMIT 1;
            """,
            (correo_limpio, correo_limpio),
        )
        fila = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not fila:
            return None

        usuario = Usuario(
            id=fila[0],
            nombre_usuario=fila[1],
            password_hash=fila[2],
            rol=(fila[3] or "empleado").lower(),
            empleado_id=fila[4],
        )

        if id_ingresado not in (usuario.empleado_id, usuario.id):
            return None

        if not self._verificar_password(password, usuario.password_hash):
            return None

        return usuario

    def iniciar_sesion(self, correo_o_usuario: str, password: str) -> Usuario | None:
        identificador = correo_o_usuario.strip().lower()
        p = marcador_parametro()
        conexion = abrir_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            f"""
            SELECT u.id, u.nombre_usuario, u.password_hash, u.rol, u.empleado_id
            FROM usuario u
            LEFT JOIN empleado e ON u.empleado_id = e.id
            WHERE LOWER(u.nombre_usuario) = {p} OR LOWER(e.correo) = {p}
            LIMIT 1;
            """,
            (identificador, identificador),
        )
        fila = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not fila:
            return None

        usuario = Usuario(
            id=fila[0],
            nombre_usuario=fila[1],
            password_hash=fila[2],
            rol=(fila[3] or "empleado").lower(),
            empleado_id=fila[4],
        )

        if not self._verificar_password(password, usuario.password_hash):
            return None

        return usuario

    def cambiar_password(self, usuario_id: int, nueva_password: str) -> None:
        nuevo_hash = self._hashear_password(nueva_password)
        p = marcador_parametro()
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            f"UPDATE usuario SET password_hash = {p} WHERE id = {p};",
            (nuevo_hash, usuario_id),
        )
        conexion.commit()
        cursor.close()
        conexion.close()