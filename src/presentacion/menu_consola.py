from datetime import date

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from presentacion.entrada import leer_password
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

    def _registrar_usuario(self) -> None:
        print("\n=== REGISTRO DE USUARIO ===")
        nombre = self._leer_texto("Nombre: ")
        correo = self._leer_texto("Nombre de usuario: ").lower()
        if "@" not in correo or "." not in correo.split("@")[-1]:
            print("El nombre de usuario debe ser un correo electrónico válido.")
            return

        password = leer_password("Contraseña (mínimo 4 caracteres): ")
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
            self.servicio_autenticacion.registrar_por_correo(
                correo=correo,
                password=password,
                rol=rol,
                nombre=nombre,
            )
            print(f"Registro completado como '{rol}'.")
            print("Ahora puedes iniciar sesión con tu nombre de usuario y tu contraseña.")
        except ValueError as err:
            print(f"Error de validación: {err}")
        except Exception as err:
            print(f"No se pudo registrar el usuario: {err}")

    def iniciar_login(self):
        while True:
            print("\n=== ACCESO AL SISTEMA ===")
            print("1. Iniciar sesión")
            print("2. Registrarse")
            print("0. Salir")
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                correo = self._leer_texto("Nombre de usuario: ").lower()
                password = leer_password("Contraseña: ")

                usuario = self.servicio_autenticacion.iniciar_sesion(correo, password)
                if usuario is None:
                    print("Nombre de usuario o contraseña incorrectos. Intenta de nuevo.")
                    continue

                rol_legible = "Administrador" if usuario.rol == "admin" else "Empleado"
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