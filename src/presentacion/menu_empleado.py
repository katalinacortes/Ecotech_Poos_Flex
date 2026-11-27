from datetime import date
import json
import urllib.error
import urllib.request

from dominio.registro_tiempo import RegistroTiempo
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from persistencia.usuario_dao import UsuarioDAO
from presentacion.entrada import leer_con_valor, leer_password
from servicios.autenticacion import ServicioAutenticacion


class MenuEmpleado:
    def __init__(self, empleado_id: int, usuario=None, servicio_autenticacion=None) -> None:
        self.empleado_id = empleado_id
        self.usuario = usuario
        self.servicio_autenticacion = servicio_autenticacion or ServicioAutenticacion()

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

    def iniciar(self) -> None:
        while True:
            print("\n--- MENÚ EMPLEADO ---")
            print("1. Mi perfil")
            print("2. Editar perfil")
            print("3. Registro de tiempo")
            print("4. Indicadores Económicos (API)")
            print("5. Cambiar contraseña")
            print("0. Salir")
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                self._ver_perfil()
            elif opcion == "2":
                self._editar_perfil()
            elif opcion == "3":
                self._registrar_tiempo()
            elif opcion == "4":
                self._consultar_api()
            elif opcion == "5":
                self._cambiar_password()
            elif opcion == "0":
                print("Cerrando sesión...")
                break
            else:
                print("Opción no válida.")

    def _ver_perfil(self) -> None:
        emp = EmpleadoDAO.buscar_por_id(self.empleado_id)
        if emp is None:
            print("No se encontró tu ficha de empleado.")
            return
        print("\n=== MI PERFIL ===")
        print(f"ID: {emp.id}")
        print(f"Nombre: {emp.nombre}")
        print(f"Correo: {emp.correo}")
        print(f"Salario: {emp.salario}")
        print(f"Fecha inicio contrato: {emp.fecha_inicio_contrato}")

    def _editar_perfil(self) -> None:
        emp = EmpleadoDAO.buscar_por_id(self.empleado_id)
        if emp is None:
            print("No se encontró tu ficha de empleado.")
            return
        try:
            print("\n=== EDITAR PERFIL ===")
            nuevo_nombre = leer_con_valor("Nombre del empleado: ", emp.nombre)
            nuevo_usuario = leer_con_valor("Nombre de usuario: ", emp.correo).lower()

            correo_anterior = emp.correo
            if nuevo_usuario and nuevo_usuario != correo_anterior:
                if "@" not in nuevo_usuario or "." not in nuevo_usuario.split("@")[-1]:
                    print("El nombre de usuario debe ser un correo electrónico válido.")
                    return
                otro_empleado = EmpleadoDAO.buscar_por_correo(nuevo_usuario)
                if UsuarioDAO.buscar_por_usuario(nuevo_usuario) is not None or (
                    otro_empleado is not None and otro_empleado.id != emp.id
                ):
                    print("Ese usuario ya está en uso.")
                    return

            if nuevo_nombre:
                emp.nombre = nuevo_nombre
            if nuevo_usuario:
                emp.correo = nuevo_usuario
            EmpleadoDAO.actualizar(emp)

            # El correo es el usuario para iniciar sesión: se actualiza también la cuenta.
            usuario = self._obtener_usuario()
            if usuario is not None and emp.correo != correo_anterior:
                UsuarioDAO.actualizar_nombre_usuario(usuario.id, emp.correo)
                usuario.nombre_usuario = emp.correo
            print("Perfil actualizado correctamente.")
        except ValueError as err:
            print(f"Error de validación: {err}")
        except Exception as err:
            print(f"Error al actualizar perfil: {err}")

    def _obtener_usuario(self):
        if self.usuario is None:
            self.usuario = UsuarioDAO.buscar_por_empleado_id(self.empleado_id)
        return self.usuario

    def _cambiar_password(self) -> None:
        usuario = self._obtener_usuario()
        if usuario is None:
            print("No se encontró tu cuenta de usuario.")
            return

        print("\n=== CAMBIAR CONTRASEÑA ===")
        nueva = leer_password("Nueva contraseña: ")
        repetida = leer_password("Repita contraseña: ")

        if nueva != repetida:
            print("Las contraseñas no coinciden. No se realizaron cambios.")
            return

        try:
            self.servicio_autenticacion.cambiar_password(usuario.id, nueva)
            print("Contraseña actualizada correctamente.")
        except ValueError as err:
            print(f"Error de validación: {err}")
        except Exception as err:
            print(f"Error al cambiar la contraseña: {err}")

    def _registrar_tiempo(self) -> None:
        try:
            proyectos = ProyectoDAO.listar()
            if not proyectos:
                print("No hay proyectos registrados. Pide a un administrador que cree uno.")
                return

            print("\n=== PROYECTOS DISPONIBLES ===")
            for p in proyectos:
                print(f"  {p.id}. {p.nombre_proyecto}")

            id_proyecto = self._leer_entero("ID del proyecto: ")
            proyecto = ProyectoDAO.buscar_por_id(id_proyecto)
            if proyecto is None:
                print("El proyecto indicado no existe.")
                return
            fecha_reg = self._leer_fecha_opcional("Fecha (YYYY-MM-DD, vacío = hoy): ") or date.today()
            horas = self._leer_flotante("Horas trabajadas: ")
            tareas = self._leer_texto("Descripción de tareas: ")

            reg = RegistroTiempo(
                fecha=fecha_reg,
                horas_trabajadas=horas,
                descripcion_de_tareas=tareas,
                empleado_id=self.empleado_id,
                proyecto_id=id_proyecto,
            )
            RegistroTiempoDAO.insertar(reg)
            print(f"Registro de tiempo guardado (ID {reg.id}).")
        except ValueError as err:
            print(f"Error de validación: {err}")
        except Exception as err:
            print(f"Error al guardar registro: {err}")

    def _consultar_api(self) -> None:
        url = "https://mindicador.cl/api"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EcoTechApp/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            uf = data.get("uf", {}).get("valor")
            dolar = data.get("dolar", {}).get("valor")
            print("\n=== INDICADORES ECONÓMICOS (API) ===")
            print(f"UF: {uf} | Dólar observado: {dolar}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
            print(f"No se pudo consultar la API externa: {err}")