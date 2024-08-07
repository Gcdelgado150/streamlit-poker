import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
st.set_page_config(layout="wide")

df = pd.read_csv("data/geral.csv").sort_values("Total com corte", ascending=True).reset_index(drop=True)
st.dataframe(df, hide_index=True, on_select="ignore")

cols_rodadas = [c for c in df.columns if c.startswith("Rodada")]
df = df[["Players"] + cols_rodadas]

# Valor total cumulativo por rodada
if 1:
    st.write("Valor total cumulativo por rodada")
    fig = go.Figure()
    for player in df.Players.values:
        df_here = df[df["Players"] == player][["Players"] + cols_rodadas].set_index('Players').T
        df_here = df_here.reset_index()
        df_here.columns = ["Rodadas", "Pontuacao"]
        df_here = df_here.cumsum()
        df_here["Rodadas"] = cols_rodadas    

        random_x = df_here.Rodadas.values
        random_y0 = df_here.Pontuacao.values

        fig.add_trace(go.Scatter(x=random_x, y=random_y0,
                            mode='lines+markers',
                            name=player))
        fig.update_layout(title="Valor total cumulativo por rodada")

    st.plotly_chart(fig, use_container_width=True)

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
        title='Top 10 Individual Scores',
        xaxis_title='Players',
        yaxis_title='Score',
        xaxis_tickangle=-45,
        uniformtext_mode='hide'
    )

    st.plotly_chart(fig, use_container_width=True)
