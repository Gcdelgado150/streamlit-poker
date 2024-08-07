import streamlit as st
from datetime import datetime
import pandas as pd
import os
from time import sleep
st.set_page_config(layout="wide")

def check_month_in_geral():
    df = pd.read_csv("data/geral.csv")
    if df[f"Rodada {st.session_state.current_month}"].isnull().all():
        status_save = True
    else:
        st.warning(f"O mês especificado {st.session_state.current_month} já ocorreu")
        status_save = False

    return status_save

current_date = datetime.now()
if "current_month" not in st.session_state:
    st.session_state.current_month = current_date.month

status_save = check_month_in_geral()

with st.expander("Configurar mes"):
    mes = st.selectbox("Mês para atualizar a classificação geral:", 
                       [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
                       index=None)
    if st.button("Concluir"):
        if mes:
            st.session_state.current_month = mes
            st.rerun()

st.title(f"Sessão - Mês {st.session_state.current_month}")
table_name = f"data/classificacao_{current_date.year}_{st.session_state.current_month}.csv"
    
# Configure f1 score
f1_score = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def create_empty_df(status_save):
    # Start empty df
    d = {"Players": [],
        "Qtdy_Buy_in": [],
        "Qtdy_Rebuy": [],
        "Qtdy_Hit": [],
        "Qtdy_Numero_fichas": [],
        "Valor_Buy_in": [],
        "Valor_Rebuy": [],
        "Valor_Numero_fichas": [],
        "RS_total": [],
        "Ranking": [],
        "Fidelidade": [],
        "Hit": [],
        "F1": [],
        "Total": [],
        }

    df = pd.DataFrame(d)
    if status_save:
        df.to_csv(table_name, index=False)
    
    return df

if os.path.isfile(table_name):
    df = pd.read_csv(table_name)
    d = int(df["Qtdy_Rebuy"].sum()/len(df))if len(df) > 0 else 1
    st.session_state.current_rebuys = d if d > 0  else 1 # Rebuy can never be 0
else:
    df = create_empty_df(status_save)
    st.session_state.current_rebuys = 1

def add_player(new_player):
    # TODO: Add player options based on geral
    if new_player not in df.Players.values:
        s = len(df)
        df.loc[s, "Players"] = new_player
        df.loc[s, "Qtdy_Buy_in"] = 1
        df.loc[s, "Qtdy_Rebuy"] = 0
        df.loc[s, "Qtdy_Hit"] = 0

        df.loc[s, "Valor_Buy_in"] = 0
        df.loc[s, "Valor_Rebuy"] = 0

        if status_save:
            df.to_csv(table_name, index=False)
            st.success("Player added!")
    else:
        st.warning(f'Player {new_player} already exists.')

def define_howmany_rebuys(amount_players_elim):
    rebuys_done_already = df["Qtdy_Rebuy"].sum()

    if rebuys_done_already + amount_players_elim >= int(len(df)/st.session_state.current_rebuys):
        st.session_state.current_rebuys += 1

@st.dialog("Eliminação")
def add_hit():
    who_eliminated = st.selectbox("Quem eliminou:", df.Players.values)

    # Checkbox marker to see eliminated players
    st.write("Quais jogadores foram eliminados?")
    players_eliminated = [st.checkbox(player) for player in df.Players.values]
    players_elim = {player: players_eliminated[i] for i, player in enumerate(df.Players.values) if players_eliminated[i]}

    if st.button("Concluir"):
        define_howmany_rebuys(len(players_elim))
        for player, _ in players_elim.items():
            df.loc[df["Players"] == who_eliminated, ["Qtdy_Hit"]] = df.loc[df["Players"] == who_eliminated, ["Qtdy_Hit"]] + 1
            df.loc[df["Players"] == player, ["Qtdy_Rebuy"]] = df.loc[df["Players"] == player, ["Qtdy_Rebuy"]] + st.session_state.current_rebuys
            if status_save:
                df.to_csv(table_name, index=False)

        st.rerun()

@st.dialog("Adicionando quantidade de fichas final!")
def add_final_score():
    player = st.selectbox("Qual jogador:", df.Players.values)
    valor = st.number_input(label="Valor", value=None, placeholder="Type a number...", format='%d', step=1)

    if st.button("Concluires"):
        df.loc[df["Players"] == player, ["Qtdy_Numero_fichas"]] = valor
        if status_save:
            df.to_csv(table_name, index=False)
            st.rerun()

cols = st.columns(5)
with cols[0]:
    df_geral = pd.read_csv("data/geral.csv").sort_values("Players", ascending=True)
    lista_jogadores = [player for player in df_geral.Players.values if player not in df.Players.values]

    defaulted_player = st.selectbox("Adicionar um jogador já existente", lista_jogadores, index=None)
    new_player = st.text_input('Adicionar um novo jogador:')

    if defaulted_player and not new_player:
        new_player = defaulted_player
    elif defaulted_player and new_player:
        new_player = defaulted_player

    # if not defaulted_player and 
    if st.button('Adidionar jogador'):
        add_player(new_player)
        st.rerun()

with cols[1]:
    st.write("Durante a partida:")
    if st.button("Adicionar um hit"):
        add_hit()
  
with cols[2]:
    st.write("Ao final da partida:")
    if st.button("Configurar qtd fichas final"):
        add_final_score()

with cols[3]:
    valor_buyin = st.number_input(label="Valor do buyin/rebuy", value=40, placeholder=40, format='%d', step=1)
    valor_fidelidade = st.number_input(label="Valor da fidelidade", value=10, placeholder=40, format='%d', step=1)

    if st.button("Resetar sessao"):
        if len(df) > 0:
            df = create_empty_df(status_save)
            st.rerun()
        else:
            st.warning("Sem necessidade!")

st.write(f"Quantos rebuys no momento: {st.session_state.current_rebuys}")
st.dataframe(df, hide_index=True, on_select="ignore")

if st.button("Encerrar sessao"):
    if df[["Qtdy_Numero_fichas"]].isnull().values.any():
        st.warning("Ainda há jogadores que não informaram as fichas finais")
    else:
        df["Valor_Buy_in"] = -df["Qtdy_Buy_in"]*valor_buyin
        df["Valor_Rebuy"] = -df["Qtdy_Rebuy"]*valor_buyin
        df["Valor_Numero_fichas"] = df["Qtdy_Numero_fichas"]
        df["RS_total"] = df["Valor_Buy_in"] + df["Valor_Rebuy"] + df["Valor_Numero_fichas"]

        if df["RS_total"].sum() != 0:
            st.warning(f"A soma final não deu 0, algo está errado. deu {df['RS_total'].sum()}")
        else:
            df = df.sort_values("RS_total", ascending=False)
            df["Ranking"] = range(1, len(df)+1)
            df["Fidelidade"] = valor_fidelidade
            df["Hit"] = 0.5 * df["Qtdy_Hit"]
            df["F1"] = f1_score[0:len(df)]

            df["Total"] = df["Fidelidade"] + df["Hit"] + df["F1"]
            df = df.sort_values("Total", ascending=False)

            if status_save:
                df.to_csv(table_name, index=False)
                st.write('Sessão encerrada com sucesso!', icon="✅")
            else:
                st.warning(f'Sessão encerrada! Dado foi descartado pois já ocorreu a sessão desse mês {st.session_state.current_month}!', icon="❗")
