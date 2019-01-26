import pandas as pd    

def _list_files(currentpath):
    from os import listdir 
    from os.path import isfile, join 
    files = [join(currentpath, f) for f in listdir(currentpath) if isfile(join(currentpath, f))]
    return files

def _merge_files(listoffiles,columnname='Maxprec'):
    data=[]
    for i in listoffiles:
        data.append(pd.read_csv(i))
    alldata=pd.concat(data)
    countydf=pd.read_csv('countystate.csv',sep='\t')
    mergedf=alldata.merge(countydf,how='left',left_on=['NAME','STATEFP'],right_on=['County','State_FIPS'])
    mergedf.rename(columns={'mean':columnname},inplace=True)
    mergedf.dropna(axis=0,how='any',inplace=True)
    mergedf.to_csv(columnname+'.csv',columns=['Year','State','County','Latitude','Longitude']+[columnname],index=False)

def process_folder(currentpath,columnname):
    files=_list_files(currentpath)
    _merge_files(files,columnname)

process_folder('ee_prec_max','Maxprec')
process_folder('ee_prec_mean','Meanprec')
process_folder('ee_temp_max','Maxtemp')
process_folder('ee_temp_min','Mintemp')