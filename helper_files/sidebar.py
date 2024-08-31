import streamlit as st

def create_sidebar():
    st.sidebar.image("data/logo.jpg")
    
    st.sidebar.page_link("home.py", label="Inicio") 
    st.sidebar.page_link("pages/geral.py", label="Visão Geral") 
    st.sidebar.page_link("pages/sessao.py", label="Visão de Sessão") 