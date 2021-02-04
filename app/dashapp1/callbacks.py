from datetime import datetime as dt

# import pandas_datareader as pdr
from dash.dependencies import Input
from dash.dependencies import Output


def register_callbacks(dashapp):
    @dashapp.callback(Output('display-value', 'children'),
              [Input('dropdown', 'value')])
    def display_value(value):
        return 'You have selected "{}"'.format(value)
