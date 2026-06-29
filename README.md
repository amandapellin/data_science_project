# Projeto de Ciência de Dados — Aquecimento de Água e Eficiência Energética (Brasil)

Análise, por Unidade da Federação (UF), do potencial regional para soluções de aquecimento de
água (**coletor solar** e **bomba de calor**), tendo o **chuveiro elétrico** como mercado a
substituir. Apoia a priorização de vendas e o posicionamento de mercado de uma empresa do setor.

Todos os notebooks foram desenvolvidos no **Google Colab** e leem/escrevem em:
`/content/drive/MyDrive/dados_projeto_ciencia_dados/`

---

## Ordem de execução dos notebooks

### Etapa 1 — Extração e tratamento (independentes entre si)
| # | Notebook | Lê (entrada bruta) | Gera |
|---|---|---|---|
| 1 | `pipeline_censo_ibge_2022.ipynb` | API SIDRA/IBGE (sidrapy) | `censo2022_tipo_domicilio.csv`, `censo2022_abastecimento_agua.csv`, `censo2022_moradores.csv`, `pnadc_rendimento_domiciliar.csv` |
| 2 | `pipeline_epe_consumo_energetico.ipynb` | `consumo_mensal_energia_eletrica_por_classe.xlsx` | `epe_consumo_por_segmento_uf.csv` |
| 3 | `pipeline_inmet.ipynb` | `2021.zip` … `2025.zip` (BDMEP/INMET) | `inmet_horario_tratado.csv`, `inmet_mensal_por_uf.csv` |
| 4 | `pipeline_google_trends.ipynb` | Google Trends (pytrends) | `gtrends_serie_temporal.csv`, `gtrends_por_estado.csv` |
| 5 | `pipeline_pdfs_institucionais.ipynb` | `pdfs_institucionais/*.pdf` | `pdfs_frequencia_termos.csv`, `pdfs_frequencia_pivot.csv` |

### Etapa 2 — Integração e EDA cruzada (depende de 1–5)
| # | Notebook | Lê | Gera |
|---|---|---|---|
| 6 | `pipeline_integracao_uf.ipynb` | todos os CSVs tratados acima | `painel_uf_integrado.csv`, `painel_mensal_uf.csv` |

### Etapa 3 — Modelagem / Machine Learning (depende de 6)
| # | Notebook | Lê | Gera |
|---|---|---|---|
| 7 | `pipeline_clusterizacao_uf.ipynb` | `painel_uf_integrado.csv` | `painel_uf_clusters.csv` |
| 8 | `pipeline_modelagem_complementar.ipynb` | `painel_mensal_uf.csv`, `painel_uf_clusters.csv` | (modelos e métricas; sem CSV) |

> **Importante:** rodar **7 antes de 8** — a árvore de decisão usa o `painel_uf_clusters.csv`.

---

## Mapa dos dados (`dados_projeto_ciencia_dados/`)

**Entradas brutas:** `2021.zip`–`2025.zip` (INMET), `consumo_mensal_energia_eletrica_por_classe.xlsx` (EPE), `pdfs_institucionais/` (12 PDFs PROCEL/EPE/ANEEL).

> ⚠️ **Não versionados no GitHub** (muito grandes / dados brutos intermediários — ver `.gitignore`): `*.zip` do INMET, `inmet_horario_tratado.csv` (~1,4 GB), o `.xlsx` da EPE e os PDFs institucionais maiores. Estão no Google Drive do projeto; o repositório guarda os **CSVs tratados e integrados**, que bastam para reproduzir os dashboards.

**Saídas tratadas (por fonte):** `censo2022_*.csv`, `pnadc_rendimento_domiciliar.csv`, `epe_consumo_por_segmento_uf.csv`, `inmet_horario_tratado.csv`, `inmet_mensal_por_uf.csv`, `gtrends_*.csv`, `pdfs_frequencia_*.csv`.

**Saídas integradas / modeladas:**
- `painel_uf_integrado.csv` — 1 linha por UF, 29 variáveis (clima, COP, aptidão solar, domicílios, renda, consumo, busca, oportunidade de conversão). **Base da clusterização.**
- `painel_mensal_uf.csv` — UF × ano × mês (clima + consumo). Base da regressão e da sazonalidade.
- `painel_uf_clusters.csv` — 1 linha por UF com o **segmento comercial** atribuído.

---

## Documentos
- `Projeto de Ciência de Dados - Amanda (revisado UF).docx` — descrição do projeto (versão revisada; usar esta).
- `RELATORIO_recomendacoes.md` — relatório de negócio com achados e recomendações por segmento.
- `GUIA_DASHBOARD.md` — guia para montar o dashboard (Power BI/Tableau).
- `GUIA_DASHBOARD_DATA_STUDIO.md` — guia para montar o dashboard no Looker Studio (Google Data Studio).
- `relatorio_data_studio.pdf` — exportação do relatório montado no Looker Studio.
- `2 ETAPA … INSTRUCOES.docx` — enunciado da atividade (referência).

---

## Dashboards e visualização

O projeto tem duas formas de visualização, ambas em nível de UF:

**1. Looker Studio (Google Data Studio)** — montado a partir dos CSVs, seguindo o `GUIA_DASHBOARD_DATA_STUDIO.md`. Exportação em `relatorio_data_studio.pdf`.

**2. App Streamlit (`app.py`)** — 4 páginas: (1) Visão regional com mapa do Brasil, (2) Aptidão por produto, (3) Sazonalidade clima × consumo, (4) Consumidor (Google Trends) e discurso institucional. Lê os CSVs do próprio repositório.

> 🔗 **App online:** _adicione aqui a URL gerada no deploy_ (ex.: `https://data-science-project-xxxx.streamlit.app`).

### Rodar o app localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```
Abre em `http://localhost:8501`.

### Publicar online (Streamlit Community Cloud — gratuito)
1. Acesse https://share.streamlit.io e entre com a conta GitHub.
2. **Create app → Deploy a public app from GitHub.**
3. Repositório `amandapellin/data_science_project`, branch `main`, *main file path* `app.py`.
4. **Deploy.** Gera uma URL pública fixa; cada novo `push` redeploia automaticamente.

> O dado consolidado usado pelo app é gerado por `dados_consolidados_looker.ipynb` (junta `painel_uf_clusters` + `painel_uf_integrado` + `painel_mensal_uf` → `dados_consolidados_looker.csv`).

---

## Dependências (Python)
`sidrapy`, `pandas`, `numpy`, `matplotlib`, `openpyxl`, `pdfplumber`, `spacy` (+ modelo `pt_core_news_sm`), `wordcloud`, `pytrends`, `scikit-learn`.
Cada notebook instala o que precisa na 1ª célula. No Colab, montar o Google Drive antes de executar.

## Modelos de Machine Learning
- **K-Means** (não supervisionado) — segmenta as 27 UFs em 4 perfis comerciais (silhueta ≈ 0,34).
- **Regressão Linear / Random Forest** — consumo residencial por domicílio em função do clima (métricas MAE/RMSE).
- **Árvore de Decisão** — regras interpretáveis dos segmentos.

## Limitações
- Granularidade em **UF** (menor unidade comum a todas as bases públicas).
- **Tipo de aquecimento adotado** indisponível (microdados do Censo 2022 não liberados) → uso de proxies.
- Google Trends é índice **relativo** (0–100); proxy de COP é função da temperatura média (indicador comparativo, não cálculo de engenharia).
