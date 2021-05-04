import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import dash_html_components as html
import dash_core_components as dcc

from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import math

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css',
                        'https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

metadata_df = pd.read_csv('static_files/nifty_500_metadata.csv')
metadict = metadata_df[['symbol', 'companyName']].to_dict(orient='records')
val_dict = [{'label':item['companyName'], 'value':item['symbol']} for item in metadict]

app.layout = html.Div([
    dcc.Dropdown(
        id='demo-dropdown',
        options=val_dict,
        value='3MINDIA'
    ),
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Stock', value='tab-1'),
        dcc.Tab(label='OHLC', value='tab-2'),
        dcc.Tab(label='Technical Analysis', value='tab-3'),
        dcc.Tab(label='Fundamental Analysis', value='tab-4'),
        dcc.Tab(label='Portfolio', value='tab-5'),
    ]),
    html.Div(id='tabs-example-content')
])

def row_wrap(func):
    return html.Div(style={'padding':'2rem'}, className='row', children=func)

def card(title, value, text_color='text-white', bg_color='bg-info'):
    return html.Div(style={'max-width': '20rem', 'margin':'2rem'}, className="card {} {} mb-3".format(text_color, bg_color), 
        children=[html.Div(className='card-header', children=title),
        html.Div(className='card-body', children=[html.P(className='card-title', children=value)])])

def data_mapper(dump):
    n_vals = 0
    cards = []
    for key, value in dump.items():
        try:
            if(type(value)==float):
                if(math.isnan(value)):
                    continue
                elif(value < 0):
                    cards.append(card(key, value, 'text-white', 'bg-danger'))
                else:
                    cards.append(card(key, value)) 
            elif(type(value)==str):
                if(key == 'Unnamed: 0' or key=='isExDateFlag'):
                    continue
                else:
                    cards.append(card(key, value, 'text-white'))

        except Exception as e:
            print(e)
    return row_wrap(cards)

df3 = pd.read_csv("static_files/nifty_500_metadata.csv")
@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'),
              Input('demo-dropdown', 'value'))
def render_content(tab, stock):
    if tab == 'tab-1':
        return html.Div(className='jumbotron', children=[
            #row_wrap(html.H1('3MINDIA')),
            dcc.Graph(figure=px.scatter(pd.read_csv('static_files/NSE/{}.csv'.format(stock)), x='Date', y='Close')),
            #html.Div(style={'padding':'2rem'}, className='row', children=[cards, cards, cards, cards, cards, cards]),
            #row_wrap(card())
            data_mapper(df3[df3['symbol'] == stock].to_dict(orient='records')[0])
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Tab content 4')
        ])
    elif tab == 'tab-5':
        return html.Div([
            html.H3('Tab content 5')
        ])

if __name__ == "__main__":
    import os

    debug = False if os.environ["DASH_DEBUG_MODE"] == "False" else True
    app.run_server(host="0.0.0.0", port=8050, debug=debug)