'''
Descripttion: file content
version: 
Author: Xuesong_Zhang
Date: 2023-03-04 15:47:35
LastEditors: Xuesong_Zhang
LastEditTime: 2023-03-04 16:22:23
'''
import sys
import glob
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt

def multiSHP2one(path,outputname):
    shapefiles = glob.glob(path+"/"+"*.shp")
    gdf = pd.concat([
        gpd.read_file(shp)
        for shp in shapefiles
    ]).pipe(gpd.GeoDataFrame)
    gdf.to_file(outputname)

    print("*******************************************************")
    print("Then please run the following commands")
    print("in the cmd or other terminal in Windows or other Linux,")
    print("to import shp file into the PostgreSQL database")
    print("*******************************************************")
    print("shp2pgsql -s 4326 -W \"UTF-8\" <shp_name> > <sql_name>")
    print("psql -U <username> -h <host> -p <port> -d <database_name> -f <sql_name>")

def main(argv):
    print("*****************************************")
    print("*        multi SHP to one SHP           *")
    print("*            Xuesong Zhang              *")
    print("*             2023.03.04                *")
    print("*****************************************")
    if (len(argv) < 2 or len(argv) > 2):
        print("usage:")
        print("    multiSHP2one.py <path> <result_name>")
        print("        path          path of *.shp")
        print("        result_name   result file path and name")
    else:
        multiSHP2one(argv[0], argv[1])


if __name__ == '__main__':
    main(sys.argv[1:])