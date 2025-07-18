import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'tienda.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM productos")
productos = cursor.fetchall()

print("📦 Productos disponibles:")
for producto in productos:
    print(producto)

conn.close()
