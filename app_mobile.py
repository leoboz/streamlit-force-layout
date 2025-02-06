import streamlit as st
import json
import os
import gspread

# Configuração da página
st.set_page_config(page_title="Juego - Mobile", layout="centered")
st.title("Juego de Adivinanza de Palabras (Mobile)")
st.write("Ingresá tu nombre y adiviná las palabras.")

# Inicializa a conexão com o Google Sheets usando as credenciais dos secrets
gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
spreadsheet_id = st.secrets["SPREADSHEET_ID"]
sheet = gc.open_by_key(spreadsheet_id).sheet1

# Se o sheet estiver vazio, cria o cabeçalho na célula A1
if not sheet.get("A1"):
    sheet.update("A1", "word")

def read_game_data():
    """Lê os dados do Google Sheet e retorna um dicionário com as palavras descobertas."""
    records = sheet.get_all_values()
    # Considera que a primeira linha é o cabeçalho; pega os valores da coluna A
    words = [row[0].lower() for row in records[1:] if row]
    return {"discovered": words}

def update_game_data(word):
    """Adiciona a palavra (em minúsculas) no Google Sheet, se ainda não existir."""
    data = read_game_data()
    if word.lower() not in data["discovered"]:
        sheet.append_row([word.lower()])

name = st.text_input("Poné tu nombre:")
guess = st.text_input("Escribí una palabra:")

# Lista de palavras válidas (excluyendo la palabra central "SÍNTESIS")
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
# Link para ir ao app de display (substitua pela URL correta do seu app display)
st.markdown('[Ver Proyección](https://app-force-layout-oz7bsyxrplpkahr2dzr6xp.streamlit.app/)', unsafe_allow_html=True)
