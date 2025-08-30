# productos.py
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# -----------------------------
# Ruta única de la base de datos (compartida por toda la app)
# -----------------------------
db_path = os.path.join(os.path.dirname(__file__), "tienda.db")


# -----------------------------
# Utilidades de BD
# -----------------------------
def _get_con():
    return sqlite3.connect(db_path)

def _get_cols(cur):
    return [c[1] for c in cur.execute("PRAGMA table_info(productos)")]

def ensure_schema():
    """
    Crea la tabla productos si no existe y agrega columnas faltantes.
    Mantenemos compatibilidad con esquemas viejos.
    """
    con = _get_con()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            precio REAL NOT NULL DEFAULT 0,      -- compatibilidad: algunos usan 'precio'
            costo REAL NOT NULL DEFAULT 0,
            categoria TEXT NOT NULL,
            precio_venta REAL,                   -- precio preferido por la UI
            stock INTEGER DEFAULT 0
        )
    """)
    cols = _get_cols(cur)
    if "precio_venta" not in cols:
        cur.execute("ALTER TABLE productos ADD COLUMN precio_venta REAL")
    if "stock" not in cols:
        cur.execute("ALTER TABLE productos ADD COLUMN stock INTEGER DEFAULT 0")
    con.commit()
    con.close()

ensure_schema()


# -----------------------------
# Operaciones CRUD
# -----------------------------
def agregar_o_actualizar_producto(nombre, costo, precio, categoria, stock=None, rowid=None):
    """
    Inserta o actualiza un producto.
    - Si rowid está, actualiza por id.
    - Si no, intenta insertar; si el nombre ya existe, actualiza por nombre.
    Siempre escribe tanto 'precio' como 'precio_venta' para compatibilidad.
    """
    con = _get_con()
    cur = con.cursor()
    cols = _get_cols(cur)

    # Valores definitivos
    val_stock = int(stock) if (stock is not None and str(stock).strip() != "") else None
    precio = float(precio)
    costo = float(costo)

    try:
        if rowid:  # actualizar por id conocido
            if "stock" in cols and val_stock is not None:
                cur.execute(
                    "UPDATE productos SET nombre=?, categoria=?, costo=?, precio=?, precio_venta=?, stock=? WHERE id=?",
                    (nombre, categoria, costo, precio, precio, val_stock, rowid)
                )
            else:
                cur.execute(
                    "UPDATE productos SET nombre=?, categoria=?, costo=?, precio=?, precio_venta=? WHERE id=?",
                    (nombre, categoria, costo, precio, precio, rowid)
                )
        else:
            # intentar insertar
            if "stock" in cols and val_stock is not None:
                cur.execute(
                    "INSERT INTO productos (nombre, categoria, costo, precio, precio_venta, stock) VALUES (?,?,?,?,?,?)",
                    (nombre, categoria, costo, precio, precio, val_stock)
                )
            else:
                cur.execute(
                    "INSERT INTO productos (nombre, categoria, costo, precio, precio_venta) VALUES (?,?,?,?,?)",
                    (nombre, categoria, costo, precio, precio)
                )

    except sqlite3.IntegrityError:
        # nombre ya existe -> actualizar por nombre
        if "stock" in cols and val_stock is not None:
            cur.execute(
                "UPDATE productos SET categoria=?, costo=?, precio=?, precio_venta=?, stock=? WHERE nombre=?",
                (categoria, costo, precio, precio, val_stock, nombre)
            )
        else:
            cur.execute(
                "UPDATE productos SET categoria=?, costo=?, precio=?, precio_venta=? WHERE nombre=?",
                (categoria, costo, precio, precio, nombre)
            )

    con.commit()
    con.close()


def borrar_producto_por_id(rowid):
    con = _get_con()
    cur = con.cursor()
    cur.execute("DELETE FROM productos WHERE id=?", (rowid,))
    con.commit()
    con.close()


def buscar_productos(texto=""):
    """
    Devuelve lista de tuplas:
    (id, nombre, categoria, costo, precio_mostrar, stock)
    donde precio_mostrar = COALESCE(precio_venta, precio)
    """
    con = _get_con()
    cur = con.cursor()
    like = f"%{texto}%"
    try:
        rows = cur.execute(
            """SELECT id, nombre, categoria, costo,
                      COALESCE(precio_venta, precio) AS precio_mostrar,
                      stock
               FROM productos
               WHERE nombre LIKE ? OR categoria LIKE ?
               ORDER BY nombre ASC""",
            (like, like)
        ).fetchall()
    except sqlite3.OperationalError:
        # esquemas muy viejos sin stock
        rows = cur.execute(
            """SELECT id, nombre, categoria, costo,
                      COALESCE(precio_venta, precio) AS precio_mostrar,
                      NULL as stock
               FROM productos
               WHERE nombre LIKE ? OR categoria LIKE ?
               ORDER BY nombre ASC""",
            (like, like)
        ).fetchall()
    con.close()
    return rows


# -----------------------------
# UI: Registrar nuevo producto (simple)
# -----------------------------
def interfaz_registro_producto(frame_destino, categorias, categoria_inicial=None):
    for w in frame_destino.winfo_children():
        w.destroy()

    # Título
    tk.Label(frame_destino, text="Registrar nuevo producto",
             font=("Segoe UI", 16, "bold")).pack(pady=8)

    # Entradas
    entries = {}
    def fila(label):
        tk.Label(frame_destino, text=label, anchor="w").pack(fill="x", pady=(8, 2))
        e = tk.Entry(frame_destino)
        e.pack(fill="x")
        return e

    entries["nombre"] = fila("Nombre del producto")
    entries["costo"]  = fila("Costo (compra)")
    entries["precio"] = fila("Precio de venta")

    # Categoría (radio en grid)
    tk.Label(frame_destino, text="Categoría", anchor="w").pack(fill="x", pady=(10,2))
    cat_var = tk.StringVar(value=categoria_inicial or (categorias[0] if categorias else "Otros"))
    frame_cats = tk.Frame(frame_destino, bg="#f3f4f6")
    frame_cats.pack(fill="x", pady=(0,8))
    for i, cat in enumerate(categorias):
        tk.Radiobutton(frame_cats, text=cat, value=cat, variable=cat_var, bg="#f3f4f6")\
            .grid(row=i//2, column=i%2, sticky="w", padx=8, pady=4)

    entries["stock"] = fila("Stock (opcional)")

    # Botón
    def registrar():
        nombre = entries["nombre"].get().strip()
        costo  = entries["costo"].get().strip()
        precio = entries["precio"].get().strip()
        stock  = entries["stock"].get().strip()
        categoria = cat_var.get()

        if not nombre or not costo or not precio or not categoria:
            messagebox.showerror("Error", "Todos los campos (excepto stock) son obligatorios.")
            return
        try:
            costo = float(costo)
            precio = float(precio)
        except ValueError:
            messagebox.showerror("Error", "Costo y precio deben ser numéricos.")
            return

        agregar_o_actualizar_producto(nombre, costo, precio, categoria, stock if stock else None, rowid=None)
        messagebox.showinfo("OK", f"Producto '{nombre}' guardado.")
        for e in entries.values():
            e.delete(0, tk.END)

    tk.Button(frame_destino, text="Registrar producto",
              bg="#22c55e", fg="white", font=("Segoe UI", 11, "bold"),
              padx=10, pady=6, command=registrar)\
        .pack(pady=12)


# -----------------------------
# UI: Administrar (buscar/editar) productos
# -----------------------------
def interfaz_admin_productos(frame_destino, categorias, categoria_inicial=None, on_saved=None):
    """
    Ventana con buscador + tabla + formulario para editar/crear.
    """
    for w in frame_destino.winfo_children():
        w.destroy()

    # -------- Top: búsqueda ----------
    top = tk.Frame(frame_destino)
    top.pack(fill="x")
    tk.Label(top, text="Buscar: ").pack(side="left", padx=(0,4))
    var_busca = tk.StringVar()
    ent_busca = tk.Entry(top, textvariable=var_busca, width=40)
    ent_busca.pack(side="left", pady=6)
    btn_buscar = tk.Button(top, text="Refrescar", command=lambda: cargar_tabla(var_busca.get()))
    btn_buscar.pack(side="left", padx=6)
    tk.Label(top, text="(por nombre o categoría)").pack(side="left")

    # -------- Centro: tabla + formulario ----------
    center = tk.Frame(frame_destino)
    center.pack(fill="both", expand=True, pady=(6,0))

    # Tabla
    cols = ("id","nombre","categoria","costo","precio","stock")
    tv = ttk.Treeview(center, columns=cols, show="headings", height=12)
    tv.heading("id", text="ID");          tv.column("id", width=40, anchor="e")
    tv.heading("nombre", text="Nombre");  tv.column("nombre", width=200, anchor="w")
    tv.heading("categoria", text="Categoría"); tv.column("categoria", width=140, anchor="w")
    tv.heading("costo", text="Costo");    tv.column("costo", width=70, anchor="e")
    tv.heading("precio", text="Precio");  tv.column("precio", width=70, anchor="e")
    tv.heading("stock", text="Stock");    tv.column("stock", width=60, anchor="e")
    tv.pack(side="left", fill="both", expand=True)

    sb = ttk.Scrollbar(center, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sb.set)
    sb.pack(side="left", fill="y")

    # Formulario
    form = tk.Frame(center, padx=10)
    form.pack(side="left", fill="y")

    def fila(label, width=28):
        tk.Label(form, text=label, anchor="w").pack(fill="x", pady=(6,2))
        e = tk.Entry(form, width=width)
        e.pack(fill="x")
        return e

    ent_id     = fila("ID (solo lectura)"); ent_id.config(state="readonly")
    ent_nombre = fila("Nombre")
    ent_costo  = fila("Costo")
    ent_precio = fila("Precio de venta")
    tk.Label(form, text="Categoría", anchor="w").pack(fill="x", pady=(6,2))
    cat_var = tk.StringVar(value=categoria_inicial or (categorias[0] if categorias else "Otros"))
    frame_cats = tk.Frame(form, bg="#f3f4f6"); frame_cats.pack(fill="x", pady=(0,8))
    for i, cat in enumerate(categorias):
        tk.Radiobutton(frame_cats, text=cat, value=cat, variable=cat_var, bg="#f3f4f6")\
            .grid(row=i//2, column=i%2, sticky="w", padx=6, pady=3)
    ent_stock  = fila("Stock (opcional)")

    # Botones
    btns = tk.Frame(form); btns.pack(fill="x", pady=6)
    btn_nuevo = tk.Button(btns, text="Nuevo", width=9)
    btn_guardar = tk.Button(btns, text="Guardar", width=9, bg="#2563eb", fg="white")
    btn_eliminar = tk.Button(btns, text="Eliminar", width=9, bg="#ef4444", fg="white")
    btn_nuevo.pack(side="left", padx=3); btn_guardar.pack(side="left", padx=3); btn_eliminar.pack(side="left", padx=3)

    # -------- Lógica --------
    def cargar_tabla(texto=""):
        tv.delete(*tv.get_children())
        for row in buscar_productos(texto):
            rid, nombre, categoria, costo, precio, stock = row
            tv.insert("", "end", iid=str(rid),
                      values=(rid, nombre, categoria, f"{costo:.0f}", f"{precio:.0f}", "" if stock is None else stock))

    def limpiar_form():
        ent_id.config(state="normal"); ent_id.delete(0, tk.END); ent_id.config(state="readonly")
        ent_nombre.delete(0, tk.END)
        ent_costo.delete(0, tk.END)
        ent_precio.delete(0, tk.END)
        ent_stock.delete(0, tk.END)
        if categorias:
            cat_var.set(categorias[0])

    def cargar_desde_tabla(_=None):
        sel = tv.selection()
        if not sel: return
        rowid = int(sel[0])
        vals = tv.item(sel[0], "values")
        # values: (id, nombre, categoria, costo, precio, stock)
        ent_id.config(state="normal"); ent_id.delete(0, tk.END); ent_id.insert(0, vals[0]); ent_id.config(state="readonly")
        ent_nombre.delete(0, tk.END); ent_nombre.insert(0, vals[1])
        cat_var.set(vals[2])
        ent_costo.delete(0, tk.END); ent_costo.insert(0, vals[3])
        ent_precio.delete(0, tk.END); ent_precio.insert(0, vals[4])
        ent_stock.delete(0, tk.END); ent_stock.insert(0, vals[5] if vals[5] is not None else "")

    def guardar():
        nombre = ent_nombre.get().strip()
        costo  = ent_costo.get().strip()
        precio = ent_precio.get().strip()
        stock  = ent_stock.get().strip()
        cat    = cat_var.get()
        rid    = ent_id.get().strip()
        if not nombre or not costo or not precio:
            messagebox.showerror("Error", "Nombre, costo y precio son obligatorios.")
            return
        try:
            float(costo); float(precio)
        except ValueError:
            messagebox.showerror("Error", "Costo y precio deben ser numéricos.")
            return

        agregar_o_actualizar_producto(
            nombre=nombre,
            costo=costo,
            precio=precio,
            categoria=cat,
            stock=stock if stock else None,
            rowid=int(rid) if rid else None
        )
        cargar_tabla(var_busca.get())
        if on_saved:
            try:
                on_saved(cat)
            except Exception:
                pass
        messagebox.showinfo("OK", "Producto guardado.")

    def eliminar():
        sel = tv.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un producto en la tabla.")
            return
        if not messagebox.askyesno("Eliminar", "¿Eliminar el producto seleccionado?"):
            return
        borrar_producto_por_id(int(sel[0]))
        limpiar_form()
        cargar_tabla(var_busca.get())
        if on_saved:
            try:
                on_saved(None)
            except Exception:
                pass

    btn_nuevo.config(command=limpiar_form)
    btn_guardar.config(command=guardar)
    btn_eliminar.config(command=eliminar)
    tv.bind("<<TreeviewSelect>>", cargar_desde_tabla)
    tv.bind("<Double-1>", cargar_desde_tabla)

    # Carga inicial
    if categoria_inicial:
        var_busca.set(categoria_inicial)
    cargar_tabla(var_busca.get())
    ent_busca.focus_set()

