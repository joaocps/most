import numpy as np
from osgeo import ogr

# http://pcjericks.github.io/py-gdalogr-cookbook/geometry.html#create-a-linestring

l = np.load("converted.npy", allow_pickle=True)

for z in l:
    for z2 in z:
        print(z2[0])

# -------------------------------------------------------- correct -----------------------------------
multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)

for x in range(len(l)):
    print("New Polygon » ", x)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for x2 in l[x]:
        ring.AddPoint(x2[0], x2[1])
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)
    multipolygon.AddGeometry(polygon)

# f = open("multipolygon.wkt", "w")
# f.write(multipolygon.ExportToWkt())

# extract polygons from multipolygons
for q in multipolygon:
    print(q)

# -----------------------------------------------------------------------------------------------------

