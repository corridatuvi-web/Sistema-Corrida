import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Sistema Integrado de Treinamento", layout="wide")

# ===============================
# Banco de dados
# ===============================
conn = sqlite3.connect("dados.db", check_same_thread=False)

def criar_tabelas():
    conn.execute("""
        CREATE TABLE IF NOT EXISTS avaliacao (
            data TEXT, aluno TEXT,
            vo2 REAL, vlac REAL, vlan REAL, vvo2 REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS composicao (
            data TEXT, aluno TEXT,
            peso REAL, gordura REAL, massa_magra REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS treinos_semanais (
            data TEXT, aluno TEXT,
            seg TEXT, ter TEXT, qua TEXT, qui TEXT,
            sex TEXT, sab TEXT, dom TEXT,
            feedback TEXT
        )
    """)
    conn.commit()

criar_tabelas()

def hoje():
    return datetime.now().strftime("%Y-%m-%d")

# ===============================
# INTERFACE
# ===============================
st.title("📊 Sistema Integrado de Avaliação e Treinamento")

aluno = st.text_input("Nome do aluno")

abas = st.tabs([
    "🏃 Avaliação",
    "📏 Composição",
    "🗓️ Treinos Semanais",
    "📈 Visão Geral"
])

# ===============================
# AVALIAÇÃO
# ===============================
with abas[0]:
    st.subheader("Avaliação Fisiológica")

    vo2 = st.number_input("VO₂máx", 0.0)
    vlac = st.number_input("Velocidade Limiar de Lactato", 0.0)
    vlan = st.number_input("Velocidade Limiar Anaeróbico", 0.0)
    vvo2 = st.number_input("Velocidade VO₂máx", 0.0)

    if st.button("Salvar Avaliação"):
        conn.execute(
            "INSERT INTO avaliacao VALUES (?, ?, ?, ?, ?, ?)",
            (hoje(), aluno, vo2, vlac, vlan, vvo2)
        )
        conn.commit()
        st.success("Avaliação salva")

    df = pd.read_sql("SELECT * FROM avaliacao WHERE aluno=?", conn, params=[aluno])
    st.dataframe(df, use_container_width=True)

# ===============================
# COMPOSIÇÃO
# ===============================
with abas[1]:
    st.subheader("Composição Corporal")

    peso = st.number_input("Peso (kg)", 0.0)
    gordura = st.number_input("% Gordura", 0.0)
    massa = st.number_input("Massa Magra (kg)", 0.0)

    if st.button("Salvar Composição"):
        conn.execute(
            "INSERT INTO composicao VALUES (?, ?, ?, ?, ?)",
            (hoje(), aluno, peso, gordura, massa)
        )
        conn.commit()
        st.success("Composição salva")

    df = pd.read_sql("SELECT * FROM composicao WHERE aluno=?", conn, params=[aluno])
    st.dataframe(df, use_container_width=True)

# ===============================
# TREINOS SEMANAIS
# ===============================
with abas[2]:
    st.subheader("Planejamento Semanal de Treinos")

    seg = st.text_area("Segunda-feira")
    ter = st.text_area("Terça-feira")
    qua = st.text_area("Quarta-feira")
    qui = st.text_area("Quinta-feira")
    sex = st.text_area("Sexta-feira")
    sab = st.text_area("Sábado")
    dom = st.text_area("Domingo")

    feedback = st.text_area("Feedback da semana")

    if st.button("Salvar semana de treino"):
        conn.execute("""
            INSERT INTO treinos_semanais
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (hoje(), aluno, seg, ter, qua, qui, sex, sab, dom, feedback))
        conn.commit()
        st.success("Treino semanal salvo")

    st.divider()
    st.subheader("Semanas registradas")

    df = pd.read_sql(
        "SELECT * FROM treinos_semanais WHERE aluno=?",
        conn, params=[aluno]
    )
    st.dataframe(df, use_container_width=True)

# ===============================
# VISÃO GERAL
# ===============================
with abas[3]:
    st.subheader("Histórico completo do aluno")

    for tabela, nome in [
        ("avaliacao", "Avaliação Fisiológica"),
        ("composicao", "Composição Corporal"),
        ("treinos_semanais", "Treinos Semanais")
    ]:
        st.markdown(f"### {nome}")
        df = pd.read_sql(
            f"SELECT * FROM {tabela} WHERE aluno=?",
            conn, params=[aluno]
        )
        st.dataframe(df, use_container_width=True)
