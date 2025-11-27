import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from business.auth_service import AuthService
from business.sales_service import SalesService

class AdminWindow(tk.Tk):
    def __init__(self, usuario_id):
        super().__init__()
        self.usuario_id = usuario_id
        self.auth_service = AuthService()
        self.sales_service = SalesService()
        
        self.title("Administración del Sistema")
        self.geometry("900x650")
        
        # Estilos visuales básicos
        style = ttk.Style()
        style.configure("KPI.TLabel", font=("Arial", 24, "bold"), foreground="#2E7D32")
        style.configure("KPITitle.TLabel", font=("Arial", 10), foreground="gray")
        
        # Notebook (Pestañas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._init_tab_dashboard()
        self._init_tab_usuarios()

    # --- PESTAÑA 1: DASHBOARD Y ESTADÍSTICAS ---
    def _init_tab_dashboard(self):
        frame_dash = ttk.Frame(self.notebook)
        self.notebook.add(frame_dash, text="Resumen y Estadísticas")
        
        # 1. Tarjetas de KPI (Key Performance Indicators)
        frame_kpis = ttk.Frame(frame_dash)
        frame_kpis.pack(fill=tk.X, pady=20, padx=20)
        
        # KPI: Ventas Hoy
        kpi1 = tk.LabelFrame(frame_kpis, text="Ventas de Hoy", bg="white", padx=20, pady=10)
        kpi1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.lbl_ventas_hoy = ttk.Label(kpi1, text="$0", style="KPI.TLabel", background="white")
        self.lbl_ventas_hoy.pack()
        
        # KPI: Producto Top
        kpi2 = tk.LabelFrame(frame_kpis, text="Producto Más Vendido", bg="white", padx=20, pady=10)
        kpi2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.lbl_prod_top = ttk.Label(kpi2, text="---", style="KPI.TLabel", background="white")
        self.lbl_prod_top.config(font=("Arial", 16, "bold")) # Un poco más pequeño si el nombre es largo
        self.lbl_prod_top.pack()

        # 2. Gráfica (Canvas manual)
        lbl_graph = ttk.Label(frame_dash, text="Histórico de Ventas (Últimos 7 días)", font=("Arial", 12, "bold"))
        lbl_graph.pack(pady=(20, 5))
        
        self.canvas = tk.Canvas(frame_dash, bg="white", height=300, bd=2, relief="groove")
        self.canvas.pack(fill=tk.X, padx=30, pady=10)
        
        # Botón actualizar
        ttk.Button(frame_dash, text="Actualizar Datos", command=self.cargar_datos_dashboard).pack(pady=10)
        
        # Cargar datos iniciales
        self.after(500, self.cargar_datos_dashboard)

    def cargar_datos_dashboard(self):
        # 1. Cargar Textos
        total_hoy = self.sales_service.obtener_kpi_hoy()
        mejor_prod = self.sales_service.obtener_mejor_producto()
        
        self.lbl_ventas_hoy.config(text=f"${total_hoy:,.0f}")
        self.lbl_prod_top.config(text=mejor_prod)
        
        # 2. Dibujar Gráfica
        self.canvas.delete("all")
        datos = self.sales_service.obtener_ventas_grafica() # [(fecha, total), ...]
        
        if not datos:
            self.canvas.create_text(400, 150, text="No hay ventas recientes", fill="gray")
            return

        # Dimensiones
        w = self.canvas.winfo_width()
        h = 300
        margen = 40
        ancho_barra = 60
        sep = 30
        
        max_val = max(d[1] for d in datos) if datos else 1
        factor_h = (h - 2*margen) / max_val

        x = margen
        for fecha, total in datos:
            alto = total * factor_h
            x0 = x
            y0 = h - margen - alto
            x1 = x + ancho_barra
            y1 = h - margen
            
            # Barra
            color = "#4CAF50" if total == max_val else "#81C784"
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            
            # Valor encima
            self.canvas.create_text((x0+x1)/2, y0-10, text=f"${total:.0f}", font=("Arial", 9, "bold"))
            
            # Fecha debajo (MM-DD)
            dia = fecha[5:] 
            self.canvas.create_text((x0+x1)/2, y1+15, text=dia, font=("Arial", 8))
            
            x += ancho_barra + sep

    # --- PESTAÑA 2: GESTIÓN DE USUARIOS ---
    def _init_tab_usuarios(self):
        frame_users = ttk.Frame(self.notebook)
        self.notebook.add(frame_users, text="Gestión de Usuarios")
        
        # Formulario Crear
        f_crear = ttk.LabelFrame(frame_users, text="Crear Nuevo Usuario", padding=15)
        f_crear.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(f_crear, text="Usuario:").grid(row=0, column=0, padx=5)
        self.entry_user = ttk.Entry(f_crear)
        self.entry_user.grid(row=0, column=1, padx=5)
        
        ttk.Label(f_crear, text="Contraseña:").grid(row=0, column=2, padx=5)
        self.entry_pass = ttk.Entry(f_crear)
        self.entry_pass.grid(row=0, column=3, padx=5)
        
        ttk.Label(f_crear, text="Rol:").grid(row=0, column=4, padx=5)
        self.combo_rol = ttk.Combobox(f_crear, values=["cajero", "admin"], state="readonly", width=10)
        self.combo_rol.current(0)
        self.combo_rol.grid(row=0, column=5, padx=5)
        
        ttk.Button(f_crear, text="Crear Usuario", command=self.crear_usuario).grid(row=0, column=6, padx=20)
        
        # Lista de Usuarios
        cols = ("ID", "Usuario", "Rol")
        self.tree = ttk.Treeview(frame_users, columns=cols, show="headings", height=10)
        for c in cols: self.tree.heading(c, text=c)
        self.tree.column("ID", width=50, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Botones de Acción (Editar/Borrar)
        frame_acc = ttk.Frame(frame_users)
        frame_acc.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(frame_acc, text="Cambiar Contraseña", command=self.cambiar_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acc, text="Eliminar Usuario", command=self.borrar_usuario).pack(side=tk.RIGHT, padx=5)
        
        self.cargar_usuarios()

    def cargar_usuarios(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for u in self.auth_service.obtener_todos_los_usuarios():
            self.tree.insert("", "end", values=u)

    def crear_usuario(self):
        u = self.entry_user.get()
        p = self.entry_pass.get()
        r = self.combo_rol.get()
        
        if u and p:
            ok, msg = self.auth_service.crear_usuario(u, p, r)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.entry_user.delete(0, tk.END)
                self.entry_pass.delete(0, tk.END)
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", msg)
        else:
            messagebox.showwarning("Atención", "Complete todos los campos")

    def borrar_usuario(self):
        sel = self.tree.selection()
        if not sel: return
        
        item = self.tree.item(sel[0])
        uid, uname, urol = item['values']
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario '{uname}'?"):
            ok, msg = self.auth_service.eliminar_usuario(uid)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", msg)

    def cambiar_password(self):
        sel = self.tree.selection()
        if not sel: 
            messagebox.showwarning("!", "Seleccione un usuario de la lista")
            return
            
        item = self.tree.item(sel[0])
        uid, uname, _ = item['values']
        
        new_pass = simpledialog.askstring("Cambiar Contraseña", f"Nueva contraseña para '{uname}':", parent=self)
        if new_pass:
            ok, msg = self.auth_service.actualizar_contrasena(uid, new_pass)
            messagebox.showinfo("Resultado", msg)