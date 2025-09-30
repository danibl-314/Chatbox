import sqlite3
import os

# Define el nombre de la base de datos (usando sisemasexp.db como en tu estructura)
DATABASE = 'sisemasexp.db'
# Define la ruta al archivo SQL para la inicialización
SQL_FILE = 'sentencias.sql'

def create_connection():
    """Crea una conexión a la base de datos y asegura UTF-8 para texto."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        # Asegura que el texto se maneje como strings Python (Unicode/UTF-8)
        conn.text_factory = str 
        return conn
    except sqlite3.Error as e:
        print(f"Error de conexión a la base de datos: {e}")
    return conn

def init_db():
    """Inicializa la base de datos creando la tabla 'carrera'."""
    conn = create_connection()
    if conn:
        try:
            sql_file_path = os.path.join(os.path.dirname(__file__), SQL_FILE)
            
            # Asegúrate de usar encoding='utf-8' para leer el script SQL
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            cursor = conn.cursor()
            cursor.executescript(sql_script)
            conn.commit()
            print("Base de datos inicializada correctamente.")
        except FileNotFoundError:
            print(f"Error: El archivo {SQL_FILE} no se encontró.")
        except sqlite3.Error as e:
            print(f"Error al ejecutar script SQL: {e}")
        finally:
            if conn:
                conn.close()

# --- Funciones de Soporte CRUD ---

def get_carrera(carrera_id):
    """Obtiene una carrera por ID, incluyendo todos los campos."""
    conn = create_connection()
    carrera = None
    if conn:
        try:
            cursor = conn.cursor()
            # SELECT debe traer las 4 columnas: id, descripcion, duracion_semestres, precio_semestre
            cursor.execute("SELECT id, descripcion, duracion_semestres, precio_semestre FROM carrera WHERE id = ?", (carrera_id,))
            carrera = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error al obtener carrera por ID: {e}")
        finally:
            if conn:
                conn.close()
    return carrera

def update_carrera(carrera_id, descripcion, duracion, precio):
    """Actualiza todos los campos de una carrera por ID."""
    conn = create_connection()
    success = False
    if conn:
        try:
            cursor = conn.cursor()
            # UPDATE debe actualizar la descripción, duración y precio
            cursor.execute(
                "UPDATE carrera SET descripcion = ?, duracion_semestres = ?, precio_semestre = ? WHERE id = ?",
                (descripcion, duracion, precio, carrera_id)
            )
            conn.commit()
            success = True
        except sqlite3.Error as e:
            print(f"Error al actualizar carrera: {e}")
        finally:
            if conn:
                conn.close()
    return success

def delete_carrera(carrera_id):
    """Elimina una carrera por ID."""
    conn = create_connection()
    success = False
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM carrera WHERE id = ?", (carrera_id,))
            conn.commit()
            success = True
        except sqlite3.Error as e:
            print(f"Error al eliminar carrera: {e}")
        finally:
            if conn:
                conn.close()
    return success