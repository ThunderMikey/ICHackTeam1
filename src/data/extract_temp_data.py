import ee
from ee import batch
ee.Initialize()

for year in range(2009, 2018):
    print("Extracting data for year {}".format(year))
    # reduce daily precipitation data to annual total 
    # load precip data (mm, daily total): 365 images per year 
    precipCollection = ee.ImageCollection('IDAHO_EPSCOR/GRIDMET').select('pr')\
                        .filterDate('{}-01-02'.format(year), '{}-12-31'.format(year))

    # reduce the image collection to one image by summing the 365 daily rasters
    annualPrecip = precipCollection.reduce(ee.Reducer.min());

    # Image stats by regions: A spatial reducer ------------------------------------- 
    # Get mean annual precip by county 

    # load regions: counties from a public fusion table, removing non-conus states
    # by using a custom filter
    nonCONUS = [2,15,60,66,69,72,78]
    counties = ee.FeatureCollection('ft:1ZMnPbFshUI3qbk9XE0H7t1N5CjsEGyl8lZfWfVn4')\
            .filter(ee.Filter.inList('STATEFP',nonCONUS).Not())

    # get mean precipitation values by county polygon
    countyPrecip = annualPrecip.reduceRegions(\
      collection = counties,\
      reducer = ee.Reducer.mean(),\
      scale = 4000
    )

    # add a new column for year to each feature in the feature collection
    countyPrecip = countyPrecip.map(
        lambda feature: feature.set('Year',year)
    )
    # Export ---------------------------------------------------------------------
    out = batch.Export.table.toDrive(
      collection = countyPrecip,\
      description = '{}_mean_precip_usa'.format(year),\
      folder = 'ee_data',\
      fileFormat = 'CSV'
    )
    process = batch.Task.start(out)
    print("Process sent to cloud")
