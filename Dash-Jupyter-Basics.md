# Getting Started with Dash in Jupyter Notebooks

A quick guide to building interactive dashboards with Plotly Dash in Jupyter/Colab notebooks.

## What is Dash?

Dash is a Python framework for building interactive web applications. It's built on top of:
- **Plotly**: For interactive charts
- **Flask**: For web server (runs behind the scenes)
- **React.js**: For UI components (you don't need to know JavaScript!)

## Installation

```python
%pip install dash plotly pandas
```

## Basic Structure

Every Dash app has three main parts:

### 1. Initialize the App

```python
from dash import Dash, html, dcc

app = Dash(__name__)
```

### 2. Define the Layout

The layout describes what the app looks like:

```python
app.layout = html.Div([
    html.H1('My Dashboard Title'),
    html.P('Some descriptive text'),
    dcc.Graph(figure=my_plotly_figure)
])
```

### 3. Run the App

For Jupyter/Colab, use `jupyter_mode`:

```python
app.run(jupyter_mode='inline', height=700, port=8050)
```

> **Note**: In regular Python scripts, use `app.run(debug=True)` instead.

---

## Layout Components

Dash provides two main types of components:

### HTML Components (`html.*`)

Standard HTML elements wrapped for Python:

```python
from dash import html

html.Div()        # <div>
html.H1()         # <h1> heading
html.H3()         # <h3> subheading
html.P()          # <p> paragraph
html.Br()         # <br> line break
html.Hr()         # <hr> horizontal rule
html.Table()      # <table>
```

### Core Components (`dcc.*`)

Interactive Dash components:

```python
from dash import dcc

dcc.Graph()          # Interactive Plotly charts
dcc.Dropdown()       # Dropdown selector
dcc.RadioItems()     # Radio buttons
dcc.Checklist()      # Checkboxes
dcc.Slider()         # Slider
dcc.Input()          # Text input
dcc.Tabs()           # Tab container
dcc.Tab()            # Individual tab
```

### Layout Example

```python
app.layout = html.Div([
    # Title
    html.H1('IFC Building Dashboard'),
    
    # Description
    html.P('Explore building elements and materials'),
    
    # Tabs
    dcc.Tabs([
        dcc.Tab(label='Overview', children=[
            html.H3('Elements per Storey'),
            dcc.Graph(figure=storey_chart)
        ]),
        
        dcc.Tab(label='Materials', children=[
            html.H3('Material Distribution'),
            dcc.Graph(figure=material_chart)
        ])
    ])
])
```

---

## Creating Charts

Dash uses Plotly Express for easy chart creation:

```python
import plotly.express as px
import pandas as pd

# Sample data
df = pd.DataFrame({
    'Storey': ['Ground', 'First', 'Second'],
    'Count': [150, 120, 100]
})

# Create a bar chart
fig = px.bar(df, x='Storey', y='Count', title='Elements per Storey')

# Use in layout
app.layout = html.Div([
    dcc.Graph(figure=fig)
])
```

### Common Chart Types

```python
# Bar chart
px.bar(df, x='category', y='value')

# Histogram
px.histogram(df, x='category', y='value', histfunc='avg')

# Line chart
px.line(df, x='date', y='value')

# Scatter plot
px.scatter(df, x='x_value', y='y_value')

# Pie chart
px.pie(df, names='category', values='value')

# Heatmap
px.density_heatmap(df, x='x_col', y='y_col', z='value')
```

---

## Adding Interactivity with Callbacks

Callbacks make your dashboard interactive by updating components based on user input.

### Basic Callback Structure

```python
from dash import callback, Input, Output

@callback(
    Output('output-component-id', 'component-property'),
    Input('input-component-id', 'component-property')
)
def update_function(input_value):
    # Process the input
    result = do_something(input_value)
    
    # Return the output
    return result
```

### Complete Example: Interactive Chart

```python
from dash import Dash, dcc, html, callback, Input, Output
import plotly.express as px
import pandas as pd

# Sample data
df = pd.DataFrame({
    'Storey': ['Ground', 'First', 'Second'],
    'Elements': [150, 120, 100],
    'Area': [500, 450, 400]
})

app = Dash(__name__)

# Layout with dropdown and graph
app.layout = html.Div([
    html.H1('Interactive Building Dashboard'),
    
    # Dropdown to select metric
    html.Label('Select Metric:'),
    dcc.Dropdown(
        id='metric-dropdown',
        options=[
            {'label': 'Number of Elements', 'value': 'Elements'},
            {'label': 'Floor Area (m²)', 'value': 'Area'}
        ],
        value='Elements'  # Default value
    ),
    
    # Graph that will update
    dcc.Graph(id='storey-chart')
])

# Callback to update chart
@callback(
    Output('storey-chart', 'figure'),
    Input('metric-dropdown', 'value')
)
def update_chart(selected_metric):
    fig = px.bar(
        df, 
        x='Storey', 
        y=selected_metric,
        title=f'{selected_metric} per Storey'
    )
    return fig

app.run(jupyter_mode='inline', height=600, port=8050)
```

### Multiple Inputs

You can have multiple inputs to a single callback:

```python
@callback(
    Output('output-graph', 'figure'),
    Input('dropdown-1', 'value'),
    Input('dropdown-2', 'value')
)
def update_chart(input1, input2):
    # Use both inputs
    filtered_df = df[(df['col1'] == input1) & (df['col2'] == input2)]
    fig = px.bar(filtered_df, x='x', y='y')
    return fig
```

### Multiple Outputs

One callback can update multiple components:

```python
@callback(
    Output('graph-1', 'figure'),
    Output('graph-2', 'figure'),
    Input('dropdown', 'value')
)
def update_both_charts(selected_value):
    # Filter data
    filtered = df[df['category'] == selected_value]
    
    # Create two figures
    fig1 = px.bar(filtered, x='x', y='y')
    fig2 = px.pie(filtered, names='name', values='value')
    
    # Return both (order matters!)
    return fig1, fig2
```

---

## Common Patterns for IFC Dashboards

### Pattern 1: Toggle to Show/Hide Data

```python
app.layout = html.Div([
    dcc.Checklist(
        id='show-unassigned',
        options=[{'label': ' Include unassigned elements', 'value': 'show'}],
        value=['show']  # Default checked
    ),
    dcc.Graph(id='my-chart')
])

@callback(
    Output('my-chart', 'figure'),
    Input('show-unassigned', 'value')
)
def update_chart(checklist_value):
    if 'show' in checklist_value:
        filtered_df = ifc_df  # Show all
    else:
        filtered_df = ifc_df[ifc_df['Storey'] != 'Not assigned']  # Hide unassigned
    
    fig = px.bar(filtered_df, x='Storey', y='Count')
    return fig
```

### Pattern 2: Filter by Category

```python
app.layout = html.Div([
    dcc.Dropdown(
        id='element-type-dropdown',
        options=[{'label': t, 'value': t} for t in df['ElementType'].unique()],
        value='IfcWall'  # Default
    ),
    dcc.Graph(id='filtered-chart')
])

@callback(
    Output('filtered-chart', 'figure'),
    Input('element-type-dropdown', 'value')
)
def filter_by_type(selected_type):
    filtered = df[df['ElementType'] == selected_type]
    fig = px.bar(filtered, x='Storey', y='Count')
    return fig
```

### Pattern 3: Tabs with Different Views

```python
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='By Storey', children=[
            dcc.Graph(id='storey-view', figure=storey_fig)
        ]),
        dcc.Tab(label='By Type', children=[
            dcc.Graph(id='type-view', figure=type_fig)
        ]),
        dcc.Tab(label='By Material', children=[
            dcc.Graph(id='material-view', figure=material_fig)
        ])
    ])
])
```

---

## Styling Tips

### Inline Styles

```python
html.Div(
    'My content',
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

### Common Style Properties

- `textAlign`: 'left', 'center', 'right'
- `color`: Text color (hex or name)
- `backgroundColor`: Background color
- `fontSize`: '12px', '1.5rem'
- `padding`: '10px' (space inside)
- `margin`: '10px' (space outside)
- `border`: '1px solid black'
- `borderRadius`: '5px' (rounded corners)

---

## Complete Minimal IFC Dashboard Template

```python
from dash import Dash, dcc, html, callback, Input, Output
import plotly.express as px
import pandas as pd
import ifcopenshell

# Load IFC file
model = ifcopenshell.open('your_file.ifc')

# Parse data
elements = []
for element in model.by_type('IfcElement'):
    elements.append({
        'Type': element.is_a(),
        'Id': element.GlobalId
    })

df = pd.DataFrame(elements)

# Count by type
type_counts = df.groupby('Type').size().reset_index(name='Count')

# Create app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1('IFC Dashboard', style={'textAlign': 'center'}),
    
    html.Label('Select Chart Type:'),
    dcc.RadioItems(
        id='chart-type',
        options=[
            {'label': 'Bar Chart', 'value': 'bar'},
            {'label': 'Pie Chart', 'value': 'pie'}
        ],
        value='bar'
    ),
    
    dcc.Graph(id='main-chart')
])

# Callback
@callback(
    Output('main-chart', 'figure'),
    Input('chart-type', 'value')
)
def update_chart(chart_type):
    if chart_type == 'bar':
        fig = px.bar(type_counts, x='Type', y='Count', title='Elements by Type')
    else:
        fig = px.pie(type_counts, names='Type', values='Count', title='Elements by Type')
    
    return fig

# Run
app.run(jupyter_mode='inline', height=600, port=8050)
```

---

## Troubleshooting

### Common Issues

1. **Port already in use**: Change `port=8050` to `port=8051`, `port=8052`, etc.

2. **Callback not updating**: Make sure:
   - Component IDs match exactly
   - The callback returns the right type
   - You're using `@callback` decorator

3. **Graph not showing**: Check that:
   - Your figure is valid Plotly figure
   - Component ID in callback matches layout ID
   - Data exists in your DataFrame

4. **"TypeError: unhashable type: 'list'"**: In callbacks, wrap list outputs in a list:
   ```python
   return [fig1, fig2]  # NOT: return fig1, fig2
   ```

---

## Next Steps

1. **Experiment**: Try different chart types and layouts
2. **Combine**: Use multiple filters and callbacks
3. **Polish**: Add styling and better organization
4. **Share**: Deploy to Colab or Plotly Cloud

## Resources

- [Dash Documentation](https://dash.plotly.com/)
- [Plotly Chart Types](https://plotly.com/python/)
- [IFCOpenShell Docs](https://docs.ifcopenshell.org/)
- [Full IFC Dashboard Example](https://github.com/louistrue/learn-ifc/blob/main/BFH-25-Tabbed-Dashboard.ipynb)

---

**Ready to build?** Start with the [IFC Dashboard Starter Template](IFC-Dashboard-Starter.ipynb) and gradually add features!
