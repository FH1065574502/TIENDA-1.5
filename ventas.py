import sqlite3
import os
from datetime import datetime

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'tienda.db')

def obtener_productos():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM productos")
    productos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return productos

def obtener_precio(producto):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT precio FROM productos WHERE nombre = ?", (producto,))
    precio = cursor.fetchone()[0]
    conn.close()
    return precio

def registrar_venta(producto, cantidad):
    if not producto or cantidad <= 0:
        raise ValueError("Producto inválido o cantidad menor a 1")
    
    precio_unitario = obtener_precio(producto)
    total = precio_unitario * cantidad
    fecha = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ventas (producto, cantidad, total, fecha) VALUES (?, ?, ?, ?)",
                   (producto, cantidad, total, fecha))
    conn.commit()
    conn.close()
    return True

def obtener_historial():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT producto, cantidad, total, fecha FROM ventas ORDER BY fecha DESC")
    ventas = cursor.fetchall()
    conn.close()
    return ventas

def total_dia():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT SUM(total) FROM ventas WHERE fecha = ?", (fecha,))
    total = cursor.fetchone()[0]
    conn.close()
    return total or 0

