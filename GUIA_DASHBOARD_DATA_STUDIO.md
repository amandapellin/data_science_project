# Guia do Dashboard — Google Data Studio (Looker Studio)

Guia para montar o painel interativo a partir dos CSVs já gerados, usando o **Google Data Studio / Looker Studio** (gratuito, em [lookerstudio.google.com](https://lookerstudio.google.com)). Tudo está em nível de UF, então as tabelas se ligam pela coluna `uf` (sigla) — exceto a série de buscas, que é nacional por termo.

> Observação: o "Google Data Studio" foi renomeado para **Looker Studio** em 2022. O produto e os passos são os mesmos; aqui usamos os dois nomes como sinônimos.

## 1. Fontes de dados (conectar)

No Looker Studio não se "importa" um arquivo como no Power BI: cada CSV vira uma **fonte de dados (data source)**. Duas formas de subir os CSVs:

- **File Upload (mais simples):** em *Criar → Fonte de dados → Upload de arquivos (CSV)*, envie cada CSV. Bom para arquivos estáticos.
- **Google Sheets (recomendado p/ atualização):** suba cada CSV para uma planilha no Google Sheets (uma aba/planilha por arquivo) e conecte via conector *Google Sheets*. Permite reabrir e atualizar os dados depois.

| Arquivo | Grão | Fonte de dados (nome sugerido) | Uso |
|---|---|---|---|
| `painel_uf_clusters.csv` | 1 linha por UF | `ds_clusters` | Tabela principal: segmento, aptidão solar, COP, oportunidade, renda |
| `painel_uf_integrado.csv` | 1 linha por UF | `ds_integrado` | Detalhe completo (29 colunas) para drill-down |
| `painel_mensal_uf.csv` | UF × ano × mês | `ds_mensal` | Sazonalidade (temperatura × consumo) |
| `gtrends_serie_temporal.csv` | semana × termo | `ds_trends` | Tendência de busca do consumidor |
| `pdfs_frequencia_termos.csv` | período × termo | `ds_pdfs` | Evolução do discurso institucional |

**Relacionamentos → use "Combinação de dados" (data blending):** o Looker Studio não tem modelo de relacionamento como o Power BI. Para cruzar tabelas no mesmo gráfico, use *Recurso → Combinar dados (Blend)* com **`uf` como chave de junção (join key)**:

- `ds_clusters` ⟕ `ds_mensal` por `uf` (junção *left*, 1:N) — para visuais que misturam segmento e série mensal.
- `ds_clusters` ⟕ `ds_integrado` por `uf` (1:1) — para enriquecer a tabela principal com colunas de detalhe.

Na prática, **a maioria dos gráficos não precisa de blend**: cada visual aponta para uma única fonte. Só combine quando um mesmo gráfico precisar de campos de duas tabelas. `ds_trends` e `ds_pdfs` não têm chave de UF — ficam em visuais próprios.

> Dica: defina o tipo do campo `uf` como **Geo → Region/Country subdivision** e `regiao` como dimensão, para habilitar mapas e facilitar os filtros.

**Controles globais sugeridos (slicers):** adicione *Controle → Lista suspensa (drop-down)* para `regiao` e `segmento`. Posicione-os no **nível do relatório** (*Organizar → Tornar disponível em nível de relatório*) para filtrarem todas as páginas.

## 2. Páginas e visuais

> No Looker Studio cada "página" é uma **Page** do relatório (*Página → Nova página*). Os "visuais" são os gráficos da barra *Adicionar um gráfico*.

### Página 1 — Visão regional (mapa de priorização)
- **Mapa do Brasil** — gráfico *Mapa do Google (Filled map / Mapa preenchido)* ou *Gráfico geográfico (Geo chart)*. Dimensão = `uf` (tipo Geo: subdivisão de país, com país base = Brasil); cor por `segmento` (Prêmio premium / Vitrine solar / Fronteira morna / Baixa prioridade). Se o reconhecimento por sigla falhar, crie um campo calculado com o nome do estado por extenso ou use o código ISO (`BR-SP`, `BR-SC`…).
- **Scorecards (KPIs):** cartão com *Contagem distinta de `uf`* por segmento; cartão com *Média de `oportunidade_conversao`* (responde ao filtro de segmento).
- **Gráfico de barras horizontais:** `oportunidade_conversao` por `uf`, ordenado decrescente (destaque SC, RS, SP, PR, DF).

### Página 2 — Aptidão por produto
- **Dispersão (Scatter):** dimensão = `uf`; Métrica X = `aptidao_solar`, Métrica Y = `cop_medio_anual`, *Bubble size* = `oportunidade_conversao`, *Bubble color* = `segmento`. (Replica o "mapa de priorização comercial" do notebook.) Ative os rótulos de dados para mostrar a sigla da UF.
- **Barras:** top UFs por `aptidao_solar` (vender coletor solar) — destaque Nordeste.
- **Barras:** `cop_medio_anual` por `uf` (eficiência da bomba de calor).

### Página 3 — Sazonalidade (clima × consumo)
- **Gráfico de linhas com eixo duplo** (fonte `ds_mensal`): série esquerda = `temp_media_mensal`, série direita = `consumo_residencial_mwh`, dimensão de tempo = mês (ou ano-mês). Em *Estilo*, mova uma das séries para o **Eixo Y direito**.
- **Controle:** lista suspensa de `regiao` / `uf` para comparar regiões.
- Leitura: consumo cai no inverno (efeito aquecimento parcial; verão puxado por ar-condicionado).

### Página 4 — Consumidor e discurso
- **Série temporal** (fonte `ds_trends`): gráfico *Série temporal* ou *Linhas* com `indice_busca` por `termo` (dimensão de detalhamento/breakdown = `termo`) ao longo do tempo. Destacar a sazonalidade de "aquecimento de piscina" e a dominância de "chuveiro elétrico".
- **Barras/linha** (fonte `ds_pdfs`): `frequencia` por `termo` e `periodo` (evolução do discurso institucional).
- **Imagem:** use *Inserir → Imagem* para incorporar as nuvens de palavras geradas no notebook de PDFs como elemento visual.

## 3. Campos calculados úteis (equivalente ao DAX)

No Looker Studio não há DAX. As métricas saem de duas formas:

- **Agregação direta no gráfico:** basta escolher a função na própria métrica (ex.: `oportunidade_conversao` com agregação *Average*; `consumo_residencial_mwh` com *Sum*).
- **Campo calculado** (*Adicionar um campo* na fonte de dados), quando precisar de fórmula:

```
Oportunidade Média   →  AVG(oportunidade_conversao)
Qtd UFs              →  COUNT_DISTINCT(uf)
Consumo Total (MWh)  →  SUM(consumo_residencial_mwh)
```

> Campos calculados a nível de fonte são reutilizáveis em qualquer gráfico; agregações simples podem ser feitas direto no gráfico via o seletor de agregação da métrica.

## 4. Paleta sugerida por segmento (consistência com os notebooks)

Em *Estilo → Cores por dimensão*, fixe a cor de cada valor de `segmento`:
- Prêmio premium → roxo
- Vitrine solar → laranja
- Fronteira morna → verde
- Baixa prioridade → cinza

> Para garantir consistência entre páginas, defina o mapeamento de cores no **tema do relatório** (*Tema e layout → Personalizar*) ou repita a atribuição "cor por dimensão" em cada gráfico.

## 5. Mensagem-chave de cada página
1. *Onde priorizar* (mapa de segmentos).
2. *Qual produto vender em cada lugar* (solar × bomba de calor).
3. *Quando a demanda acontece* (sazonalidade).
4. *O que o consumidor quer e o que o setor fala* (Trends × PDFs).

## 6. Diferenças-chave vs. Power BI / Tableau (resumo rápido)
- **Importar dados →** conectar fonte de dados (CSV via Upload ou Google Sheets).
- **Relacionamentos do modelo →** *Combinar dados (Blend)* por `uf`, só quando o gráfico misturar duas tabelas.
- **Medidas DAX →** campos calculados (função `AVG/SUM/COUNT_DISTINCT`) ou agregação direta na métrica.
- **Slicer →** *Controle* (lista suspensa), tornado disponível em nível de relatório.
- **Mapa coroplético →** Mapa do Google / Geo chart com `uf` como dimensão geográfica.
- **Páginas →** Pages do relatório; filtros de relatório valem para todas, filtros de página só para uma.
