from datetime import date


class RegistroTiempo:
    MIN_HORAS = 0.5
    MAX_HORAS = 24.0
    MAX_DESCRIPCION = 200

    def __init__(
        self,
        fecha: date,
        horas_trabajadas: float,
        descripcion_de_tareas: str,
        empleado_id: int | None = None,
        proyecto_id: int | None = None,
        id: int | None = None,
    ):
        self.id = id
        self.empleado_id = empleado_id
        self.proyecto_id = proyecto_id
        self.fecha = fecha
        self.horas_trabajadas = horas_trabajadas
        self.descripcion_de_tareas = descripcion_de_tareas

    @classmethod
    def validar_horas_trabajadas(cls, horas: float) -> float:
        if isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise ValueError("Las horas trabajadas deben ser un número.")
        horas_float = float(horas)
        if not (cls.MIN_HORAS <= horas_float <= cls.MAX_HORAS):
            raise ValueError(
                f"Las horas trabajadas deben estar entre {cls.MIN_HORAS} y {cls.MAX_HORAS}."
            )
        return horas_float

    @property
    def fecha(self) -> date:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: date) -> None:
        if not isinstance(valor, date):
            raise ValueError("La fecha del registro debe ser un objeto date válido.")
        self._fecha = valor

    @property
    def horas_trabajadas(self) -> float:
        return self._horas_trabajadas

    @horas_trabajadas.setter
    def horas_trabajadas(self, valor: float) -> None:
        self._horas_trabajadas = self.validar_horas_trabajadas(valor)

    @property
    def descripcion_de_tareas(self) -> str:
        return self._descripcion_de_tareas

    @descripcion_de_tareas.setter
    def descripcion_de_tareas(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValueError("La descripción de tareas debe ser texto.")
        texto_limpio = valor.strip()
        if not texto_limpio:
            raise ValueError("La descripción de tareas no puede estar vacía.")
        if len(texto_limpio) > self.MAX_DESCRIPCION:
            raise ValueError(
                f"La descripción de tareas no puede superar los {self.MAX_DESCRIPCION} caracteres."
            )
        self._descripcion_de_tareas = texto_limpio

    def mostrar_resumen(self) -> str:
        return (
            f"ID: {self.id} | Fecha: {self.fecha.isoformat()} | "
            f"Horas: {self.horas_trabajadas} | Tareas: {self.descripcion_de_tareas}"
        )