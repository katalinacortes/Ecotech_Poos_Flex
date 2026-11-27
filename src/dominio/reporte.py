from datetime import date


class Reporte:
    def __init__(
        self,
        titulo: str,
        items: list | tuple | None = None,
        formato: str = "TEXTO",
        fecha_generacion: date | None = None,
        id: int | None = None,
    ):
        self.id = id
        self.titulo = titulo
        self.items = list(items) if items is not None else []
        self.formato = formato
        self.fecha_generacion = fecha_generacion if fecha_generacion is not None else date.today()

    def _formatear_encabezado(self) -> str:
        return (
            f"=== {self.titulo} ===\n"
            f"Formato: {self.formato} | Fecha: {self.fecha_generacion.isoformat()} | "
            f"Total registros: {len(self.items)}"
        )

    def _formatear_cuerpo(self) -> str:
        if not self.items:
            return "Sin registros para mostrar."
        return "\n".join(f"- {item}" for item in self.items)

    def generar(self) -> str:
        return f"{self._formatear_encabezado()}\n{self._formatear_cuerpo()}"


class ReportePDF(Reporte):
    def __init__(
        self,
        titulo: str,
        items: list | tuple | None = None,
        fecha_generacion: date | None = None,
        id: int | None = None,
    ):
        super().__init__(
            titulo=titulo,
            items=items,
            formato="PDF",
            fecha_generacion=fecha_generacion,
            id=id,
        )

    def generar(self) -> str:
        return f"[EXPORTACIÓN PDF]\n{self._formatear_encabezado()}\n{self._formatear_cuerpo()}"


class ReporteExcel(Reporte):
    def __init__(
        self,
        titulo: str,
        items: list | tuple | None = None,
        fecha_generacion: date | None = None,
        id: int | None = None,
    ):
        super().__init__(
            titulo=titulo,
            items=items,
            formato="EXCEL",
            fecha_generacion=fecha_generacion,
            id=id,
        )

    def generar(self) -> str:
        return f"[EXPORTACIÓN EXCEL]\n{self._formatear_encabezado()}\n{self._formatear_cuerpo()}"