import dash
from passport.layouts import layout
from passport.callbacks import register_callbacks


app = dash.Dash(__name__, suppress_callback_exceptions=True, title='Отдел сопровождения пользователей')
server = app.server

app.layout = layout
register_callbacks(app)

if __name__ == '__main__':
    app.run_server()
