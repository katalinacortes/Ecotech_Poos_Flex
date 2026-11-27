from datetime import date, datetime
from dominio.empleado import Empleado
from persistencia.conexion import abrir_conexion, obtener_motor


class EmpleadoDAO:
    @staticmethod
    def _marcador() -> str:
        return "?" if obtener_motor() == "sqlite" else "%s"

    @staticmethod
    def _convertir_fecha(valor) -> date | None:
        if valor is None:
            return None
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        return date.fromisoformat(str(valor))

    @classmethod
    def _fila_a_empleado(cls, fila: tuple) -> Empleado:
        id_empleado, nombre, correo, salario, fecha_inicio = fila
        return Empleado(
            nombre=nombre,
            correo=correo,
            salario=float(salario),
            fecha_inicio_contrato=cls._convertir_fecha(fecha_inicio),
            id=id_empleado,
        )

    @classmethod
    def insertar(cls, empleado: Empleado) -> Empleado:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            fecha_bd = (
                empleado.fecha_inicio_contrato.isoformat()
                if empleado.fecha_inicio_contrato is not None
                else None
            )
            sql = f"""
                INSERT INTO empleado (nombre, correo, salario, fecha_inicio_contrato)
                VALUES ({m}, {m}, {m}, {m})
            """
            cursor.execute(
                sql,
                (
                    empleado.nombre,
                    empleado.correo,
                    empleado.salario,
                    fecha_bd,
                ),
            )
            empleado.id = cursor.lastrowid
            conexion.commit()
            return empleado
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def listar(cls) -> list[Empleado]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            sql = """
                SELECT id, nombre, correo, salario, fecha_inicio_contrato
                FROM empleado
                ORDER BY id
            """
            cursor.execute(sql)
            filas = cursor.fetchall()
            return [cls._fila_a_empleado(fila) for fila in filas]
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_por_id(cls, id_empleado: int) -> Empleado | None:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"""
                SELECT id, nombre, correo, salario, fecha_inicio_contrato
                FROM empleado
                WHERE id = {m}
            """
            cursor.execute(sql, (id_empleado,))
            fila = cursor.fetchone()
            if fila is None:
                return None
            return cls._fila_a_empleado(fila)
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar(cls, empleado: Empleado) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            fecha_bd = (
                empleado.fecha_inicio_contrato.isoformat()
                if empleado.fecha_inicio_contrato is not None
                else None
            )
            sql = f"""
                UPDATE empleado
                SET nombre = {m}, correo = {m}, salario = {m}, fecha_inicio_contrato = {m}
                WHERE id = {m}
            """
            cursor.execute(
                sql,
                (
                    empleado.nombre,
                    empleado.correo,
                    empleado.salario,
                    fecha_bd,
                    empleado.id,
                ),
            )
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def eliminar(cls, id_empleado: int) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"DELETE FROM empleado WHERE id = {m}"
            cursor.execute(sql, (id_empleado,))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()