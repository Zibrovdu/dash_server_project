import dash
import dash_bootstrap_components as dbc
from passport.layouts import serve_layout
from passport.callbacks import register_callbacks


app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True,
                title='Отдел сопровождения пользователей')
server = app.server

app.layout = serve_layout
register_callbacks(app)

if __name__ == '__main__':
    app.run_server()
