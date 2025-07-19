import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime
import pandas as pd

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'tienda.db')

# Conexión a la base de datos
def obtener_productos():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, precio FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

def registrar_venta(nombre, precio, cantidad):
    fecha = datetime.now().strftime("%Y-%m-%d")
    total = precio * cantidad
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ventas (producto, cantidad, total, fecha) VALUES (?, ?, ?, ?)",
                   (nombre, cantidad, total, fecha))
    conn.commit()
    conn.close()

def obtener_historial_ventas():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT producto, cantidad, total, fecha FROM ventas ORDER BY fecha DESC")
    ventas = cursor.fetchall()
    conn.close()
    return ventas

def exportar_excel():
    ventas = obtener_historial_ventas()
    if not ventas:
        messagebox.showwarning("Sin datos", "No hay ventas registradas.")
        return
    df = pd.DataFrame(ventas, columns=["Producto", "Cantidad", "Total", "Fecha"])
    archivo = os.path.join(os.path.dirname(__file__), 'historial_ventas.xlsx')
    df.to_excel(archivo, index=False)
    messagebox.showinfo("Exportado", f"Historial exportado correctamente a:\n{archivo}")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Ventas")
ventana.geometry("700x500")

# --- Lista de productos ---
productos = obtener_productos()
producto_var = tk.StringVar()
cantidad_var = tk.IntVar(value=1)

tk.Label(ventana, text="Producto:").pack()
combo = ttk.Combobox(ventana, textvariable=producto_var, values=[f"{p[0]} - ${p[1]}" for p in productos])
combo.pack()

tk.Label(ventana, text="Cantidad:").pack()
tk.Entry(ventana, textvariable=cantidad_var).pack()

# Función de venta
def vender():
    try:
        if not producto_var.get():
            raise ValueError("Seleccione un producto.")
        nombre = producto_var.get().split(" -")[0]
        precio = next(p[1] for p in productos if p[0] == nombre)
        cantidad = cantidad_var.get()
        if cantidad < 1:
            raise ValueError("Cantidad debe ser mayor a cero.")
        registrar_venta(nombre, precio, cantidad)
        mostrar_historial()
        messagebox.showinfo("Venta registrada", f"Venta registrada: {nombre} x{cantidad}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

tk.Button(ventana, text="Registrar Venta", command=vender).pack(pady=10)

# --- Historial de ventas ---
tabla = ttk.Treeview(ventana, columns=("Producto", "Cantidad", "Total", "Fecha"), show='headings')
for col in tabla["columns"]:
    tabla.heading(col, text=col)
tabla.pack(expand=True, fill='both')

# Mostrar historial
def mostrar_historial():
    for row in tabla.get_children():
        tabla.delete(row)
    ventas = obtener_historial_ventas()
    for v in ventas:
        tabla.insert("", "end", values=v)

# Total diario
def calcular_total_diario():
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total) FROM ventas WHERE fecha = ?", (fecha_actual,))
    total = cursor.fetchone()[0]
    conn.close()
    total_var.set(f"${total:,.0f}" if total else "$0")

# Mostrar total
total_var = tk.StringVar()
tk.Label(ventana, text="Total del día:").pack()
tk.Label(ventana, textvariable=total_var, font=("Arial", 12, "bold")).pack()

# Botones adicionales
tk.Button(ventana, text="Actualizar Historial", command=mostrar_historial).pack(pady=5)
tk.Button(ventana, text="Calcular Total Diario", command=calcular_total_diario).pack()
tk.Button(ventana, text="Exportar a Excel", command=exportar_excel).pack(pady=5)

# Inicializar proyecto
mostrar_historial()
calcular_total_diario()
ventana.mainloop()
