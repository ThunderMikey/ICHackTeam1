import pandas as pd 
import mongodbutil as ml 


dbhost='localhost'
dbclient=ml.mongoclient(dbhost)

df1=pd.read_csv('data/min_temperature.csv',sep='\t')
ml.df2mongo(dbclient,'USweather','mintemperature',df1)
df2=pd.read_csv('data/max_temperature.csv',sep='\t')
ml.df2mongo(dbclient,'USweather','maxtemperature',df2)
df3=pd.read_csv('data/max_precipitation.csv',sep='\t')
ml.df2mongo(dbclient,'USweather','maxprecipitation',df3)
df4=pd.read_csv('data/mean_precipitation.csv',sep='\t')
ml.df2mongo(dbclient,'USweather','meanprecipitation',df4)
df5=pd.read_csv('data/countystate.csv',sep='\t')
ml.df2mongo(dbclient,'USweather','countystate',df5)

