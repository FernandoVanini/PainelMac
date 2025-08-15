import streamlit as st
import altair as alt
import pandas as pd
import plotly.graph_objects as go
                   
from utils import loadData, getHospitalNames, getMonthNames, toFloat, toMoney, getProdData, getProdData_2

# Cria e exibe o gráfico de barras empilhadas usando Altair, para o hospital e tipo de atendimento específicos
def makeChart(col, hospital, tipo, height = 150, teto = False):
    hospitalList = getHospitalNames() if hospital == 'Todos' else [hospital]
    tipoList = ['Ambulatorial', 'Hospitalar'] if tipo == 'Ambos' else [tipo]    
    df, totRec = getProdData(theTable, hospitalList, tipoList, teto)
    if tipo == 'Ambos': tipo = "Ambulatorial e Hospitalar"
    with col:
        with st.container(border = True):
            #st.subheader(f"{hospital}: {tipo}")
            st.markdown(f"##### {hospital}: {tipo}")
            st.markdown(f"###### Alta: {toMoney(totRec['Alta'])}   Média: {toMoney(totRec['Média'])}")
            month_order = getMonthNames()
            chart = alt.Chart(df).mark_line(strokeWidth=3).encode(
                x=alt.X("Mes:N", sort = month_order, stack="zero", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Produção:Q"),
                color=alt.Color("Complexidade:N", scale=alt.Scale(range=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])),
                tooltip=["Mes", "Complexidade", "Produção"]
            ).properties(height=height)
            # apresentação do gráfico pelo streamlit
            st.altair_chart(chart, use_container_width=True)

# Cria e exibe o gráfico de barras empilhadas usando Altair, para o hospital e tipo de atendimento específicos
def makeGChart(tipo, height = 150):
    tipoList = ['Ambulatorial', 'Hospitalar'] if tipo == 'Ambos' else [tipo]
    df = getProdData_2(theTable, tipoList)            
    if tipo == 'Ambos': tipo = "Ambulatorial e Hospitalar"
    with st.container(border = True):
        st.markdown(f"##### Quadro Geral: {tipo}")

        #st.subheader(f"{tipo}")
        #st.write(f"Alta Complexidade: {toMoney(totRec['Alta'])}, Média Complexidade: {toMoney(totRec['Média'])}")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Produção:Q", stack="zero"),
            y=alt.Y("Hospital:N", sort=df["Hospital"].tolist()),
            color=alt.Color("Complexidade:N", scale=alt.Scale(range=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])),
            tooltip=["Hospital", "Complexidade", "Produção"]
        ).properties(height=height)
        # apresentação do gráfico pelo streamlit
        st.altair_chart(chart, use_container_width=True)

# Carrega os dados do arquivo CSV e converte para o formato de mapa
theTable = loadData('Indicadores_MAC.csv')  # the book is on the table

# Configuração da página do Streamlit
st.set_page_config(page_title = "Indicadores MAC - UNICAMP ", layout = 'wide')

hospital = None
tipo = None
names = getHospitalNames()
#names.append('Todos')
HGRID = [[ 'CAISM', 'CEPRE'], ['CIPOI', 'GASTRO'], ['HC', 'HEMO']]
with st.sidebar:
    st.title("Indicadores MAC")
    st.header("Configuração")
    #hospital = st.selectbox("Selecione o hospital", names)
    tipo = st.selectbox("Selecione o tipo de atendimento", ['Ambulatorial', 'Hospitalar', 'Ambos'])
    #complexidade = st.selectbox("Selecione a complexidade", ['Alta', 'Média', 'Ambas'])

    #print('==> hospital:', hospital, 'names:', names)

# Gráfico de produção por hospital
st.subheader("Atendimentos MAC - UNICAMP 2025")
cols = st.columns(2)
for c in range(len(HGRID)):
    for h in range(len(HGRID[c])):
        hospital = HGRID[c][h]
        if hospital:
            makeChart(cols[h], hospital, tipo)

col = st.columns(1)[0]
with col:
    st.subheader(" Produção Total")
    makeChart(col, 'Todos', tipo, 360, True)
    makeGChart(tipo, 360)
        

