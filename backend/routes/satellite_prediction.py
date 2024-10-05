import geopandas as gpd
from shapely.geometry import Point

wrs2_shapefile = "path_to_your_shapefile/WRS2_descending.shp"
wrs2 = gpd.read_file(wrs2_shapefile)

def latlon_to_wrs2(lat, lon):
    point = Point(lon, lat)
    wrs2_containing_point = wrs2[wrs2.contains(point)]
    
    if not wrs2_containing_point.empty:
        path = wrs2_containing_point.iloc[0]["PATH"]
        row = wrs2_containing_point.iloc[0]["ROW"]
        return path, row
    else:
        return None, None

# Example: convert latitude and longitude to WRS-2 path/row
lat = 34.0522  # Latitude for Los Angeles, CA
lon = -118.2437  # Longitude for Los Angeles, CA
path, row = latlon_to_wrs2(lat, lon)
