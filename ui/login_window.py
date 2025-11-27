import tkinter as tk
from tkinter import messagebox
from business.auth_service import AuthService

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema POS - Login")
        self.geometry("300x250")
        self.resizable(False, False)
        
        self.auth_service = AuthService()
        self.usuario_autenticado = None

        tk.Label(self, text="INICIO DE SESIÓN", font=("Arial", 14, "bold")).pack(pady=20)

        tk.Label(self, text="Usuario:").pack()
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        tk.Label(self, text="Contraseña:").pack()
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack(pady=5)

        btn_login = tk.Button(self, text="Ingresar", command=self.validar_login, bg="#4CAF50", fg="black")
        btn_login.pack(pady=20, ipadx=20)

    def validar_login(self):
        user = self.entry_user.get()
        password = self.entry_pass.get()

        datos_usuario = self.auth_service.login(user, password)

        if datos_usuario:
            self.usuario_autenticado = datos_usuario
            self.destroy() 
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def iniciar(self):
        """Arranca el loop de la ventana y espera a que se cierre."""
        self.mainloop()
        return self.usuario_autenticado