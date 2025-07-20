# productos.py
import tkinter as tk
from tkinter import messagebox
import sqlite3
import os

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'tienda.db')

def agregar_producto(nombre, costo, precio):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO productos (nombre, costo, precio) VALUES (?, ?, ?)",
                       (nombre, costo, precio))
        conn.commit()
        messagebox.showinfo("Éxito", f"Producto '{nombre}' registrado.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"El producto '{nombre}' ya existe.")
    finally:
        conn.close()

def interfaz_registro_producto():
    ventana = tk.Tk()
    ventana.title("Registrar Producto")

    tk.Label(ventana, text="Nombre del producto:").pack(pady=5)
    entry_nombre = tk.Entry(ventana)
    entry_nombre.pack()

    tk.Label(ventana, text="Costo:").pack(pady=5)
    entry_costo = tk.Entry(ventana)
    entry_costo.pack()

    tk.Label(ventana, text="Precio de venta:").pack(pady=5)
    entry_precio = tk.Entry(ventana)
    entry_precio.pack()

    def registrar():
        nombre = entry_nombre.get().strip()
        try:
            costo = float(entry_costo.get())
            precio = float(entry_precio.get())
        except ValueError:
            messagebox.showerror("Error", "Costo y precio deben ser números.")
            return

        if not nombre or costo <= 0 or precio <= 0:
            messagebox.showerror("Error", "Datos inválidos.")
            return

        agregar_producto(nombre, costo, precio)
        entry_nombre.delete(0, tk.END)
        entry_costo.delete(0, tk.END)
        entry_precio.delete(0, tk.END)

    tk.Button(ventana, text="Registrar producto", command=registrar).pack(pady=10)
    ventana.mainloop()

if __name__ == "__main__":
    interfaz_registro_producto()
