import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import urllib.request

# ==========================================
# 1. CONFIGURAÇÃO E DADOS
# ==========================================
st.set_page_config(page_title="Dashboard Estratégico", layout="wide")

# Paleta de cores exata do seu guia
cores_segmento = {
    'Prêmio premium': '#663399',  # Roxo
    'Vitrine solar': '#FF8C00',   # Laranja
    'Fronteira morna': '#2E8B57', # Verde
    'Baixa prioridade': '#808080' # Cinza
}

MESES = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
         7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
ORDEM_MESES = list(MESES.values())

@st.cache_data
def carregar_dados():
    caminho_base = 'dados_projeto_ciencia_dados/'
    df_principal = pd.read_csv(f'{caminho_base}dados_consolidados_looker.csv')
    df_trends = pd.read_csv(f'{caminho_base}gtrends_serie_temporal.csv')
    df_pdfs = pd.read_csv(f'{caminho_base}pdfs_frequencia_termos.csv')

    # (#2) eixo temporal de verdade na série de buscas
    df_trends['data'] = pd.to_datetime(df_trends['data'])
    return df_principal, df_trends, df_pdfs

df, df_trends, df_pdfs = carregar_dados()

@st.cache_data
def carregar_geojson_uf():
    # GeoJSON das UFs do Brasil; a chave de junção é properties.SIGLA (ex.: 'SP')
    url = "https://raw.githubusercontent.com/giuliano-macedo/geodata-br-states/main/geojson/br_states.json"
    with urllib.request.urlopen(url) as r:
        return json.load(r)

geojson_uf = carregar_geojson_uf()

# ==========================================
# 2. BARRA LATERAL (MENU E FILTROS)
# ==========================================
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Ir para a página:",
    ["1. Visão Regional", "2. Aptidão por Produto", "3. Sazonalidade", "4. Consumidor e Discurso"]
)

st.sidebar.markdown("---")
st.sidebar.header("Filtros Globais (Páginas 1 a 3)")

regioes_selecionadas = st.sidebar.multiselect("Região", options=sorted(df['regiao'].unique()), default=sorted(df['regiao'].unique()))
segmentos_selecionados = st.sidebar.multiselect("Segmento", options=list(cores_segmento.keys()), default=list(cores_segmento.keys()))

df_filtrado = df[(df['regiao'].isin(regioes_selecionadas)) & (df['segmento'].isin(segmentos_selecionados))]

# (#1) guarda contra seleção vazia — evita gráficos/KPIs quebrados
if df_filtrado.empty and pagina != "4. Consumidor e Discurso":
    st.warning("Nenhum dado para os filtros selecionados. Ajuste a Região/Segmento na barra lateral.")
    st.stop()

# Grão UF para as páginas 1 e 2 (colunas por UF são constantes nas linhas mensais)
df_uf = df_filtrado.drop_duplicates(subset=['uf'])

# ==========================================
# 3. PÁGINAS DO DASHBOARD
# ==========================================

if pagina == "1. Visão Regional":
    st.title("📍 Visão Regional (Priorização)")

    st.subheader("Mapa de Priorização por Segmento")
    fig_mapa = px.choropleth(
        df_uf, geojson=geojson_uf, locations='uf', featureidkey='properties.SIGLA',
        color='segmento', color_discrete_map=cores_segmento,
        hover_name='uf_nome',
        hover_data={'uf': False, 'oportunidade_conversao': ':.1f', 'aptidao_solar': ':.2f'},
        title="Segmento estratégico de cada UF"
    )
    fig_mapa.update_geos(fitbounds="locations", visible=False)
    fig_mapa.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig_mapa, width='stretch')

    col1, col2 = st.columns(2)
    col1.metric("Quantidade de UFs", len(df_uf))
    col2.metric("Oportunidade Média de Conversão", f"{df_uf['oportunidade_conversao'].mean():.1f}")

    st.subheader("Oportunidade de Conversão por UF")
    df_uf_sorted = df_uf.sort_values(by='oportunidade_conversao', ascending=True)
    fig = px.bar(df_uf_sorted, x='oportunidade_conversao', y='uf', orientation='h',
                 color='segmento', color_discrete_map=cores_segmento,
                 title="Estados com maior potencial (Destaque Sul/Sudeste)")
    st.plotly_chart(fig, width='stretch')

elif pagina == "2. Aptidão por Produto":
    st.title("☀️ Aptidão por Produto (Solar vs. Bomba de Calor)")

    fig_scatter = px.scatter(df_uf, x='aptidao_solar', y='cop_medio_anual',
                             size='oportunidade_conversao', color='segmento',
                             hover_name='uf', text='uf', color_discrete_map=cores_segmento,
                             title="Mapa de Priorização Comercial")
    fig_scatter.update_traces(textposition='top center')
    st.plotly_chart(fig_scatter, width='stretch')

    col1, col2 = st.columns(2)
    with col1:
        fig_solar = px.bar(df_uf.sort_values(by='aptidao_solar', ascending=False).head(10),
                           x='uf', y='aptidao_solar', color='segmento', color_discrete_map=cores_segmento,
                           title="Top 10 UFs - Venda de Aquecedor Solar")
        st.plotly_chart(fig_solar, width='stretch')
    with col2:
        fig_bc = px.bar(df_uf.sort_values(by='cop_medio_anual', ascending=False).head(10),
                        x='uf', y='cop_medio_anual', color='segmento', color_discrete_map=cores_segmento,
                        title="Top 10 UFs - Eficiência Bomba de Calor (COP)")
        st.plotly_chart(fig_bc, width='stretch')

elif pagina == "3. Sazonalidade":
    st.title("❄️ Sazonalidade: Clima × Consumo")

    # (#5) deixa escolher entre volume total (Soma) e padrão (Média)
    agg = st.radio("Métrica de consumo", ["Soma", "Média"], horizontal=True)
    func = 'sum' if agg == "Soma" else 'mean'

    df_mensal = df_filtrado.groupby('mes').agg(
        consumo=('consumo_residencial_mwh', func),
        temp=('temp_media_mensal', 'mean')
    ).reset_index()
    df_mensal['mes_nome'] = df_mensal['mes'].map(MESES)  # (#4) meses por nome

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df_mensal['mes_nome'], y=df_mensal['consumo'],
                             name=f"Consumo (MWh) - {agg}", mode='lines+markers'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_mensal['mes_nome'], y=df_mensal['temp'],
                             name="Temperatura Média (°C)", mode='lines+markers'), secondary_y=True)
    fig.update_layout(title_text=f"Consumo residencial ({agg}) vs Temperatura ao longo do ano")
    fig.update_xaxes(title_text="Mês", categoryorder='array', categoryarray=ORDEM_MESES)
    fig.update_yaxes(title_text="Consumo (MWh)", secondary_y=False)
    fig.update_yaxes(title_text="Temperatura (°C)", secondary_y=True)
    st.plotly_chart(fig, width='stretch')
    st.info("Leitura: o consumo cai no inverno (jun–ago), acompanhando a queda de temperatura.")

elif pagina == "4. Consumidor e Discurso":
    st.title("🔍 O Consumidor e o Discurso Institucional")

    st.subheader("Tendência de Buscas (Google Trends)")
    # (#7) escolher quais termos comparar
    termos = st.multiselect("Termos", options=sorted(df_trends['termo'].unique()),
                            default=sorted(df_trends['termo'].unique()))
    df_t = df_trends[df_trends['termo'].isin(termos)]
    fig_trends = px.line(df_t, x='data', y='indice_busca', color='termo',
                         title="Volume de buscas por tecnologia ao longo das semanas")
    st.plotly_chart(fig_trends, width='stretch')
    st.caption("\"Chuveiro elétrico\" domina o interesse; \"aquecimento de piscina\" tem picos sazonais.")

    st.subheader("Evolução do Discurso (Documentos do Setor)")
    fig_pdfs = px.bar(df_pdfs, x='periodo', y='frequencia', color='termo', barmode='group',
                      title="Frequência de termos institucionais por período")
    st.plotly_chart(fig_pdfs, width='stretch')
