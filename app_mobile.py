import streamlit as st
import json, os, gspread

st.set_page_config(page_title="Juego - Mobile", layout="centered")
st.title("Juego de Adivinanza de Palabras (Mobile)")
st.write("Ingresá tu nombre y adiviná las palabras.")

# Carrega as credenciais do secret; se for string, tenta convertê-las
service_account_info = st.secrets["gcp_service_account"]
if isinstance(service_account_info, str):
    try:
        service_account_info = json.loads(service_account_info)
    except json.JSONDecodeError as e:
        st.error("Error al decodificar las credenciales de gcp_service_account. Asegurate de que estén correctamente formateadas en TOML.")
        st.stop()

gc = gspread.service_account_from_dict(service_account_info)
spreadsheet_id = st.secrets["SPREADSHEET_ID"]
sheet = gc.open_by_key(spreadsheet_id).sheet1

# Se o sheet estiver vazio, cria o cabeçalho na célula A1
if not sheet.get("A1"):
    sheet.update("A1", "word")

def read_game_data():
    records = sheet.get_all_values()
    words = [row[0].lower() for row in records[1:] if row]
    return {"discovered": words}

def update_game_data(word):
    data = read_game_data()
    if word.lower() not in data["discovered"]:
        sheet.append_row([word.lower()])

name = st.text_input("Poné tu nombre:")
guess = st.text_input("Escribí una palabra:")

all_possible_words = [
    "integración", "simplificar", "resumen", "reducción",
    "guión", "recopilación", "compendio", "acortamiento",
    "extracto", "sinopsis", "compilación", "sumario"
]

if st.button("Enviar"):
    if not name:
        st.error("¡Por favor, ingresá tu nombre!")
    else:
        if guess.lower() in [w.lower() for w in all_possible_words]:
            data = read_game_data()
            if guess.lower() not in data["discovered"]:
                update_game_data(guess)
                st.success(f"¡Buenísimo, {name}! Adivinaste '{guess}'.")
            else:
                st.warning("¡Esa palabra ya fue descubierta!")
        else:
            st.error("¡Palabra inválida!")

st.markdown("---")
st.write("Después de enviar tu respuesta, la proyección se actualiza en la pantalla grande.")
st.markdown('[Ver Proyección](https://app-force-layout-oz7bsyxrplpkahr2dzr6xp.streamlit.app/)', unsafe_allow_html=True)
