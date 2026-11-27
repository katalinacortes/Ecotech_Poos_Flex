from datetime import date
import json
import urllib.error
import urllib.request

from dominio.registro_tiempo import RegistroTiempo
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO


class MenuEmpleado:
    def __init__(self, empleado_id: int) -> None:
        self.empleado_id = empleado_id

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
            print("4. Consultar API")
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
            nuevo_nombre = self._leer_texto("Nuevo nombre: ")
            nuevo_correo = self._leer_texto("Nuevo correo: ")
            emp.nombre = nuevo_nombre
            emp.correo = nuevo_correo
            EmpleadoDAO.actualizar(emp)
            print("Perfil actualizado correctamente.")
        except ValueError as err:
            print(f"Error de validación: {err}")
        except Exception as err:
            print(f"Error al actualizar perfil: {err}")

    def _registrar_tiempo(self) -> None:
        try:
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