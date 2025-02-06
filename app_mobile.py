import streamlit as st
import os
import psycopg2

# Configuração da página
st.set_page_config(page_title="Juego - Mobile", layout="centered")
st.title("🎮 Juego de Adivinanza de Palabras (Mobile)")
st.write("Ingresá tu nombre y adiviná las palabras.")

# Obter a variável de conexão do Supabase (configurada no Streamlit Secrets)
DATABASE_URL = os.environ.get("DATABASE_URL")

# 📌 Teste de conexão com o banco
st.subheader("🔄 Testando conexão com o banco...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    result = cur.fetchone()
    conn.close()
    st.success(f"✅ Conexión exitosa! Hora del servidor: {result[0]}")
except Exception as e:
    st.error(f"❌ Error al conectar: {e}")

# Função para obter conexão
def get_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        st.error(f"⚠️ Erro ao conectar ao banco: {e}")
        return None

# Inicializa o banco de dados (cria a tabela, se necessário)
def init_db():
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS discovered_words (
                word TEXT PRIMARY KEY
            );
        """)
        conn.commit()
        cur.close()
        conn.close()

# Lê palavras já descobertas
def read_game_data():
    conn = get_connection()
    if not conn:
        return {"discovered": []}
    cur = conn.cursor()
    cur.execute("SELECT word FROM discovered_words;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    discovered = [row[0] for row in rows]
    return {"discovered": discovered}

# Adiciona uma palavra ao banco de dados
def update_game_data(word):
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO discovered_words (word) VALUES (%s) ON CONFLICT DO NOTHING;", (word,))
        conn.commit()
        cur.close()
        conn.close()

# Inicializa a base de dados
init_db()

# Formulário de entrada
name = st.text_input("📝 Poné tu nombre:")
guess = st.text_input("🔤 Escribí una palabra:")

# Lista de palavras válidas (excluindo a palavra central "SÍNTESIS")
all_possible_words = [
    "integración", "simplificar", "resumen", "reducción",
    "guión", "recopilación", "compendio", "acortamiento",
    "extracto", "sinopsis", "compilación", "sumario"
]

# Botão para enviar resposta
if st.button("🚀 Enviar"):
    if not name.strip():
        st.error("⚠️ ¡Por favor, ingresá tu nombre!")
    else:
        guess = guess.lower().strip()
        if guess in [w.lower() for w in all_possible_words]:
            data = read_game_data()
            if guess not in data["discovered"]:
                update_game_data(guess)
                st.success(f"🎉 ¡Buenísimo, {name}! Adivinaste '{guess}'.")
            else:
                st.warning("⏳ ¡Esa palabra ya fue descubierta!")
        else:
            st.error("❌ ¡Palabra inválida!")

# Exibir palavras descobertas
st.markdown("---")
st.subheader("📜 Palabras descubiertas")
data = read_game_data()
if data["discovered"]:
    for word in data["discovered"]:
        st.write(f"✅ **{word}**")
else:
    st.write("❌ Aún no se han descubierto palabras.")

# Link para a projeção
st.markdown("📺 [Ver Proyección](https://app-force-layout-oz7bsyxrplpkahr2dzr6xp.streamlit.app/)", unsafe_allow_html=True)
