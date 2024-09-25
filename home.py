import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from helper_files import find_key_with_values
from helper_files.sidebar import create_sidebar
from helper_files import update_table_geral

st.set_page_config(page_title="Poker GMaia", page_icon=":spades:", layout="wide")
st.title(f"Classificação Geral com os cortes")
create_sidebar()

current_date= datetime.now()


df = pd.read_csv("data/geral_2024.csv").sort_values("Total com corte", ascending=False).reset_index(drop=True)
cols_rodadas = [c for c in df.columns if c.startswith("Rodada")]

# Function to highlight the first 3 rows (champions)
def sum_desconsidering_lowest_cells(s):
  lowest = s[cols_rodadas].sort_values(ascending=True).head(2).keys().tolist()
  filtered_s = s.drop(lowest)
  return filtered_s[filtered_s.index.str.contains('Rodada')].sum()

def recalculate_geral(df):
    for rodada in cols_rodadas + ["Total", "Total com corte"]:
      df[rodada] = df[rodada].astype(float)

    df["Total"] = df[cols_rodadas].sum(axis=1)
    df["Total com corte"] = df.apply(sum_desconsidering_lowest_cells, axis=1)
    df = df.sort_values("Total com corte", ascending=False).reset_index(drop=True)
    df.to_csv("data/geral_2024.csv", index=False)

# Apply formatting to specified columns
df[cols_rodadas + ["Total", "Total com corte"]] = df[cols_rodadas + ["Total", "Total com corte"]].applymap('{:,.2f}'.format)

# Function to highlight the first 3 rows (champions)
def highlight_lowest_cells(s):
  lowest = s[cols_rodadas].sort_values(ascending=True).head(2)
  return ['background-color: #c98181' if col in lowest.index.tolist() else ''  for col, value in s.items()]

# Apply the highlight functions
styled_data = df.style.apply(highlight_lowest_cells, axis=1)

# Display the styled DataFrame in Streamlit
st.dataframe(styled_data, hide_index=True, on_select="ignore")


with st.expander("Faltando algum mês?"):
  # Create two columns
  col1, col2 = st.columns([1, 5])

  # Place the button in the first column
  with col1:
      month = st.selectbox("Mês para atualizar a classificação geral:", 
                          [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
                          index=current_date.month-1)
      
      if st.button("Atualizar a classificação geral"):
          update_table_geral(month)
  
with st.expander("Os totais e totais com corte estão errados?"):
  if st.button("Recalcular os totais da tabela geral"):
    with st.spinner("Recalculando..."):
      recalculate_geral(df)
      
    st.rerun()

st.divider()

def read_df():
    df = pd.read_csv("data/geral_2024.csv").sort_values("Total com corte", ascending=False).reset_index(drop=True)
    df["Classificação"] = df.index + 1
    return df

df = read_df()
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
