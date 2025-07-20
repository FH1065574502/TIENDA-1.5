# 🛍️ TIENDA-1.5

Aplicación de escritorio en Python con interfaz gráfica (Tkinter) para gestionar ventas de productos, calcular totales diarios y exportar historial a Excel.

## 📦 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Las siguientes librerías:
  - `pandas`
  - `openpyxl` (para exportar a Excel)
  - `tkinter` (viene incluido con Python en Windows)

## 🚀 Instalación

1. **Clona o descarga este repositorio**

2. **Abre una terminal y ubícate en la carpeta del proyecto**:

```bash
cd ruta/a/TIENDA-1.5
```

3. **Instala las dependencias**:

```bash
pip install -r requirements.txt
```

Si no tienes el archivo `requirements.txt`, puedes instalar manualmente:

```bash
pip install pandas openpyxl
```

## 🗃️ Base de datos

El archivo `tienda.db` debe estar ubicado en la misma carpeta que `app.py`. Contiene dos tablas:

- `productos(nombre TEXT, precio REAL)`
- `ventas(producto TEXT, cantidad INTEGER, total REAL, fecha TEXT)`

Si no tienes el archivo, puedes crearlo ejecutando el script de inicialización (no incluido por defecto, pero se puede agregar).

## ▶️ Cómo ejecutar la aplicación

Desde la terminal, ejecuta:

```bash
python app.py
```

Se abrirá una ventana con la interfaz gráfica.

## 🧰 Funcionalidades

- Registrar ventas
- Ver historial de ventas
- Calcular total diario
- Exportar historial a Excel (`historial_ventas.xlsx`)
- Interfaz amigable con Tkinter

## 🐞 Errores comunes

- `ModuleNotFoundError: No module named 'pandas'`  
  → Ejecuta: `pip install pandas openpyxl`

- `sqlite3.OperationalError: no such table: productos`  
  → Asegúrate de que `tienda.db` existe y contiene las tablas necesarias.

## 📁 Estructura del proyecto

```
TIENDA-1.5/
│
├── app.py                 # Archivo principal (interfaz y lógica)
├── tienda.db              # Base de datos SQLite
├── historial_ventas.xlsx  # (Se genera al exportar)
├── requirements.txt       # (Opcional) Lista de dependencias
└── README.md              # Este archivo
```

## 👤 Autor

Proyecto en desarrollo por [Nombre del autor].