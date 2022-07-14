# dataIO_funcs.py
# provided = datatype (point,raster)
import s3fs
import xarray as xr
import xesmf
from snowexsql.db import get_db
import requests 
import datetime
from bs4 import BeautifulSoup
from snowexsql.db import get_db
from snowexsql.data import LayerData,PointData# Import the function to get connect to the db
from snowexsql.conversions import query_to_geopandas # Import a useful function to format that data into a dataframe 
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
import dateutil.parser


def date_between_prime_snowEx(start_date, end_date, folder_date):
    result = [folder_date[i] for i in range(len(folder_date)) if (folder_date[i].date >= start_date and folder_date[i].date <= end_date)]
    return result

class access_SWESARR:
    def get_url_paths(url, ext='', params={}):
        """
        Funtion to extract list of folders in an online directory
        INPUT:
            url: Source url
        OUTPUT:
            List of folders in an online directory 
            Note this does not download any files
        """
        response = requests.get(url, params=params)
        if response.ok:
            response_text = response.text
        else:
            return response.raise_for_status()
        soup = BeautifulSoup(response_text, 'html.parser')
        folder_names = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
        folder_names = folder_names[5:-1]
        folder_names = [name[62:] for name in folder_names]
        folder_date = [datetime.datetime.strptime(date[24:30] , '%y%m%d') for date in folder_names]
        return folder_names,folder_date

def access_LIS(lon_range,lat_range,dates,variables,path,dx,dy,rsmpl):
    # access lis model outputs staged in a given location for a given box and set of dates

    # access amazon database
    s3 = s3fs.S3FileSystem(anon=False)
    lis_output_mapper = s3.get_mapper(path)
    lis_output_ds = xr.open_zarr(lis_output_mapper,
                                 consolidated=True)
    
    # specify spatiotemporal filtering
    lis_output_ds = lis_output_ds.sel(time=dates)
    lis_output_ds = lis_output_ds.where((lis_output_ds.lat >=  lat_range[0]) & 
                                        (lis_output_ds.lat <= lat_range[1]) &
                                        (lis_output_ds.lon >=  lon_range[0]) &
                                        (lis_output_ds.lon <=  lon_range[1]) ,drop=True)
    
    # regrid the data to a rectangular grid
    lis_output_ds = lis_output_ds.rename_dims({'east_west':'x','north_south':'y'})
    ds_out = xesmf.util.grid_2d(lis_output_ds['lon'].min(),lis_output_ds['lon'].max(),dx,
                                lis_output_ds['lat'].min(),lis_output_ds['lat'].max(),dy)
    regridder = xesmf.Regridder(lis_output_ds,ds_out,rsmpl)
    outt = regridder(lis_output_ds[variables])
    
    # finalize the datafile properties and return it to the user
    out_reproj = outt.assign_coords({'longitude':outt['lon'][0,:],'latitude':outt['lat'][:,0]})
    out_reproj = out_reproj.rename({'x':'longitude','y':'latitude'})
    out_reproj = out_reproj.rio.write_crs(4326)
    
    return out_reproj

class access_snowEx:
    def access_pointData(db_name,time_sel,time_buffer_dy,var_name,lat_range,lon_range):
        # open the session
        engine, session = get_db(db_name)

        # do date filtering
        pointDates = session.query(PointData.date).distinct().all()

        time_sel_newForm = dateutil.parser.parse(time_sel)
        start_date = time_sel_newForm-datetime.timedelta(days=time_buffer_dy)
        start_date = start_date.date()
        end_date = time_sel_newForm+datetime.timedelta(days=time_buffer_dy)
        end_date = end_date.date()

        filtered_dates = date_between_prime_snowEx(start_date, end_date, pointDates)

        # query the dataset and concatenate
        q = session.query(PointData).filter(PointData.type == var_name)   

        data_day_list = []
        for dt_count,dtt in enumerate(filtered_dates):
            print(dtt)
            dt_sel = datetime.date(dtt[0].year,dtt[0].month,dtt[0].day)
            q_sub = q.filter(PointData.date == dt_sel)
            df = query_to_geopandas(q_sub, engine)

            # i think this is what you do to concatenate??
            data_day_list.append(df)
        df_concat = pd.concat(data_day_list)
        df_concat_gpd = gpd.GeoDataFrame(df_concat)

        session.close()

        # list of coordindate pairs
        coordinates = [[ lon_range[0], lat_range[0] ], [ lon_range[1], lat_range[0] ], [ lon_range[1], lat_range[1]], [lon_range[0], lat_range[1]]]        
        print(coordinates)
        # Create a Shapely polygon from the coordinate-tuple list
        ply_coord = Polygon(coordinates)
        # create a dictionary with needed attributes and required geometry column
        df = {'Attribute': ['name1'], 'geometry': ply_coord}
        # Convert shapely object to a geodataframe 
        poly = gpd.GeoDataFrame(df, geometry='geometry', crs ="EPSG:4326").to_crs("EPSG:26912")
        df_clipped = gpd.clip(df_concat_gpd, poly)
        
        return df_clipped
