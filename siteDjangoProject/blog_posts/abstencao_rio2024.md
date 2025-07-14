# A Abstenção nas Eleições Municipais de 2024 no Rio de Janeiro: Diagnóstico e Implicações Democráticas

## Resumo Executivo

Nas eleições municipais de 2024, o Rio de Janeiro registrou uma das **mais elevadas taxas de abstenção entre as capitais brasileiras**, com **1,5 milhão de eleitores ausentes**, representando **30,58% dos eleitores aptos** no primeiro turno. Esta análise traça o cenário, compara com pleitos anteriores e discute suas consequências.

---

## 1. Dados Oficiais – 1º Turno (06/10/2024)

- **Eleitores aptos:** 5.009.373  
- **Abstenções:** 1.532.093 → **30,58%** :contentReference[oaicite:1]{index=1}  
- **Votos válidos:** 3.079.171 (60,47% Eduardo Paes; 30,81% Alexandre Ramagem; outros) :contentReference[oaicite:2]{index=2}  
- **Brancos:** 152.491 → 4,39%  
- **Nulos:** 245.618 → 7,06%  
- **Percentual total ausente/nulo/branco:** 38,53% :contentReference[oaicite:3]{index=3}

---

## 2. Comparativo Histórico

| Eleição | Abstenção (%) |
|---------|----------------|
| 2016    | 24,3%          |
| 2020    | 32,8%          |
| **2024**| **30,6%**      |

👉 Houve uma diminuição em relação a 2020, mas a abstenção se mantém em níveis muito elevados :contentReference[oaicite:4]{index=4}.

---

## 3. Contexto e Causas Prováveis

### 3.1 Polarização Política
A reeleição de **Eduardo Paes (PSD)** com 60,47% dos votos ocorreu em um cenário eleitoral polarizado, com candidatos como Alexandre Ramagem (PL) e Tarcísio Motta (PSOL), o que pode ter levado à **desmotivação segmentada do eleitorado** :contentReference[oaicite:5]{index=5}.

### 3.2 Comparativo Nacional
O percentual de abstenção no Rio (30,58%) ficou bem acima da média nacional de 21,71% :contentReference[oaicite:6]{index=6} e só foi superado por Porto Alegre (31,51%) :contentReference[oaicite:7]{index=7}.

### 3.3 Pós-pandemia
Em 2020, com a pandemia, o Rio registrou 32,79% de abstenção – maior até então. Em 2024, o recuo foi leve, mas a participação ainda não retornou a patamares pré-2016 (24%) :contentReference[oaicite:8]{index=8}.

---

## 4. Visualização da Abstenção

Para incluir no seu artigo, use o seguinte comando para gerar um gráfico comparativo de abstenção (barras) vs. total de abstenções (linha):

```python
import matplotlib.pyplot as plt

turnos = ['2016', '2020', '2024']
abst_percent = [24.3, 32.8, 30.58]
abst_qtde = [1189187, 1720154, 1532093]

fig, ax1 = plt.subplots(figsize=(8,5))
ax1.bar(turnos, abst_percent, color='skyblue', label='Abstenção (%)')
ax1.set_ylabel('Abstenção (%)')
ax2 = ax1.twinx()
ax2.plot(turnos, abst_qtde, color='red', marker='o', label='Número de Abstenções')
ax2.set_ylabel('Abstenções (milhões)')

plt.title('Abstenção no Rio de Janeiro: Evolução 2016–2024')
plt.savefig('abstencao_rj_2016_2024.png', dpi=300)
plt.show()
