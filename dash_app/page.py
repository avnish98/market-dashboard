import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from processor import NSEProcessor

class MainPage:
    def __init__(self, exchange, stock_name):
        self.exchange = exchange
        self.stock_name = stock_name
        self.data_processor = NSEProcessor(self.exchange, self.stock_name)
        self.page_content = []

    def render_graph(self):
        df = self.data_processor.process_ohlc()
        page_content.append(dcc.Graph(figure=px.scatter(df, x='Date', y='Close')))

    def render_data(self, metadata):
        data_dump = self.data_processor.process_metadata()

        page_content.append()

    def render_page(self):
        return html.Div(className='jumbotron',  children=page_content)
