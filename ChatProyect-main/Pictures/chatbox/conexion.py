import sqlite3

def create_connection(db_file):
    """Crear una conexión a la base de datos SQLite."""
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        print("Conexión exitosa a SQLite")
    except sqlite3.Error as e:
        print(f"El error '{e}' ocurrió")
    return connection

def execute_sql_script(connection, script_file):
    """Ejecutar un archivo .sql para inicializar la base de datos."""
    try:
        with open(script_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{script_file}' no fue encontrado.")
        return
    except Exception as e:
        print(f"Error al leer el archivo '{script_file}': {e}")
        return

    cursor = connection.cursor()
    try:
        cursor.executescript(sql_script)
        connection.commit()
        print("Sentencias SQL ejecutadas correctamente.")
    except sqlite3.Error as e:
        print(f"El error '{e}' ocurrió al ejecutar las sentencias.")

if __name__ == '__main__':
    db_file = "sisemasexp.db"      # Ruta o nombre de tu base de datos SQLite
    sql_file = "sentencias.sql"    # Archivo con las sentencias SQL para inicializar

    conn = create_connection(db_file)
    if conn:
        execute_sql_script(conn, sql_file)
        conn.close()
