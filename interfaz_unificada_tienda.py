# interfaz_unificada_tienda.py
from productos import (
    interfaz_registro_producto,
    interfaz_admin_productos,
    db_path,  # misma BD que productos.py
)
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


# -----------------------------
# Helpers de BD
# -----------------------------
def ensure_stock_column():
    """Garantiza que exista la columna stock en la tabla productos."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cols = [c[1] for c in cur.execute("PRAGMA table_info(productos)")]
    if "stock" not in cols:
        try:
            cur.execute("ALTER TABLE productos ADD COLUMN stock INTEGER DEFAULT 0")
            con.commit()
        except sqlite3.OperationalError:
            pass
    con.close()


def obtener_productos_por_categoria(categoria, filtro=""):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        if filtro:
            cur.execute(
                """SELECT nombre, COALESCE(precio_venta,precio) AS precio_venta, stock
                   FROM productos
                   WHERE categoria=? AND nombre LIKE ?
                   ORDER BY nombre ASC""",
                (categoria, f"%{filtro}%"),
            )
        else:
            cur.execute(
                """SELECT nombre, COALESCE(precio_venta,precio) AS precio_venta, stock
                   FROM productos
                   WHERE categoria=?
                   ORDER BY nombre ASC""",
                (categoria,),
            )
        productos = cur.fetchall()
    except sqlite3.OperationalError:
        if filtro:
            cur.execute(
                """SELECT nombre, COALESCE(precio_venta,precio) AS precio_venta
                   FROM productos
                   WHERE categoria=? AND nombre LIKE ?
                   ORDER BY nombre ASC""",
                (categoria, f"%{filtro}%"),
            )
        else:
            cur.execute(
                """SELECT nombre, COALESCE(precio_venta,precio) AS precio_venta
                   FROM productos
                   WHERE categoria=?
                   ORDER BY nombre ASC""",
                (categoria,),
            )
        productos = [(n, p, None) for (n, p) in cur.fetchall()]
    finally:
        con.close()
    return productos


def fmt_moneda(v):
    try:
        return f"${float(v):,.0f}".replace(",", ".")
    except Exception:
        return f"${v}"


# -----------------------------
# Scrollable (para tarjetas)
# -----------------------------
class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        canvas = tk.Canvas(self, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas)
        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))


# -----------------------------
# App
# -----------------------------
class TiendaApp:
    CATEGORIAS = [
        "Verduras y Frutas",
        "Lácteos y Huevos",
        "Carnes y Embutidos",
        "Aseo",
        "Gaseosa",
        "Licores",
        "Granos",
        "Otros",
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Ventas - Tienda 2.0")
        self.root.geometry("1150x650")
        self.root.minsize(1000, 600)

        ensure_stock_column()  # importante para inventario/ventas

        self._configurar_tema()

        self.carrito = {}       # nombre -> {"precio": float, "cantidad": int}
        self.categoria_actual = None
        self.filtro_actual = tk.StringVar()

        self._crear_topbar()
        self._crear_sidebar()
        self._crear_contenido()
        self._crear_carrito()

        # Atajos
        self.root.bind("<Control-f>", lambda e: self.entry_buscar.focus_set())
        self.root.bind("<Delete>", lambda e: self.eliminar_seleccion())
        self.root.bind("<Control-n>", lambda e: self.vaciar_carrito())

        self.mostrar_categorias()

    # --------- UI Base ----------
    def _configurar_tema(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        primario = "#2563eb"; primario_hover = "#1e4fc2"
        fondo = "#f5f7fb"; surface = "#ffffff"

        style.configure("TFrame", background=fondo)
        style.configure("Surface.TFrame", background=surface)
        style.configure("Title.TLabel", background=surface, font=("Segoe UI", 14, "bold"))
        style.configure("H1.TLabel", background=fondo, font=("Segoe UI", 16, "bold"))
        style.configure("Muted.TLabel", background=surface, foreground="#6b7280")
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))
        style.map("Primary.TButton",
                  background=[("!disabled", primario), ("active", primario_hover)],
                  foreground=[("!disabled", "white")])
        style.configure("Sidebar.TButton", anchor="w", padding=12)
        style.configure("Card.TFrame", background=surface, relief="flat", borderwidth=1)
        style.configure("Card.TLabel", background=surface, font=("Segoe UI", 10))
        style.configure("Strong.TLabel", background=surface, font=("Segoe UI", 10, "bold"))

    def _crear_topbar(self):
        top = ttk.Frame(self.root, style="Surface.TFrame"); top.pack(side="top", fill="x")
        ttk.Label(top, text="🛒 Sistema de Ventas", style="H1.TLabel").pack(side="left", padx=16, pady=10)
        self.lbl_reloj = ttk.Label(top, text="", style="Muted.TLabel"); self.lbl_reloj.pack(side="right", padx=16)
        self._tick()

    def _tick(self):
        self.lbl_reloj.config(text=datetime.now().strftime("⏱ %d/%m/%Y %H:%M:%S"))
        self.root.after(1000, self._tick)

    def _crear_sidebar(self):
        side = ttk.Frame(self.root, width=230); side.pack(side="left", fill="y"); side.pack_propagate(False)
        ttk.Label(side, text="Menú", style="Title.TLabel").pack(padx=14, pady=(14, 6), anchor="w")

        ttk.Button(side, text="🧾 Realizar venta", style="Sidebar.TButton",
                   command=self.mostrar_categorias).pack(fill="x", padx=10, pady=4)
        ttk.Button(side, text="📦 Ingresar productos", style="Sidebar.TButton",
                   command=self.ingresar_productos).pack(fill="x", padx=10, pady=4)
        ttk.Button(side, text="🔎 Buscar/Editar productos", style="Sidebar.TButton",
                   command=self.editar_productos).pack(fill="x", padx=10, pady=4)
        ttk.Button(side, text="📊 Inventario", style="Sidebar.TButton",
                   command=self.ventana_inventario).pack(fill="x", padx=10, pady=4)
        ttk.Button(side, text="📈 Exportar reportes", style="Sidebar.TButton",
                   command=self.exportar_reportes).pack(fill="x", padx=10, pady=4)
        ttk.Separator(side).pack(fill="x", padx=10, pady=10)
        ttk.Button(side, text="🗑 Vaciar carrito", style="Sidebar.TButton",
                   command=self.vaciar_carrito).pack(fill="x", padx=10, pady=4)

    def _crear_contenido(self):
        cont = ttk.Frame(self.root); cont.pack(side="left", fill="both", expand=True)

        barra = ttk.Frame(cont, style="Surface.TFrame"); barra.pack(fill="x")
        ttk.Label(barra, text="Selecciona categoría o busca:", style="Title.TLabel")\
            .pack(side="left", padx=14, pady=10)

        self.entry_buscar = ttk.Entry(barra, textvariable=self.filtro_actual, width=30)
        self.entry_buscar.pack(side="right", padx=10, pady=10)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self._refrescar_productos())

        cats = ttk.Frame(cont); cats.pack(fill="x", padx=10, pady=(8, 0))
        for cat in self.CATEGORIAS:
            ttk.Button(cats, text=cat, command=lambda c=cat: self.mostrar_productos(c))\
                .pack(side="left", padx=6, pady=6)

        self.scroll_prod = ScrollableFrame(cont)
        self.scroll_prod.pack(fill="both", expand=True, padx=10, pady=10)

    def _crear_carrito(self):
        wrap = ttk.Frame(self.root, width=440)
        wrap.pack(side="right", fill="y")
        wrap.pack_propagate(False)

        header = ttk.Frame(wrap, style="Surface.TFrame"); header.pack(fill="x")
        ttk.Label(header, text="Resumen de Venta", style="Title.TLabel").pack(side="left", padx=14, pady=10)

        cols = ("producto", "cant", "precio", "subtotal")
        self.tv = ttk.Treeview(wrap, columns=cols, show="headings", height=18)

        self.tv.heading("producto", text="Producto")
        self.tv.heading("cant", text="Cant")
        self.tv.heading("precio", text="Precio")
        self.tv.heading("subtotal", text="Subtotal")

        self.tv.column("producto", width=220, anchor="w", stretch=False)
        self.tv.column("cant",     width=55,  anchor="center", stretch=False)
        self.tv.column("precio",   width=90,  anchor="e", stretch=False)
        self.tv.column("subtotal", width=100, anchor="e", stretch=False)

        self.tv.pack(fill="both", expand=True, padx=10, pady=(4, 0))

        xsb = ttk.Scrollbar(wrap, orient="horizontal", command=self.tv.xview)
        self.tv.configure(xscrollcommand=xsb.set)
        xsb.pack(fill="x", padx=10, pady=(0, 6))

        controles = ttk.Frame(wrap); controles.pack(fill="x", padx=10, pady=4)
        ttk.Button(controles, text="➕", width=4, command=self.incrementar_seleccion).pack(side="left", padx=3)
        ttk.Button(controles, text="➖", width=4, command=self.decrementar_seleccion).pack(side="left", padx=3)
        ttk.Button(controles, text="Eliminar", command=self.eliminar_seleccion).pack(side="left", padx=6)

        bottom = ttk.Frame(wrap, style="Surface.TFrame"); bottom.pack(fill="x", padx=10, pady=6)
        self.lbl_total = ttk.Label(bottom, text="Total: $0", style="Strong.TLabel")
        self.lbl_total.pack(side="left", padx=6, pady=10)
        ttk.Button(bottom, text="Finalizar Venta", style="Primary.TButton",
                   command=self.finalizar_venta).pack(side="right", padx=6, pady=6)

        def _ajustar_cols(event=None):
            w = max(self.tv.winfo_width() - 20, 300)
            self.tv.column("producto", width=int(w * 0.56))
            self.tv.column("cant",     width=int(w * 0.10))
            self.tv.column("precio",   width=int(w * 0.16))
            self.tv.column("subtotal", width=int(w * 0.18))

        self.tv.bind("<Configure>", _ajustar_cols)
        self.root.after(150, _ajustar_cols)

    # --------- Acciones ----------
    def mostrar_categorias(self):
        self.categoria_actual = None
        for w in self.scroll_prod.inner.winfo_children():
            w.destroy()
        card = ttk.Frame(self.scroll_prod.inner, style="Card.TFrame"); card.pack(padx=10, pady=10, fill="x")
        ttk.Label(card, text="Elige una categoría o usa la búsqueda para ver productos.",
                  style="Card.TLabel").pack(padx=12, pady=12)

    def mostrar_productos(self, categoria):
        self.categoria_actual = categoria
        self.filtro_actual.set("")
        self._refrescar_productos()

    def _refrescar_productos(self):
        for w in self.scroll_prod.inner.winfo_children():
            w.destroy()
        if not self.categoria_actual:
            return

        productos = obtener_productos_por_categoria(
            self.categoria_actual, self.filtro_actual.get().strip()
        )
        if not productos:
            ttk.Label(self.scroll_prod.inner, text="Sin resultados…", style="Muted.TLabel")\
                .pack(padx=12, pady=16, anchor="w")
            return

        cols = 2
        for i, (nombre, precio, stock) in enumerate(productos):
            tarjeta = ttk.Frame(self.scroll_prod.inner, style="Card.TFrame")
            r, c = divmod(i, cols); tarjeta.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

            body = ttk.Frame(tarjeta, style="Surface.TFrame")
            body.pack(fill="both", expand=True, padx=10, pady=10)

            ttk.Label(body, text=f"🧺  {nombre}", style="Strong.TLabel").pack(anchor="w")
            ttk.Label(body, text=f"Precio: {fmt_moneda(precio or 0)}", style="Card.TLabel")\
                .pack(anchor="w", pady=(2, 0))
            if stock is not None:
                ttk.Label(body, text=f"Stock: {stock}", style="Muted.TLabel").pack(anchor="w")

            fila = ttk.Frame(body); fila.pack(fill="x", pady=6)
            ttk.Button(fila, text="Agregar", style="Primary.TButton",
                       command=lambda n=nombre, p=precio or 0: self.agregar_producto(n, p)).pack(side="left")
            ttk.Button(fila, text="+1", width=4,
                       command=lambda n=nombre, p=precio or 0: self.agregar_producto(n, p)).pack(side="left", padx=6)
            ttk.Button(fila, text="+5", width=4,
                       command=lambda n=nombre, p=precio or 0: self.agregar_producto(n, p, cantidad=5)).pack(side="left")

        for c in range(cols):
            self.scroll_prod.inner.grid_columnconfigure(c, weight=1)

    def agregar_producto(self, nombre, precio, cantidad=1):
        item = self.carrito.get(nombre)
        if item:
            item["cantidad"] += cantidad
        else:
            self.carrito[nombre] = {"precio": float(precio or 0), "cantidad": int(cantidad)}
        self._refrescar_carrito()

    def _refrescar_carrito(self):
        for i in self.tv.get_children():
            self.tv.delete(i)
        total = 0
        for nombre, data in sorted(self.carrito.items()):
            cant = data["cantidad"]
            precio = data["precio"]
            subtotal = cant * precio
            total += subtotal
            self.tv.insert("", "end", iid=nombre,
                           values=(nombre, cant, fmt_moneda(precio), fmt_moneda(subtotal)))
        self.lbl_total.config(text=f"Total: {fmt_moneda(total)}")

    def eliminar_seleccion(self):
        sel = self.tv.selection()
        if not sel:
            return
        for iid in sel:
            self.carrito.pop(iid, None)
        self._refrescar_carrito()

    def incrementar_seleccion(self):
        sel = self.tv.selection()
        if not sel:
            return
        for iid in sel:
            self.carrito[iid]["cantidad"] += 1
        self._refrescar_carrito()

    def decrementar_seleccion(self):
        sel = self.tv.selection()
        if not sel:
            return
        for iid in sel:
            self.carrito[iid]["cantidad"] -= 1
            if self.carrito[iid]["cantidad"] <= 0:
                self.carrito.pop(iid)
        self._refrescar_carrito()

    def vaciar_carrito(self):
        if not self.carrito:
            return
        if messagebox.askyesno("Vaciar carrito", "¿Seguro que quieres vaciar el carrito?"):
            self.carrito.clear()
            self._refrescar_carrito()

    # --------- Ventanas de productos ----------
    def ingresar_productos(self):
        try:
            win = tk.Toplevel(self.root); win.title("Ingresar productos"); win.geometry("520x460")
            cont = tk.Frame(win, padx=12, pady=12); cont.pack(fill="both", expand=True)
            interfaz_registro_producto(
                frame_destino=cont,
                categorias=self.CATEGORIAS,
                categoria_inicial=self.categoria_actual
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ventana.\n{str(e)}")

    def editar_productos(self):
        try:
            win = tk.Toplevel(self.root); win.title("Buscar/Editar productos"); win.geometry("900x540")
            cont = tk.Frame(win, padx=12, pady=12); cont.pack(fill="both", expand=True)
            interfaz_admin_productos(
                frame_destino=cont,
                categorias=self.CATEGORIAS,
                categoria_inicial=self.categoria_actual,
                on_saved=lambda cat: self.mostrar_productos(cat) if cat else None
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el administrador.\n{str(e)}")

    # --------- Inventario ----------
    def ventana_inventario(self):
        ensure_stock_column()

        win = tk.Toplevel(self.root)
        win.title("Inventario")
        win.geometry("920x560")

        top = ttk.Frame(win); top.pack(fill="x", padx=10, pady=8)

        # categorías dinámicas desde la BD
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cats_db = [r[0] for r in cur.execute(
            "SELECT DISTINCT categoria FROM productos ORDER BY categoria"
        ).fetchall()]
        con.close()
        categorias = ["Todas"] + (cats_db or self.CATEGORIAS)

        tk.Label(top, text="Categoría:").pack(side="left")
        cat_var = tk.StringVar(value="Todas")
        cb = ttk.Combobox(top, textvariable=cat_var, values=categorias, width=28, state="readonly")
        cb.pack(side="left", padx=6)

        tk.Label(top, text="Buscar:").pack(side="left", padx=(14, 4))
        buscar_var = tk.StringVar()
        ent_buscar = ttk.Entry(top, textvariable=buscar_var, width=28)
        ent_buscar.pack(side="left")

        auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="Auto-refresco", variable=auto_var).pack(side="left", padx=10)
        ttk.Button(top, text="Refrescar", command=lambda: _refrescar()).pack(side="left", padx=6)

        mid = ttk.Frame(win); mid.pack(fill="both", expand=True, padx=10, pady=6)

        # Treeview agrupado por categoría: columna árbol = producto, columna "stock"
        tree = ttk.Treeview(mid, columns=("stock",), show="tree headings", selectmode="browse")
        tree.heading("#0", text="Producto")
        tree.heading("stock", text="Stock")
        tree.column("#0", width=640, anchor="w")
        tree.column("stock", width=120, anchor="e")

        ysb = ttk.Scrollbar(mid, orient="vertical", command=tree.yview)
        xsb = ttk.Scrollbar(mid, orient="horizontal", command=tree.xview)
        tree.configure(yscroll=ysb.set, xscroll=xsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")
        mid.rowconfigure(0, weight=1)
        mid.columnconfigure(0, weight=1)

        # Panel de acciones
        actions = ttk.Frame(win); actions.pack(fill="x", padx=10, pady=(4, 10))
        tk.Label(actions, text="Cantidad:").pack(side="left")
        qty_var = tk.StringVar(value="1")
        ttk.Entry(actions, textvariable=qty_var, width=10).pack(side="left", padx=6)

        def _sel_producto():
            sel = tree.selection()
            if not sel:
                return None
            iid = sel[0]
            # ignorar nodos de categoría (no tienen parent vacío?)
            if tree.parent(iid) == "":
                return None
            return tree.item(iid, "text")  # nombre en la columna árbol

        def _parse_qty():
            try:
                q = int(qty_var.get().strip())
                if q < 0:
                    raise ValueError
                return q
            except Exception:
                messagebox.showwarning("Cantidad inválida", "Ingresa un número entero ≥ 0.")
                return None

        def _ajustar(delta=None, fijar=None):
            nombre = _sel_producto()
            if not nombre:
                messagebox.showinfo("Inventario", "Selecciona un producto primero.")
                return
            q = _parse_qty()
            if q is None:
                return
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            try:
                if delta is not None:
                    # entrada/salida
                    cur.execute(
                        "UPDATE productos SET stock = MAX(COALESCE(stock,0) + ?, 0) WHERE nombre=?",
                        (delta * q, nombre),
                    )
                elif fijar is not None:
                    cur.execute(
                        "UPDATE productos SET stock = ? WHERE nombre=?",
                        (fijar, nombre),
                    )
                con.commit()
            finally:
                con.close()
            _refrescar()

        ttk.Button(actions, text="Entrar (+)", command=lambda: _ajustar(delta=+1)).pack(side="left", padx=4)
        ttk.Button(actions, text="Salir (–)",  command=lambda: _ajustar(delta=-1)).pack(side="left", padx=4)
        ttk.Button(actions, text="Fijar (=)",  command=lambda: _ajustar(fijar=_parse_qty() or 0)).pack(side="left", padx=8)

        # --- refresco de la grilla ---
        def _refrescar():
            tree.delete(*tree.get_children())
            cat = cat_var.get()
            buscar = buscar_var.get().strip()
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            if cat == "Todas":
                if buscar:
                    cur.execute(
                        """SELECT categoria, nombre, COALESCE(stock,0)
                           FROM productos
                           WHERE nombre LIKE ?
                           ORDER BY categoria, nombre""",
                        (f"%{buscar}%",),
                    )
                else:
                    cur.execute(
                        """SELECT categoria, nombre, COALESCE(stock,0)
                           FROM productos
                           ORDER BY categoria, nombre"""
                    )
            else:
                if buscar:
                    cur.execute(
                        """SELECT categoria, nombre, COALESCE(stock,0)
                           FROM productos
                           WHERE categoria=? AND nombre LIKE ?
                           ORDER BY nombre""",
                        (cat, f"%{buscar}%",),
                    )
                else:
                    cur.execute(
                        """SELECT categoria, nombre, COALESCE(stock,0)
                           FROM productos
                           WHERE categoria=?
                           ORDER BY nombre""",
                        (cat,),
                    )
            rows = cur.fetchall()
            con.close()

            # agrupar por categoría
            padres = {}
            for categoria, nombre, stock in rows:
                if categoria not in padres:
                    padres[categoria] = tree.insert("", "end", text=categoria, values=("",), open=True)
                tree.insert(padres[categoria], "end", text=nombre, values=(stock,))

        cb.bind("<<ComboboxSelected>>", lambda e: _refrescar())
        ent_buscar.bind("<KeyRelease>", lambda e: _refrescar())

        _refrescar()

        # auto refresco periódico
        def _loop_auto():
            if not win.winfo_exists():
                return
            if auto_var.get():
                _refrescar()
            win.after(2000, _loop_auto)

        win.after(2000, _loop_auto)

    # --------- Venta ----------
    def finalizar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Aviso", "No hay productos en la venta.")
            return

        con = sqlite3.connect(db_path)
        cur = con.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for nombre, data in self.carrito.items():
            cantidad = data["cantidad"]
            total = data["precio"] * cantidad
            cur.execute("INSERT INTO ventas (producto, cantidad, total, fecha) VALUES (?,?,?,?)",
                        (nombre, cantidad, total, fecha_actual))
            try:
                cur.execute("UPDATE productos SET stock = MAX(COALESCE(stock,0) - ?, 0) WHERE nombre=?",
                            (cantidad, nombre))
            except sqlite3.OperationalError:
                # por si no existe stock (muy raro si ensure_stock_column corrió)
                pass

        con.commit(); con.close()
        self.carrito.clear(); self._refrescar_carrito()
        messagebox.showinfo("Venta registrada", "La venta ha sido finalizada exitosamente.")

    def exportar_reportes(self):
        messagebox.showinfo("Exportar reportes", "Función aún en desarrollo.")


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TiendaApp(root)
    root.mainloop()













