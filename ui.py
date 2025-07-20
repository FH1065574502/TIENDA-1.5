import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime

# Ruta absoluta a tienda.db
db_path = os.path.join(os.path.dirname(__file__), 'tienda.db')

def obtener_productos():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM productos")
    productos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return productos

def registrar_venta(nombre_producto):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO ventas (producto, fecha) VALUES (?, ?)", (nombre_producto, fecha_actual))
    conn.commit()
    conn.close()
    messagebox.showinfo("✅ Venta registrada", f"Producto: {nombre_producto}")
    actualizar_historial()

def obtener_historial():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, producto, fecha FROM ventas ORDER BY fecha DESC")
    historial = cursor.fetchall()
    conn.close()
    return historial

def actualizar_historial():
    for item in tabla.get_children():
        tabla.delete(item)
    for venta in obtener_historial():
        tabla.insert("", "end", values=venta)

# Interfaz
root = tk.Tk()
root.title("Sistema de Ventas")

tk.Label(root, text="Selecciona un producto:").pack(pady=5)

productos = obtener_productos()
producto_var = tk.StringVar()
producto_combo = ttk.Combobox(root, textvariable=producto_var, values=productos, state="readonly")
producto_combo.pack(pady=5)

def registrar():
    producto = producto_var.get()
    if producto:
        registrar_venta(producto)
    else:
        messagebox.showwarning("⚠️ Atención", "Selecciona un producto antes de registrar.")

tk.Button(root, text="Registrar Venta", command=registrar).pack(pady=10)

# Historial 1
tk.Label(root, text="Historial de Ventas").pack(pady=(20, 5))
tabla = ttk.Treeview(root, columns=("ID", "Producto", "Fecha"), show="headings")
tabla.heading("ID", text="ID")
tabla.heading("Producto", text="Producto")
tabla.heading("Fecha", text="Fecha")
tabla.pack(padx=10, pady=5, fill="x")

actualizar_historial()

root.mainloop()


