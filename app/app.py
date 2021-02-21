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

metadata_df = pd.read_csv('nifty_500_metadata.csv')
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

df = px.data.iris()
df2 = pd.read_csv('3MINDIA.csv')

# <div class="card border-secondary mb-3" style="max-width: 20rem;">
#   <div class="card-header">Header</div>
#   <div class="card-body">
#     <h4 class="card-title">Secondary card title</h4>
#     <p class="card-text">Some quick example text to build on the card title and make up the bulk of the card's content.</p>
#   </div>
# </div>

def row_wrap(func):
    return html.Div(style={'padding':'2rem'}, className='row', children=func)

def card(title, value, text_color='text-white', bg_color='bg-primary'):
    return html.Div(style={'max-width': '20rem', 'margin':'2rem'}, className="card {} {} mb-3".format(text_color, bg_color), 
        children=[html.Div(className='card-header', children=title),
        html.Div(className='card-body', children=[html.H4(className='card-title', children=value)])])

def data_mapper(dump):
    n_vals = 0
    cards = []
    for key, value in dump.items():
        try:
            if(math.isnan(value)):
                continue
            elif(value < 0):
                cards.append(card(key, value, 'text-white', 'bg-danger'))
            else:
                cards.append(card(key, value)) 
        except Exception as e:
            print(e)
    return row_wrap(cards)

df3 = pd.read_csv("nifty_500_metadata.csv")
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

# app = dash.Dash(external_stylesheets=['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css'])
# app.config.suppress_callback_exceptions = True

# app.layout = html.Div(
#     children=[
#         html.H1(children="Market Dashboard"),
#         html.Ul(className="nav nav-tabs", children=[html.Li(className='nav-item', children=[html.A(className='nav-link active', href='#home', children="Home", **{'data-toggle':'tab'})]),
#         html.Li(className='nav-item', children=[html.A(className='nav-link', href='#ohlc', children="OHLC", **{'data-toggle':'tab'})]),
#         html.Li(className='nav-item', children=[html.A(className='nav-link', href='#ta', children="Technical Analysis", **{'data-toggle':'tab'})]),
#         html.Li(className='nav-item', children=[html.A(className='nav-link', href='#fa', children="Fundamental Analysis", **{'data-toggle':'tab'})]),
#         html.Li(className='nav-item', children=[html.A(className='nav-link', href='#portfolio', children="Portfolio", **{'data-toggle':'tab'})]),
#         html.Li(className='nav-item', children=[html.A(className='nav-link', href='#ml', children="Machine Learning", **{'data-toggle':'tab'})]),
#         ]),
#         html.Div(id='myTabContent', className='tab-content', children=[html.Div(className="tab-pane fade active show", id='home', children="Raw denim you probably haven't heard of them jean shorts Austin.\
#         Nesciunt tofu stumptown aliqua, retro synth master cleanse. Mustache cliche tempor, williamsburg carles vegan helvetica. Reprehenderit butcher retro keffiyeh dreamcatcher synth. Cosby sweater eu \
#         banh mi, qui irure terry richardson ex squid. Aliquip placeat salvia cillum iphone. Seitan aliquip quis cardigan american apparel, butcher voluptate nisi qui."),
#         html.Div(className="tab-pane fade", id='ohlc', children="."),
#         html.Div(className="tab-pane fade", id='ta', children="RA.")])])
    
# <div id="myTabContent" class="tab-content">
#   <div class="tab-pane fade active show" id="home">
#     <p>Raw denim you probably haven't heard of them jean shorts Austin. Nesciunt tofu stumptown aliqua, retro synth master cleanse. Mustache cliche tempor, williamsburg carles vegan helvetica. Reprehenderit butcher retro keffiyeh dreamcatcher synth. Cosby sweater eu banh mi, qui irure terry richardson ex squid. Aliquip placeat salvia cillum iphone. Seitan aliquip quis cardigan american apparel, butcher voluptate nisi qui.</p>
#   </div>
#   <div class="tab-pane fade" id="profile">
#     <p>Food truck fixie locavore, accusamus mcsweeney's marfa nulla single-origin coffee squid. Exercitation +1 labore velit, blog sartorial PBR leggings next level wes anderson artisan four loko farm-to-table craft beer twee. Qui photo booth letterpress, commodo enim craft beer mlkshk aliquip jean shorts ullamco ad vinyl cillum PBR. Homo nostrud organic, assumenda labore aesthetic magna delectus mollit.</p>
#   </div>
#   <div class="tab-pane fade" id="dropdown1">
#     <p>Etsy mixtape wayfarers, ethical wes anderson tofu before they sold out mcsweeney's organic lomo retro fanny pack lo-fi farm-to-table readymade. Messenger bag gentrify pitchfork tattooed craft beer, iphone skateboard locavore carles etsy salvia banksy hoodie helvetica. DIY synth PBR banksy irony. Leggings gentrify squid 8-bit cred pitchfork.</p>
#   </div>
#   <div class="tab-pane fade" id="dropdown2">
#     <p>Trust fund seitan letterpress, keytar raw denim keffiyeh etsy art party before they sold out master cleanse gluten-free squid scenester freegan cosby sweater. Fanny pack portland seitan DIY, art party locavore wolf cliche high life echo park Austin. Cred vinyl keffiyeh DIY salvia PBR, banh mi before they sold out farm-to-table VHS viral locavore cosby sweater.</p>
#   </div>
# </div>

if __name__ == "__main__":
    import os

    debug = False if os.environ["DASH_DEBUG_MODE"] == "False" else True
    app.run_server(host="0.0.0.0", port=8050, debug=debug)