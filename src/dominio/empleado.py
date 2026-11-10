# src/dominio/empleado.py

class Empleado:
    def __init__(self, id_empleado: int, nombre: str, direccion: str, telefono: int, correo: str, fecha_inicio_contrato: date, salario: int):
        self.id_empleado = id_empleado
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.correo = correo
        self.fecha_inicio_contrato = fecha_inicio_contrato
        self.salario = salario

    def registrar_empleado(self) -> None:
        print(f"Registrando al empleado: {self.nombre}")

    def validar_datos_personales(self) -> bool:
        if self.correo and self.telefono:
            return True
        return False