import os
import datetime
from database.db_manager import DBManager

class SalesService:
    def __init__(self):
        self.db = DBManager()
        if not os.path.exists("ventas_logs"):
            os.makedirs("ventas_logs")

    def obtener_productos(self):
        return self.db.obtener_datos("SELECT * FROM productos ORDER BY categoria DESC, nombre ASC")

    def buscar_cliente(self, cedula):
        sql = "SELECT * FROM clientes WHERE cedula = ?"
        res = self.db.obtener_datos(sql, (cedula,))
        return res[0] if res else None

    def crear_cliente(self, cedula, nombre):
        return self.db.ejecutar_consulta("INSERT INTO clientes (cedula, nombre) VALUES (?, ?)", (cedula, nombre))


    def registrar_venta(self, usuario_id, cliente_cedula, carrito):
        if not carrito: return False, "Carrito vacío"
        
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_venta = sum(item['precio'] * item['cantidad'] for item in carrito)
        if total_venta < 0: total_venta = 0

        if not self.db.ejecutar_consulta("INSERT INTO ventas (fecha, cliente_cedula, total, usuario_id) VALUES (?, ?, ?, ?)", 
                                         (fecha_actual, cliente_cedula, total_venta, usuario_id)):
            return False, "Error BD Venta"

        venta_id = self.db.obtener_datos("SELECT MAX(id) FROM ventas WHERE usuario_id = ?", (usuario_id,))[0][0]


        sql_det = "INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, subtotal) VALUES (?, ?, ?, ?)"
        for item in carrito:
            sub = item['precio'] * item['cantidad']
            self.db.ejecutar_consulta(sql_det, (venta_id, item['id'], item['cantidad'], sub))


        cli = self.buscar_cliente(cliente_cedula)
        nom_cli = cli[1] if cli else "Desconocido"
        self._generar_factura_txt(venta_id, fecha_actual, nom_cli, carrito, total_venta)

        return True, f"Venta #{venta_id} registrada."

    def _generar_factura_txt(self, vid, fecha, cliente, carrito, total):
        with open(f"ventas_logs/factura_{vid}.txt", "w", encoding="utf-8") as f:
            f.write(f"FACTURA #{vid}\nFecha: {fecha}\nCliente: {cliente}\n{'-'*20}\n")
            for i in carrito:
                f.write(f"{i['cantidad']} x {i['nombre']} = ${i['precio']*i['cantidad']:.0f}\n")
            f.write(f"{'='*20}\nTOTAL: ${total:.0f}")
    
    def obtener_ventas_grafica(self):
        """Retorna ventas agrupadas por día (últimos 7 días)."""
        sql = "SELECT substr(fecha, 1, 10) as dia, SUM(total) FROM ventas GROUP BY dia ORDER BY dia DESC LIMIT 7"
        return self.db.obtener_datos(sql)

    def obtener_kpi_hoy(self):
        """Retorna el total vendido hoy."""
        hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        sql = "SELECT SUM(total) FROM ventas WHERE substr(fecha, 1, 10) = ?"
        res = self.db.obtener_datos(sql, (hoy,))
        return res[0][0] if res and res[0][0] else 0.0

    def obtener_mejor_producto(self):
        """Retorna el nombre del producto más vendido históricamente."""
        sql = """
            SELECT p.nombre, SUM(d.cantidad) as total_qty
            FROM detalle_ventas d
            JOIN productos p ON d.producto_id = p.id
            GROUP BY p.id
            ORDER BY total_qty DESC
            LIMIT 1
        """
        res = self.db.obtener_datos(sql)
        return f"{res[0][0]} ({res[0][1]} un.)" if res else "N/A"