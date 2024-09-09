from datetime import datetime
import pandas as pd
import streamlit as st

def find_key_with_values(row, values):
    for key, value in row.items():
        # Check if both values are in the current list
        if value in values:
            yield key
    return []

def save_csv(status_save, df, filepath):
    if status_save:
        df.to_csv(filepath, index=False)

def optimize_transactions(df, rs_total_col='RS_total'):
    # Separate creditors and debtors
    creditors = df[df[rs_total_col] > 0].sort_values(by=rs_total_col, ascending=False).reset_index(drop=True)
    debtors = df[df[rs_total_col] < 0].sort_values(by=rs_total_col).reset_index(drop=True)

    transactions = []

    creditor_index = 0
    debtor_index = 0

    while creditor_index < len(creditors) and debtor_index < len(debtors):
        creditor = creditors.iloc[creditor_index]
        debtor = debtors.iloc[debtor_index]

        creditor_amount = creditor[rs_total_col]
        debtor_amount = -debtor[rs_total_col]

        # Determine the amount to transfer
        transfer_amount = min(creditor_amount, debtor_amount)

        transactions.append({
            'Pagador': debtor['Players'],  # Replace 'Player' with the actual column name containing player names
            'Recebedor': creditor['Players'],  # Replace 'Player' with the actual column name containing player names
            'Valor (R$)': transfer_amount
        })

        # Update amounts
        creditors.at[creditor_index, rs_total_col] -= transfer_amount
        debtors.at[debtor_index, rs_total_col] += transfer_amount

        # Move to the next creditor or debtor if they are settled
        if creditors.at[creditor_index, rs_total_col] == 0:
            creditor_index += 1
        if debtors.at[debtor_index, rs_total_col] == 0:
            debtor_index += 1

    st.dataframe(pd.DataFrame(transactions), hide_index=True)
    # return pd.DataFrame(transactions)

def update_table_geral(month):
    current_date = datetime.now()
    geral_filename = f"data/geral_{current_date.year}.csv"
    monthly_filename = f"data/classificacao_{current_date.year}_{month}.csv"

    # month = st.selectbox("Mês para atualizar a classificação geral:", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], index=current_date.month-1)
    df_month = pd.read_csv(monthly_filename).sort_values("Total", ascending=False).reset_index(drop=True)
    df = pd.read_csv(geral_filename).sort_values("Total com corte", ascending=False).reset_index(drop=True)

    cols_rodadas = [c for c in df.columns if c.startswith("Rodada")]

    def apply_total_com_corte(s):
        cleanedList = sorted([x for x in s[cols_rodadas].values.tolist() 
                                if str(x) != 'nan'], reverse=True)
        return sum([value for value in cleanedList[0:-2]])

    # Para cada novo jogador do mes
    for player in df_month.Players.values:
        # Se o jogador ja existe
        if player in df.Players.values:
            df.loc[df["Players"] == player, [f"Rodada {month}"]] = df_month[df_month["Players"] == player].Total.values[0]
        else:
            s = len(df)
            df.loc[s, "Classificação"] = s+1
            df.loc[s, "Players"] = player

            # Fill all rodadas (0 before this month)
            for rodada in [c for c in df.columns if c.startswith("Rodada")]:
                number_rodada = int(rodada.split("Rodada")[1])
                if number_rodada < month:
                    df.loc[s, rodada] = 0
                elif number_rodada == month:
                    df.loc[s, rodada] = df_month[df_month["Players"] == player].Total.values[0]

    df["Total"] = df[cols_rodadas].sum()
    df["Total com corte"] = df.apply(apply_total_com_corte, axis=1)
    st.success("Saved!")
    df.to_csv("data/geral_2024.csv", index=False)

