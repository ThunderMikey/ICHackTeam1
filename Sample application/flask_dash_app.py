from dash import Dash
from werkzeug.wsgi import DispatcherMiddleware
import flask
from werkzeug.serving import run_simple
import dash_core_components as dcc
import dash_html_components as html
from pymongo import MongoClient 
import mongodbutil as ml

# Prepare static data to load into application 
# Realtime data please refer to https://dash.plot.ly/live-updates
def load_data():
    client=ml.mongoclient('localhost')
    client.drop_database('TSDB')
    ml.csv2mongo(client,'TSDB','TYX','TYX.csv')
    df=ml.mongo2df(client,'TSDB','TYX')
    return df

# Prepare data
tsdf=load_data()

# CSS 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Setting up flask server and dash applications
server = flask.Flask(__name__)
dash_app1 = Dash(__name__, server = server, url_base_pathname='/dashboard/', external_stylesheets=external_stylesheets )
dash_app2 = Dash(__name__, server = server, url_base_pathname='/reports/')

dash_app2.layout = html.Div([html.H1('Hi there, I am app2 for reports')])


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

dash_app1.layout = html.Div(children=[
    html.H4(children='10Y Treasury Yield'),
    generate_table(tsdf)
])





@server.route('/')
@server.route('/hello')
def hello():
    return 'hello world!'

@server.route('/dashboard')
def render_dashboard():
    return flask.redirect('/dash1')


@server.route('/reports')
def render_reports():
    return flask.redirect('/dash2')

app = DispatcherMiddleware(server, {
    '/dash1': dash_app1.server,
    '/dash2': dash_app2.server
})

if __name__ == "__main__":
    
    run_simple('127.0.0.1', 8080, app, use_reloader=True, use_debugger=True)