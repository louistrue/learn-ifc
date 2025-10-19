# IFC Datenvisualisierung Starter · Dash in Jupyter

Du baust:
- Eine Dash-App mit Tabs und interaktiven Diagrammen
- Einen Umschalter, z. B. für nicht zugewiesene Elemente

Du brauchst:
- Die Ergebnisse aus `BFH-25-01_Pandas-Grundlagen.md` und `BFH-25-02_Plotly-Grundlagen.md`
- Notebook-Referenzen wie `BFH-25-IFC-Dashboard-Starter.ipynb` oder `BFH-25-Tabbed-Dashboard.ipynb`

## Installation

```python
%pip install dash plotly pandas
```

## Grundstruktur einer Dash-App

Jede Dash-App folgt drei Schritten:

### 1. App initialisieren

```python
from dash import Dash, html, dcc

app = Dash(__name__)
```

### 2. Layout definieren

Das Layout bestimmt, was Nutzer*innen sehen:

```python
app.layout = html.Div([
    html.H1('Titel deines Dashboards'),
    html.P('Kurzbeschreibung'),
    dcc.Graph(figure=mein_plotly_diagramm)
])
```

### 3. App starten

In Jupyter oder Colab nutzt du `jupyter_mode`:

```python
app.run(jupyter_mode='inline', height=700, port=8050)
```

> **Tipp:** In einem normalen Python-Skript startest du die App mit `app.run(debug=True)`.

---

## Layout-Komponenten

Dash stellt zwei Hauptgruppen von Komponenten bereit:

### HTML-Komponenten (`html.*`)

Python-Wrapper rund um gängige HTML-Tags:

```python
from dash import html

html.Div()        # <div>
html.H1()         # Überschrift
html.H3()         # Unterüberschrift
html.P()          # Absatz
html.Br()         # Zeilenumbruch
html.Hr()         # Linie
html.Table()      # Tabelle
```

### Core-Komponenten (`dcc.*`)

Interaktive Elemente von Dash:

```python
from dash import dcc

dcc.Graph()        # Plotly-Diagramm
dcc.Dropdown()     # Dropdown-Menü
dcc.RadioItems()   # Optionsfelder
dcc.Checklist()    # Checkbox-Liste
dcc.Slider()       # Schieberegler
dcc.Input()        # Texteingabe
dcc.Tabs()         # Tab-Container
dcc.Tab()          # Einzelner Tab
```

### Layout-Beispiel

```python
app.layout = html.Div([
    html.H1('IFC-Gebäude-Dashboard'),
    html.P('Erkunde Elemente und Materialien'),
    dcc.Tabs([
        dcc.Tab(label='Übersicht', children=[
            html.H3('Elemente pro Geschoss'),
            dcc.Graph(figure=geschoss_diagramm)
        ]),
        dcc.Tab(label='Materialien', children=[
            html.H3('Materialverteilung'),
            dcc.Graph(figure=material_diagramm)
        ])
    ])
])
```

---

## Diagramme erstellen

Für Diagramme verwendest du Plotly Express:

```python
import plotly.express as px
import pandas as pd

# Beispieldaten
df = pd.DataFrame({
    'Geschoss': ['EG', 'OG1', 'OG2'],
    'Anzahl': [150, 120, 100]
})

fig = px.bar(df, x='Geschoss', y='Anzahl', title='Elemente pro Geschoss')

app.layout = html.Div([
    dcc.Graph(figure=fig)
])
```

### Häufige Diagrammtypen

```python
# Balkendiagramm
px.bar(df, x='kategorie', y='wert')

# Histogramm
px.histogram(df, x='kategorie', y='wert', histfunc='avg')

# Liniendiagramm
px.line(df, x='datum', y='wert')

# Streudiagramm
px.scatter(df, x='x_wert', y='y_wert')

# Kreisdiagramm
px.pie(df, names='kategorie', values='wert')

# Heatmap
px.density_heatmap(df, x='x_spalte', y='y_spalte', z='wert')
```

---

## Interaktivität mit Callbacks

Callbacks aktualisieren Komponenten, sobald sich Eingaben ändern.

### Aufbau eines Callbacks

```python
from dash import callback, Input, Output

@callback(
    Output('ausgabe-id', 'property'),
    Input('eingabe-id', 'property')
)
def update_component(eingabe_wert):
    ergebnis = mache_was(eingabe_wert)
    return ergebnis
```

### Beispiel: Interaktives Balkendiagramm

```python
from dash import Dash, dcc, html, callback, Input, Output
import plotly.express as px
import pandas as pd

df = pd.DataFrame({
    'Geschoss': ['EG', 'OG1', 'OG2'],
    'Elemente': [150, 120, 100],
    'Fläche': [500, 450, 400]
})

app = Dash(__name__)

app.layout = html.Div([
    html.H1('Interaktives Gebäude-Dashboard'),
    html.Label('Metrik wählen:'),
    dcc.Dropdown(
        id='metrik-dropdown',
        options=[
            {'label': 'Anzahl Elemente', 'value': 'Elemente'},
            {'label': 'Geschossfläche (m²)', 'value': 'Fläche'}
        ],
        value='Elemente'
    ),
    dcc.Graph(id='geschoss-diagramm')
])

@callback(
    Output('geschoss-diagramm', 'figure'),
    Input('metrik-dropdown', 'value')
)
def update_chart(ausgewählte_metrik):
    fig = px.bar(
        df,
        x='Geschoss',
        y=ausgewählte_metrik,
        title=f'{ausgewählte_metrik} pro Geschoss'
    )
    return fig

app.run(jupyter_mode='inline', height=600, port=8050)
```

### Mehrere Eingaben

```python
@callback(
    Output('diagramm', 'figure'),
    Input('dropdown-1', 'value'),
    Input('dropdown-2', 'value')
)
def update_with_two_inputs(wert1, wert2):
    gefiltert = df[(df['spalte1'] == wert1) & (df['spalte2'] == wert2)]
    return px.bar(gefiltert, x='x', y='y')
```

### Mehrere Ausgaben

```python
@callback(
    Output('diagramm-1', 'figure'),
    Output('diagramm-2', 'figure'),
    Input('dropdown', 'value')
)
def update_multiple(chosen):
    gefiltert = df[df['kategorie'] == chosen]
    fig1 = px.bar(gefiltert, x='x', y='y')
    fig2 = px.pie(gefiltert, names='name', values='wert')
    return fig1, fig2
```

---

## IFC-spezifische Muster

### Umschalter für nicht zugewiesene Elemente

```python
app.layout = html.Div([
    dcc.Checklist(
        id='zeige-nicht-zugewiesen',
        options=[{'label': ' Nicht zugewiesene Elemente einbeziehen', 'value': 'show'}],
        value=['show']
    ),
    dcc.Graph(id='ifc-chart')
])

@callback(
    Output('ifc-chart', 'figure'),
    Input('zeige-nicht-zugewiesen', 'value')
)
def toggle_unassigned(optionen):
    if 'show' in optionen:
        data = ifc_df
    else:
        data = ifc_df[ifc_df['Geschoss'] != 'Nicht zugewiesen']
    return px.bar(data, x='Geschoss', y='Anzahl')
```

### Dropdown-Filter

```python
app.layout = html.Div([
    dcc.Dropdown(
        id='elementtyp-dropdown',
        options=[{'label': typ, 'value': typ} for typ in df['ElementTyp'].unique()],
        value='IfcWall'
    ),
    dcc.Graph(id='filter-chart')
])

@callback(
    Output('filter-chart', 'figure'),
    Input('elementtyp-dropdown', 'value')
)
def filter_by_type(typ):
    gefiltert = df[df['ElementTyp'] == typ]
    return px.bar(gefiltert, x='Geschoss', y='Anzahl')
```

### Tabs für verschiedene Sichtweisen

```python
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Nach Geschoss', children=[
            dcc.Graph(id='geschoss-view', figure=geschoss_fig)
        ]),
        dcc.Tab(label='Nach Typ', children=[
            dcc.Graph(id='typ-view', figure=typ_fig)
        ]),
        dcc.Tab(label='Nach Material', children=[
            dcc.Graph(id='material-view', figure=material_fig)
        ])
    ])
])
```

---

## Styling-Tipps

### Inline-Styles

```python
html.Div(
    'Mein Inhalt',
    style={
        'textAlign': 'center',
        'color': 'blue',
        'backgroundColor': '#f0f0f0',
        'padding': '20px',
        'margin': '10px',
        'borderRadius': '5px'
    }
)
```

### Nützliche Eigenschaften

- `textAlign`: 'left', 'center', 'right'
- `color`: Textfarbe
- `backgroundColor`: Hintergrundfarbe
- `fontSize`: Schriftgröße (z. B. '14px')
- `padding`: Innenabstand
- `margin`: Außenabstand
- `border`: Rahmen (z. B. '1px solid #ccc')
- `borderRadius`: abgerundete Ecken

---

## Minimales IFC-Dashboard

```python
from dash import Dash, dcc, html, callback, Input, Output
import plotly.express as px
import pandas as pd
import ifcopenshell

model = ifcopenshell.open('dein_modell.ifc')

elemente = []
for element in model.by_type('IfcElement'):
    elemente.append({'Typ': element.is_a(), 'Id': element.GlobalId})

df = pd.DataFrame(elemente)
counts = df.groupby('Typ').size().reset_index(name='Anzahl')

app = Dash(__name__)

app.layout = html.Div([
    html.H1('IFC-Dashboard', style={'textAlign': 'center'}),
    html.Label('Diagrammtyp wählen:'),
    dcc.RadioItems(
        id='chart-type',
        options=[
            {'label': 'Balken', 'value': 'bar'},
            {'label': 'Kreis', 'value': 'pie'}
        ],
        value='bar'
    ),
    dcc.Graph(id='main-chart')
])

@callback(
    Output('main-chart', 'figure'),
    Input('chart-type', 'value')
)
def update_main_chart(chart_type):
    if chart_type == 'bar':
        return px.bar(counts, x='Typ', y='Anzahl', title='Elemente nach Typ')
    return px.pie(counts, names='Typ', values='Anzahl', title='Elemente nach Typ')

app.run(jupyter_mode='inline', height=600, port=8050)
```

---

## Fehler schnell beheben

1. **Port belegt:** Ändere `port=8050` auf `port=8051` oder höher.
2. **Callback reagiert nicht:** Prüfe IDs, Rückgabewerte und den `@callback`-Dekorator.
3. **Diagramm bleibt leer:** Kontrolliere, ob die Daten existieren und die IDs korrekt sind.
4. **"TypeError: unhashable type: 'list'":** Gib mehrere Ergebnisse als Liste zurück: `return [fig1, fig2]`.

---

## Nächste Schritte

1. Experimentiere mit weiteren Diagrammtypen und Layouts.
2. Kombiniere mehrere Filter und Callbacks.
3. Verleihe deinem Dashboard ein einheitliches Styling.
4. Teile dein Ergebnis über Colab, Plotly Cloud oder eigene Server.

## Ressourcen

- [Dash-Dokumentation](https://dash.plotly.com/)
- [Plotly Python](https://plotly.com/python/)
- [IFCOpenShell Docs](https://docs.ifcopenshell.org/)
- [Komplettes Dashboard-Beispiel](https://github.com/louistrue/learn-ifc/blob/main/BFH-25-Tabbed-Dashboard.ipynb)

---

**Bereit zum Start?** Hol dir die [IFC-Dashboard-Starter-Vorlage](IFC-Dashboard-Starter.ipynb) und erweitere sie Schritt für Schritt!

## Recap
- Dash-Layout, Callbacks und Interaktivität direkt in Jupyter umgesetzt

## Nächste Schritte
- Baue auf `BFH-25-IFC-Dashboard-Starter.ipynb` auf oder erweitere `BFH-25-Tabbed-Dashboard.ipynb`.
- Schau dir `BFH-25-PropertySets-Dashboard.ipynb` für weitere Ideen an.

Weiterführend:
- [Dash Tutorial](https://dash.plotly.com/tutorial)
- [Dash Layout](https://dash.plotly.com/layout)
- [Interaktive Graphen](https://dash.plotly.com/interactive-graphing)
- [Callbacks (Basics)](https://dash.plotly.com/basic-callbacks)
