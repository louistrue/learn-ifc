# IFC Datenvisualisierung Starter · Pandas-Grundlagen

Du lernst:
- IFC-Tabellen laden, erkunden, filtern und gruppieren
- Kennzahlen und Aggregationen für Visualisierungen vorbereiten

Du brauchst:
- Einen Jupyter- oder Colab-Workspace (z. B. `BFH-25-IFC-Dashboard-Starter.ipynb`)
- Zugang zu den Beispiel-IFC-Dateien in diesem Repository

## Installation

```python
%pip install pandas
```

## Wichtige Datenstrukturen

### DataFrame

```python
import pandas as pd

df = pd.DataFrame({
    'Geschoss': ['Erdgeschoss', 'OG1', 'OG2'],
    'Elemente': [150, 120, 100],
    'Fläche': [500, 450, 400]
})
```

### Series

```python
# Einzelne Spalte
geschosse = df['Geschoss']
```

## Daten laden

```python
# CSV
df = pd.read_csv('daten.csv')

# CSV mit Optionen
df = pd.read_csv(
    'daten.csv',
    sep=';',
    encoding='utf-8',
    index_col=0
)

# Excel
df = pd.read_excel('daten.xlsx', sheet_name='Tabelle1')

# Dictionary
data = {
    'ElementId': ['id1', 'id2', 'id3'],
    'ElementTyp': ['IfcWall', 'IfcDoor', 'IfcWindow'],
    'Geschoss': ['EG', 'EG', 'OG1']
}

df = pd.DataFrame(data)
```

## Daten erkunden

```python
df.head()      # erste Zeilen

df.tail()      # letzte Zeilen

df.shape       # (Zeilen, Spalten)

df.columns     # Spaltennamen

df.dtypes      # Datentypen

df.describe()  # Statistik

df.info()      # Struktur
```

### Fehlende Werte

```python
df.isnull().sum()
df.dropna()
df.fillna('Unbekannt')
```

## Daten auswählen und filtern

```python
# Spalten
df['ElementTyp']
df[['ElementTyp', 'Geschoss']]

# Zeilen über Position
df.iloc[0]

# Zeilen über Label
df.loc[0]

# Bedingungen
df[df['ElementTyp'] == 'IfcWall']
df[(df['ElementTyp'] == 'IfcWall') & (df['Geschoss'] == 'EG')]
df[df['ElementTyp'].isin(['IfcWall', 'IfcDoor'])]
df[df['ElementTyp'].str.contains('Wall')]
```

## Gruppieren & Aggregieren

```python
# Gruppieren
df.groupby('Geschoss').size()

df.groupby(['Geschoss', 'ElementTyp']).size()

# Aggregationen
df.groupby('Geschoss')['Elemente'].sum()
df.groupby('Geschoss')['Fläche'].mean()

df.groupby('Geschoss').agg({
    'Elemente': 'sum',
    'Fläche': ['mean', 'max']
})
```

### Weitere Aggregationen

```python
funktionen = ['count', 'sum', 'mean', 'median', 'min', 'max', 'std']
for func in funktionen:
    print(func, df.groupby('Geschoss')['Elemente'].__getattribute__(func)())
```

### Einzigartige Werte

```python
df['ElementTyp'].nunique()
df['ElementTyp'].value_counts()

counts = df['ElementTyp'].value_counts().reset_index()
counts.columns = ['ElementTyp', 'Anzahl']
```

## Daten transformieren

```python
# Neue Spalte
df['Dichte'] = df['Elemente'] / df['Fläche']

# Kategorie aus Bedingung
df['Kategorie'] = df['Elemente'].apply(lambda x: 'Groß' if x > 100 else 'Klein')

# Spalten umbenennen
df.rename(columns={'Elemente': 'AnzahlElemente'}, inplace=True)

# Sortieren
df.sort_values('Elemente', ascending=False)

# Datentypen
df['ElementId'] = df['ElementId'].astype(str)
df['ElementTyp'] = df['ElementTyp'].astype('category')
```

## DataFrames kombinieren

```python
# Zeilen anhängen
df_gesamt = pd.concat([df1, df2], ignore_index=True)

# Tabellen verbinden
df_merge = pd.merge(
    df1,
    df2,
    on='ElementId',
    how='left'
)
```

## Pandas-Muster für IFC-Projekte

```python
# Elemente pro Geschoss
geschoss_counts = (
    df.groupby('Geschoss')['ElementId']
    .nunique()
    .reset_index(name='Anzahl')
    .sort_values('Anzahl', ascending=False)
)

# Heatmap-Daten
dichte = df.pivot_table(
    values='ElementId',
    index='Geschoss',
    columns='ElementTyp',
    aggfunc='count',
    fill_value=0
)

# Nur zugewiesene Elemente
assigned = df[df['Geschoss'] != 'Nicht zugewiesen']
type_summary = (
    assigned.groupby('ElementTyp')['ElementId']
    .nunique()
    .reset_index(name='Anzahl')
    .sort_values('Anzahl', ascending=False)
)
```

## Best Practices

1. **Method Chaining** hilft dir, Datenpipelines lesbar zu halten.
2. **Nutze `.copy()`**, bevor du DataFrames manipulierst, um Seiteneffekte zu vermeiden.
3. **Kategorische Typen** sparen Speicher und beschleunigen GroupBy-Operationen.
4. **Vektorisiere statt zu loopen** – pandas-Methoden sind fast immer schneller.

## Ressourcen

- [Pandas-Dokumentation](https://pandas.pydata.org/docs/)
- [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
- [10 Minutes to Pandas](https://pandas.pydata.org/docs/user_guide/10min.html)

---

**Nächster Schritt:** Sobald deine Daten sauber sind, kannst du sie mit Plotly visualisieren.

## Recap
- DataFrames und Series sicher einsetzen
- IFC-Daten filtern, gruppieren und aggregieren

## Nächster Schritt
Weiter mit `BFH-25-02_Plotly-Grundlagen.md`, um die Ergebnisse zu visualisieren.
Begleitendes Notebook: `BFH-25-IFC-Dashboard-Starter.ipynb`
