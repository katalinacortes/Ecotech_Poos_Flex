from datetime import date
from getpass import getpass
import json
import urllib.error
import urllib.request

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from persistencia.conexion import abrir_conexion, obtener_motor
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from presentacion.menu_empleado import MenuEmpleado
from servicios.autenticacion import ServicioAutenticacion


class MenuConsola:
    def __init__(self) -> None:
        self.servicio_autenticacion = ServicioAutenticacion()

    @staticmethod
    def _leer_texto(mensaje: str, permitir_vacio: bool = False) -> str:
        while True:
            valor = input(mensaje).strip()
            if valor or permitir_vacio:
                return valor
            print("El campo no puede quedar vacío.")

    @staticmethod
    def _leer_entero(mensaje: str) -> int:
        while True:
            texto = input(mensaje).strip()
            try:
                return int(texto)
            except ValueError:
                print("Ingresa un número entero válido.")

    @staticmethod
    def _leer_flotante(mensaje: str) -> float:
        while True:
            texto = input(mensaje).strip().replace(",", ".")
            try:
                return float(texto)
            except ValueError:
                print("Ingresa un número válido.")

    @staticmethod
    def _leer_fecha_opcional(mensaje: str) -> date | None:
        while True:
            texto = input(mensaje).strip()
            if not texto:
                return None
            try:
                return date.fromisoformat(texto)
            except ValueError:
                print("Usa el formato YYYY-MM-DD o deja vacío.")

    @staticmethod
    def _obtener_o_crear_empleado_por_correo(correo: str, rol: str) -> int:
        for emp in EmpleadoDAO.listar():
            if getattr(emp, "correo", "").strip().lower() == correo.lower():
                return emp.id

        nombre_base = correo.split("@")[0] if "@" in correo else correo
        etiqueta_rol = "Admin" if rol == "admin" else "Empleado"
        emp = Empleado(
            nombre=f"{etiqueta_rol} {nombre_base}",
            correo=correo,
            salario=500000.0,
        )
        EmpleadoDAO.insertar(emp)
        return emp.id

    def _invocar_registro(self, correo: str, password: str, empleado_id: int, rol: str) -> None:
        candidatos = [
            "registrar",
            "registrar_usuario",
            "crear_usuario",
            "registro",
            "alta_usuario",
        ]
        for nombre_metodo in candidatos:
            metodo = getattr(self.servicio_autenticacion, nombre_metodo, None)
            if callable(metodo):
                for args in (
                    (correo, password, empleado_id, rol),
                    (correo, correo, password, empleado_id, rol),
                    (correo, password, rol),
                ):
                    try:
                        metodo(*args)
                        return
                    except TypeError:
                        continue

        # Fallback directo con bcrypt si el servicio no expone un método de registro estándar
        import bcrypt

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        motor = obtener_motor()
        marcador = "?" if motor == "sqlite" else "%s"

        cursor.execute(
            f"""
            INSERT INTO usuario (nombre_usuario, password_hash, rol, empleado_id)
            VALUES ({marcador}, {marcador}, {marcador}, {marcador});
            """,
            (correo, password_hash, rol, empleado_id),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

    def _registrar_usuario(self) -> None:
        print("\n=== REGISTRO DE USUARIO ===")
        correo = self._leer_texto("Correo electrónico: ").lower()
        if "@" not in correo or "." not in correo.split("@")[-1]:
            print("Ingresa un correo electrónico válido.")
            return

        password = getpass("Contraseña (mínimo 4 caracteres): ")
        if len(password) < 4:
            print("La contraseña debe tener al menos 4 caracteres.")
            return

        while True:
            print("Selecciona el rol:")
            print("1. Empleado")
            print("2. Administrador")
            op_rol = input("Opción (1 o 2): ").strip()
            if op_rol == "1":
                rol = "empleado"
                break
            if op_rol == "2":
                rol = "admin"
                break
            print("Ingresa 1 para Empleado o 2 para Administrador.")

        try:
            empleado_id = self._obtener_o_crear_empleado_por_correo(correo, rol)
            self._invocar_registro(correo, password, empleado_id, rol)
            print(f"Registro completado como '{rol}' con ID de empleado: {empleado_id}.")
            print("Ahora puedes iniciar sesión con tu correo, tu ID y tu contraseña.")
        except ValueError as err:
            print(f"Error de validación: {err}")
        except Exception as err:
            print(f"No se pudo registrar el usuario: {err}")

    def _buscar_usuario_por_correo(self, correo: str):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        motor = obtener_motor()
        marcador = "?" if motor == "sqlite" else "%s"

        # Busca por correo en empleado o directamente en nombre_usuario
        cursor.execute(
            f"""
            SELECT u.id, u.nombre_usuario, u.password_hash, u.rol, u.empleado_id
            FROM usuario u
            LEFT JOIN empleado e ON u.empleado_id = e.id
            WHERE LOWER(u.nombre_usuario) = {marcador} OR LOWER(e.correo) = {marcador}
            LIMIT 1;
            """,
            (correo.lower(), correo.lower()),
        )
        fila = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not fila:
            return None

        class _UsuarioSesion:
            pass

        u = _UsuarioSesion()
        u.id = fila[0]
        u.nombre_usuario = fila[1]
        u.password_hash = fila[2]
        u.rol = fila[3] or "empleado"
        u.empleado_id = fila[4]
        return u

    def _verificar_password(self, usuario, password: str) -> bool:
        # Intenta usar el servicio de autenticación si tiene método de verificación
        for nombre_metodo in ("verificar_password", "validar_password", "iniciar_sesion"):
            metodo = getattr(self.servicio_autenticacion, nombre_metodo, None)
            if callable(metodo) and nombre_metodo != "iniciar_sesion":
                try:
                    return bool(metodo(password, getattr(usuario, "password_hash", "")))
                except TypeError:
                    continue

        password_hash = getattr(usuario, "password_hash", "")
        if not password_hash:
            return False

        try:
            import bcrypt

            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except Exception:
            return password == password_hash

    def iniciar_login(self):
        while True:
            print("\n=== ACCESO AL SISTEMA ===")
            print("1. Iniciar sesión")
            print("2. Registrarse")
            print("0. Salir")
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                correo = self._leer_texto("Correo electrónico: ").lower()
                id_ingresado = self._leer_entero("ID: ")
                password = getpass("Contraseña: ")

                usuario = self._buscar_usuario_por_correo(correo)
                if usuario is None:
                    print("No existe un usuario registrado con ese correo.")
                    continue

                # Acepta tanto el ID del empleado asociado como el ID del usuario si coincide
                if id_ingresado not in (usuario.empleado_id, usuario.id):
                    print("El ID no coincide con el correo ingresado.")
                    continue

                if not self._verificar_password(usuario, password):
                    print("Contraseña incorrecta. Intenta de nuevo.")
                    continue

                rol_legible = "Administrador" if usuario.rol.lower() == "admin" else "Empleado"
                print(f"Sesión iniciada como {rol_legible} ({correo}).")
                return usuario

            elif opcion == "2":
                self._registrar_usuario()

            elif opcion == "0":
                return None

            else:
                print("Opción no válida.")

    def ejecutar(self) -> None:
        usuario = self.iniciar_login()
        if not usuario:
            return

        rol = getattr(usuario, "rol", "empleado").lower()
        if rol == "admin":
            self._menu_admin()
        else:
            MenuEmpleado(
                usuario.empleado_id,
                usuario=usuario,
                servicio_autenticacion=self.servicio_autenticacion,
            ).iniciar()

    # ==================== CAMINO ADMIN ====================
    def _menu_admin(self) -> None:
        while True:
            print("\n--- MENÚ ADMINISTRADOR ---")
            print("1. CRUD Empleados")
            print("2. CRUD Departamentos")
            print("3. CRUD Proyectos")
            print("0. Salir")
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                self._crud_empleados()
            elif opcion == "2":
                self._crud_departamentos()
            elif opcion == "3":
                self._crud_proyectos()
            elif opcion == "0":
                print("Cerrando sesión...")
                break
            else:
                print("Opción no válida.")

    def _crud_empleados(self) -> None:
        while True:
            print("\n[CRUD EMPLEADOS]")
            print("1. Crear empleado")
            print("2. Listar empleados")
            print("3. Buscar empleado por ID")
            print("4. Actualizar empleado")
            print("5. Eliminar empleado")
            print("0. Volver")
            op = input("Opción: ").strip()

            try:
                if op == "1":
                    nombre = self._leer_texto("Nombre: ")
                    correo = self._leer_texto("Correo: ")
                    salario = self._leer_flotante("Salario: ")
                    fecha_ini = self._leer_fecha_opcional("Fecha inicio (YYYY-MM-DD, opcional): ")
                    emp = Empleado(
                        nombre=nombre,
                        correo=correo,
                        salario=salario,
                        fecha_inicio_contrato=fecha_ini,
                    )
                    EmpleadoDAO.insertar(emp)
                    print(f"Empleado creado con ID {emp.id}.")
                elif op == "2":
                    empleados = EmpleadoDAO.listar()
                    if not empleados:
                        print("No hay empleados registrados.")
                    for e in empleados:
                        print(f"ID: {e.id} | {e.nombre} | {e.correo} | Salario: {e.salario}")
                elif op == "3":
                    id_emp = self._leer_entero("ID empleado: ")
                    e = EmpleadoDAO.buscar_por_id(id_emp)
                    if e is None:
                        print("Empleado no encontrado.")
                    else:
                        print(f"ID: {e.id} | Nombre: {e.nombre} | Correo: {e.correo} | Salario: {e.salario}")
                elif op == "4":
                    id_emp = self._leer_entero("ID empleado a actualizar: ")
                    e = EmpleadoDAO.buscar_por_id(id_emp)
                    if e is None:
                        print("Empleado no encontrado.")
                        continue
                    e.nombre = self._leer_texto("Nuevo nombre: ")
                    e.correo = self._leer_texto("Nuevo correo: ")
                    e.salario = self._leer_flotante("Nuevo salario: ")
                    EmpleadoDAO.actualizar(e)
                    print("Empleado actualizado.")
                elif op == "5":
                    id_emp = self._leer_entero("ID empleado a eliminar: ")
                    eliminados = EmpleadoDAO.eliminar(id_emp)
                    print("Empleado eliminado." if eliminados else "No existía ese ID.")
                elif op == "0":
                    break
                else:
                    print("Opción no válida.")
            except ValueError as err:
                print(f"Error de validación: {err}")
            except Exception as err:
                print(f"Error en base de datos: {err}")

    def _crud_departamentos(self) -> None:
        while True:
            print("\n[CRUD DEPARTAMENTOS]")
            print("1. Crear departamento")
            print("2. Listar departamentos")
            print("3. Buscar departamento por ID")
            print("4. Actualizar departamento")
            print("5. Eliminar departamento")
            print("0. Volver")
            op = input("Opción: ").strip()

            try:
                if op == "1":
                    nombre = self._leer_texto("Nombre del departamento: ")
                    depto = Departamento(nombre=nombre)
                    DepartamentoDAO.insertar(depto)
                    print(f"Departamento creado con ID {depto.id}.")
                elif op == "2":
                    deptos = DepartamentoDAO.listar()
                    if not deptos:
                        print("No hay departamentos registrados.")
                    for d in deptos:
                        print(f"ID: {d.id} | Nombre: {d.nombre}")
                elif op == "3":
                    id_d = self._leer_entero("ID departamento: ")
                    d = DepartamentoDAO.buscar_con_empleados(id_d)
                    if d is None:
                        print("Departamento no encontrado.")
                    else:
                        print(f"ID: {d.id} | Nombre: {d.nombre} | Empleados: {len(d.empleados)}")
                elif op == "4":
                    id_d = self._leer_entero("ID departamento a actualizar: ")
                    d = DepartamentoDAO.buscar_con_empleados(id_d)
                    if d is None:
                        print("Departamento no encontrado.")
                        continue
                    d.nombre = self._leer_texto("Nuevo nombre: ")
                    DepartamentoDAO.actualizar(d)
                    print("Departamento actualizado.")
                elif op == "5":
                    id_d = self._leer_entero("ID departamento a eliminar: ")
                    eliminados = DepartamentoDAO.eliminar(id_d)
                    print("Departamento eliminado." if eliminados else "No existía ese ID.")
                elif op == "0":
                    break
                else:
                    print("Opción no válida.")
            except ValueError as err:
                print(f"Error de validación: {err}")
            except Exception as err:
                print(f"Error en base de datos: {err}")

    def _crud_proyectos(self) -> None:
        while True:
            print("\n[CRUD PROYECTOS]")
            print("1. Crear proyecto")
            print("2. Listar proyectos")
            print("3. Buscar proyecto por ID")
            print("4. Actualizar proyecto")
            print("5. Eliminar proyecto")
            print("0. Volver")
            op = input("Opción: ").strip()

            try:
                if op == "1":
                    nombre = self._leer_texto("Nombre del proyecto: ")
                    desc = self._leer_texto("Descripción: ", permitir_vacio=True)
                    fecha_ini = self._leer_fecha_opcional("Fecha inicio (YYYY-MM-DD, opcional): ")
                    proy = Proyecto(
                        nombre_proyecto=nombre,
                        descripcion=desc,
                        fecha_de_inicio=fecha_ini,
                    )
                    ProyectoDAO.insertar(proy)
                    print(f"Proyecto creado con ID {proy.id}.")
                elif op == "2":
                    proyectos = ProyectoDAO.listar()
                    if not proyectos:
                        print("No hay proyectos registrados.")
                    for p in proyectos:
                        print(p.mostrar_informaciones())
                elif op == "3":
                    id_p = self._leer_entero("ID proyecto: ")
                    p = ProyectoDAO.buscar_por_id(id_p)
                    print(p.mostrar_informaciones() if p else "Proyecto no encontrado.")
                elif op == "4":
                    id_p = self._leer_entero("ID proyecto a actualizar: ")
                    p = ProyectoDAO.buscar_por_id(id_p)
                    if p is None:
                        print("Proyecto no encontrado.")
                        continue
                    p.nombre_proyecto = self._leer_texto("Nuevo nombre: ")
                    p.descripcion = self._leer_texto("Nueva descripción: ", permitir_vacio=True)
                    p.fecha_de_inicio = self._leer_fecha_opcional("Nueva fecha inicio (YYYY-MM-DD, opcional): ")
                    ProyectoDAO.actualizar(p)
                    print("Proyecto actualizado.")
                elif op == "5":
                    id_p = self._leer_entero("ID proyecto a eliminar: ")
                    eliminados = ProyectoDAO.eliminar(id_p)
                    print("Proyecto eliminado." if eliminados else "No existía ese ID.")
                elif op == "0":
                    break
                else:
                    print("Opción no válida.")
            except ValueError as err:
                print(f"Error de validación: {err}")
            except Exception as err:
                print(f"Error en base de datos: {err}")