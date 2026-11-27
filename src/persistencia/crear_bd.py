from persistencia.conexion import abrir_conexion, obtener_motor


def _asegurar_columna_rol_sqlite(cursor) -> None:
    cursor.execute("PRAGMA table_info(usuario);")
    columnas = [fila[1] for fila in cursor.fetchall()]
    if columnas and "rol" not in columnas:
        cursor.execute(
            "ALTER TABLE usuario ADD COLUMN rol TEXT NOT NULL DEFAULT 'empleado';"
        )


def _insertar_empleado_inicial(cursor, motor: str) -> None:
    if motor == "sqlite":
        cursor.execute(
            """
            INSERT OR IGNORE INTO empleado (id, nombre, correo, salario, fecha_inicio_contrato, departamento_id)
            VALUES (1, 'Empleado Base', 'base@ecotech.local', 500000.0, NULL, NULL);
            """
        )
    elif motor == "mysql":
        cursor.execute(
            """
            INSERT IGNORE INTO empleado (id, nombre, correo, salario, fecha_inicio_contrato, departamento_id)
            VALUES (1, 'Empleado Base', 'base@ecotech.local', 500000.00, NULL, NULL);
            """
        )


def crear_tablas() -> None:
    conexion = abrir_conexion()
    cursor = conexion.cursor()
    motor = obtener_motor()

    if motor == "sqlite":
        cursor.execute("PRAGMA foreign_keys = ON;")
        sentencias = [
            """
            CREATE TABLE IF NOT EXISTS departamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS empleado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                salario REAL NOT NULL DEFAULT 0.0,
                fecha_inicio_contrato TEXT,
                departamento_id INTEGER,
                FOREIGN KEY (departamento_id) REFERENCES departamento(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS proyecto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_proyecto TEXT NOT NULL,
                descripcion TEXT,
                fecha_de_inicio TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS registro_tiempo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                horas_trabajadas REAL NOT NULL,
                descripcion_de_tareas TEXT NOT NULL,
                empleado_id INTEGER,
                proyecto_id INTEGER,
                FOREIGN KEY (empleado_id) REFERENCES empleado(id),
                FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'empleado',
                empleado_id INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (empleado_id) REFERENCES empleado(id)
            );
            """,
        ]
    elif motor == "mysql":
        sentencias = [
            """
            CREATE TABLE IF NOT EXISTS departamento (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(80) NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS empleado (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(80) NOT NULL,
                correo VARCHAR(150) NOT NULL UNIQUE,
                salario DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
                fecha_inicio_contrato DATE NULL,
                departamento_id INT NULL,
                CONSTRAINT fk_empleado_departamento
                    FOREIGN KEY (departamento_id) REFERENCES departamento(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS proyecto (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre_proyecto VARCHAR(100) NOT NULL,
                descripcion TEXT NULL,
                fecha_de_inicio DATE NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS registro_tiempo (
                id INT PRIMARY KEY AUTO_INCREMENT,
                fecha DATE NOT NULL,
                horas_trabajadas DECIMAL(5, 2) NOT NULL,
                descripcion_de_tareas VARCHAR(200) NOT NULL,
                empleado_id INT NULL,
                proyecto_id INT NULL,
                CONSTRAINT fk_registro_empleado
                    FOREIGN KEY (empleado_id) REFERENCES empleado(id),
                CONSTRAINT fk_registro_proyecto
                    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS usuario (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre_usuario VARCHAR(40) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(20) NOT NULL DEFAULT 'empleado',
                empleado_id INT NOT NULL UNIQUE,
                CONSTRAINT fk_usuario_empleado
                    FOREIGN KEY (empleado_id) REFERENCES empleado(id)
            );
            """,
        ]
    else:
        conexion.close()
        raise ValueError(f"Motor de base de datos no soportado: {motor}")

    for sql in sentencias:
        cursor.execute(sql)

    if motor == "sqlite":
        _asegurar_columna_rol_sqlite(cursor)

    _insertar_empleado_inicial(cursor, motor)

    conexion.commit()
    cursor.close()
    conexion.close()


if __name__ == "__main__":
    crear_tablas()
    print("Base de datos preparada correctamente.")