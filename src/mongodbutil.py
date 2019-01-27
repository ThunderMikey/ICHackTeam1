import pymongo 
import pandas as pd
import dash_html_components as html
import plotly.graph_objs as go


def mongoclient(url):
    return pymongo.MongoClient(url)

def csv2mongo(client,dbname,collectionname,filename):

    try:
        db = client.get_database(dbname)
        db_cm = db[collectionname]
        tlist = pd.read_csv(filename)
        db_cm.insert_many(tlist.to_dict('records'))
        client.close()
    except:
        print('File not uploaded ', filename)

def df2mongo(client,dbname,collectionname,df):

    try:
        db = client.get_database(dbname)
        db_cm = db[collectionname]
        db_cm.insert_many(df.to_dict('records'))
        client.close()
    except:
        print('Not uploaded ', dbname,collectionname)
        
# Read dataframe from mongo, used for pricing data,
def mongo2df(client,dbname,collectionname):
    
    db = client.get_database(dbname)
    df = pd.DataFrame(list(db[collectionname].find({})))
    try:
        df.drop(['_id'], axis=1,inplace=True)
        df.drop_duplicates(keep='last', inplace=True)
    except:
        print('Record not found',collectionname)
    client.close()
    return df 

def mongo2csv(client,dbname,collectionname,filepath):
    
    db = client.get_database(dbname)
    df = pd.DataFrame(list(db[collectionname].find({})))
    try:
        df.drop(['_id'], axis=1,inplace=True)
        df.drop_duplicates(keep='last', inplace=True)
        df.to_csv(filepath,index=False)
    except:
        print('Record not found',collectionname)
    client.close()
    return df

# label value dictionary of all database
def dropdown_get_all_database(client):
    dbs=client.list_database_names()
    try:
        dbs.remove('admin')
        dbs.remove('config')
        dbs.remove('local')
    except:
        print('Error in database definition')
    dropdownoptions=[{'label':x,'value':x} for x in dbs]
    return dropdownoptions

def dropdown_get_all_table(client,dbname):
    tables=client[dbname].collection_names()
    dropdownoptions=[{'label':x,'value':x} for x in tables]
    return dropdownoptions   

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

# Retrive states and county
def get_column_unique(client,dbname='USweather',collectioname='countystate',columname='state_fullname'):
    states=mongo2df(client,dbname,collectioname)[columname].unique()
    dropdownoptions=[{'label':x,'value':x} for x in states]
    return dropdownoptions
# county depends on states
def get_depedent_column(client,state,dbname='USweather',collectioname='countystate',independent='state_fullname',dependent='County'):
    states=mongo2df(client,dbname,collectioname)
    county=states[states[independent]==state][dependent]
    dropdownoptions=[{'label':x,'value':x} for x in county]
    return dropdownoptions

def generate_metrics():
    dropdownoptions=[{'label':'Max Temperature','value':'maxtemperature'},{'label':'Min Temperature','value':'mintemperature'},{'label':'Mean Precipitation','value':'meanprecipitation'},{'label':'Max Precipitation','value':'maxprecipitation'}]
    return dropdownoptions
    
def generate_title(metric,county,state):
    mapping={'maxtemperature':'Max Temperature','mintemperature':'Min Temperature','meanprecipitation':'Mean Precipitation','maxprecipitation':'Max Precipitation'}
    newmetric=mapping[metric]
    title='{} of {} in {}'.format(newmetric,county,state)
    return title

def get_year(start=1997,end=2027):
    dropdownoptions=[{'label':x,'value':x} for x in range(start,end+1)]
    return dropdownoptions


def generate_historical_data(client,state,county,metric,dbname='USweather',collectionname='countystate'):
    db = client.get_database(dbname)
    df = pd.DataFrame(list(db[collectionname].find({'state_fullname':state,'County':county})))
    df.drop(['_id'], axis=1,inplace=True)
    df.drop_duplicates(keep='last', inplace=True)
    latitude=df.iloc[0]['Latitude']
    longitude=df.iloc[0]['Longitude']
    df2=pd.DataFrame(list(db[metric].find({'Latitude':latitude,'Longitude':longitude})))
    df2.drop(['_id'], axis=1,inplace=True)
    df2.drop_duplicates(keep='last', inplace=True)
    return {'Historical':df2,'Lat':latitude,'Long':longitude}
    
def get_missing_years(df,timecolumn,start=1997,end=2027):
    existing_year=df[timecolumn].tolist()
    fullyear=[x for x in range(start,end+1)]
    missing_year=list(set(fullyear) - set(existing_year))
    return missing_year

def create_time_series(dff,x_col,y_col,title, axis_type='Linear'):
    return {
        'data': [go.Scatter(
            x=dff[x_col],
            y=dff[y_col],
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 30, 'b': 35, 'r': 20, 't': 15},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }

def generate_spatial(df,graphtitle,metric):
    df['text'] = metric+' '+df[metric].astype(str)
    scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]
    data = [ dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = df['Longitude'],
            lat = df['Latitude'],
            text = df['text'],
            mode = 'markers',
            marker = dict(
                size = 8,
                opacity = 0.8,
                reversescale = True,
                autocolorscale = False,
                symbol = 'square',
                line = dict(
                    width=1,
                    color='rgba(102, 102, 102)'
                ),
                colorscale = scl,
                cmin = df[metric].min(),
                color = df[metric],
                cmax = df[metric].max(),
                colorbar=dict(
                    title=metric
                )
            ))]

    layout = dict(
            title = graphtitle,
            colorbar = True,
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(217, 217, 217)",
                countrycolor = "rgb(217, 217, 217)",
                countrywidth = 0.5,
                subunitwidth = 0.5
            ),
        )
    fig = dict(data=data,layout=layout) 
    return fig

def create_space_series(client,year,metric,dbname='USweather'):
    db = client.get_database(dbname)
    df = pd.DataFrame(list(db[metric].find({'Year':year})))
    graphtitle='{} of US in Year {}'.format(metric,year)
    return generate_spatial(df,graphtitle,metric)



if __name__=='__main__':
    client=mongoclient('localhost')
    df=generate_historical_data(client,'California','Imperial','meanprecipitation')
    print(get_missing_years(df,'Year'))

