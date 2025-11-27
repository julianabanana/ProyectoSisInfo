
import tkinter as tk
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DBManager
from ui.login_window import LoginWindow
from ui.admin_window import AdminWindow
from ui.cashier_window import CashierWindow

def main():
    print("Iniciando sistema...")
    
    db = DBManager()
    db.inicializar_db()

    app_login = LoginWindow()

    usuario = app_login.iniciar() 


    if usuario:
        user_id, rol = usuario
        print(f"Login exitoso -> ID: {user_id}, Rol: {rol}")


        if rol == 'admin':
            app = AdminWindow(user_id)
            app.mainloop()
        elif rol == 'cajero':
            app = CashierWindow(user_id)
            app.mainloop()
        else:
            print(f"Rol desconocido: {rol}")
    else:
        print("El usuario cerró la ventana de login o no se autenticó.")

if __name__ == "__main__":
    main()