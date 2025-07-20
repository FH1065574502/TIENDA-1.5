import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime
import pandas as pd
import subprocess
import threading

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'tienda.db')

# Funciones base de datos
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

def actualizar_combo_productos():
    global productos
    productos = obtener_productos()
    combo["values"] = [f"{p[0]} - ${p[1]}" for p in productos]

def abrir_gestion_productos():
    ruta_script = os.path.join(os.path.dirname(__file__), "productos.py")

    def lanzar_y_esperar():
        proceso = subprocess.Popen(["python", ruta_script])
        proceso.wait()
        actualizar_combo_productos()

    threading.Thread(target=lanzar_y_esperar).start()

# Ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Ventas - TIENDA 1.5")
ventana.geometry("800x600")
ventana.configure(bg="#f0f0f0")

# --- Estilo general ---
fuente = ("Segoe UI", 10)
fuente_bold = ("Segoe UI", 10, "bold")

# --- Frame: Registro de productos y venta ---
frame_registro = tk.Frame(ventana, bg="#f0f0f0")
frame_registro.pack(pady=10)

tk.Label(frame_registro, text="Producto:", font=fuente).grid(row=0, column=0, padx=5, pady=5, sticky="e")
producto_var = tk.StringVar()
combo = ttk.Combobox(frame_registro, textvariable=producto_var, width=40)
combo.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_registro, text="Cantidad:", font=fuente).grid(row=1, column=0, padx=5, pady=5, sticky="e")
cantidad_var = tk.IntVar(value=1)
tk.Entry(frame_registro, textvariable=cantidad_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky="w")

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
        calcular_total_diario()
        messagebox.showinfo("Venta registrada", f"Venta registrada: {nombre} x{cantidad}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

tk.Button(frame_registro, text="Registrar Venta", font=fuente_bold, command=vender, bg="#d9ead3").grid(row=2, column=0, columnspan=2, pady=10)

# --- Frame: Historial y total ---
frame_historial = tk.Frame(ventana, bg="#f0f0f0")
frame_historial.pack(fill="both", expand=True, padx=10)

tabla = ttk.Treeview(frame_historial, columns=("Producto", "Cantidad", "Total", "Fecha"), show='headings', height=12)
for col in tabla["columns"]:
    tabla.heading(col, text=col)
tabla.pack(fill="both", expand=True)

# Total del día
frame_total = tk.Frame(ventana, bg="#f0f0f0")
frame_total.pack(pady=5)
total_var = tk.StringVar()
tk.Label(frame_total, text="Total del día:", font=fuente_bold, bg="#f0f0f0").pack(side="left")
tk.Label(frame_total, textvariable=total_var, font=("Segoe UI", 12, "bold"), fg="green", bg="#f0f0f0").pack(side="left")

def calcular_total_diario():
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total) FROM ventas WHERE fecha = ?", (fecha_actual,))
    total = cursor.fetchone()[0]
    conn.close()
    total_var.set(f"${total:,.0f}" if total else "$0")

# --- Frame: Botones de acciones ---
frame_botones = tk.Frame(ventana, bg="#f0f0f0")
frame_botones.pack(pady=10)

tk.Button(frame_botones, text="Actualizar Historial", font=fuente, command=lambda: [mostrar_historial(), calcular_total_diario()], width=20).grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_botones, text="Exportar a Excel", font=fuente, command=exportar_excel, width=20).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_botones, text="Gestión de Productos", font=fuente, command=abrir_gestion_productos, width=20).grid(row=0, column=2, padx=5, pady=5)

# --- Inicialización ---
def mostrar_historial():
    for row in tabla.get_children():
        tabla.delete(row)
    ventas = obtener_historial_ventas()
    for v in ventas:
        tabla.insert("", "end", values=v)

productos = obtener_productos()
combo["values"] = [f"{p[0]} - ${p[1]}" for p in productos]
mostrar_historial()
calcular_total_diario()

ventana.mainloop()


