import streamlit as st
import json, os

# Define o caminho do arquivo de dados
DATA_FILE = "game_data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"discovered": []}, f, ensure_ascii=False)

def read_game_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def update_game_data(new_data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False)

# Lista de palavras válidas (exceto a palavra central)
all_possible_words = [
    "integración", "simplificar", "resumen", "reducción",
    "guión", "recopilación", "compendio", "acortamiento",
    "extracto", "sinopsis", "compilación", "sumario"
]

st.set_page_config(page_title="Jogo - Mobile", layout="centered")
st.title("Jogo de Adivinhação (Mobile)")
st.write("Digite seu nome e adivinhe as palavras.")

name = st.text_input("Digite seu nome:")
guess = st.text_input("Digite uma palavra:")

if st.button("Enviar"):
    if not name:
        st.error("Por favor, insira seu nome!")
    else:
        if guess.lower() in [word.lower() for word in all_possible_words]:
            data = read_game_data()
            if guess.lower() not in data["discovered"]:
                data["discovered"].append(guess.lower())
                update_game_data(data)
                st.success(f"Parabéns, {name}! Você acertou '{guess}'.")
            else:
                st.warning("Essa palavra já foi descoberta!")
        else:
            st.error("Palavra inválida!")

st.markdown("---")
st.write("Depois de enviar seu palpite, a projeção atualiza automaticamente na tela grande.")
st.markdown('[Clique aqui para ver a projeção](https://seu-app-display.streamlit.app)', unsafe_allow_html=True)
