from database.db_manager import DBManager

class AuthService:
    def __init__(self):
        self.db = DBManager()

    def login(self, username, password):
        """Verifica credenciales. Retorna (id, rol) o None."""
        sql = "SELECT id, rol FROM usuarios WHERE username = ? AND password = ?"
        resultados = self.db.obtener_datos(sql, (username, password))
        if resultados:
            return resultados[0] 
        return None

    def crear_usuario(self, username, password, rol):
        """Crea un nuevo usuario."""
        # Verificar duplicados
        check_sql = "SELECT id FROM usuarios WHERE username = ?"
        if self.db.obtener_datos(check_sql, (username,)):
            return False, "El usuario ya existe."

        sql = "INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)"
        if self.db.ejecutar_consulta(sql, (username, password, rol)):
            return True, "Usuario creado exitosamente."
        return False, "Error en BD."

    def obtener_todos_los_usuarios(self):
        """Lista todos los usuarios (ID, Nombre, Rol)."""
        sql = "SELECT id, username, rol FROM usuarios"
        return self.db.obtener_datos(sql)

    def eliminar_usuario(self, user_id):
        """Elimina usuario por ID (protege al admin principal)."""
        if str(user_id) == "1":
            return False, "No puedes eliminar al Admin principal."
            
        sql = "DELETE FROM usuarios WHERE id = ?"
        if self.db.ejecutar_consulta(sql, (user_id,)):
            return True, "Usuario eliminado."
        return False, "Error al eliminar."

    def actualizar_contrasena(self, user_id, nueva_pass):
        """Cambia la contraseña de un usuario."""
        sql = "UPDATE usuarios SET password = ? WHERE id = ?"
        if self.db.ejecutar_consulta(sql, (nueva_pass, user_id)):
            return True, "Contraseña actualizada."
        return False, "Error al actualizar."