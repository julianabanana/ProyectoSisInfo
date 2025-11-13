import csv

class AuthService:

    @staticmethod
    def validar_usuario(usuario, password):
        with open("data/usuarios.csv", newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["usuario"] == usuario and row["password"] == password:
                    return row["tipo"]   # devuelve rol
        return None