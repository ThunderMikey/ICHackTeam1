# Setting up multiple apps
from dash import Dash
from werkzeug.wsgi import DispatcherMiddleware
import flask
from werkzeug.serving import run_simple
# Dash application
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as depend
import dash_table
# MongoDB ML Models
from pymongo import MongoClient 
import mongodbutil as ml
import model

# Prepare static data to load into application 
# Realtime data please refer to https://dash.plot.ly/live-updates

# Prepare data
dbhost='localhost'
dbclient=ml.mongoclient(dbhost)

# CSS 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Setting up flask server and dash applications
server = flask.Flask(__name__)
dash_app1 = Dash(__name__, server = server, url_base_pathname='/dashboard/', external_stylesheets=external_stylesheets )
dash_app2 = Dash(__name__, server = server, url_base_pathname='/reports/')

dash_app2.layout = html.Div([html.H1('Hi there, I am app2 for reports')])

dash_app1.layout = html.Div(children=[
    html.Div('Database Name'),
    dcc.Dropdown(
        id='database-name',
        options=ml.dropdown_get_all_database(dbclient),
        value='Database Name'
    ),
    html.Div('Table Name'),
        dcc.Dropdown(
        id='table-name',
        options=[{'value':'Table','label':'Table'}],
        value='Table Name'
    ),
    html.Div(id='my-table')
])

@dash_app1.callback(
    depend.Output(component_id='table-name', component_property='options'),
    [depend.Input(component_id='database-name', component_property='value')]
)
def update_table_name(database):
    try:
        df=ml.dropdown_get_all_table(dbclient,database)
        return df
    except:
        return html.Div('Invalid table')


@dash_app1.callback(
    depend.Output(component_id='my-table', component_property='children'),
    [depend.Input(component_id='database-name', component_property='value'),
    depend.Input(component_id='table-name', component_property='value'),]
)
def update_output_div(database,table):
    try:
        df=ml.mongo2df(dbclient,database,table)
        return ml.generate_table(df)
    except:
        return html.Div('Invalid table')

# Setting up the Flask server and applications

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