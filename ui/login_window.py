import tkinter as tk
from tkinter import messagebox
from services.auth_service import AuthService
from ui.menu_principal import abrir_menu_principal

def abrir_login():
    root = tk.Tk()
    root.title("Punto de Venta - Login")
    root.geometry("400x500")

    # Logo
    from PIL import Image, ImageTk
    logo_img = Image.open("logo.png")
    logo_img = logo_img.resize((180, 180))
    logo_tk = ImageTk.PhotoImage(logo_img)

    tk.Label(root, image=logo_tk).pack(pady=10)

    # Inputs
    tk.Label(root, text="Usuario").pack()
    usuario_entry = tk.Entry(root)
    usuario_entry.pack()

    tk.Label(root, text="Contraseña").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    def login():
        usuario = usuario_entry.get()
        password = password_entry.get()

        rol = AuthService.validar_usuario(usuario, password)

        if rol:
            root.destroy()
            abrir_menu_principal(usuario, rol)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    tk.Button(root, text="Ingresar", command=login).pack(pady=20)

    root.mainloop()

