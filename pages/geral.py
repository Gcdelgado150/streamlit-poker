import streamlit as st
import pandas as pd
from datetime import datetime
from helper_files import update_table_geral

current_date= datetime.now()

st.set_page_config(layout="wide")
st.title(f"Classificação Geral")

df = pd.read_csv("data/geral_2024.csv").sort_values("Total com corte", ascending=False).reset_index(drop=True)
cols_rodadas = [c for c in df.columns if c.startswith("Rodada")]
# Create two columns
col1, col2 = st.columns([1, 6])

# Place the button in the first column
with col1:
    month = st.selectbox("Mês para atualizar a classificação geral:", 
                         [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
                         index=current_date.month-1)
    
    if st.button("Atualizar a classificação geral"):
        update_table_geral(month)

# Apply formatting to specified columns
df[cols_rodadas + ["Total", "Total com corte"]] = df[cols_rodadas + ["Total", "Total com corte"]].applymap('{:,.2f}'.format)

# Function to highlight the first 3 rows (champions)
def highlight_lowest_cells(s):
  lowest = s[cols_rodadas].sort_values(ascending=True).head(2)
  return ['background-color: #c98181' if col in lowest.index.tolist() else ''  for col, value in s.items()]

# Apply the highlight functions
styled_data = df.style.apply(highlight_lowest_cells, axis=1)

# Display the styled DataFrame in Streamlit
st.title('Highlighted Data Table')
st.dataframe(styled_data, hide_index=True, on_select="ignore")