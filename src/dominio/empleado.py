from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dominio.departamento import Departamento


class Empleado:
    MIN_SALARIO = 0.0

    def __init__(
        self,
        nombre: str,
        correo: str,
        salario: float = 0.0,
        fecha_inicio_contrato: date | str | None = None,
        departamento_id: int | None = None,
        departamento: "Departamento | None" = None,
        id: int | None = None,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.salario = salario
        self.fecha_inicio_contrato = fecha_inicio_contrato
        self._departamento: "Departamento | None" = None
        self._departamento_id: int | None = departamento_id

        if departamento is not None:
            self.departamento = departamento

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre del empleado no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip() or "@" not in valor:
            raise ValueError("El correo del empleado no es válido.")
        self._correo = valor.strip().lower()

    @property
    def salario(self) -> float:
        return self._salario

    @salario.setter
    def salario(self, valor: float) -> None:
        monto = float(valor)
        if monto < self.MIN_SALARIO:
            raise ValueError("El salario no puede ser negativo.")
        self._salario = monto

    @property
    def departamento(self) -> "Departamento | None":
        return self._departamento

    @departamento.setter
    def departamento(self, valor: "Departamento | None") -> None:
        self._departamento = valor
        if valor is not None and getattr(valor, "id", None) is not None:
            self._departamento_id = valor.id

    @property
    def departamento_id(self) -> int | None:
        if self._departamento is not None and getattr(self._departamento, "id", None) is not None:
            return self._departamento.id
        return self._departamento_id

    @departamento_id.setter
    def departamento_id(self, valor: int | None) -> None:
        self._departamento_id = valor