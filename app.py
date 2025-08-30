import tkinter as tk
from interfaz_unificada_tienda import SistemaVentas

def main():
    root = tk.Tk()
    root.title("Sistema de Ventas - TIENDA 1.5")
    root.geometry("900x600")

    frame_menu = tk.Frame(root, width=250, bg="#f0f0f0")
    frame_menu.pack(side="left", fill="y")

    frame_contenido = tk.Frame(root, bg="#ffffff")
    frame_contenido.pack(side="right", expand=True, fill="both")

    sistema = SistemaVentas(frame_contenido)

    def mostrar_menu_principal():
        for widget in frame_menu.winfo_children():
            widget.destroy()
        for widget in frame_contenido.winfo_children():
            widget.destroy()

        tk.Label(frame_menu, text="Menú Principal", bg="#f0f0f0", font=("Helvetica", 16)).pack(pady=20)

        tk.Button(frame_menu, text="🛍️ Realizar Venta", width=20, height=2, command=mostrar_categorias).pack(pady=10)
        tk.Button(frame_menu, text="📊 Exportar Reportes", width=20, height=2, command=sistema.exportar_reportes).pack(pady=10)
        tk.Button(frame_menu, text="🛒 Ingresar Productos", width=20, height=2, command=sistema.ingresar_productos).pack(pady=10)
        tk.Button(frame_menu, text="❌ Salir", width=20, height=2, command=root.destroy).pack(pady=10)

    def mostrar_categorias():
        sistema.mostrar_categorias(mostrar_menu_principal)

    mostrar_menu_principal()
    root.mainloop()

if __name__ == "__main__":
    main()
