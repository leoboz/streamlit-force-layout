import streamlit as st
import psycopg2
import os

# Pegamos a URL do banco do ambiente
DATABASE_URL = os.environ.get("DATABASE_URL")

st.title("🛠 Testando conexão com o banco...")

try:
    # Tenta conectar ao Supabase
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Testa um SELECT simples para ver se o banco responde
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
    tables = cur.fetchall()

    # Exibe as tabelas encontradas
    st.success("✅ Conectado ao banco com sucesso!")
    st.write("📌 Tabelas encontradas:", tables)

    # Fecha conexão
    cur.close()
    conn.close()

except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco: {e}")
