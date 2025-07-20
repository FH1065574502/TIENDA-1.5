import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import pandas as pd

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'tienda.db')

# --------------------- FUNCIONES ---------------------

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
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else 0

def registrar_venta():
    producto = combo_productos.get()
    cantidad = entry_cantidad.get()

    if not producto or not cantidad.isdigit() or int(cantidad) <= 0:
        messagebox.showerror("Error", "Seleccione un producto y una cantidad válida.")
        return

    cantidad = int(cantidad)
    precio_unitario = obtener_precio(producto)
    total = precio_unitario * cantidad
    fecha = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ventas (producto, cantidad, total, fecha) VALUES (?, ?, ?, ?)",
                   (producto, cantidad, total, fecha))
    conn.commit()
    conn.close()

    messagebox.showinfo("Éxito", f"Venta registrada.\nTotal: ${total:,}")
    entry_cantidad.delete(0, tk.END)

def exportar_excel():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM ventas", conn)
    conn.close()

    nombre_archivo = os.path.join(os.path.dirname(__file__), f"ventas_{datetime.now().strftime('%Y%m%d')}.xlsx")
    df.to_excel(nombre_archivo, index=False)
    messagebox.showinfo("Exportado", f"Historial exportado a:\n{nombre_archivo}")

def ventana_registro_producto():
    ventana_prod = tk.Toplevel()
    ventana_prod.title("Registrar Producto")
    ventana_prod.geometry("300x250")

    tk.Label(ventana_prod, text="Nombre del producto:").pack(pady=5)
    entry_nombre = tk.Entry(ventana_prod)
    entry_nombre.pack()

    tk.Label(ventana_prod, text="Precio de venta:").pack(pady=5)
    entry_precio = tk.Entry(ventana_prod)
    entry_precio.pack()

    tk.Label(ventana_prod, text="Costo real:").pack(pady=5)
    entry_costo = tk.Entry(ventana_prod)
    entry_costo.pack()

    def registrar_producto():
        nombre = entry_nombre.get().strip()
        try:
            precio = float(entry_precio.get())
            costo = float(entry_costo.get())

            if not nombre:
                messagebox.showerror("Error", "El nombre del producto no puede estar vacío.")
                return

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (nombre, precio, costo) VALUES (?, ?, ?)", (nombre, precio, costo))
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Producto registrado correctamente")
            ventana_prod.destroy()

            # Recargar productos en el combo
            combo_productos['values'] = obtener_productos()

        except ValueError:
            messagebox.showerror("Error", "Precio y costo deben ser numéricos")

    tk.Button(ventana_prod, text="Registrar", command=registrar_producto).pack(pady=10)

# --------------------- INTERFAZ PRINCIPAL ---------------------

ventana = tk.Tk()
ventana.title("Sistema de Ventas")
ventana.geometry("400x300")

tk.Label(ventana, text="Selecciona un producto:").pack(pady=5)
combo_productos = ttk.Combobox(ventana, values=obtener_productos(), state="readonly")
combo_productos.pack()

tk.Label(ventana, text="Cantidad:").pack(pady=5)
entry_cantidad = tk.Entry(ventana)
entry_cantidad.pack()

tk.Button(ventana, text="Registrar Venta", command=registrar_venta).pack(pady=10)
tk.Button(ventana, text="Exportar Historial a Excel", command=exportar_excel).pack(pady=5)
tk.Button(ventana, text="Registrar nuevo producto", command=ventana_registro_producto).pack(pady=5)

ventana.mainloop()

