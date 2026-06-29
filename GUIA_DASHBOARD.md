# Guia do Dashboard — Power BI / Tableau

Guia para montar o painel interativo a partir dos CSVs já gerados. Tudo está em nível de UF, então as tabelas se ligam pela coluna `uf` (sigla) — exceto a série de buscas, que é nacional por termo.

## 1. Fontes de dados (importar)

| Arquivo | Grão | Uso |
|---|---|---|
| `painel_uf_clusters.csv` | 1 linha por UF | Tabela principal: segmento, aptidão solar, COP, oportunidade, renda |
| `painel_uf_integrado.csv` | 1 linha por UF | Detalhe completo (29 colunas) para drill-down |
| `painel_mensal_uf.csv` | UF × ano × mês | Sazonalidade (temperatura × consumo) |
| `gtrends_serie_temporal.csv` | semana × termo | Tendência de busca do consumidor |
| `pdfs_frequencia_termos.csv` | período × termo | Evolução do discurso institucional |

**Relacionamentos:** ligar `painel_uf_clusters[uf]` → `painel_mensal_uf[uf]` (1:N) e → `painel_uf_integrado[uf]` (1:1). A série de Trends e os termos de PDF ficam isolados (sem chave de UF) — usar em visuais próprios.

**Slicers globais sugeridos:** `regiao` e `segmento`.

## 2. Páginas e visuais

### Página 1 — Visão regional (mapa de priorização)
- **Mapa do Brasil** preenchido por UF, cor = `segmento` (Prêmio premium / Vitrine solar / Fronteira morna / Baixa prioridade). *Power BI: visual "Mapa coroplético" ou "Shape map" com UF; Tableau: mapa por estado.*
- **Cartões (KPIs):** nº de UFs por segmento; oportunidade média do segmento selecionado.
- **Barras horizontais:** `oportunidade_conversao` por UF, ordenado desc (destaque SC, RS, SP, PR, DF).

### Página 2 — Aptidão por produto
- **Dispersão:** eixo X = `aptidao_solar`, eixo Y = `cop_medio_anual`, tamanho = `oportunidade_conversao`, cor = `segmento`, rótulo = `uf`. (replica o "mapa de priorização comercial" do notebook).
- **Barras:** top UFs por `aptidao_solar` (vender coletor solar) — destaque Nordeste.
- **Barras:** `cop_medio_anual` por UF (eficiência da bomba de calor).

### Página 3 — Sazonalidade (clima × consumo)
- **Linha de eixo duplo** (de `painel_mensal_uf`): `temp_media_mensal` e `consumo_residencial_mwh` por mês.
- **Slicer:** `regiao` / `uf` para comparar regiões.
- Leitura: consumo cai no inverno (efeito aquecimento parcial; verão puxado por ar-condicionado).

### Página 4 — Consumidor e discurso
- **Linha temporal** (de `gtrends_serie_temporal`): `indice_busca` por `termo` ao longo do tempo. Destacar a sazonalidade de "aquecimento de piscina" e a dominância de "chuveiro elétrico".
- **Barras/linha** (de `pdfs_frequencia_termos`): `frequencia` por `termo` e `periodo` (evolução do discurso institucional).
- **Imagem:** incorporar as nuvens de palavras geradas no notebook de PDFs como elemento visual.

## 3. Medidas (DAX) úteis no Power BI

```
Oportunidade Média = AVERAGE(painel_uf_clusters[oportunidade_conversao])
Qtd UFs = DISTINCTCOUNT(painel_uf_clusters[uf])
Consumo Total (MWh) = SUM(painel_mensal_uf[consumo_residencial_mwh])
```

## 4. Paleta sugerida por segmento (consistência com os notebooks)
- Prêmio premium → roxo
- Vitrine solar → laranja
- Fronteira morna → verde
- Baixa prioridade → cinza

## 5. Mensagem-chave de cada página
1. *Onde priorizar* (mapa de segmentos).
2. *Qual produto vender em cada lugar* (solar × bomba de calor).
3. *Quando a demanda acontece* (sazonalidade).
4. *O que o consumidor quer e o que o setor fala* (Trends × PDFs).
