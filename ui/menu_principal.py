import tkinter as tk

def abrir_menu_principal(usuario, rol):
    win = tk.Tk()
    win.title("Menú Principal - POS")
    win.geometry("400x400")

    tk.Label(win, text=f"Bienvenida, {usuario}").pack(pady=20)
    tk.Label(win, text=f"Rol: {rol.upper()}").pack(pady=10)

    if rol == "cajero":
        tk.Button(win, text="Registrar Ventas").pack(pady=10)

    if rol == "encargado":
        tk.Button(win, text="Realizar Cierre de Caja").pack(pady=10)

    if rol == "admin":
        tk.Button(win, text="Ver Reportes").pack(pady=10)

    win.mainloop()
