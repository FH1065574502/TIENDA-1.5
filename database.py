import sqlite3
import os

# Ruta absoluta a tienda.db
db_path = os.path.join(os.path.dirname(__file__), 'tienda.db')

def crear_base_de_datos():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear tabla productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL
        )
    ''')

    # Crear tabla ventas con columnas completas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')

    # Insertar productos si está vacía
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos = [
            ('Pan', 1000),
            ('Leche', 3500),
            ('Huevos', 12000),
            ('Café', 8000)
        ]
        cursor.executemany("INSERT INTO productos (nombre, precio) VALUES (?, ?)", productos)
        print("✅ Productos iniciales insertados.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_base_de_datos()




