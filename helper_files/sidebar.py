import streamlit as st

def create_sidebar():
    st.sidebar.image("data/logo.jpg", width=300)
    st.sidebar.header("Poker GMAIA", divider="gray")
    
    st.sidebar.page_link("home.py", label="Visão Geral")

    st.divider()
    st.sidebar.page_link("pages/sessao.py", label="Visão de Sessão") 