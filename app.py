# importando as bibliotecas 
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np



# Funções *****************************************************************************
def nome_mes(dados):
   meses_portugues = {
    'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril', 'May': 'Maio','June': 'Junho',
    'July': 'Julho','August': 'Agosto','September': 'Setembro','October': 'Outubro','November': 'Novembro','December': 'Dezembro'
    }
   dados['Mes'] = dados['DATA_INICIO'].dt.month_name()
   dados['Mes'] = dados['Mes'].map(meses_portugues)

def rotulo_de_dados(figura,dados,variavel):
    """Exibe o rotulo de dados na tela

    Args:
        figura (fig): grafico que sera colocado o rotulo
        dados (dataframe): dataframe de onde sera retirado a coluna da variavel
        variavel (column): coluna da variavel
    """
    figura.update_traces(
    mode='lines+markers+text',  # Modo para exibir linhas, marcadores e texto
    text=dados[variavel],  # Dados para exibir como texto
    textposition='top center',  # Posição do texto (acima do ponto de dados)
    textfont=dict(size=12, color='black')  # Configurações de fonte do texto
)


# Configurações *****************************************************************************************************
st.set_page_config(layout = 'wide')
st.markdown("<h3 style='text-align: center;'>DASHBOARD OCORRENCIAS DE INTERRUPÇÃO DE ENERGIA PIAUÍ 💡</h3>", unsafe_allow_html=True)
# Cores personalizadas
cores_personalizadas = ['#00C0F3', '#FABD0A', '#2F2E79', '#F15B40']


# IMPORTAÇÃO DOS DADOS ****************************************************************************
df = pd.read_parquet('DADOS.parquet', engine='pyarrow')
nome_mes(df)


# CORREÇÕES ****************************************************************************
# Remover valores nan ou NaT da lista e garantir a ordem correta dos meses
meses = df['Mes'].dropna().unique().tolist()
meses_ordenados = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
# Ordenar a lista meses de acordo com a ordem correta
meses.sort(key=lambda x: meses_ordenados.index(x))
# Filtrar valores nulos e ordenar a lista de regionais
regionais = df['REGIONAL'].dropna().unique().tolist()
regionais = [str(item) for item in regionais]
regionais.sort()
df['ABRANGENCIA'] = df['ABRANGENCIA'].replace(['CR'],'CLIENTE')
df['ABRANGENCIA'] = df['ABRANGENCIA'].replace(['TF'],'TRANSFORMADOR')
df['ABRANGENCIA'] = df['ABRANGENCIA'].replace(['CH'],'CHAVE')
df['ABRANGENCIA'] = df['ABRANGENCIA'].replace(['AL'],'ALIMENTADOR')
df['ABRANGENCIA'] = df['ABRANGENCIA'].replace(['SE'],'SUBESTAÇÃO')
df['EQUIPAMENTO'].replace(['nan','semplaca4649','sem2482','semplaca4648'],'Não Identificado', inplace=True)
df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')


# FILTRO *********************************************************************
st.sidebar.title('Filtros')

# Filtro de mes
mes_inicial, mes_final = st.sidebar.select_slider('Meses:', options=meses, value=(meses[0], meses[-1]))

# Mapeamento dos nomes dos meses para números
mes_num_map = {month: i+1 for i, month in enumerate(meses_ordenados)}

# Converter os meses selecionados para números
mes_inicial_num = mes_num_map[mes_inicial]
mes_final_num = mes_num_map[mes_final]

# Filtrar o DataFrame com base no intervalo selecionado
df_filtrado = df[
    (df['DATA_INICIO'].dt.month >= mes_inicial_num) & 
    (df['DATA_INICIO'].dt.month <= mes_final_num)
]

# Filtro REGIONAL
filtro_regional = st.sidebar.multiselect('Regionais:', regionais)
df_filtrado2 = df_filtrado
# Aplicar o filtro somente se uma ou mais regionais forem selecionadas
if filtro_regional:
    df_filtrado2 = df_filtrado[df_filtrado['REGIONAL'].isin(filtro_regional)]



# Filtro ABRANGENCIA
abrangencia = df_filtrado2['ABRANGENCIA'].unique().tolist()
abrangencia.sort()
abrangencia.insert(0,'TODAS')
filtro_abrangencia = st.sidebar.selectbox('Abrangencia:',abrangencia)
if filtro_abrangencia == 'TODAS':
    df_filtrado3 = df_filtrado2
else:
    df_filtrado3 = df_filtrado2[df_filtrado2['ABRANGENCIA'] == filtro_abrangencia]

df_filtrado4 = df_filtrado3


# Filtro CAUSA
causas = df_filtrado3['CAUSA'].unique().tolist()
causas.sort()
filtro_causa = st.sidebar.multiselect('Causas:',causas)
if filtro_causa:
    df_filtrado4 = df_filtrado3[df_filtrado3['CAUSA'].isin(filtro_causa)]


# Filtro EQUIPAMENTO

equipamento = df_filtrado4['EQUIPAMENTO'].unique().tolist()
equipamento.sort()
equipamento.insert(0,'TODAS')
filtro_equipamento = st.sidebar.selectbox('Equipamento:',equipamento)
if filtro_equipamento == 'TODAS':
    df_filtrado5 = df_filtrado4
else:
    df_filtrado5 = df_filtrado4[df_filtrado4['EQUIPAMENTO'] == filtro_equipamento]



# TABELAS *********************************************************************************


# Agrupar por REGIONAL e DATA (mensal)
df_def_fec = df_filtrado5.groupby(['REGIONAL', pd.Grouper(key='DATA', freq='M')])[['DEC','FEC']].sum()

# Resetar o índice para transformar em DataFrame
df_def_fec = df_def_fec.reset_index()

# Formatar a coluna DATA para mostrar apenas o mês e o ano
df_def_fec['DATA'] = df_def_fec['DATA'].dt.to_period('M').astype(str)

# Renomear colunas conforme necessário
df_def_fec.columns = ['REGIONAL', 'MES', 'DEC','FEC']

# Dicionário de meses em português
meses_pt = {
    '2024-01': 'Janeiro',
    '2024-02': 'Fevereiro',
    '2024-03': 'Março',
    '2024-04': 'Abril',
    '2024-05': 'Maio',
    '2024-06': 'Junho',
    '2024-07': 'Julho',
    '2024-08': 'Agosto',
    '2024-09': 'Setembro',
    '2024-10': 'Outubro',
    '2024-11': 'Novembro',
    '2024-12': 'Dezembro'
}

# Substituir os valores na coluna 'MES' com os nomes dos meses em português
df_def_fec['MES'] = df_def_fec['MES'].map(meses_pt)











### graficos
# Plotar o gráfico de linhas usando Plotly Express
fig_DEC = px.line(df_def_fec, x='MES', y='DEC', color='REGIONAL',
              color_discrete_sequence=cores_personalizadas,
              title='DEC Mensal por Regional',
              labels={'MES': 'Mês', 'DEC': 'DEC'},
              height=400)

# Adicionar marcadores e configurar grids
fig_DEC.update_traces(mode='lines+markers')  # Adicionar marcadores aos pontos
fig_DEC.update_layout(
    xaxis=dict(
        title='Mês',
        showgrid=False,  # Remover grid do eixo x
        tickmode='array',
        tickvals=list(meses_pt.values()),  # Definir valores dos ticks
        ticktext=list(meses_pt.values())  # Definir textos dos ticks
    ),
    yaxis=dict(
        title='DEC',
        showgrid=True,  # Mostrar grid do eixo y
        gridcolor='LightGray',  # Cor do grid
        gridwidth=0.5  # Largura do grid
    )
)

# Cores personalizadas
cores_personalizadas = ['#00C0F3', '#FABD0A', '#2F2E79', '#F15B40']

# Plotar o gráfico de linhas usando Plotly Express
fig_FEC = px.line(df_def_fec, x='MES', y='FEC', color='REGIONAL',
              color_discrete_sequence=cores_personalizadas,
              title='FEC Mensal por Regional',
              labels={'MES': 'Mês', 'FEC': 'FEC'},
              height=400)

# Adicionar marcadores e configurar grids
fig_FEC.update_traces(mode='lines+markers')  # Adicionar marcadores aos pontos
fig_FEC.update_layout(
    xaxis=dict(
        title='Mês',
        showgrid=False,  # Remover grid do eixo x
        tickmode='array',
        tickvals=list(meses_pt.values()),  # Definir valores dos ticks
        ticktext=list(meses_pt.values())  # Definir textos dos ticks
    ),
    yaxis=dict(
        title='FEC',
        showgrid=True,  # Mostrar grid do eixo y
        gridcolor='LightGray',  # Cor do grid
        gridwidth=0.5  # Largura do grid
    )
)














# STREAMLIT ******************************************


col1,col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_DEC,use_container_width= True)
with col2:
    st.plotly_chart(fig_FEC,use_container_width= True)


