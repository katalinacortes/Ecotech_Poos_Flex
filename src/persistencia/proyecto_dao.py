from datetime import date, datetime
from dominio.proyecto import Proyecto
from persistencia.conexion import abrir_conexion, obtener_motor


class ProyectoDAO:
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
    def _fila_a_proyecto(cls, fila: tuple) -> Proyecto:
        id_proyecto, nombre_proyecto, descripcion, fecha_inicio = fila
        return Proyecto(
            nombre_proyecto=nombre_proyecto,
            descripcion=descripcion or "",
            fecha_de_inicio=cls._convertir_fecha(fecha_inicio),
            id=id_proyecto,
        )

    @classmethod
    def insertar(cls, proyecto: Proyecto) -> Proyecto:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"""
                INSERT INTO proyecto (nombre_proyecto, descripcion, fecha_de_inicio)
                VALUES ({m}, {m}, {m})
            """
            fecha_bd = (
                proyecto.fecha_de_inicio.isoformat()
                if proyecto.fecha_de_inicio is not None
                else None
            )
            cursor.execute(
                sql,
                (
                    proyecto.nombre_proyecto,
                    proyecto.descripcion,
                    fecha_bd,
                ),
            )
            proyecto.id = cursor.lastrowid
            conexion.commit()
            return proyecto
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def listar(cls) -> list[Proyecto]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            sql = """
                SELECT id, nombre_proyecto, descripcion, fecha_de_inicio
                FROM proyecto
                ORDER BY id
            """
            cursor.execute(sql)
            filas = cursor.fetchall()
            return [cls._fila_a_proyecto(fila) for fila in filas]
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_por_id(cls, id_proyecto: int) -> Proyecto | None:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"""
                SELECT id, nombre_proyecto, descripcion, fecha_de_inicio
                FROM proyecto
                WHERE id = {m}
            """
            cursor.execute(sql, (id_proyecto,))
            fila = cursor.fetchone()
            if fila is None:
                return None
            return cls._fila_a_proyecto(fila)
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar(cls, proyecto: Proyecto) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"""
                UPDATE proyecto
                SET nombre_proyecto = {m}, descripcion = {m}, fecha_de_inicio = {m}
                WHERE id = {m}
            """
            fecha_bd = (
                proyecto.fecha_de_inicio.isoformat()
                if proyecto.fecha_de_inicio is not None
                else None
            )
            cursor.execute(
                sql,
                (
                    proyecto.nombre_proyecto,
                    proyecto.descripcion,
                    fecha_bd,
                    proyecto.id,
                ),
            )
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def eliminar(cls, id_proyecto: int) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"DELETE FROM proyecto WHERE id = {m}"
            cursor.execute(sql, (id_proyecto,))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()