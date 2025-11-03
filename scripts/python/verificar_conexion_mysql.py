"""Módulo de ayuda para obtener una conexión a MySQL usando mysql-connector-python.

Provee:
 - get_connection(...): devuelve una tupla (connection | None, success: bool)
 - ejemplo de uso en __main__ para comprobar la conexión interactiva.

Notas: las credenciales no deben dejarse en código en producción; usar variables de entorno o un gestor de secretos.
"""
from typing import Optional, Tuple
import mysql.connector
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection


def get_connection(
    host: str = 'localhost',
    port: int = 3307,
    user: str = 'root',
    password: str = 'RFM_root_pass',
    database: str = 'mi_proyecto_rfm',
    connection_timeout: int = 10
    ) -> Tuple[Optional[MySQLConnection], bool]:
    """Intenta establecer y devolver una conexión MySQL.

    Retorna una tupla: (connection, success)
      - connection: objeto MySQLConnection si se pudo conectar, o None si falló
      - success: True si la conexión fue establecida, False en caso contrario

    No lanza la excepción hacia el llamador: captura errores y los convierte en (None, False).
    """
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connection_timeout=connection_timeout,
        )

        if conn.is_connected():
            return conn, True
        else:
            return None, False

    except Error:
        return None, False


if __name__ == '__main__':
    import getpass

    print("Prueba de conexión a MySQL (usa mysql-connector-python)")
    host = input("Host [127.0.0.1]: ").strip() or 'localhost'
    port_input = input("Puerto [3307]: ").strip() or '3307'
    try:
        port = int(port_input)
    except ValueError:
        port = 3307

    user = input("Usuario [root]: ").strip() or 'root'
    password = getpass.getpass("Contraseña: ") or 'RFM_root_pass'
    database = input("Base de datos (opcional): ").strip() or 'mi_proyecto_rfm'

    conn, ok = get_connection(host=host, port=port, user=user, password=password, database=database)
    print(f"Resultado -> success: {ok}, connection object: {conn}")

    if conn and ok:
        try:
            conn.close()
            print("Conexión cerrada correctamente.")
        except Exception:
            pass