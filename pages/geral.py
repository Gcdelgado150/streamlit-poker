import streamlit as st
import pandas as pd
from datetime import datetime

current_date= datetime.now()

st.set_page_config(layout="wide")
st.title(f"Classificação Geral")

df = pd.read_csv("data/geral.csv").sort_values("Total com corte", ascending=False).reset_index(drop=True)
cols_rodadas = [c for c in df.columns if c.startswith("Rodada")]

def apply_total_com_corte(s):
  cleanedList = sorted([x for x in s[cols_rodadas].values.tolist() 
                        if str(x) != 'nan'], reverse=True)
  return sum([value for value in cleanedList[0:-2]])

# Create two columns
col1, col2 = st.columns([1, 6])

# Place the button in the first column
with col1:
    if st.button("Atualizar a classificação geral"):
        month = st.selectbox("Mês para atualizar a classificação geral:", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], index=current_date.month-1)
        filepath = f"data/classificacao_{current_date.year}_{month}.csv"
        df_month = pd.read_csv(filepath).sort_values("Total", ascending=False).reset_index(drop=True)

        # Para cada novo jogador do mes
        for player in df_month.Players.values:
            # Se o jogador ja existe
            if player in df.Players.values:
                df.loc[df["Players"] == player, [f"Rodada {month}"]] = df_month[df_month["Players"] == player].Total.values[0]
            else:
                s = len(df)
                df.loc[s, "Classificação"] = s+1
                df.loc[s, "Players"] = player

                # Empty for all rodadas until this month
                for rodada in [c for c in df.columns if c.startswith("Rodada")]:
                    number_rodada = int(rodada.split("Rodada")[1])
                    if number_rodada < month:
                        df.loc[s, rodada] = 0
                    elif number_rodada == month:
                        df.loc[s, rodada] = df_month[df_month["Players"] == player].Total.values[0]

        df["Total"] = df[cols_rodadas].sum()
        df["Total com corte"] = df.apply(apply_total_com_corte, axis=0)
        st.success("Saved!")
        df.to_csv("data/geral.csv", index=False)

# Place the description in the second column
with col2:
    st.write("Clicando aqui você ira selecionar um mes para atualizar a classificacao geral utilizando aquele mes")

# Apply formatting to specified columns
df[cols_rodadas] = df[cols_rodadas].applymap('{:,.2f}'.format)

# Function to highlight the first 3 rows (champions)
def highlight_lowest_cells(s):
  lowest = s[cols_rodadas].sort_values(ascending=True).head(2)
  return ['background-color: #c98181' if col in lowest.index.tolist() else ''  for col, value in s.items()]

# # Function to highlight the first 3 rows (champions)
# def highlight_champions(s):
#   return ['background-color: #f3f8b1; color: black' if s.Classificação <= 3 else '' for _ in s]

# Function to highlight the rest
# def highlight_rest(s):
#   return ['background-color: #f3f8b1; color: black' if s.Classificação <= 3 else '' for _ in s]

# # Function to add border to a specific column
# def add_border(column):
#     def style_border(s):
#         return ['border-right: 2px solid red' if s.name == column else '' for _ in s]
#     return style_border

# def gradient_highlight(s):
#     gradient = s.rank(pct=True)
#     return ['background-color: rgba(255, 99, 71, {:.2f})'.format(val) for val in gradient]


# Apply the highlight functions
styled_data = df.style.apply(highlight_lowest_cells, axis=1)

# Display the styled DataFrame in Streamlit
st.title('Highlighted Data Table')
st.dataframe(styled_data, hide_index=True, on_select="ignore")