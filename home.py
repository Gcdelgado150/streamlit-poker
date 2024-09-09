import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from helper_files import find_key_with_values
from helper_files.sidebar import create_sidebar

st.set_page_config(page_title="Poker GMaia", page_icon=":spades:", layout="wide")

create_sidebar()

df = pd.read_csv("data/geral_2024.csv").sort_values("Total com corte", ascending=False).reset_index(drop=True)
max_value = round(int(df["Total com corte"].max()*1.1) / 10) * 10 # Max value rounded to the nearest multiple of 10

# Mostrar top 5
st.write("Top 5")
st.dataframe(df.head(5), hide_index=True, on_select="ignore")

st.divider()
cols_rodadas = [c for c in df.columns if c.startswith("Rodada")]
df = df[["Players"] + cols_rodadas]

# Valor total cumulativo por rodada
if 1:
    to_print = []

    # Pra cada player remove a dupla de rodada com menor valor 
    for i, row in df.iterrows():
        cleanedList = sorted([x for x in row[cols_rodadas].values
                                if str(x) != 'nan'], reverse=True)

        all_keys = list(find_key_with_values(row, cleanedList[-2:]))

        to_print.append([row["Players"], cleanedList[-2:], all_keys[:2]])
        for rodada in all_keys[:2]:
            df.loc[df["Players"] == row['Players'] , rodada] = 0.0

    with st.expander("Expandir para ver cortes"):
        for pr in to_print:
            st.write(f"Corte de {pr[0]}, {pr[1]} das rodadas : {pr[2]}")

    # Cria a figura
    fig = go.Figure()
    for player in df.Players.values:
        df_here = df[df["Players"] == player][["Players"] + cols_rodadas].set_index('Players').T
        df_here = df_here.reset_index()
        df_here.columns = ["Rodadas", "Pontuacao"]
        df_here = df_here.cumsum()
        df_here["Rodadas"] = cols_rodadas    

        fig.add_trace(go.Scatter(x=df_here.Rodadas.values, y=df_here.Pontuacao.values,
                            mode='lines+markers',
                            name=player))
        fig.update_layout(title={'text': "Valor total com corte cumulativo por rodada",
                                 'y':0.9,
                                 'x':0.5,
                                 'xanchor': 'center',
                                 'yanchor': 'top'})
    fig.update_yaxes(range=[0, max_value], dtick=20)
        
    st.plotly_chart(fig, use_container_width=True)

st.divider()
# Top 10 scorers
if 1:
    # Flatten the DataFrame to get all individual scores
    scores = pd.melt(df, id_vars=['Players'], value_vars=cols_rodadas, var_name='Rodada', value_name='Score').dropna()

    # Find the top 10 scores
    top_10_scores = scores.nlargest(10, 'Score')

    # Create the bar plot
    fig = go.Figure()

    # Add bars for each entry in the top_10_scores
    fig.add_trace(go.Bar(
        x=top_10_scores['Players'],
        y=top_10_scores['Score'],
        customdata=top_10_scores['Rodada'],
        text=top_10_scores['Score'],
        textposition='auto',
        hovertemplate="<br>".join([
                "Player: %{x}",
                "Rodada: %{customdata}",
                "Score: %{y}",
            ])
    ))

    # Update layout
    fig.update_layout(
        title={'text': "Top 10 Individual Scores",
                                 'y':0.9,
                                 'x':0.5,
                                 'xanchor': 'center',
                                 'yanchor': 'top'},
        xaxis_title='Players',
        yaxis_title='Score',
        xaxis_tickangle=-45,
        uniformtext_mode='hide'
    )
    fig.update_yaxes(showgrid=False)

    st.plotly_chart(fig, use_container_width=True)
