from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dominio.empleado import Empleado


class Departamento:
    MIN_NOMBRE = 2
    MAX_NOMBRE = 80

    def __init__(self, nombre: str, id: int | None = None, empleados: list["Empleado"] | None = None):
        self.id = id
        self.nombre = nombre
        self._empleados: list["Empleado"] = []
        if empleados:
            for emp in empleados:
                self.agregar_empleado(emp)

    @staticmethod
    def validar_nombre(nombre: str) -> str:
        if not isinstance(nombre, str):
            raise ValueError("El nombre del departamento debe ser texto.")
        nombre_limpio = nombre.strip()
        if not (Departamento.MIN_NOMBRE <= len(nombre_limpio) <= Departamento.MAX_NOMBRE):
            raise ValueError(
                f"El nombre del departamento debe tener entre {Departamento.MIN_NOMBRE} y {Departamento.MAX_NOMBRE} caracteres."
            )
        return nombre_limpio

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = self.validar_nombre(valor)

    @property
    def empleados(self) -> tuple["Empleado", ...]:
        return tuple(self._empleados)

    def cantidad_empleados(self) -> int:
        return len(self._empleados)

    def agregar_empleado(self, empleado: "Empleado") -> bool:
        from dominio.empleado import Empleado

        if not isinstance(empleado, Empleado):
            raise ValueError("Solo se pueden agregar objetos de tipo Empleado.")
        if empleado in self._empleados:
            return False

        departamento_actual = getattr(empleado, "departamento", None)
        if departamento_actual is not None and departamento_actual is not self:
            return False

        self._empleados.append(empleado)
        if hasattr(empleado, "departamento"):
            empleado.departamento = self
        if self.id is not None and hasattr(empleado, "departamento_id"):
            empleado.departamento_id = self.id
        return True

    def remover_empleado(self, empleado: "Empleado") -> bool:
        if empleado not in self._empleados:
            return False
        self._empleados.remove(empleado)
        if getattr(empleado, "departamento", None) is self:
            empleado.departamento = None
        if hasattr(empleado, "departamento_id") and getattr(empleado, "departamento_id", None) == self.id:
            empleado.departamento_id = None
        return True