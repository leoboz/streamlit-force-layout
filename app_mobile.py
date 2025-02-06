import streamlit as st
import json, os, psycopg2

# Configuração da página
st.set_page_config(page_title="Juego - Mobile", layout="centered")
st.title("Juego de Adivinanza de Palabras (Mobile)")
st.write("Ingresá tu nombre y adiviná las palabras.")

# Obter a variável de conexão do Supabase (configurada no secret DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS discovered_words (
            word TEXT PRIMARY KEY
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def read_game_data():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT word FROM discovered_words;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    discovered = [row[0] for row in rows]
    return {"discovered": discovered}

def update_game_data(word):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO discovered_words (word) VALUES (%s) ON CONFLICT DO NOTHING;", (word,))
    conn.commit()
    cur.close()
    conn.close()

# Inicializa o banco de dados (cria a tabela, se necessário)
init_db()

name = st.text_input("Poné tu nombre:")
guess = st.text_input("Escribí una palabra:")

# Lista de palavras válidas (excluindo a palavra central "SÍNTESIS")
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
# Substitua pela URL real do app display (obtida após implantar o app_display.py)
st.markdown('[Ver Proyección](https://app-force-layout-oz7bsyxrplpkahr2dzr6xp.streamlit.app/)', unsafe_allow_html=True)
