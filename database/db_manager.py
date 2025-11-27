import sqlite3
import os

class DBManager:
    def __init__(self, db_name="tienda.db"):
        self.db_name = db_name
        self.conexion = None
        self.cursor = None

    def conectar(self):
        try:
            self.conexion = sqlite3.connect(self.db_name)
            self.cursor = self.conexion.cursor()
            self.conexion.execute("PRAGMA foreign_keys = 1")
            return True
        except sqlite3.Error as e:
            print(f"Error conectando a la BD: {e}")
            return False

    def cerrar(self):
        if self.conexion:
            self.conexion.close()

    def ejecutar_consulta(self, sql, parametros=()):
        try:
            self.conectar()
            self.cursor.execute(sql, parametros)
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error ejecución SQL: {e}")
            return False
        finally:
            self.cerrar()

    def obtener_datos(self, sql, parametros=()):
        try:
            self.conectar()
            self.cursor.execute(sql, parametros)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error obteniendo datos: {e}")
            return []
        finally:
            self.cerrar()

    def inicializar_db(self):
        print("Verificando integridad de la base de datos...")
        self.conectar()
        
 
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                rol TEXT NOT NULL CHECK(rol IN ('admin', 'cajero'))
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                imagen TEXT,
                categoria TEXT -- Campo opcional para ordenar mejor en el futuro
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                cedula TEXT PRIMARY KEY,
                nombre TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                cliente_cedula TEXT,
                total REAL NOT NULL,
                usuario_id INTEGER,
                FOREIGN KEY(cliente_cedula) REFERENCES clientes(cedula),
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER,
                producto_id INTEGER,
                cantidad INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY(venta_id) REFERENCES ventas(id),
                FOREIGN KEY(producto_id) REFERENCES productos(id)
            )
        """)
        
        # --- USUARIOS (Solo si no existen) ---
        self.cursor.execute("SELECT count(*) FROM usuarios")
        if self.cursor.fetchone()[0] == 0:
            print("Creando usuarios iniciales...")
            self.cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)", ('admin', 'admin', 'admin'))
            self.cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)", ('cajero1', '1234', 'cajero'))
        

        self.cursor.execute("SELECT count(*) FROM productos")
        if self.cursor.fetchone()[0] == 0:
            print("Tabla vacía. Cargando menú de productos inicial...")

            productos_menu = [
            # Principales
            ('Hamburguesa', 25000.00, 'hamburguesa.png', 'Principal'),
            ('Papas Fritas', 8000.00, 'papas.png', 'Principal'),
            # Bebidas
            ('Gaseosa', 8000.00, 'gaseosa.png', 'Bebida'),
            ('Cerveza', 10000.00, 'cerveza.png', 'Bebida'),
            ('Agua', 5000.00, 'agua.png', 'Bebida'),
            # Panes (Precio 0 o costo adicional si quisieras)
            ('Pan 1 (Normal)', 0.00, 'pan1.png', 'Pan'),
            ('Pan 2 (Artesanal)', 0.00, 'pan2.png', 'Pan'),
            ('Pan 3 (Sesamo)', 0.00, 'pan3.png', 'Pan'),
            ('Pan 4 (Picante)', 0.00, 'pan4.png', 'Pan'),
            # Adicionales (Suman)
            ('Extra Carne', 4000.00, 'carne.png', 'Extra'),
            ('Extra Queso', 2000.00, 'queso.png', 'Extra'),
            ('Extra Tocineta', 3000.00, 'tocineta.png', 'Extra'),
            ('Extra Tomate', 500.00, 'tomate.png', 'Extra'),
            ('Extra Cebolla', 500.00, 'cebolla.png', 'Extra'),
            ('Extra Lechuga', 500.00, 'lechuga.png', 'Extra'),
            ('Extra Pepinillos', 500.00, 'pepinillos.png', 'Extra'),
            # "Sin Ingredientes" (Restan precio, según solicitud)
            ('SIN Cebolla', -0.00, 'cebolla.png', 'Resta'),
            ('SIN Tomate', -0.00, 'tomate.png', 'Resta'),
            ('SIN Lechuga', -0.00, 'lechuga.png', 'Resta'),
            ('SIN Carne', -4000.00, 'carne.png', 'Resta'),
            ('SIN Pepinillos', -0.00, 'pepinillos.png', 'Resta'),
            ('SIN Pan', -0.00, 'pan1.png', 'Resta'),
            # Promociones
            ('COMBO', -3000.00, 'combo.png', 'Promo')

        ]
            self.cursor.executemany("INSERT INTO productos (nombre, precio, imagen, categoria) VALUES (?, ?, ?, ?)", productos_menu)
        else:
            print("Productos ya existentes. Omitiendo carga inicial.")

        self.conexion.commit()
        self.cerrar()