from dominio.departamento import Departamento
from dominio.empleado import Empleado
from persistencia.conexion import abrir_conexion, obtener_motor


class DepartamentoDAO:
    @staticmethod
    def _marcador() -> str:
        return "?" if obtener_motor() == "sqlite" else "%s"

    @classmethod
    def insertar(cls, departamento: Departamento) -> Departamento:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"INSERT INTO departamento (nombre) VALUES ({m})"
            cursor.execute(sql, (departamento.nombre,))
            departamento.id = cursor.lastrowid
            conexion.commit()
            return departamento
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def listar(cls) -> list[Departamento]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            sql = "SELECT id, nombre FROM departamento ORDER BY id"
            cursor.execute(sql)
            filas = cursor.fetchall()
            return [Departamento(nombre=nombre, id=id_depto) for id_depto, nombre in filas]
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_con_empleados(cls, id_departamento: int) -> Departamento | None:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"""
                SELECT
                    d.id AS depto_id,
                    d.nombre AS depto_nombre,
                    e.id AS emp_id,
                    e.nombre AS emp_nombre,
                    e.correo AS emp_correo
                FROM departamento d
                LEFT JOIN empleado e ON e.departamento_id = d.id
                WHERE d.id = {m}
                ORDER BY e.id
            """
            cursor.execute(sql, (id_departamento,))
            filas = cursor.fetchall()
            if not filas:
                return None

            departamento = Departamento(nombre=filas[0][1], id=filas[0][0])
            for id_emp, nombre_emp, correo_emp in (
                (fila[2], fila[3], fila[4]) for fila in filas
            ):
                if id_emp is not None:
                    empleado = Empleado(
                        nombre=nombre_emp,
                        correo=correo_emp,
                        id=id_emp,
                    )
                    departamento.agregar_empleado(empleado)

            return departamento
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar(cls, departamento: Departamento) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"UPDATE departamento SET nombre = {m} WHERE id = {m}"
            cursor.execute(sql, (departamento.nombre, departamento.id))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def eliminar(cls, id_departamento: int) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            m = cls._marcador()
            sql = f"DELETE FROM departamento WHERE id = {m}"
            cursor.execute(sql, (id_departamento,))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()