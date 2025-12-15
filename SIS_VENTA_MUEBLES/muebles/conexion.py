import mysql.connector
from mysql.connector import Error

class ConexionDB:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "sistema_venta_muebles"

    def conectar(self):
        try:
            conexion = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if conexion.is_connected():
                return conexion
        except Error as e:
            print(f"❌ Error al conectar con la base de datos: {e}")
        return None

    def cerrar(self, conexion):
        try:
            if conexion and getattr(conexion, "is_connected", lambda: False)():
                conexion.close()
        except Exception:
            pass