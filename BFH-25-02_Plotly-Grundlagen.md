# IFC Datenvisualisierung Starter · Plotly-Grundlagen

Du lernst:
- Interaktive Diagramme (Bar, Pie, Heatmap, …) mit Plotly Express erstellen
- Layout, Achsen, Farben und Hover-Infos anpassen

Du brauchst:
- Die vorbereiteten DataFrames aus `BFH-25-01_Pandas-Grundlagen.md`
- Ein Notebook-Setup wie `BFH-25-IFC-Dashboard-Starter.ipynb`

## Installation

```python
%pip install plotly
```

## Plotly Express Basics

```python
import plotly.express as px

fig = px.bar(df, x='Geschoss', y='Anzahl')
fig.show()
```

## Häufige Diagrammtypen

```python
# Balkendiagramm
px.bar(df, x='Geschoss', y='Anzahl', title='Elemente pro Geschoss')

# Gestapelte Balken
px.bar(df, x='Geschoss', y='Anzahl', color='ElementTyp')

# Horizontale Balken
px.bar(df, x='Anzahl', y='ElementTyp', orientation='h')

# Liniendiagramm
px.line(df, x='Datum', y='Wert', markers=True)

# Scatter
px.scatter(df, x='Fläche', y='Anzahl', color='Geschoss', size='Volumen')

# Kreisdiagramm
px.pie(df, names='ElementTyp', values='Anzahl', hole=0.3)

# Histogramm
px.histogram(df, x='Geschoss', y='Anzahl', histfunc='avg')

# Heatmap
px.density_heatmap(df, x='ElementTyp', y='Geschoss', z='Anzahl')

# Treemap
px.treemap(df, path=['Geschoss', 'ElementTyp'], values='Anzahl')

# Sunburst
px.sunburst(df, path=['Gebäude', 'Geschoss', 'ElementTyp'], values='Anzahl')
```

## Diagramme verfeinern

```python
fig.update_layout(
    title='Mein Diagramm',
    xaxis_title='X-Achse',
    yaxis_title='Y-Achse',
    font=dict(size=14),
    height=600,
    showlegend=True,
    legend_title='Legende'
)

fig.update_xaxes(tickangle=-45, showgrid=True)
fig.update_yaxes(range=[0, 100], showgrid=True)

fig.update_traces(hovertemplate='<b>%{x}</b><br>Anzahl: %{y}<extra></extra>')
```

### Farben

```python
# Kontinuierliche Skalen
fig = px.bar(df, x='x', y='y', color='z', color_continuous_scale='Blues')
fig.update_layout(coloraxis_showscale=False)

# Diskrete Paletten
fig = px.bar(df, x='x', y='y', color='Kategorie',
             color_discrete_sequence=px.colors.qualitative.Set3)
```

## Subplots verwendet

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(rows=1, cols=2, subplot_titles=('Diagramm 1', 'Diagramm 2'))
fig.add_trace(go.Bar(x=df['x'], y=df['y']), row=1, col=1)
fig.add_trace(go.Scatter(x=df['x'], y=df['z']), row=1, col=2)
fig.update_layout(height=400, showlegend=False)
fig.show()
```

## IFC-Daten visualisieren

```python
import pandas as pd
import plotly.express as px

ifc_data = {
    'ElementId': ['id1', 'id2', 'id3', 'id4', 'id5', 'id6'],
    'ElementTyp': ['IfcWall', 'IfcWall', 'IfcDoor', 'IfcWindow', 'IfcSlab', 'IfcSlab'],
    'Geschoss': ['EG', 'OG1', 'EG', 'OG1', 'EG', 'OG1'],
    'Material': ['Beton', 'Beton', 'Holz', 'Glas', 'Beton', 'Beton']
}

df = pd.DataFrame(ifc_data)

# 1) Elemente pro Geschoss
geschoss_counts = (
    df.groupby('Geschoss')['ElementId']
    .nunique()
    .reset_index(name='Anzahl')
)

fig1 = px.bar(geschoss_counts, x='Geschoss', y='Anzahl',
              title='Anzahl Elemente pro Geschoss', text_auto='.0f')
fig1.show()

# 2) Elemente nach Typ
typ_counts = df['ElementTyp'].value_counts().reset_index()
typ_counts.columns = ['ElementTyp', 'Anzahl']

fig2 = px.pie(typ_counts, names='ElementTyp', values='Anzahl',
              title='Verteilung Elementtypen')
fig2.show()

# 3) Heatmap
heatmap_data = (
    df.groupby(['Geschoss', 'ElementTyp'])
    .size()
    .reset_index(name='Anzahl')
)

fig3 = px.density_heatmap(
    heatmap_data,
    x='ElementTyp',
    y='Geschoss',
    z='Anzahl',
    title='Elemente: Geschoss vs. Typ',
    text_auto=True
)
fig3.show()
```

## Diagramme exportieren

```python
# Als Bild (Benötigt: pip install -U kaleido)
fig.write_image('diagramm.png')
fig.write_image('diagramm.pdf')

# Als HTML
fig.write_html('diagramm.html')
```

## Plotly-Muster für IFC

```python
# Top-10-Elementtypen
counts = (
    df.groupby('ElementTyp')['ElementId']
    .nunique()
    .reset_index(name='Anzahl')
    .sort_values('Anzahl', ascending=False)
    .head(10)
)

fig = px.bar(
    counts,
    x='ElementTyp',
    y='Anzahl',
    text_auto='.0f',
    title='Top 10 Elementtypen',
    color='Anzahl',
    color_continuous_scale='Blues'
)
fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-45)
fig.show()
```

## Best Practices

1. **Plotly Express zuerst:** Die schnellste Variante für Standarddiagramme.
2. **Gute Titel & Labels:** Hilft beim Verständnis – besonders bei IFC-Daten.
3. **Höhe anpassen:** Mit `height=` sorgst du für klare Visualisierungen.
4. **Hover-Daten nutzen:** Mehr Kontext im Tooltip = bessere Analyse.

## Ressourcen

- [Plotly Python Docs](https://plotly.com/python/)
- [Plotly Express API](https://plotly.com/python-api-reference/plotly.express.html)
- [Plotly Fundamentals](https://plotly.com/python/plotly-fundamentals/)

---

**Bereit zum Plotten?** Importiere deinen Pandas-DataFrame und bau in Minuten interaktive IFC-Charts mit Plotly.

## Recap
- Gängige Plotly-Diagrammtypen anwenden
- Diagramm-Layout und Stil gezielt steuern

## Nächster Schritt
Weiter mit `BFH-25-03_Dash-Jupyter-Grundlagen.md`, um die Visualisierungen in ein Dashboard zu bringen.
Inspiration: `BFH-25-Tabbed-Dashboard.ipynb`
