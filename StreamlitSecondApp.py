# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 12:32:48 2022

@author: proc12
"""

import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:12345@localhost:5432/Engenharia')

st.title('Projeto POP')

df= pd.read_sql("select * from \"EngenhariaSecondProj\"", engine)
df=df.rename(columns={"ItemId": "Item", "MPS_ItensAltTipoComponente": "Tipo","ScheduledQuantity":"Quantidade da Op",
                      "ProductionOrderNumber": "Op", "Bom*ScheduledQuantity": "Quantidade Total","Adjust":"Ajuste","Category":"Categoria"})
data=df[['Item','Op','Quantidade da Op','Tipo','Quantidade Total','Categoria','Ajuste']]
data['Item'] = data['Item'].astype(str)
data["Quantidade POP"]=(data["Quantidade Total"]*data['Ajuste']).round()
data["Porcentagem POP"]=((data["Quantidade POP"]/data["Quantidade Total"])).replace((np.nan,np.NINF,np.inf), 0)
data['Porcentagem POP'] = pd.Series(["{0:.2f}%".format(val * 100) for val in data['Porcentagem POP']], index = data.index)
data['Quantidade Ajuste']=data['Quantidade POP']
data['Ajuste'] = pd.Series(["{0:.2f}%".format(val * 100) for val in data['Ajuste']], index = data.index)

def display_dataframe_quickly(df, max_rows=5000, **st_dataframe_kwargs):
    n_rows = len(df)
    if n_rows <= max_rows:
        # As a special case, display small dataframe directly.
        st.write(df)
    else:
        # Slice the DataFrame to display less information.
        start_row = st.slider('Linha inicial', 0, n_rows - max_rows)
        end_row = start_row + max_rows
        df = df[start_row:end_row]
        # Reindex Numpy arrays to make them more understadable.
        if type(df) == np.ndarray:
            df = pd.DataFrame(df)
            df.index = range(start_row,end_row)

        st.dataframe(df, **st_dataframe_kwargs)
        st.text('Mostrando colunas %i até %i de %i.' % (start_row, end_row - 1, n_rows))
        
#display_dataframe_quickly(data,200)
st.dataframe(data)


def apply_observation(row):
    if row['Quantidade Ajuste']==row['Quantidade POP']:
        return f"Quantidade padrão de perda {row['Quantidade Ajuste']}"
    elif row['Quantidade Ajuste']>row['Quantidade POP']:
        return f"Quantidade foi aumentada em {row['Quantidade Ajuste']-row['Quantidade POP']}"
    #peças ({row['Porcentagem Adjust']-row['Porcentagem POP']})"
    elif row['Quantidade Ajuste']<row['Quantidade POP']:
        return f"Quantidade foi reduzida  em {row['Quantidade POP']-row['Quantidade Ajuste']}"
    #peças ({row['Porcentagem POP']-row['Porcentagem Adjust']})"


st.download_button(label='📥 Baixar POP padrão',
                            data=data.to_csv(index=False).encode('utf-8'),
                            file_name= 'POP.csv')

uploaded_file1 = st.file_uploader("Escolha a planilha com os ajustes finais")

if uploaded_file1:
    if uploaded_file1.type == "text/csv":
        df1 = pd.read_csv(uploaded_file1)
    else:
        df1 = pd.read_excel(uploaded_file1)
    test1=True
    df2=df1
    df2["Porcentagem Ajuste"]=((df2["Quantidade Ajuste"]/df2["Quantidade Total"])).replace((np.nan,np.NINF,np.inf), 0)
    df2["Porcentagem Ajuste"]= pd.Series(["{0:.2f}%".format(val * 100) for val in df2['Porcentagem Ajuste']], index = data.index)


    #df2= df2.loc[df2["new adjustment values"].notnull()]
    st.dataframe(df2)
    df2['Observação'] = df2.apply(lambda row : apply_observation(row), axis=1)
    st.download_button(label='📥 Baixar relatório final POP',
                                data=df2.to_csv(index=False).encode('utf-8'),
                                file_name= 'Relatorio de perdas.csv')



