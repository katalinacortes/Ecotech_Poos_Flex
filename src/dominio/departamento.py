# src/dominio/departamento.py
from dominio.empleado import Empleado

class Departamento:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.empleados: list[Empleado] = []

    def agregar_empleado(self, empleado: Empleado) -> bool:
        if empleado in self.empleados:
            return False
        
        self.empleados.append(empleado)
        return True

    # Método genérico basado en el "+ method(type): type" del UML
    def method(self, tipo: str) -> str:
        return f"Método ejecutado para el tipo: {tipo}"