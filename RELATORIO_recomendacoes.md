# Relatório de Recomendações — Priorização Regional de Aquecimento de Água

**Projeto:** Análise da demanda de aquecimento de água e eficiência energética em residências brasileiras
**Cliente:** Empresa de soluções de aquecimento de água (coletor solar, bomba de calor e reservatório térmico)
**Granularidade:** Unidade da Federação (UF) | **Período climático/consumo:** 2021–2025
**Análise detalhada e gráficos:** `analise_insights.ipynb`

---

## 1. Pergunta de decisão

> Com **capacidade de vendas limitada**, em **quais UFs entrar primeiro**, com **qual produto** e com **qual discurso** em cada uma?

Tudo neste relatório serve a essa pergunta. A resposta curta: **não há uma lista única de "melhores UFs"** — há **dois mercados distintos**, com produtos e argumentos opostos, porque o lugar onde a tecnologia rende mais não é o lugar onde o cliente paga e precisa.

## 2. Sumário executivo — a tensão central

A análise integrou cinco bases públicas (INMET, Censo 2022/IBGE, PNAD Contínua, EPE e Google Trends) numa tabela-mestre por UF e segmentou as 27 unidades por K-Means. O achado que organiza a estratégia:

- **O produto que funciona melhor e o cliente que paga estão em regiões opostas.** O Nordeste tem a **maior aptidão solar** do país, mas **renda baixa** e **pouca necessidade de aquecer** (clima quente). O Sul/Sudeste tem **renda alta, frio e necessidade real**, porém é onde o **solar rende menos** e a **bomba de calor é menos eficiente** (o COP cai no frio). Numericamente, o índice de oportunidade correlaciona **−0,75 com o COP** e **−0,29 com a aptidão solar** — ou seja, ranqueia como "melhor" justamente onde os produtos rendem pior.
- **A necessidade de aquecimento é hiperconcentrada no Sul.** Em graus-dia de aquecimento (proxy físico da energia para aquecer água), **RS (4.628), SC (4.499) e PR (1.899)** estão uma ordem de grandeza acima do 4º colocado (SP, 618). O foco geográfico do *produto de aquecimento* é o Sul.
- **A demanda acontece no inverno (mai–jul)** — segundo o Google Trends, não segundo o consumo elétrico total (que é dominado por ar-condicionado e pica no verão).

## 3. Dados e método (resumo)

- **Clima (INMET):** temperatura, mínima de inverno, irradiação → proxy de **COP** (bomba de calor) e índice de **aptidão solar** (irradiação × eficiência do coletor); **graus-dia de aquecimento** (base 20 °C) como proxy de necessidade.
- **Domicílios (Censo 2022):** nº de domicílios, moradores, tipo, abastecimento de água.
- **Renda (PNAD):** rendimento médio domiciliar per capita por UF.
- **Consumo (EPE):** consumo residencial mensal.
- **Consumidor (Google Trends):** busca por aquecimento solar, aquecedor solar, aquecimento de piscina, chuveiro elétrico e bomba de calor.
- **Discurso institucional (PDFs PROCEL/EPE/ANEEL):** evolução do vocabulário do setor.
- **Modelagem:** K-Means (k=4, silhueta ≈ 0,34) para a segmentação; regressão (Linear e Random Forest) para consumo × clima; árvore de decisão para extrair as regras dos segmentos.

## 4. Principais achados

### 4.1 Fit do produto × capacidade de pagar estão invertidos
Médias por segmento:

| Segmento (região) | Radiação | COP | Renda p/c | Temp. mín. inverno | Busca "chuveiro" |
|---|---|---|---|---|---|
| **Prêmio premium** (S/SE) | 4,73 | **3,35** (menor) | **R$ 2.502** (maior) | **13,4 °C** (frio) | 44 (baixa) |
| **Vitrine solar** (NE) | **5,24** (maior) | 3,57 | R$ 1.494 | 19,5 °C | 72 (alta) |
| Fronteira morna (N) | 4,78 | 3,62 | R$ 1.781 | 20,8 °C | 66 |
| Baixa prioridade (N/NE) | 4,51 | 3,63 | R$ 1.252 | 21,8 °C | 76 |

Há **dois mercados**, não um ranking: alta aptidão técnica e alta capacidade de pagar quase não coincidem na mesma UF.

### 4.2 O consumo elétrico total mede ar-condicionado, não aquecimento
A correlação intra-UF entre temperatura e consumo residencial é **positiva** (+0,5 a +0,65) e o consumo **pica no verão** (Sul: fev/mar ≈ 115 vs. set ≈ 92, base 100). Se a carga fosse de aquecimento, subiria no frio. Conclusão: **MWh total não é proxy de aquecimento** — segue a refrigeração. O proxy físico correto é **graus-dia**, que (ao contrário do consumo) pica no inverno e concentra-se no Sul.

### 4.3 Quando vender: a sazonalidade está no Trends
O interesse de busca por todas as soluções **pica no inverno**: "chuveiro elétrico" em maio (mês de pico), "aquecimento solar" em junho, "aquecedor solar" em julho. Esse é o calendário comercial — e ele **concorda com os graus-dia**, não com o consumo elétrico.

### 4.4 Discurso institucional
Os termos de tecnologias eficientes aparecem pouco nos relatórios do setor; "energia solar" cresce de forma tênue ao longo dos períodos. A leitura qualitativa é melhor capturada pelas nuvens de palavras do que pela contagem de termos compostos.

## 5. Segmentação comercial (K-Means)

| Segmento | UFs | Renda média | Oportunidade | Aptidão solar | Leitura |
|---|---|---|---|---|---|
| **Prêmio premium** | RJ, ES, PR, SC, RS, SP, MS, GO, DF | R$ 2.502 | 56 | 2,4 | Frio + renda alta → maior necessidade e poder de compra |
| **Fronteira morna** | RO, RR, TO, AP, MT | R$ 1.781 | 46 | 2,4 | Potencial intermediário, segundo estágio |
| **Vitrine solar** | RN, PI, PE, AL, SE, PB, BA, MG | R$ 1.494 | 23 | 2,6 | Melhor sol, mas renda e necessidade baixas |
| **Baixa prioridade** | AM, PA, AC, CE, MA | R$ 1.252 | 21 | 2,3 | Baixa renda + pouca necessidade |

> O K-Means basicamente **redescobre região + clima + renda** (silhueta ≈ 0,34, fraca). É uma rotulagem útil para a comunicação, **não uma descoberta** — deve ser apresentada como tal.

## 6. Recomendações

**Estratégia geográfica e de produto (uma decisão por mercado)**

| Mercado | Evidência | Produto | Discurso | Quando |
|---|---|---|---|---|
| **Sul (RS, SC, PR)** | Graus-dia 5–25× o resto; renda alta; frio | Substituição premium do chuveiro / solar com apoio elétrico | Conforto + custo de operação no inverno | Campanha **abr–jul** |
| **Sudeste (SP, RJ, MG, ES)** | Renda alta, frio moderado | Solar + apoio elétrico | Economia na conta + conforto | abr–jul |
| **Nordeste (BA, PE, CE…)** | Melhor radiação, renda baixa | Solar de baixo custo | **Financiamento / payback rápido** | ano todo (demanda estável) |
| **Norte** | Baixa necessidade e renda | — | Despriorizar | — |

**Marketing**
1. **Calibrar a linguagem pelo que o consumidor busca:** "aquecimento/aquecedor solar" têm tração; "bomba de calor" aparece mais via mercado de **piscina**. Usar esses termos.
2. **Concentrar mídia entre abril e julho**, antes do pico de busca. Mensagem no Sul: *"troque o chuveiro antes do inverno"*.
3. No Nordeste, o gargalo **não é desejo, é preço** — comunicar financiamento e payback, não tecnologia abstrata.

## 7. Limitações

- **n = 27 UFs:** correlações são frágeis; tratar como indicativas, não conclusivas.
- **Índice `oportunidade_conversao` parcialmente circular:** correlaciona +0,84 com renda e ±0,8 com sinais do próprio Trends que entraram em sua construção, e **não foi validado** contra adoção real. Deve ser lido como **índice de decisão com pesos explícitos**, não como achado.
- **K-Means (silhueta ≈ 0,34)** aproxima região/clima/renda; rotulagem, não descoberta.
- **Tipo de aquecimento adotado** indisponível (microdados do Censo 2022 não liberados) → inferido por proxies.
- **COP e aptidão solar** são proxies derivados de temperatura/radiação, não medições de engenharia.
- **Google Trends** é índice relativo (0–100): compara interesse, não volume absoluto.
- Granularidade **UF** esconde heterogeneidade intraestadual (litoral × serra).

## 8. Próximos passos

1. **Validar o índice** contra a **geração distribuída fotovoltaica por UF** (relatórios ANEEL já no projeto): se a aptidão/oportunidade prevê adoção real, o índice ganha credibilidade; se não, vira hipótese a investigar.
2. **Substituir o proxy de demanda** definitivamente por graus-dia (+ estimativa de carga = domicílios × ΔT de aquecimento) nos painéis e no dashboard.
3. Refinar os pesos do índice de oportunidade junto ao time comercial e rodar **análise de sensibilidade**.
4. Quando os microdados do Censo forem liberados, trocar os proxies pela variável real de tipo de aquecimento.
5. Dashboards: ver `analise_insights.ipynb` (achados), `app.py` (Streamlit) e `GUIA_DASHBOARD_DATA_STUDIO.md` (Looker).
