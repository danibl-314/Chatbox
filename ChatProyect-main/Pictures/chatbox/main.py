from flask import Flask, render_template, request, redirect, url_for
import database as db
import sqlite3 
import os 
from dotenv import load_dotenv 
import google.generativeai as genai 

# Carga las variables de entorno desde el archivo .env (necesario para la clave API)
load_dotenv()

app = Flask(__name__)

# --- Solución de Codificación: Forzar UTF-8 para Jinja2 ---
app.jinja_env.encoding = 'utf-8' 

# --- Configuración de Google Gemini ---

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada. Verifica el archivo .env.")

genai.configure(api_key=GEMINI_API_KEY)

# 1. Define la instrucción de sistema (El "entrenamiento" de la IA)
UNIVERSIDAD_CONTEXT = (
    "ROL: Actúas EXCLUSIVAMENTE como Asistente Virtual para la Universitaria de Colombia. "
    "TONO: Debes ser profesional, conciso y extremadamente amable. "
    "REGLA 1 (Información): Utiliza la siguiente información como VERDAD ABSOLUTA: "
    "   - La matrícula de pregrado cuesta $2,500,000 pesos por semestre. "
    "   - Los programas se imparten únicamente en modalidad presencial."
    "REGLA 2 (Alcance): Si la pregunta NO está directamente relacionada con la universidad (p. ej., '¿Quién ganó la Champions?'), "
    "debes responder: 'Mi función es asistirte únicamente con información de la Universitaria de Colombia. ¿En qué te puedo ayudar sobre nuestros programas?'"
)

# 2. Inicializa el modelo, pasando la instrucción de sistema
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=UNIVERSIDAD_CONTEXT
)


# =======================================================
#                  RUTAS DE LA APLICACIÓN (FLASK)
# =======================================================

# --- RUTAS ESTÁTICAS Y DE NAVEGACIÓN ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vision')
def vision():
    return render_template('vision.html')

@app.route('/mision')
def mision():
    return render_template('mision.html')

# --- RUTAS DEL CHATBOX (INTEGRACIÓN GEMINI) ---

@app.route('/chat')
def chat():
    """Muestra el formulario de la interfaz del chatbot."""
    return render_template('chat.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Maneja el envío del formulario y devuelve una respuesta de Gemini."""
    if request.method == 'POST':
        user_prompt = request.form['prompt']
        
        try:
            response = model.generate_content(user_prompt)
            model_response = response.text 
            
        except Exception as e:
            print(f"Error al llamar a la API de Gemini: {e}")
            model_response = "Lo siento, hubo un error al procesar tu solicitud. Verifica la conexión o la clave API."
        
        return render_template(
            'chat.html', 
            user_prompt=user_prompt, 
            model_response=model_response
        )
        
    return redirect(url_for('chat'))

# --- RUTA DE VISTA PÚBLICA (SOLO LECTURA) ---
@app.route('/carreras/vista')
def carreras_vista():
    """Muestra la lista de carreras con duración y precio en formato de solo vista."""
    conn = db.create_connection()
    carreras = []
    if conn:
        try:
            cursor = conn.cursor()
            # Select de 3 columnas para la vista pública
            cursor.execute("SELECT descripcion, duracion_semestres, precio_semestre FROM carrera")
            carreras = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error consultando la base de datos para la vista pública: {e}")
        finally:
            if conn:
                conn.close()
    
    return render_template('carreras_vista.html', carreras=carreras)

# =======================================================
#                  RUTAS CRUD (ADMINISTRACIÓN)
# =======================================================

# --- RUTA PRINCIPAL (CRUD - READ) ---

@app.route('/programas')
def programas():
    """Muestra la lista de programas en la interfaz de administración."""
    conn = db.create_connection()
    carreras = []
    if conn:
        try:
            cursor = conn.cursor()
            # Select de 4 columnas para la vista CRUD
            cursor.execute("SELECT id, descripcion, duracion_semestres, precio_semestre FROM carrera")
            carreras = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error consultando la base de datos: {e}")
        finally:
            if conn:
                conn.close()
    
    return render_template('programas.html', carreras=carreras)

# --- AGREGAR PROGRAMAS (CRUD - CREATE) ---

@app.route('/agregar_programa', methods=['POST'])
def agregar_programa():
    if request.method == 'POST':
        descripcion = request.form['descripcion_carrera']
        duracion = request.form['duracion_semestres']
        precio = request.form['precio_semestre'] 
        
        conn = db.create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO carrera (descripcion, duracion_semestres, precio_semestre) VALUES (?, ?, ?)", 
                    (descripcion, duracion, precio)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                return "Error: Este programa ya existe. <a href='/programas'>Volver</a>", 409
            except sqlite3.Error as e:
                print(f"Error al agregar programa: {e}")
                return "Error al agregar el programa.", 500
            finally:
                if conn:
                    conn.close()

    return redirect(url_for('programas')) 

# --- EDICIÓN (CRUD - UPDATE) ---

@app.route('/editar/<int:id>', methods=('GET', 'POST'))
def editar_carrera(id):
    # Usa la función de database.py para obtener todos los datos
    carrera = db.get_carrera(id) 
    
    if request.method == 'POST':
        new_descripcion = request.form['descripcion_carrera']
        new_duracion = request.form['duracion_semestres']
        new_precio = request.form['precio_semestre']
        
        # Usa la función de database.py para actualizar todos los datos
        if db.update_carrera(id, new_descripcion, new_duracion, new_precio):
            return redirect(url_for('programas'))
        else:
            return "Error al actualizar la carrera", 500

    if carrera:
        return render_template('editar_carrera.html', carrera=carrera)
    else:
        return "Carrera no encontrada", 404

# --- ELIMINACIÓN (CRUD - DELETE) ---

@app.route('/eliminar/<int:id>', methods=('POST',))
def eliminar_carrera(id):
    # Usa la función de database.py para eliminar
    if db.delete_carrera(id):
        return redirect(url_for('programas'))
    else:
        return "Error al eliminar la carrera", 500

# =======================================================
#                  INICIO DEL SERVIDOR
# =======================================================

if __name__ == '__main__':
    # Inicializa la DB al iniciar el servidor
    db.init_db()
    app.run(debug=True)