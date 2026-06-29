import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import urllib.request

# ==========================================
# 1. CONFIGURAÇÃO E DADOS
# ==========================================
st.set_page_config(page_title="Aquecimento de Água — Painel de Decisão", layout="wide")

# Paleta de cores por segmento (consistente com os notebooks/guia)
cores_segmento = {
    'Prêmio premium': '#663399',  # Roxo
    'Vitrine solar': '#FF8C00',   # Laranja
    'Fronteira morna': '#2E8B57', # Verde
    'Baixa prioridade': '#808080' # Cinza
}

MESES = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
         7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
ORDEM_MESES = list(MESES.values())
BASE_HDD = 20.0  # temperatura-base dos graus-dia de aquecimento (escolha de sensibilidade)


@st.cache_data
def carregar_dados():
    caminho_base = 'dados_projeto_ciencia_dados/'
    df_principal = pd.read_csv(f'{caminho_base}dados_consolidados_looker.csv')
    df_trends = pd.read_csv(f'{caminho_base}gtrends_serie_temporal.csv')
    df_pdfs = pd.read_csv(f'{caminho_base}pdfs_frequencia_termos.csv')

    df_trends['data'] = pd.to_datetime(df_trends['data'])
    # Graus-dia de aquecimento por linha UF×ano×mês (proxy físico da necessidade de aquecer)
    df_principal['graus_dia'] = np.clip(BASE_HDD - df_principal['temp_media_mensal'], 0, None) * df_principal['n_dias']
    return df_principal, df_trends, df_pdfs


df, df_trends, df_pdfs = carregar_dados()


@st.cache_data
def carregar_geojson_uf():
    # GeoJSON das UFs do Brasil; chave de junção = properties.SIGLA (ex.: 'SP')
    url = "https://raw.githubusercontent.com/giuliano-macedo/geodata-br-states/main/geojson/br_states.json"
    with urllib.request.urlopen(url) as r:
        return json.load(r)


geojson_uf = carregar_geojson_uf()


def idx100(s):
    """Normaliza uma série para média = 100 (compara formato, não magnitude)."""
    return 100 * s / s.mean()


# ==========================================
# 2. BARRA LATERAL (MENU E FILTROS)
# ==========================================
st.sidebar.title("Painel de Decisão")
st.sidebar.caption("Aquecimento de água no Brasil — onde, com quê e quando vender.")

pagina = st.sidebar.radio("Página:", [
    "1. A decisão (onde entrar)",
    "2. Qual produto (fit × renda)",
    "3. Quanta demanda (graus-dia)",
    "4. Quando vender (Trends)",
])

st.sidebar.markdown("---")
st.sidebar.header("Filtros (páginas 1 a 3)")
regioes_selecionadas = st.sidebar.multiselect("Região", options=sorted(df['regiao'].unique()), default=sorted(df['regiao'].unique()))
segmentos_selecionados = st.sidebar.multiselect("Segmento", options=list(cores_segmento.keys()), default=list(cores_segmento.keys()))

df_filtrado = df[(df['regiao'].isin(regioes_selecionadas)) & (df['segmento'].isin(segmentos_selecionados))]

# Guarda contra seleção vazia (a página 4 é nacional e não depende desses filtros)
if df_filtrado.empty and not pagina.startswith("4"):
    st.warning("Nenhum dado para os filtros selecionados. Ajuste a Região/Segmento na barra lateral.")
    st.stop()

# Grão UF (colunas por UF são constantes nas linhas mensais)
df_uf = df_filtrado.drop_duplicates(subset=['uf'])

# ==========================================
# 3. PÁGINAS — uma decisão por página
# ==========================================

if pagina.startswith("1"):
    st.title("📍 A decisão: onde entrar primeiro?")
    st.markdown("**Não existe uma lista única de melhores UFs — existem dois mercados opostos.** "
                "O Nordeste é onde o produto rende mais (sol); o Sul/Sudeste é onde há frio, renda e necessidade.")

    c1, c2, c3 = st.columns(3)
    c1.metric("UFs em análise", len(df_uf))
    c2.metric("Oportunidade média", f"{df_uf['oportunidade_conversao'].mean():.1f}")
    c3.metric("Renda média p/c", f"R$ {df_uf['rendimento_medio_pc'].mean():,.0f}")

    fig_mapa = px.choropleth(
        df_uf, geojson=geojson_uf, locations='uf', featureidkey='properties.SIGLA',
        color='segmento', color_discrete_map=cores_segmento, hover_name='uf_nome',
        hover_data={'uf': False, 'oportunidade_conversao': ':.1f', 'aptidao_solar': ':.2f',
                    'rendimento_medio_pc': ':,.0f'},
        title="Segmento estratégico de cada UF",
    )
    fig_mapa.update_geos(fitbounds="locations", visible=False)
    fig_mapa.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig_mapa, width='stretch')

    st.success("**Recomendação:** trate o Nordeste (Vitrine solar) e o Sul/Sudeste (Prêmio premium) como dois "
               "go-to-markets distintos, com produtos e discursos próprios — detalhe nas páginas 2 a 4.")

elif pagina.startswith("2"):
    st.title("☀️ Qual produto: o fit técnico e a renda estão invertidos")
    st.markdown("Eixo X = capacidade de pagar (renda); eixo Y = aptidão solar. "
                "As linhas marcam as medianas. O canto **superior-direito** (apto **e** paga) é quase vazio — esse é o problema.")

    mx, my = df_uf['rendimento_medio_pc'].median(), df_uf['aptidao_solar'].median()
    fig = px.scatter(df_uf, x='rendimento_medio_pc', y='aptidao_solar',
                     size='oportunidade_conversao', color='segmento', text='uf',
                     color_discrete_map=cores_segmento, hover_name='uf_nome',
                     title="Mapa estratégico: quem paga × onde o solar rende")
    fig.update_traces(textposition='top center')
    fig.add_vline(x=mx, line_dash="dash", line_color="gray")
    fig.add_hline(y=my, line_dash="dash", line_color="gray")
    fig.add_annotation(x=df_uf['rendimento_medio_pc'].max(), y=df_uf['aptidao_solar'].min(),
                       text="PAGA, sol fraco (S/SE)<br>→ premium: conforto/backup", showarrow=False,
                       xanchor="right", yanchor="bottom", font=dict(size=11), bgcolor="rgba(245,245,245,0.8)")
    fig.add_annotation(x=df_uf['rendimento_medio_pc'].min(), y=df_uf['aptidao_solar'].max(),
                       text="APTO, renda baixa (NE)<br>→ solar c/ financiamento", showarrow=False,
                       xanchor="left", yanchor="top", font=dict(size=11), bgcolor="rgba(245,245,245,0.8)")
    fig.update_layout(xaxis_title="Renda média per capita (R$)", yaxis_title="Aptidão solar")
    st.plotly_chart(fig, width='stretch')

    corr = df_uf[['oportunidade_conversao', 'cop_medio_anual', 'aptidao_solar']].corr()['oportunidade_conversao']
    st.caption(f"Inversão: oportunidade × COP = {corr['cop_medio_anual']:+.2f} · "
               f"oportunidade × aptidão solar = {corr['aptidao_solar']:+.2f} "
               "→ a 'oportunidade' cai onde os produtos rendem mais.")

    st.success("**Recomendação:** solar de baixo custo **com financiamento** no Nordeste (gargalo é preço, não desejo); "
               "substituição premium do chuveiro / solar com apoio elétrico no Sul/Sudeste (vender conforto e custo de operação).")

elif pagina.startswith("3"):
    st.title("❄️ Quanta demanda — e por que o consumo elétrico engana")
    st.markdown("O consumo elétrico total **pica no verão** (ar-condicionado). A necessidade de aquecer água, "
                "medida por **graus-dia**, pica no inverno e se concentra no Sul.")

    # Necessidade de aquecimento por UF (graus-dia anuais médios)
    hdd_uf = (df_filtrado.groupby(['uf', 'ano'])['graus_dia'].sum()
              .groupby('uf').mean().sort_values(ascending=False).reset_index())
    fig_hdd = px.bar(hdd_uf.head(12), x='uf', y='graus_dia',
                     title=f"Graus-dia de aquecimento por UF (base {BASE_HDD:.0f}°C, média anual) — top 12")
    fig_hdd.update_layout(yaxis_title="graus-dia · ano", xaxis_title="")
    st.plotly_chart(fig_hdd, width='stretch')

    # Os três proxies discordam (formato sazonal normalizado)
    consumo_m = idx100(df_filtrado.groupby('mes')['consumo_residencial_mwh'].sum())
    hdd_m = idx100(df_filtrado.groupby('mes')['graus_dia'].mean())
    trd = df_trends[df_trends['termo'] == 'aquecedor solar'].groupby('mes')['indice_busca'].mean()
    trd_m = idx100(trd)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[MESES[m] for m in consumo_m.index], y=consumo_m.values, mode='lines+markers', name="Consumo total (MWh)"))
    fig.add_trace(go.Scatter(x=[MESES[m] for m in hdd_m.index], y=hdd_m.values, mode='lines+markers', name="Necessidade (graus-dia)"))
    fig.add_trace(go.Scatter(x=[MESES[m] for m in trd_m.index], y=trd_m.values, mode='lines+markers', name="Busca 'aquecedor solar'"))
    fig.update_xaxes(categoryorder='array', categoryarray=ORDEM_MESES, title_text="Mês")
    fig.update_yaxes(title_text="Índice (média do ano = 100)")
    fig.update_layout(title_text="Os proxies discordam: consumo pica no verão; demanda de aquecimento, no inverno")
    st.plotly_chart(fig, width='stretch')

    st.success("**Recomendação:** pare de usar MWh total como sinal de aquecimento — ele segue o ar-condicionado. "
               "Use graus-dia: a necessidade de aquecimento de água é dominada por **RS, SC e PR**.")

else:  # página 4
    st.title("🔍 Quando vender: o consumidor e o discurso do setor")
    st.markdown("O interesse de busca por aquecimento **pica no inverno (mai–jul)** — esse é o calendário comercial. "
                "_(Esta página é nacional; não depende dos filtros de região/segmento.)_")

    st.subheader("Sazonalidade do interesse (Google Trends)")
    saz = df_trends.groupby(['mes', 'termo'])['indice_busca'].mean().reset_index()
    saz['mes_nome'] = saz['mes'].map(MESES)
    fig_saz = px.line(saz, x='mes_nome', y='indice_busca', color='termo', markers=True,
                      title="Índice médio de busca por mês")
    fig_saz.update_xaxes(categoryorder='array', categoryarray=ORDEM_MESES, title_text="Mês")
    fig_saz.add_vrect(x0=3.5, x1=6.5, fillcolor="gray", opacity=0.12, line_width=0)
    st.plotly_chart(fig_saz, width='stretch')

    st.subheader("Série semanal (tendência de longo prazo)")
    termos = st.multiselect("Termos", options=sorted(df_trends['termo'].unique()),
                            default=sorted(df_trends['termo'].unique()))
    df_t = df_trends[df_trends['termo'].isin(termos)]
    fig_trends = px.line(df_t, x='data', y='indice_busca', color='termo',
                         title="Volume de buscas ao longo das semanas")
    st.plotly_chart(fig_trends, width='stretch')

    st.subheader("Evolução do discurso institucional (PDFs do setor)")
    fig_pdfs = px.bar(df_pdfs, x='periodo', y='frequencia', color='termo', barmode='group',
                      title="Frequência de termos por período")
    st.plotly_chart(fig_pdfs, width='stretch')

    st.success("**Recomendação:** concentre mídia e estoque entre **abril e julho**. Mensagem no Sul: "
               "\"troque o chuveiro antes do inverno\". Use os termos que o consumidor já busca (\"aquecedor/aquecimento solar\").")
