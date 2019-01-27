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
import pandas as pd

# Prepare static data to load into application 
# Realtime data please refer to https://dash.plot.ly/live-updates

# Prepare data
dbhost='localhost'
dbclient=ml.mongoclient(dbhost)

# CSS 
external_stylesheets = [#'https://codepen.io/chriddyp/pen/bWLwgP.css',
        '/static/main.css']

# Setting up flask server and dash applications
server = flask.Flask(__name__)
dash_app1 = Dash(__name__, server = server, url_base_pathname='/database/', external_stylesheets=external_stylesheets )
dash_app2 = Dash(__name__, server = server, url_base_pathname='/time/', external_stylesheets=external_stylesheets)
dash_app3 = Dash(__name__, server = server, url_base_pathname='/space/', external_stylesheets=external_stylesheets)
dash_app4 = Dash(__name__, server = server, url_base_pathname='/spacetime/', external_stylesheets=external_stylesheets)

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

# Application 2
dash_app2.layout = html.Div(children=[
    html.H1('Historical Data', className='subpage-heading'),
    html.H2('State Name'),
    dcc.Dropdown(
        id='state-name',
        options=ml.get_column_unique(dbclient),
        value='State Name'
    ),
    html.H2('County Name'),
    dcc.Dropdown(
        id='county-name',
        options=[{'value':'Table','label':'Table'}],
        value='County Name'
    ),
    html.Div('Weather Metrics'),
    dcc.Dropdown(
        id='weather-metric',
        options=ml.generate_metrics(),
        value='Weather metric'
    ),
    html.Div(id='time'),
    html.Label(['Return ', html.A('mainpage', href='/')])
])

@dash_app2.callback(
    depend.Output(component_id='county-name', component_property='options'),
    [depend.Input(component_id='state-name', component_property='value')]
)
def update_county_name(state):
    try:
        county=ml.get_depedent_column(dbclient,state)
        return county
    except:
        return html.Div('Invalid county')

@dash_app2.callback(
    depend.Output('time', 'children'),
    [depend.Input('state-name', 'value'),
     depend.Input('county-name', 'value'),
     depend.Input('weather-metric', 'value')])
def predict_time(state,county,metric):
    hist=ml.generate_historical_data(dbclient,state,county,metric)
    data=hist['Historical']
    if data.size<1:
        return['No data for {} in {}'.format(county,state)]
    if metric=='maxtemperature' or metric=='mintemperature':
        data[metric]=data[metric].astype(float)-273.15
    data.sort_values('Year',inplace=True)
    title = ml.generate_title(metric,county,state)
    return [dcc.Graph(id='ts',figure=ml.create_time_series(data,'Year',metric,title))]

dash_app3.layout= html.Div(children=[
    html.Div('Historical Weather Data in the US from 1997 to 2007 by geographical distribution'),
    html.Div('Year'),
    dcc.Dropdown(
        id='year-name',
        options=ml.get_year(),
        value='Year'
    ),
    html.Div('Weather Metrics'),
    dcc.Dropdown(
        id='weather-metric',
        options=ml.generate_metrics(),
        value='Weather metric'
    ),
    html.Div(id='space'),
    html.Label(['Return ', html.A('mainpage', href='/')])
])

@dash_app3.callback(
    depend.Output('space', 'children'),
    [depend.Input('year-name', 'value'),
     depend.Input('weather-metric', 'value')])
def predict_space(year,metric):
    df=ml.download_space_series(dbclient,year,metric)
    if df.size<1:
        return ['No data in Year {}'.format(year)]
    return [dcc.Graph(id='newspace',figure=ml.create_space_series(dbclient,df,year,metric))]

dash_app4.layout= html.Div(children=[
    html.Div('Weather Forecast in California from 2018 to 2025'),
    html.Div('Year'),
    dcc.Dropdown(
        id='year-name',
        options=ml.get_year2(),
        value='Year'
    ),
    html.Div('Weather Metrics'),
    dcc.Dropdown(
        id='weather-metric',
        options=ml.generate_metrics2(),
        value='Weather metric'
    ),
    html.Div(id='space'),
    html.Label(['Return ', html.A('mainpage', href='/')])
])

@dash_app4.callback(
    depend.Output('space', 'children'),
    [depend.Input('year-name', 'value'),
     depend.Input('weather-metric', 'value')])
def predict_spacetime(year,metric):
    df=ml.download_space_series2(dbclient,year,metric)
    if df.size<1:
        return ['No data in Year {}'.format(year)]
    return [dcc.Graph(id='newspace',figure=ml.create_space_series(dbclient,df,year,metric))]

# Setting up the Flask server and applications

@server.route('/')
@server.route('/hello')
def hello():
    return flask.render_template('index.html')

@server.route('/database')
def render_dashboard():
    return flask.redirect('/dash1')


@server.route('/time')
def render_time():
    return flask.redirect('/dash2')

@server.route('/space')
def render_space():
    return flask.redirect('/dash3')

@server.route('/spacetime')
def render_spacetime():
    return flask.redirect('/dash4')

app = DispatcherMiddleware(server, {
    '/dash1': dash_app1.server,
    '/dash2': dash_app2.server,
    '/dash3': dash_app3.server,
    '/dash4': dash_app4.server
})

if __name__ == "__main__":
    run_simple('127.0.0.1', 8080, app, use_reloader=True, use_debugger=True)
