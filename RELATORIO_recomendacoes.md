# Relatório de Recomendações — Priorização Regional de Aquecimento de Água

**Projeto:** Análise da demanda de aquecimento de água e eficiência energética em residências brasileiras
**Cliente:** Empresa de soluções de aquecimento de água (coletor solar, bomba de calor e reservatório térmico)
**Granularidade:** Unidade da Federação (UF) | **Período climático/consumo:** 2021–2025

---

## 1. Sumário executivo

A análise integrou cinco bases públicas (INMET, Censo 2022/IBGE, PNAD Contínua, EPE e Google Trends) em uma tabela-mestre por UF e segmentou as 27 unidades em **quatro perfis comerciais** por K-Means. As conclusões centrais para o negócio:

- **O maior valor de conversão do chuveiro elétrico está no Sul/Sudeste** (frio + renda alta): SC, RS, SP, PR, DF lideram a oportunidade. A oportunidade de conversão é fortemente correlacionada com a renda (**+0,84**) — os melhores alvos também têm poder de compra.
- **O Nordeste é a melhor vitrine solar do país** (maior aptidão técnica), mas **o interesse do consumidor por solar ainda não acompanha o potencial** (correlação ~0 entre irradiação e busca). É uma oportunidade de **marketing educativo**.
- **O interesse por bomba de calor cresce no frio** (correlação −0,52 entre COP de inverno e busca): demanda surge onde a tecnologia é mais necessária.

## 2. Contexto e objetivo

O chuveiro elétrico está em ~85% dos domicílios brasileiros e é um dos maiores responsáveis pelo pico noturno de demanda elétrica. O objetivo do projeto é apoiar a empresa a **priorizar regiões e posicionar cada linha de produto** (coletor solar e bomba de calor), tratando o chuveiro elétrico como o mercado a capturar.

## 3. Dados e método (resumo)

- **Clima (INMET):** temperatura, mínima de inverno, irradiação → proxy de **COP** (bomba de calor, equações When2Heat) e índice de **aptidão solar** (irradiação × eficiência do coletor).
- **Domicílios (Censo 2022):** nº de domicílios, moradores, tipo, abastecimento de água.
- **Renda (PNAD):** rendimento médio domiciliar per capita por UF.
- **Consumo (EPE):** consumo residencial mensal → proxy da carga do chuveiro elétrico por domicílio.
- **Consumidor (Google Trends):** busca por aquecimento solar, aquecedor solar, aquecimento de piscina, chuveiro elétrico e bomba de calor.
- **Discurso institucional (PDFs PROCEL/EPE/ANEEL):** evolução do vocabulário do setor.
- **Modelagem:** padronização (StandardScaler) + K-Means (k=4, silhueta 0,34) para a segmentação; regressão (Linear e Random Forest) para o consumo em função do clima (MAE/RMSE); e árvore de decisão para extrair as regras dos segmentos.

## 4. Principais achados

**Clima e tecnologia.** O Sul atinge mínimas absolutas de até −8,9 °C no inverno, com COP estimado de ~2,9 (bomba de calor menos eficiente, porém mais necessária); o Norte/Nordeste operam com COP ~3,6 (clima ameno). A aptidão solar é maior no Nordeste (até ~2,8 kWh/m²/dia de calor útil).

**Consumo.** O consumo residencial cai no inverno (jun–jul) e sobe no verão — sinal de que parte relevante da carga é ar-condicionado, o que **qualifica** a leitura de aquecimento e reforça o uso de proxies regionais em vez de assumir aquecimento puro. A regressão confirma a **temperatura como principal preditor** do consumo por domicílio, com relação em **"U"** (sobe no frio e no calor) — por isso o Random Forest (R²≈0,52) supera a regressão linear (R²≈0,44).

**Segmentos por regra.** A árvore de decisão reproduz os segmentos com cortes simples: a **renda** é o primeiro critério; entre os de renda alta, o **clima (COP)** isola o "Prêmio premium"; entre os de renda menor, a **aptidão solar** isola a "Vitrine solar".

**Consumidor.** Na cesta comparativa de buscas, o **chuveiro elétrico domina** (a tecnologia ainda mental-default), o **solar vem em segundo**, e bomba de calor/piscina têm volume baixo. Renda puxa a busca por solar (**+0,61**).

**Discurso institucional.** Os termos de tecnologias eficientes aparecem pouco nos relatórios; "energia solar" cresce de forma tênue ao longo dos períodos (3 → 7 → 11 ocorrências). A leitura qualitativa é melhor capturada pelas nuvens de palavras do que pela contagem de termos compostos.

## 5. Segmentação comercial (K-Means)

| Segmento | UFs | Renda média | Oportunidade | Aptidão solar | Leitura |
|---|---|---|---|---|---|
| **Prêmio premium** | RJ, ES, PR, SC, RS, SP, MS, GO, DF | R$ 2.502 | 56 | 2,4 | Frio + renda alta → maior valor de conversão |
| **Fronteira morna** | RO, RR, TO, AP, MT | R$ 1.781 | 46 | 2,4 | Potencial intermediário, segundo estágio |
| **Vitrine solar** | RN, PI, PE, AL, SE, PB, BA, MG | R$ 1.494 | 23 | 2,6 | Melhor sol, demanda ainda baixa |
| **Baixa prioridade** | AM, PA, AC, CE, MA | R$ 1.252 | 21 | 2,3 | Baixa renda + pouca necessidade |

## 6. Recomendações por área

**Comercial**
1. **Concentrar esforço no segmento Prêmio premium**, com foco nas maiores oportunidades: **SC, RS, SP, PR, DF**. É onde a carga do chuveiro elétrico e a capacidade de pagamento se encontram — maior ticket e maior taxa de conversão esperada.
2. **Posicionar bomba de calor no Sul/Sudeste** (clima mais frio, mercado de piscina) e **coletor solar no Nordeste** (irradiação máxima), evitando empurrar o produto errado para a região errada.
3. Tratar a **Fronteira morna** como pipeline de segundo estágio, priorizando UFs com renda em ascensão (ex.: MT).

**Marketing**
1. **Campanha educativa de solar no Nordeste:** o potencial técnico é o maior do país, mas o consumidor ainda não busca solar na mesma proporção — há demanda latente a ser ativada.
2. **Calibrar a linguagem pelo que o consumidor já busca:** "aquecimento solar" e "aquecedor solar" têm tração; "bomba de calor" tem mais aderência via mercado de **piscina**. Usar esses termos na comunicação.
3. No segmento Premium, a mensagem é de **substituição do chuveiro elétrico** (economia + conforto), não de tecnologia abstrata.

## 7. Limitações

- **Tipo de aquecimento adotado** não está disponível (microdados do Censo 2022 não liberados); a adoção é inferida por **proxies** (consumo, clima, renda), não medida diretamente.
- **Google Trends** é um índice relativo normalizado (0–100); compara interesse, não volume absoluto.
- A **proxy de COP** é função direta da temperatura média mensal (suaviza extremos); serve como indicador comparativo regional, não como cálculo de engenharia.
- Granularidade limitada a **UF**, pois é a menor unidade comum a todas as bases públicas.

## 8. Próximos passos

- Dashboard interativo (Power BI/Tableau) — ver `GUIA_DASHBOARD.md`.
- Refinar o índice de oportunidade com pesos validados pelo time comercial (hoje 50% intensidade / 50% necessidade).
- Quando os microdados do Censo forem liberados, substituir os proxies pela variável real de tipo de aquecimento.
