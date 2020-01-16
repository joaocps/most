import numpy as np
from osgeo import ogr
from osgeo import osr
import datetime

# http://pcjericks.github.io/py-gdalogr-cookbook/geometry.html#create-a-linestring


l = np.load("converted_last.npy", allow_pickle=True)

for z in l:
    for z2 in z:
        print(z2[0])

# -------------------------------------------------------- correct -----------------------------------
multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)

for x in range(len(l)):
    print("New Polygon » ", x, datetime.datetime.now())
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for x2 in l[x]:
        ring.AddPoint_2D(x2[0], x2[1])
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)
    multipolygon.AddGeometry(polygon)

driver = ogr.GetDriverByName("Esri Shapefile")
ds = driver.CreateDataSource("NewShapes/shape_output.shp")

srs = osr.SpatialReference()
srs.ImportFromEPSG(32629)

layer = ds.CreateLayer('', srs, ogr.wkbMultiPolygon)
layer.CreateField(ogr.FieldDefn('FID', ogr.OFTInteger))
layer.CreateField(ogr.FieldDefn('Shape *', ogr.OFTString))
layer.CreateField(ogr.FieldDefn('Fire_Type', ogr.OFTString))
layer.CreateField(ogr.FieldDefn('Time', ogr.OFTDateTime))

defn = layer.GetLayerDefn()
feat = ogr.Feature(defn)
feat.SetField('FID', 0)
feat.SetField('Shape *', "Multipolygon")
feat.SetField('Fire_Type', "Expanding Fire")
# feat.SetField('Time', str(datetime))

feat.SetGeometry(multipolygon)
layer.CreateFeature(feat)
# ds.Destroy()

# ---------------------try-----------------

defn = layer.GetLayerDefn()
feat = ogr.Feature(defn)
feat.SetField('FID', 1)
feat.SetField('Shape *', "Multipolygon")
feat.SetField('Fire_Type', "Expanding Fire")
# feat.SetField('Time', str(datetime))

feat.SetGeometry(multipolygon)
layer.CreateFeature(feat)
ds.Destroy()

# ------------------------------------------

# Export file to WKT
# f = open("multipolygon.wkt", "w")
# f.write(multipolygon.ExportToWkt())

print(multipolygon.ExportToJson())

# extract polygons from multipolygons
for q in multipolygon:
    print(q)

# -------------------------------------------BAD FEATURES BUT USEFULL----------------------------------------------------------
#
# for q in multipolygon:
#     P = shapely.wkt.loads(q)
#     print(P)

# schema = {
#     'geometry': 'MultiPolygon',
#     'properties': {'id': 'int'},
# }
# with fiona.open('my_shp2.shp', 'w', 'ESRI Shapefile', schema) as c:
#
#     for q in multipolygon:
#
#         c.write({
#             'geometry': multipolygon,
#             'properties': {'id': 1},
#         })
