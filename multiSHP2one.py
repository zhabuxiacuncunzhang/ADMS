'''
Descripttion: file content
version: 
Author: Xuesong_Zhang
Date: 2023-03-04 15:47:35
LastEditors: Xuesong_Zhang
LastEditTime: 2023-03-04 16:02:21
'''
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
import glob

shapefiles = glob.glob("../data/test03011/*.shp")
gdf = pd.concat([
    gpd.read_file(shp)
    for shp in shapefiles
]).pipe(gpd.GeoDataFrame)
gdf.to_file('./compiled.shp')
