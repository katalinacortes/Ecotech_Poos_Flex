from datetime import date, datetime
from dominio.registro_tiempo import RegistroTiempo
from persistencia.conexion import abrir_conexion, obtener_motor


class RegistroTiempoDAO:
    @staticmethod
    def _marcador() -> str:
        return "?" if obtener_motor() == "sqlite" else "%s"

    @staticmethod
    def _convertir_fecha(valor) -> date:
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        return date.fromisoformat(str(valor))

    @classmethod
    def _fila_a_registro(cls, fila: tuple) -> RegistroTiempo:
        (
            id_registro,
            fecha_valor,
            horas_trabajadas,
            descripcion_de_tareas,
            empleado_id,
            proyecto_id,
        ) = fila
        return RegistroTiempo(
            fecha=cls._convertir_fecha(fecha_valor),
            horas_trabajadas=float(horas_trabajadas),
            descripcion_de_tareas=descripcion_de_tareas,
            empleado_id=empleado_id,
            proyecto_id=proyecto_id,
            id=id_registro,
        )

    @classmethod
    def insertar(cls, registro: RegistroTiempo) -> RegistroTiempo:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"""
                INSERT INTO registro_tiempo (
                    fecha, horas_trabajadas, descripcion_de_tareas,
                    empleado_id, proyecto_id
                )
                VALUES ({m}, {m}, {m}, {m}, {m})
            """
            cursor.execute(
                sql,
                (
                    registro.fecha.isoformat(),
                    registro.horas_trabajadas,
                    registro.descripcion_de_tareas,
                    registro.empleado_id,
                    registro.proyecto_id,
                ),
            )
            registro.id = cursor.lastrowid
            conexion.commit()
            return registro
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def listar(cls) -> list[RegistroTiempo]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            sql = """
                SELECT
                    id, fecha, horas_trabajadas, descripcion_de_tareas,
                    empleado_id, proyecto_id
                FROM registro_tiempo
                ORDER BY fecha DESC, id DESC
            """
            cursor.execute(sql)
            filas = cursor.fetchall()
            return [cls._fila_a_registro(fila) for fila in filas]
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_por_id(cls, id_registro: int) -> RegistroTiempo | None:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"""
                SELECT
                    id, fecha, horas_trabajadas, descripcion_de_tareas,
                    empleado_id, proyecto_id
                FROM registro_tiempo
                WHERE id = {m}
            """
            cursor.execute(sql, (id_registro,))
            fila = cursor.fetchone()
            if fila is None:
                return None
            return cls._fila_a_registro(fila)
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar(cls, registro: RegistroTiempo) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"""
                UPDATE registro_tiempo
                SET fecha = {m}, horas_trabajadas = {m},
                    descripcion_de_tareas = {m}, empleado_id = {m},
                    proyecto_id = {m}
                WHERE id = {m}
            """
            cursor.execute(
                sql,
                (
                    registro.fecha.isoformat(),
                    registro.horas_trabajadas,
                    registro.descripcion_de_tareas,
                    registro.empleado_id,
                    registro.proyecto_id,
                    registro.id,
                ),
            )
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def eliminar(cls, id_registro: int) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"DELETE FROM registro_tiempo WHERE id = {m}"
            cursor.execute(sql, (id_registro,))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()