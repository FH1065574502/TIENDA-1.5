import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class SistemaVentas:
    def __init__(self, parent, frame_venta):
        self.parent = parent
        self.frame_venta = frame_venta
        self.carrito = []

    def conectar_db(self):
        return sqlite3.connect("tienda.db")

    def obtener_productos_por_categoria(self, categoria):
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM productos WHERE categoria = ?", (categoria,))
        productos = [fila[0] for fila in cursor.fetchall()]
        conn.close()
        return productos

    def mostrar_productos(self, categoria):
        for widget in self.frame_venta.winfo_children():
            widget.destroy()

        productos = self.obtener_productos_por_categoria(categoria)
        for producto in productos:
            boton = tk.Button(self.frame_venta, text=producto, width=20, command=lambda p=producto: self.seleccionar_producto(p))
            boton.pack(pady=2)

    def seleccionar_producto(self, nombre_producto):
        cantidad = tk.IntVar(value=1)

        def aumentar():
            cantidad.set(cantidad.get() + 1)

        def disminuir():
            if cantidad.get() > 1:
                cantidad.set(cantidad.get() - 1)

        def agregar():
            self.registrar_venta(nombre_producto, cantidad.get())
            top.destroy()

        top = tk.Toplevel(self.parent)
        top.title("Seleccionar cantidad")
        tk.Label(top, text=f"Cantidad para '{nombre_producto}':").pack(padx=10, pady=5)

        entry = tk.Entry(top, textvariable=cantidad, width=5, justify="center")
        entry.pack(pady=5)

        frame_botones = tk.Frame(top)
        frame_botones.pack(pady=5)

        tk.Button(frame_botones, text="-", width=3, command=disminuir).pack(side="left", padx=5)
        tk.Button(frame_botones, text="+", width=3, command=aumentar).pack(side="left", padx=5)

        tk.Button(top, text="Agregar", command=agregar).pack(pady=5)

    def registrar_venta(self, nombre_producto, cantidad):
        conn = self.conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, precio FROM productos WHERE nombre = ?", (nombre_producto,))
        resultado = cursor.fetchone()
        if resultado:
            producto_id, precio = resultado
            total = precio * cantidad
            fecha = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("INSERT INTO ventas (producto_id, cantidad, total, fecha) VALUES (?, ?, ?, ?)",
                           (producto_id, cantidad, total, fecha))
            conn.commit()

            self.carrito.append((nombre_producto, cantidad, total))
            messagebox.showinfo("Venta registrada", f"Se vendió {cantidad} unidad(es) de '{nombre_producto}'.")
        else:
            messagebox.showerror("Error", f"Producto '{nombre_producto}' no encontrado en la base de datos.")

        conn.close()
