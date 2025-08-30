import tkinter as tk
import sqlite3

class VentanaVenta:
    def __init__(self, root_menu):
        self.root_menu = root_menu
        self.ventana = tk.Toplevel()
        self.ventana.title("Realizar Venta")
        self.ventana.geometry("600x500")
        self.crear_interfaz_categorias()

    def crear_interfaz_categorias(self):
        for widget in self.ventana.winfo_children():
            widget.destroy()

        tk.Label(self.ventana, text="Selecciona una categoría", font=("Arial", 14)).pack(pady=10)

        categorias = self.obtener_categorias()
        for cat in categorias:
            tk.Button(self.ventana, text=cat, width=30, height=2,
                      command=lambda c=cat: self.mostrar_productos_por_categoria(c)).pack(pady=5)

        tk.Button(self.ventana, text="⬅ Volver al Menú Principal", bg="lightgray",
                  command=self.volver_al_menu_principal).pack(pady=20)

    def obtener_categorias(self):
        conn = sqlite3.connect("tienda.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT categoria FROM productos WHERE categoria IS NOT NULL")
        categorias = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categorias

    def mostrar_productos_por_categoria(self, categoria):
        for widget in self.ventana.winfo_children():
            widget.destroy()

        tk.Label(self.ventana, text=f"Productos de {categoria}", font=("Arial", 14)).pack(pady=10)

        conn = sqlite3.connect("tienda.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, precio FROM productos WHERE categoria = ?", (categoria,))
        productos = cursor.fetchall()
        conn.close()

        for nombre, precio in productos:
            texto = f"{nombre} - ${precio:,.0f}"
            tk.Button(self.ventana, text=texto, width=30, height=2,
                      command=lambda n=nombre, p=precio: self.registrar_venta(n, p)).pack(pady=5)

        tk.Button(self.ventana, text="⬅ Volver a Categorías", bg="lightgray",
                  command=self.crear_interfaz_categorias).pack(pady=20)

    def registrar_venta(self, nombre, precio):
        print(f"Venta registrada: {nombre} - ${precio:,.0f}")
        # Aquí puedes implementar la lógica para guardar la venta

    def volver_al_menu_principal(self):
        self.ventana.destroy()
        self.root_menu.deiconify()


