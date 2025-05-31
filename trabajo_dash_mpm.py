# -*- coding: utf-8 -*-

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# Cargar base de datos desde raíz del repo
df = pd.read_csv("sales_data_sample.csv", encoding="ISO-8859-1")
df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')
df['Month'] = df['ORDERDATE'].dt.to_period('M').astype(str)

# Iniciar la app
app = Dash(__name__)
server = app.server

# Layout del dashboard
app.layout = html.Div([
    html.H1("Dashboard de Ventas", style={
        'textAlign': 'center',
        'backgroundColor': 'white',
        'color': 'black',
        'padding': '10px',
        'borderRadius': '10px'
    }),

    html.Div([
        html.Label("Selecciona el año:"),
        dcc.Dropdown(
            id='year-selector',
            options=[{'label': y, 'value': y} for y in sorted(df['YEAR_ID'].unique())],
            value=2003
        ),

        html.Label("Tipo de gráfico de barras:"),
        dcc.RadioItems(
            id='bar-style',
            options=[
                {'label': 'Agrupado', 'value': 'group'},
                {'label': 'Apilado', 'value': 'stack'}
            ],
            value='group',
            labelStyle={'display': 'inline-block', 'marginRight': '15px'}
        ),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 20px'}),

    html.Div([
        html.Label("Filtrar por país:"),
        dcc.Dropdown(
            id='country-selector',
            options=[{'label': c, 'value': c} for c in sorted(df['COUNTRY'].unique())],
            value='USA'
        ),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 20px'}),

    html.Br(),

    html.Div([
        html.Div([dcc.Graph(id='line-chart')], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='bar-chart')], style={'width': '48%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='pie-chart')], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='scatter-chart')], style={'width': '48%', 'display': 'inline-block'}),
    ])
])

@app.callback(Output('line-chart', 'figure'), Input('year-selector', 'value'))
def update_line_chart(year):
    filtered = df[df['YEAR_ID'] == year]
    grouped = filtered.groupby('Month')['SALES'].sum().reset_index()
    if grouped.empty:
        return px.line().update_layout(title=f"No hay datos de ventas para el año {year}", xaxis=dict(visible=False), yaxis=dict(visible=False))
    fig = px.line(grouped, x='Month', y='SALES', title=f'Ventas mensuales en {year}')
    fig.update_xaxes(rangeslider_visible=True)
    return fig

@app.callback(Output('bar-chart', 'figure'), [Input('year-selector', 'value'), Input('bar-style', 'value')])
def update_bar_chart(year, barmode):
    filtered = df[df['YEAR_ID'] == year]
    grouped = filtered.groupby(['PRODUCTLINE', 'DEALSIZE'])['SALES'].sum().reset_index()
    if grouped.empty:
        return px.bar().update_layout(title="No hay datos para gráfico de barras", xaxis=dict(visible=False), yaxis=dict(visible=False))
    fig = px.bar(grouped, x='PRODUCTLINE', y='SALES', color='DEALSIZE', barmode=barmode, title='Ventas por línea de producto')
    return fig

@app.callback(Output('pie-chart', 'figure'), Input('country-selector', 'value'))
def update_pie_chart(country):
    filtered = df[df['COUNTRY'] == country]
    grouped = filtered.groupby('DEALSIZE')['SALES'].sum().reset_index()
    if grouped.empty:
        return px.pie().update_layout(title=f"No hay ventas para {country}", showlegend=False)
    return px.pie(grouped, values='SALES', names='DEALSIZE', title=f'Participación por tamaño en {country}')

@app.callback(Output('scatter-chart', 'figure'), Input('year-selector', 'value'))
def update_scatter_chart(year):
    filtered = df[df['YEAR_ID'] == year]
    filtered = filtered.dropna(subset=['PRICEEACH', 'SALES', 'PRODUCTLINE', 'QUANTITYORDERED'])
    if filtered.empty:
        return px.scatter().update_layout(title=f"No hay datos para gráfico de dispersión ({year})", xaxis=dict(visible=False), yaxis=dict(visible=False))
    fig = px.scatter(filtered, x='PRICEEACH', y='SALES', color='PRODUCTLINE', size='QUANTITYORDERED', title=f'Precio vs Ventas en {year}')
    return fig

# Ejecutar servidor
app.run()
