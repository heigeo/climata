from __init__ import CDECMetaIO
from wq.io.gis import ShapeIO, GisIO
from shapely.geometry import Point
from shapely.ops import cascaded_union
import fiona
basins = ShapeIO(filename='/var/www/klamath/db/loaddata/scripts/data/basins.shp')
#klamath = cascaded_union([basin.geometry for basin in basins.values()])

#all_stations = CDECMetaIO()

#for station in all_stations:
#    sitebasin = None
#    loc = Point(station.long, station.lat)
#    if klamath.contains(loc):
#        print loc
    
