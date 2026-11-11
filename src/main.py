from dominio.empleado import Empleado
from persistencia.crear_bd import Departamento
from dominio.empleado import EmpleadoDAOO
from persistencia.creacion_bd import crear_tablas 
crear_tablas()

try:
    empleado = Empleado ("Ana", "ana@ecotech.cl")
except ValueError as error:
    print (f"no se pudo crear el empleado:{error}")
else:
    print (f"datos validos:{empleado.nombre} ")

EmpleadoDAO.insertar(empleado)
empleados = EmpleadoDAO.listar()

if not empleados:
    print("Todavía no hay empleados registrados.")
else:
    for empleado in empleados:
print(
    f"{empleado.id}: {empleado.nombre} "
    f"- {empleado.correo}"
)
