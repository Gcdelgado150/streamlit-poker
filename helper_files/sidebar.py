import streamlit as st

def create_sidebar():
    st.sidebar.title("Poker GMaia")
    st.sidebar.image("data/logo.jpg")
    
    st.sidebar.page_link("home.py", label="Análises")

    st.divider()
    st.sidebar.page_link("pages/geral.py", label="Visão Geral") 
    st.sidebar.page_link("pages/sessao.py", label="Visão de Sessão") 