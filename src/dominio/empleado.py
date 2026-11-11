# src/dominio/empleado.py

class Empleado:
    MIN_NOMBRE = 2
    MAX_NOMBRE = 25
    MIN_CORREO = 2
    MAX_CORREO = 150

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

    @staticmethod
    def validar_nombre(nombre):
        if not isinstance(nombre, str):
             raise ValueError("El nombre debe ser texto.")
        nombre = nombre.strip()
        if not (Empleado.MIN_NOMBRE <= len(nombre)
                <= Empleado.MAX_NOMBRE):
            raise ValueError(
                 "El nombre debe tener entre 2 y 80 caracteres."
                )
            return nombre 

        # Dentro de Empleado
            @property
            def nombre(self):
            return self._nombre
            @nombre.setter
            def nombre(self, valor):
            self._nombre = self.validar_nombre(valor)

        @nombre.setter
     def nombre(self, valor):
            self._nombre = self.validar_nombre(valor)