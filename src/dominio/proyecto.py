from datetime import date


class Proyecto:
    MIN_NOMBRE = 2
    MAX_NOMBRE = 100

    def __init__(
        self,
        nombre_proyecto: str,
        descripcion: str = "",
        fecha_de_inicio: date | None = None,
        id: int | None = None,
    ):
        self.id = id
        self.nombre_proyecto = nombre_proyecto
        self.descripcion = descripcion
        self.fecha_de_inicio = fecha_de_inicio

    @staticmethod
    def validar_nombre_proyecto(nombre: str) -> str:
        if not isinstance(nombre, str):
            raise ValueError("El nombre del proyecto debe ser texto.")
        nombre_limpio = nombre.strip()
        if not (Proyecto.MIN_NOMBRE <= len(nombre_limpio) <= Proyecto.MAX_NOMBRE):
            raise ValueError(
                f"El nombre del proyecto debe tener entre {Proyecto.MIN_NOMBRE} y {Proyecto.MAX_NOMBRE} caracteres."
            )
        return nombre_limpio

    @property
    def nombre_proyecto(self) -> str:
        return self._nombre_proyecto

    @nombre_proyecto.setter
    def nombre_proyecto(self, valor: str) -> None:
        self._nombre_proyecto = self.validar_nombre_proyecto(valor)

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValueError("La descripción debe ser texto.")
        self._descripcion = valor.strip()

    @property
    def fecha_de_inicio(self) -> date | None:
        return self._fecha_de_inicio

    @fecha_de_inicio.setter
    def fecha_de_inicio(self, valor: date | None) -> None:
        if valor is not None and not isinstance(valor, date):
            raise ValueError("La fecha de inicio debe ser una fecha válida o None.")
        self._fecha_de_inicio = valor

    def mostrar_informaciones(self) -> str:
        fecha_texto = (
            self.fecha_de_inicio.isoformat()
            if self.fecha_de_inicio is not None
            else "Sin fecha"
        )
        return (
            f"ID: {self.id} | Proyecto: {self.nombre_proyecto} | "
            f"Inicio: {fecha_texto} | Descripción: {self.descripcion}"
        )