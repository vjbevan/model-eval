# dataIO_funcs.py
# provided = datatype (point,raster)
import s3fs
import xarray as xr
import xesmf
from snowexsql.db import get_db
import requests 
from datetime import datetime
from bs4 import BeautifulSoup

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
    folder_date = [datetime.strptime(date[24:30] , '%y%m%d') for date in folder_names]
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
    
    # finalize file properties and return it to the user
    out_reproj = outt.assign_coords({'longitude':outt['lon'][0,:],'latitude':outt['lat'][:,0]})
    out_reproj = out_reproj.rename({'x':'longitude','y':'latitude'})
    out_reproj = out_reproj.rio.write_crs(4326)
    
    return out_reproj


    
