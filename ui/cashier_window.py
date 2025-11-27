import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from business.sales_service import SalesService

class CashierWindow(tk.Tk):
    def __init__(self, usuario_id):
        super().__init__()
        self.usuario_id = usuario_id
        self.sales_service = SalesService()
        self.carrito = [] 
        self.cliente_actual = None 
        self.imagenes_ref = [] 

        self.title("Punto de Venta - Cajero")
        self.geometry("1100x700")
        self.state('zoomed') 
        
        self._init_layout()
        self._cargar_productos()

    def _init_layout(self):
   
        self.frame_izq_container = tk.Frame(self)
        self.frame_izq_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame_izq_container, bg="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self.frame_izq_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")


        self.panel_der = tk.Frame(self, bg="white", width=420, bd=2, relief="groove")
        self.panel_der.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        self.panel_der.pack_propagate(False)

        self._setup_panel_derecho()

    def _setup_panel_derecho(self):
        frame_cli = tk.LabelFrame(self.panel_der, text="Cliente", bg="white", padx=5, pady=5)
        frame_cli.pack(fill=tk.X, pady=10, padx=10)

        row1 = tk.Frame(frame_cli, bg="white")
        row1.pack(fill=tk.X)
        self.entry_cedula = ttk.Entry(row1)
        self.entry_cedula.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_cedula.bind('<Return>', lambda e: self.buscar_cliente())
        ttk.Button(row1, text="Buscar", width=6, command=self.buscar_cliente).pack(side=tk.LEFT, padx=(5,0))

        self.lbl_cliente = tk.Label(frame_cli, text="---", fg="blue", bg="white")
        self.lbl_cliente.pack(anchor="w")
        ttk.Button(frame_cli, text="Nuevo Cliente", command=self.registrar_cliente_popup).pack(fill=tk.X)

        # 2. Lista Productos
        tk.Label(self.panel_der, text="Ticket de Venta", bg="white", font=("Arial", 11, "bold")).pack(pady=(10,0))
        
        cols = ("Producto", "Cant", "Total")
        self.tree = ttk.Treeview(self.panel_der, columns=cols, show="headings", height=15)
        self.tree.heading("Producto", text="Item")
        self.tree.heading("Cant", text="#")
        self.tree.heading("Total", text="Valor")
        
        self.tree.column("Producto", width=220)
        self.tree.column("Cant", width=40, anchor="center")
        self.tree.column("Total", width=80, anchor="e")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Button(self.panel_der, text="Quitar Item", command=self.quitar_producto).pack(fill=tk.X, padx=10)

 
        self.lbl_total = tk.Label(self.panel_der, text="TOTAL: $0.00", font=("Arial", 20, "bold"), fg="#d32f2f", bg="white")
        self.lbl_total.pack(pady=10)


        btn_combo = tk.Button(self.panel_der, text="★ APLICAR COMBO", 
                              bg="#FF9800", fg="black", font=("Arial", 10, "bold"),
                              command=self.aplicar_combo_automatico)
        btn_combo.pack(fill=tk.X, padx=10, pady=5)

        btn_cobrar = tk.Button(self.panel_der, text="COBRAR", bg="#4CAF50", fg="black", font=("Arial", 14, "bold"), command=self.cobrar)
        btn_cobrar.pack(fill=tk.X, padx=10, pady=5, ipady=5)
        
        ttk.Button(self.panel_der, text="Limpiar / Cancelar", command=self.limpiar_venta).pack(fill=tk.X, padx=10, pady=5)

    def _cargar_productos(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.imagenes_ref = []

        self.productos_memoria = self.sales_service.obtener_productos()
        
        COLUMNAS = 4 
        
        for i, prod in enumerate(self.productos_memoria):
            p_id, p_nombre, p_precio, p_img, p_cat = prod
            

            bg_color = "white"
            if p_cat == 'Resta': bg_color = "#ffebee" # Rojito
            elif p_cat == 'Extra': bg_color = "#e8f5e9" # Verdoso
            elif p_cat == 'Pan': bg_color = "#fff3e0" # Naranja suave
            elif p_cat == 'Promo': bg_color = "#fffde7" # Amarillo

            frame_btn = tk.Frame(self.scrollable_frame, bg=bg_color, bd=1, relief="raised", width=140, height=140)
            frame_btn.grid_propagate(False)
            
            img_obj = None
            path_img = os.path.join("assets", p_img) if p_img else ""
            if p_img and os.path.exists(path_img):
                try:
                    img_raw = tk.PhotoImage(file=path_img)
                    if img_raw.width() > 100:
                        factor = int(img_raw.width() / 80)
                        img_obj = img_raw.subsample(factor, factor)
                    else:
                        img_obj = img_raw
                    self.imagenes_ref.append(img_obj)
                except: pass

            btn = tk.Button(
                frame_btn, 
                text=f"{p_nombre}\n${p_precio:.0f}",
                image=img_obj, compound="top", font=("Arial", 8, "bold"),
                bg=bg_color, activebackground="#cccccc", relief="flat",
                command=lambda pid=p_id, pnom=p_nombre, ppre=p_precio: self.agregar_al_carrito(pid, pnom, ppre)
            )
            btn.pack(fill=tk.BOTH, expand=True)
            
            fila = i // COLUMNAS
            col = i % COLUMNAS
            frame_btn.grid(row=fila, column=col, padx=5, pady=5)

    def agregar_al_carrito(self, pid, nombre, precio):
        encontrado = False
        for item in self.carrito:
            if item['id'] == pid:
                item['cantidad'] += 1
                encontrado = True
                break
        
        if not encontrado:
            self.carrito.append({'id': pid, 'nombre': nombre, 'precio': precio, 'cantidad': 1})
        
        self._actualizar_ticket()

    def aplicar_combo_automatico(self):
        combo_prod = next((p for p in self.productos_memoria if "COMBO" in p[1]), None)
        if combo_prod:
            self.agregar_al_carrito(combo_prod[0], combo_prod[1], combo_prod[2])
        else:
            messagebox.showinfo("Info", "No se encontró el ítem de combo en la BD")

    def quitar_producto(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            del self.carrito[idx]
            self._actualizar_ticket()

    def _actualizar_ticket(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        total = 0
        for item in self.carrito:
            sub = item['precio'] * item['cantidad']
            total += sub
            self.tree.insert("", "end", values=(item['nombre'], item['cantidad'], f"${sub:.0f}"))
            
        self.lbl_total.config(text=f"TOTAL: ${total:.0f}")

    def buscar_cliente(self):
        cedula = self.entry_cedula.get()
        if not cedula: return
        cliente = self.sales_service.buscar_cliente(cedula)
        if cliente:
            self.cliente_actual = cliente
            self.lbl_cliente.config(text=cliente[1], fg="green")
        else:
            self.cliente_actual = None
            self.lbl_cliente.config(text="No encontrado", fg="red")
            if messagebox.askyesno("Nuevo", "Cliente no existe. ¿Crearlo?"):
                self.registrar_cliente_popup()

    def registrar_cliente_popup(self):
        cedula = simpledialog.askstring("Nuevo", "Cédula:", parent=self)
        if not cedula: return
        nombre = simpledialog.askstring("Nuevo", "Nombre:", parent=self)
        if not nombre: return
        if self.sales_service.crear_cliente(cedula, nombre):
            messagebox.showinfo("OK", "Cliente creado")
            self.entry_cedula.delete(0, tk.END)
            self.entry_cedula.insert(0, cedula)
            self.buscar_cliente()
        else: messagebox.showerror("Error", "No se pudo crear")

    def cobrar(self):
        if not self.carrito: return messagebox.showwarning("!", "Carrito vacío")
        if not self.cliente_actual: return messagebox.showwarning("!", "Seleccione cliente")
        
        total = sum(x['precio']*x['cantidad'] for x in self.carrito)
        if messagebox.askyesno("Cobrar", f"Total: ${total:.0f}\n¿Confirmar?"):
            ok, msg = self.sales_service.registrar_venta(self.usuario_id, self.cliente_actual[0], self.carrito)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.limpiar_venta()
            else: messagebox.showerror("Error", msg)

    def limpiar_venta(self):
        self.carrito = []
        self.cliente_actual = None
        self.entry_cedula.delete(0, tk.END)
        self.lbl_cliente.config(text="---", fg="blue")
        self._actualizar_ticket()