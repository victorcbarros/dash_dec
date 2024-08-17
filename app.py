# importando as bibliotecas 
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


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


# Agrupar por REGIONAL e DATA (mensal)
df_causa = df_filtrado5.groupby('CAUSA' )[['DEC']].sum().sort_values(by='DEC',ascending=False)
df_causa.reset_index(inplace=True)
df_causa['PERCENTUAL'] = (df_causa['DEC'] / df_causa['DEC'].sum()) * 100
df_causa['PERCENTUAL ACUMULADO'] = df_causa['PERCENTUAL'].cumsum() / df_causa['PERCENTUAL'].sum() * 100



# Agrupar por EQUIPAMENTO e somar os valores de DEC
df_equipamentos = df_filtrado5.groupby('EQUIPAMENTO')[['DEC']].sum().sort_values(by='DEC', ascending=False)
df_equipamentos.reset_index(inplace=True)
df_equipamentos['DEC'] = df_equipamentos['DEC'].round(4)
# Garantir que a coluna 'EQUIPAMENTO' seja tratada como uma categoria
df_equipamentos['EQUIPAMENTO'] = df_equipamentos['EQUIPAMENTO'].astype('category')
# Garantir que a coluna 'EQUIPAMENTO' seja tratada como string
df_equipamentos['EQUIPAMENTO'] = df_equipamentos['EQUIPAMENTO'].astype(str)
# Garantir que a coluna 'EQUIPAMENTO' seja tratada como uma categoria
df_equipamentos['EQUIPAMENTO'] = pd.Categorical(df_equipamentos['EQUIPAMENTO'], categories=df_equipamentos['EQUIPAMENTO'].unique())
# Remover a categoria 'não identificado'
df_equipamentos = df_equipamentos[df_equipamentos['EQUIPAMENTO'] != 'Não Identificado']
# Encontre o valor máximo de DEC
max_dec = df_equipamentos['DEC'].max()


# Agrupar por REGIONAL e DATA (mensal)
df_num_interrup_equipamentos = df_filtrado5.groupby( pd.Grouper(key='DATA', freq='M'))['OCORRENCIA_ID'].count().reset_index()
df_num_interrup_equipamentos.columns = ['DATA','CONTAGEM']
# Formatar a coluna DATA para mostrar apenas o mês e o ano
df_num_interrup_equipamentos['MES'] = df_num_interrup_equipamentos['DATA'].dt.to_period('M').astype(str)
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
df_num_interrup_equipamentos['MES'] = df_num_interrup_equipamentos['MES'].map(meses_pt)
# Encontre o valor máximo de CONTAGEM
max_contagem = df_num_interrup_equipamentos['CONTAGEM'].max()





df_pergunta4 = df_filtrado5.copy()
df_pergunta4['DATA'] = pd.to_datetime(df_pergunta4['DATA'])
df_pergunta4.set_index('DATA', inplace=True)
# Agrupar dados por mês e calcular o DEC total
df_dec_mensal = df_pergunta4[['DEC']].resample('M').sum()
# Calcular o DEC acumulado
df_dec_mensal['DEC_ACUMULADO'] = df_dec_mensal['DEC'].cumsum()



df_dec_regional = df_filtrado5.groupby('REGIONAL')['DEC'].sum().reset_index()
# Ordenar os dados do maior para o menor
df_dec_regional = df_dec_regional.sort_values(by='DEC', ascending=False)


# Agrupar dados por regional e calcular o FEC total
df_fec_regional = df_filtrado5.groupby('REGIONAL')['FEC'].sum().reset_index()
# Ordenar os dados do menor para o maior
df_fec_regional = df_fec_regional.sort_values(by='FEC', ascending=True)


df_abrangencia_regional = df_filtrado5.groupby('ABRANGENCIA')['DEC'].sum().reset_index()
# Ordenar os dados do maior para o menor
df_abrangencia_regional = df_abrangencia_regional.sort_values(by='DEC', ascending=False)

df_conjunto = df_filtrado5.groupby('CONJUNTO')['FEC'].sum().reset_index()
# Ordenar os dados do maior para o menor
df_conjunto = df_conjunto.sort_values(by='FEC', ascending=False)
df_conjunto_top10 = df_conjunto.head(10)









### graficos ************************************************************************************************************
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



# Criar o gráfico de barras para o DEC por causa
fig_pareto = go.Figure()

# Adicionar barras sem rótulos de dados
fig_pareto.add_trace(go.Bar(
    x=df_causa['CAUSA'],
    y=df_causa['DEC'],
    name='DEC',
    marker=dict(color='#00C0F3'),
    textposition='none'  # Remove os rótulos de dados das barras
))

# Adicionar linha de Percentual Acumulado com rótulos condicionais
fig_pareto.add_trace(go.Scatter(
    x=df_causa['CAUSA'],
    y=df_causa['PERCENTUAL ACUMULADO'],
    name='Percentual Acumulado',
    yaxis='y2',
    mode='lines+markers+text',
    line=dict(color='#FABD0A', width=2),
    marker=dict(size=8),  # Tamanho dos marcadores
    text=[f'{val:.2f}%' if val <= 85 else '' for val in df_causa['PERCENTUAL ACUMULADO']],  # Adiciona rótulos com porcentagem até 81%
    textposition='top center',  # Posiciona os rótulos acima dos pontos
    textfont=dict(size=12, color='black'),  # Ajusta o tamanho da fonte e a cor dos rótulos
))

# Atualizar layout para ajustar espaçamento, tamanho de fonte e largura do gráfico
fig_pareto.update_layout(
    title='Gráfico de Pareto - DEC por Causa',
    title_font=dict(size=18),
    xaxis=dict(
        title_font=dict(size=14),
        tickangle=-45,  # Gira os rótulos do eixo X em 45 graus
        tickfont=dict(size=12),  # Ajusta o tamanho da fonte dos rótulos do eixo X
    ),
    yaxis=dict(
        title='DEC',
        title_font=dict(size=14),
        tickfont=dict(size=12),  # Ajusta o tamanho da fonte dos rótulos do eixo Y
        gridcolor='rgba(0,0,0,0)'  # Remove as grades verticais
    ),
    yaxis2=dict(
        title='Percentual Acumulado',
        overlaying='y',
        side='right',
        range=[0, 110],  # Escala da porcentagem ajustada de 0 a 100%
        title_font=dict(size=14),
        tickfont=dict(size=12),  # Ajusta o tamanho da fonte dos rótulos do eixo Y2
        showgrid=True,  # Exibe a grade horizontal para o eixo Y2
        gridcolor='rgba(211, 211, 211, 0.5)'  # Define a cor e a opacidade da grade horizontal
    ),
    width=1090,  # Aumenta a largura do gráfico
    margin=dict(l=60, r=60, t=80, b=120),  # Ajusta as margens do gráfico
    showlegend=False
)



# Crie o gráfico de barras com rótulos de dados
fig_top20 = px.bar(df_equipamentos.head(20), x='EQUIPAMENTO', y='DEC', 
             title='Valores de DEC por Equipamento',
             labels={'EQUIPAMENTO': 'Nome do Equipamento', 'DEC': 'Valor do DEC'},
             text='DEC',  # Adiciona os rótulos de dados
             color_discrete_sequence=['#2F2E79'])  # Define uma cor uniforme para todas as barras

# Ajuste o layout do gráfico
fig_top20.update_layout(
    xaxis_title='Nome do Equipamento',
    yaxis_title='Valor do DEC',
    xaxis_tickangle=-45,  # Inclina os rótulos do eixo x para melhor leitura
    yaxis=dict(range=[0, max_dec * 1.3]),  # Define o intervalo do eixo y
    xaxis_type='category',  # Força o eixo x a ser categórico
    bargap=0.2  # Ajusta a largura das barras (reduza o valor para barras mais largas)
)

# Ajuste a aparência dos rótulos de dados
fig_top20.update_traces(
    texttemplate='%{text:.4f}',  # Ajusta a precisão dos rótulos
    textposition='inside',  # Coloca os rótulos dentro das barras
    textfont=dict(color='white', size=12),  # Define a cor dos rótulos como branca e aumenta o tamanho da fonte
    textangle=0  # Define a rotação dos rótulos para horizontal
)




# Crie o gráfico de linha por mês com marcadores e rótulos de dados
fig_num_int = px.line(df_num_interrup_equipamentos, x='MES', y='CONTAGEM', 
             title='Quantidade de Interrupções por Mês',
             #labels={'MES': 'Mês', 'CONTAGEM': 'Número de Interrupções'},
             color_discrete_sequence=['#2F2E79'],  # Define uma cor uniforme para a linha
             text='CONTAGEM')  # Adiciona os rótulos de dados

# Ajuste o layout do gráfico
fig_num_int.update_layout(
    xaxis_title='Mês',
    yaxis_title='Número de Interrupções',
    xaxis_tickangle=0,  # Inclina os rótulos do eixo x para melhor leitura
    yaxis=dict(range=[0, max_contagem * 1.3]),  # Define o intervalo do eixo y
    height=400,  # Ajusta a altura do gráfico
    width=800  # Ajusta a largura do gráfico
)

# Adicione marcadores e rótulos de dados à linha
fig_num_int.update_traces(
    mode='lines+markers+text',  # Adiciona marcadores e rótulos de dados
    marker=dict(size=8, color='#2F2E79', line=dict(width=2, color='#2F2E79')),  # Estilo dos marcadores
    line=dict(width=3),  # Define a largura da linha
    textposition='top center',  # Posição dos rótulos de dados
    texttemplate='%{text:.0f}'  # Formato dos rótulos de dados (número inteiro)
)



# Criar a visualização
fig = go.Figure()
# Gráfico de barras para os valores mensais
fig.add_trace(go.Bar(
    x=df_dec_mensal.index,
    y=df_dec_mensal['DEC'],
    name='DEC Mensal',
    marker_color='#00C0F3',
    text=df_dec_mensal['DEC'].apply(lambda x: f'{x:.5f}'),  # Adiciona rótulos com 5 casas decimais
    texttemplate='%{text}',  # Usa o texto formatado
    textposition='outside'  # Posiciona rótulos fora das barras
))

# Linha para o valor acumulado
fig.add_trace(go.Scatter(
    x=df_dec_mensal.index,
    y=df_dec_mensal['DEC_ACUMULADO'],
    mode='lines+markers',
    name='DEC Acumulado',
    line=dict(color='#F15B40', width=4),
    text=df_dec_mensal['DEC_ACUMULADO'].apply(lambda x: f'{x:.5f}'),  # Adiciona rótulos com 5 casas decimais
    texttemplate='%{text}',  # Usa o texto formatado
    textposition='top right'  # Posiciona rótulos acima dos pontos
))

# Formatar o eixo X para mostrar apenas mês e ano
fig.update_xaxes(
    tickformat='%b %Y',  # Formata as datas para Mês Ano
    tickvals=df_dec_mensal.index,  # Define os valores dos ticks
    ticktext=[date.strftime('%b %Y') for date in df_dec_mensal.index]  # Define o texto dos ticks
)

# Layout
fig.update_layout(
    title='DEC Mensal e DEC Acumulado',
    xaxis_title='Data',
    yaxis_title='DEC',
    yaxis2=dict(
        title='DEC Acumulado',
        overlaying='y',
        side='right'
    ),
    legend=dict(x=0.1, y=1.1, orientation="h"),
    bargap=0.2
)


# Calcular o limite máximo do eixo Y
max_dec = df_dec_regional['DEC'].max()
max_fec = df_fec_regional['FEC'].max()
y_max_dec = max_dec * 1.3
y_max_fec = max_fec * 1.3

# Criar a visualização para DEC
fig_dec2 = go.Figure()

fig_dec2.add_trace(go.Bar(
    x=df_dec_regional['REGIONAL'],
    y=df_dec_regional['DEC'],
    name='DEC Total',
    marker_color='#00C0F3',
    text=df_dec_regional['DEC'].apply(lambda x: f'{x:.5f}'),  # Adiciona rótulos com 5 casas decimais
    texttemplate='%{text}',  # Usa o texto formatado
    textposition='outside'  # Posiciona rótulos fora das barras
))

# Layout para DEC
fig_dec2.update_layout(
    title='DEC Total por Regional (Ordenado do Maior para o Menor)',
    xaxis_title='Regional',
    yaxis_title='DEC Total',
    yaxis=dict(range=[0, y_max_dec]),  # Define o limite do eixo Y
    xaxis=dict(
        tickangle=-45  # Inclina os rótulos do eixo X para melhor visualização
    ),
    legend=dict(x=0.1, y=1.1, orientation="h")
)

# Criar a visualização para FEC
fig_fec2 = go.Figure()

fig_fec2.add_trace(go.Bar(
    x=df_fec_regional['REGIONAL'],
    y=df_fec_regional['FEC'],
    name='FEC Total',
    marker_color='#FABD0A',
    text=df_fec_regional['FEC'].apply(lambda x: f'{x:.5f}'),  # Adiciona rótulos com 5 casas decimais
    texttemplate='%{text}',  # Usa o texto formatado
    textposition='outside'  # Posiciona rótulos fora das barras
))

# Layout para FEC
fig_fec2.update_layout(
    title='FEC Total por Regional (Ordenado do Menor para o Maior)',
    xaxis_title='Regional',
    yaxis_title='FEC Total',
    yaxis=dict(range=[0, y_max_fec]),  # Define o limite do eixo Y
    xaxis=dict(
        tickangle=-45  # Inclina os rótulos do eixo X para melhor visualização
    ),
    legend=dict(x=0.1, y=1.1, orientation="h")
)

# Calcular o limite máximo do eixo Y para DEC
max_dec_abrangencia = df_abrangencia_regional['DEC'].max()
y_max_dec_abrangencia = max_dec_abrangencia * 1.3

# Calcular o limite máximo do eixo Y para FEC
max_fec_conjunto = df_conjunto['FEC'].max()
y_max_fec_conjunto = max_fec_conjunto * 1.3

# Criar a visualização para DEC por Abrangência
fig_dec_abrangencia = go.Figure()

fig_dec_abrangencia.add_trace(go.Bar(
    x=df_abrangencia_regional['ABRANGENCIA'],
    y=df_abrangencia_regional['DEC'],
    name='DEC Total',
    marker_color='#F15B40',
    text=df_abrangencia_regional['DEC'].apply(lambda x: f'{x:.5f}'),  # Adiciona rótulos com 5 casas decimais
    texttemplate='%{text}',  # Usa o texto formatado
    textposition='outside'  # Posiciona rótulos fora das barras
))

# Layout para DEC por Abrangência
fig_dec_abrangencia.update_layout(
    title='DEC Total por Abrangência (Ordenado do Maior para o Menor)',
    xaxis_title='Abrangência',
    yaxis_title='DEC Total',
    yaxis=dict(range=[0, y_max_dec_abrangencia]),  # Define o limite do eixo Y
    xaxis=dict(
        tickangle=-45  # Inclina os rótulos do eixo X para melhor visualização
    ),
    legend=dict(x=0.1, y=1.1, orientation="h")
)

# Criar a visualização para FEC por Conjunto (Top 10)
fig_fec_conjunto = go.Figure()

fig_fec_conjunto.add_trace(go.Bar(
    x=df_conjunto_top10['CONJUNTO'],
    y=df_conjunto_top10['FEC'],
    name='FEC Total',
    marker_color='#2F2E79',
    text=df_conjunto_top10['FEC'].apply(lambda x: f'{x:.5f}'),  # Adiciona rótulos com 5 casas decimais
    texttemplate='%{text}',  # Usa o texto formatado
    textposition='outside'  # Posiciona rótulos fora das barras
))

# Layout para FEC por Conjunto (Top 10)
fig_fec_conjunto.update_layout(
    title='FEC Total por Conjunto (Top 10)',
    xaxis_title='Conjunto',
    yaxis_title='FEC Total',
    yaxis=dict(range=[0, y_max_fec_conjunto]),  # Define o limite do eixo Y
    xaxis=dict(
        tickangle=-45  # Inclina os rótulos do eixo X para melhor visualização
    ),
    legend=dict(x=0.1, y=1.1, orientation="h")
)


# STREAMLIT ******************************************


col1,col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_DEC,use_container_width= True)
with col2:
    st.plotly_chart(fig_FEC,use_container_width= True)

col1 = st.columns(1)[0]
with col1:
    st.plotly_chart(fig_pareto,use_container_width= True)
col1 = st.columns(1)[0]
with col1:
    st.plotly_chart(fig_top20,use_container_width= True)


col1,col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_num_int,use_container_width= True)
with col2:
    st.plotly_chart(fig,use_container_width= True)


col1,col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_dec2,use_container_width= True)
with col2:
    st.plotly_chart(fig_fec2,use_container_width= True)


col1,col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_dec_abrangencia,use_container_width= True)
with col2:
    st.plotly_chart(fig_fec_conjunto,use_container_width= True)