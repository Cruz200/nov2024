import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import requests
import streamlit as st
from PIL import Image
from io import BytesIO
# CSS para establecer el fondo negro
st.markdown(
    """
    <style>
        .main {
            background-color: black;
            color: white;
        }
        
        .stButton>button {
            background-color: #333;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)
# Configuración de credenciales
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(
    "/Users/HP/Desktop/interfazcambio/StreamlitKev.json",  # Cambia aquí la ruta a tu archivo de credenciales
    scopes=scope
)
client = gspread.authorize(creds)

# Abre el archivo de Google Sheets y selecciona la hoja
sheet = client.open_by_key("1cBsi5EVMBW9-SauUQVkdc1EF4Yk14uRbvyjSJWXwyOQ").sheet1

# Variables para el control de la fila actual
if "fila_actual" not in st.session_state:
    st.session_state.fila_actual = 2  # Empieza desde la fila 2

# Configuración de columnas
columna_id = 1  # Columna 1: ID
columna_imagen = 2  # Columna 2: Enlaces a imágenes
columna_b = 3  # Columna B (JSON editable)
columna_c = 4  # Columna C (resultado en texto)
fila_inicio = 2

# Función para cargar el contenido de una celda específica
def cargar_celda(fila, columna):
    return sheet.cell(fila, columna).value

# Función para cargar y procesar JSON desde una celda
def cargar_registro(fila, columna):
    registro_json = sheet.cell(fila, columna).value
    if registro_json:
        try:
            return json.loads(registro_json)
        except json.JSONDecodeError:
            st.error("Error en el JSON. Revisa el contenido de la celda.")
            return {}
    else:
        sheet.update_cell(fila, columna, "{}")  # Inicializa si está vacío
        return {}


# Título de la app
st.title("Editor de JSON en Google Sheets")

# Variables para el control de la fila actual
if "fila_actual" not in st.session_state:
    st.session_state.fila_actual = 2  # Empieza desde la fila 2

# Función para extraer el ID de un enlace de Google Drive
def extraer_id_google_drive(enlace):
    try:
        return enlace.split("/file/d/")[1].split("/view")[0]
    except IndexError:
        st.error("El enlace de Google Drive no es válido.")
        return None

# Cargar la celda de imagen y extraer ID
enlace_imagen = sheet.cell(st.session_state.fila_actual, 2).value  # Cambia al índice de la columna que corresponda
id_imagen = extraer_id_google_drive(enlace_imagen) if enlace_imagen else None

if id_imagen:
    url = f"https://drive.google.com/uc?export=view&id={id_imagen}"
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            # Convertir respuesta a imagen
            image = Image.open(BytesIO(response.content))
            st.image(image, caption="Imagen cargada de Google Drive", use_container_width =True)
        except Exception as e:
            st.error(f"No se pudo cargar la imagen: {e}")
    else:
        st.error(f"No se pudo obtener la imagen. Código de estado: {response.status_code}")
else:
    st.warning("No se encontró un enlace válido para esta fila.")



# Función para mostrar un formulario editable
def mostrar_formulario(data, titulo, columna):
    campos_actualizados = {}
    st.write(titulo)
    for key, value in data.items():
        nuevo_valor = st.text_input(f"{key}", value, key=f"{st.session_state.fila_actual}_{columna}_{key}")
        campos_actualizados[key] = nuevo_valor
    return campos_actualizados



# Mostrar la fila actual
#st.write(f"Estás modificando la fila: {st.session_state.fila_actual}")

# Cargar y mostrar ID y enlace de imagen
id_actual = cargar_celda(st.session_state.fila_actual, columna_id)
enlace_imagen = cargar_celda(st.session_state.fila_actual, columna_imagen)

st.subheader(f"ID: {id_actual}")


# Cargar los valores de las columnas B y C
data_b = cargar_registro(st.session_state.fila_actual, columna_b)
data_c = cargar_registro(st.session_state.fila_actual, columna_c)

# Crear dos columnas para mostrar y editar datos
col1, col2 = st.columns(2)

with col1:
    st.write("Editar valores en la columna B (para actualizar la columna C):")
    campos_actualizados_b = mostrar_formulario(data_b, "Columna B", "B")

#with col2:
#    st.write("Valores en la columna C:")
#    for key, value in data_c.items():
#        st.write(f"{key}: {value}")

# Botón para guardar cambios
if st.button("Guardar"):
    nuevo_json_c = json.dumps(campos_actualizados_b)
    sheet.update_cell(st.session_state.fila_actual, columna_c, nuevo_json_c)
    st.success(f"Registro actualizado correctamente en la fila {st.session_state.fila_actual}")

    # Recargar y mostrar los datos actualizados
    data_c = cargar_registro(st.session_state.fila_actual, columna_c)
    with col2:
        st.write("Valores actuales en la columna C (actualizados):")
        for key, value in data_c.items():
            st.write(f"{key}: {value}")

# Botón para avanzar a la siguiente fila
if st.button("Siguiente"):
    st.session_state.fila_actual += 1

   