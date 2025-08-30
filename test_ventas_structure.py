
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'tienda.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(ventas)")
columnas = cursor.fetchall()

print("🧾 Columnas en la tabla ventas:")
for col in columnas:
    print(f"- {col[1]}")

conn.close()
