import streamlit as st
from datetime import datetime
import pandas as pd
import os
from time import sleep
from helper_files import update_table_geral, optimize_transactions
from helper_files.sidebar import create_sidebar


st.set_page_config(page_title="Visão Sessão", page_icon=":spades:", layout="wide")

create_sidebar()

def check_month_in_geral():
    df = pd.read_csv("data/geral_2024.csv")
    if df[f"Rodada {st.session_state.current_month}"].isnull().all():
        status_save = True
    else:
        st.warning(f"O mês especificado {st.session_state.current_month} já ocorreu")
        status_save = False

    return status_save

# Configuring session variables
current_date = datetime.now()
if 'valor_buyin' not in st.session_state:
    st.session_state.valor_buyin = 40
if 'valor_fidelidade' not in st.session_state:
    st.session_state.valor_fidelidade = 10
if "current_month" not in st.session_state:
    st.session_state.current_month = current_date.month

status_save = check_month_in_geral()

with st.expander("Configurar mes"):
    mes = st.selectbox("Mês para atualizar a classificação geral:", 
                       [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
                       index=None,
                       placeholder="Selecionar mês da sessão")
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
    lista_players = sorted(df.Players.values)
    who_eliminated = st.selectbox("Quem eliminou:", lista_players)

    # Checkbox marker to see eliminated players
    st.write("Quais jogadores foram eliminados?")
    players_eliminated = [st.checkbox(player) for player in lista_players]
    players_elim = {player: players_eliminated[i] for i, player in enumerate(lista_players) if players_eliminated[i]}

    if st.button("Hit!"):
        define_howmany_rebuys(len(players_elim))
        for player, _ in players_elim.items():
            df.loc[df["Players"] == who_eliminated, ["Qtdy_Hit"]] = df.loc[df["Players"] == who_eliminated, ["Qtdy_Hit"]] + 1
            df.loc[df["Players"] == player, ["Qtdy_Rebuy"]] = df.loc[df["Players"] == player, ["Qtdy_Rebuy"]] + st.session_state.current_rebuys
            if status_save:
                df.to_csv(table_name, index=False)

        st.rerun()

@st.dialog("Adicionando quantidade de fichas final!")
def add_final_score():
    lista_players = df[df['Qtdy_Numero_fichas'].isna()].Players.values

    player = st.selectbox("Qual jogador:", lista_players)
    valor = st.number_input(label="Valor", value=None, placeholder="Type a number...", format='%d', step=1)

    if st.button("Final"):
        df.loc[df["Players"] == player, ["Qtdy_Numero_fichas"]] = valor
        if status_save:
            df.to_csv(table_name, index=False)
            st.rerun()

cols = st.columns(5)
with cols[0]:
    with st.container(border=True):
        df_geral = pd.read_csv("data/geral_2024.csv").sort_values("Players", ascending=True)
        lista_jogadores = [player for player in df_geral.Players.values]
        
        defaulted_player = st.selectbox("Adicionar um jogador já existente", 
                                        options=lista_jogadores, 
                                        index=None, 
                                        placeholder="Selecione um jogador...")
        new_player = st.text_input('Adicionar um novo jogador:')

        if defaulted_player and not new_player:
            new_player = defaulted_player
        elif defaulted_player and new_player:
            new_player = defaulted_player

        # if not defaulted_player and 
        if st.button('Adidionar jogador'):
            with st.spinner("Adicionando..."):
                add_player(new_player)
            st.rerun()

with cols[1]:
    with st.container(border=True):
        st.write("Durante a partida:")
        if st.button("Adicionar um hit"):
            add_hit()
  
with cols[2]:
    with st.container(border=True):
        st.write("Ao final da partida:")
        if st.button("Configurar qtd fichas final"):
            add_final_score()

with cols[3]:
    with st.container(border=True):
        st.session_state.valor_buyin = st.number_input(label="Valor do buyin/rebuy", 
                                                    value=st.session_state.valor_buyin, 
                                                    placeholder=st.session_state.valor_buyin, 
                                                    format='%d', step=1)
        st.session_state.valor_fidelidade = st.number_input(label="Valor da fidelidade", 
                                                            value=st.session_state.valor_fidelidade, 
                                                            placeholder=st.session_state.valor_fidelidade, 
                                                            format='%d', step=1)

        if st.button("Resetar sessao"):
            if len(df) > 0:
                df = create_empty_df(status_save)
                st.rerun()
            else:
                st.warning("Sem necessidade!")

st.divider()
st.write(f"Quantos rebuys no momento: ", st.session_state.current_rebuys)
st.dataframe(df.sort_values("Players"), hide_index=True, on_select="ignore")
st.write(f"Quantidade de fichas que tem na mesa: ", (df.Qtdy_Buy_in.sum() + df.Qtdy_Rebuy.sum()) * st.session_state.valor_buyin)

st.divider()
@st.dialog("Encerrando sessão!")
def encerrar_sessao(df, status_save):
    st.write("Encerrar a sessão irá: ")
    st.write("- Calcular os valores restantes (Buy-in, Rebuy, Numero de fichas, Rs Total, Ranking, Fidelidade, Hit, F1) ")
    st.write("- Calcular o valor total ")


    if st.button("Confirmar encerramento da sessão"):
        df["Valor_Buy_in"] = - df["Qtdy_Buy_in"]*st.session_state.valor_buyin
        df["Valor_Rebuy"] = - df["Qtdy_Rebuy"]*st.session_state.valor_buyin
        df["Valor_Numero_fichas"] = df["Qtdy_Numero_fichas"]
        df["RS_total"] = df["Valor_Buy_in"] + df["Valor_Rebuy"] + df["Valor_Numero_fichas"]

        if df["RS_total"].sum() != 0:
            st.warning(f"A soma final não deu 0, algo está errado. deu {df['RS_total'].sum()}")
        else:
            df = df.sort_values("RS_total", ascending=False)
            df["Ranking"] = range(1, len(df)+1)
            df["Fidelidade"] = st.session_state.valor_fidelidade
            df["Hit"] = 0.5 * df["Qtdy_Hit"]
            df["F1"] = f1_score[0:len(df)]

            df["Total"] = df["Fidelidade"] + df["Hit"] + df["F1"]
            df = df.sort_values("Total", ascending=False)

            if status_save:
                df.to_csv(table_name, index=False)
                optimize_transactions(df)
                update_table_geral(st.session_state.current_month)
                st.write('Sessão encerrada com sucesso!', icon="✅")
            else:
                st.warning(f'Sessão encerrada! Dado foi descartado pois já ocorreu a sessão desse mês {st.session_state.current_month}!', icon="❗")

##
if st.button("Encerrar sessao"):
    if df[["Qtdy_Numero_fichas"]].isnull().values.any():
        st.warning("Ainda há jogadores que não informaram as fichas finais")
    else:
        encerrar_sessao(df, status_save)
