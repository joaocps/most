import numpy as np

from osgeo import ogr
from osgeo import osr

import datetime

import glob


class Shape_Creation_DAO(object):

    def __init__(self):
        self.layer_name = "Fire Propagation"
        self.output_file = "NewShapes/shape_output.shp"
        self.spatial_reference = 32629
        self.enclave_fire = "Enclave Fire"
        self.expanding_fire = "Expanding Fire"
        self.directory = "/home/jcps/Desktop/Projeto2018/most-g4/opencv_demo/DAO"

        self.elapsed_time = 0.0

    def create_layer_and_metadata(self, ds, srs):

        # --------------------------------
        # Layer.
        # --------------------------------

        layer = ds.CreateLayer(self.layer_name, srs, ogr.wkbMultiPolygon)

        # --------------------------------
        # Fields (Metadata).
        # --------------------------------

        shape_type = ogr.FieldDefn("Shape *", ogr.OFTString)
        fire_type_field = ogr.FieldDefn("Fire_Type", ogr.OFTString)
        month_field = ogr.FieldDefn("Month", ogr.OFTInteger)
        day_field = ogr.FieldDefn("Day", ogr.OFTInteger)
        hour_field = ogr.FieldDefn("Hour", ogr.OFTInteger)
        elapsed_mi_field = ogr.FieldDefn("Elapsed_Mi", ogr.OFTReal)

        layer.CreateField(shape_type)
        layer.CreateField(fire_type_field)
        layer.CreateField(month_field)
        layer.CreateField(day_field)
        layer.CreateField(hour_field)
        layer.CreateField(elapsed_mi_field)

        self.openfile_and_iterate(layer)

        ds.Destroy()

    def openfile_and_iterate(self, layer):

        # --------------------------------
        # Multipolygons.
        # --------------------------------

        multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)

        # --------------------------------
        # LOOP FOR N FILES WITH MULTIPOLYGONS !
        # .npy must be ordered by number
        # --------------------------------

        for filepath in sorted(glob.iglob(self.directory + '/*.npy')):
            print(filepath)
            l = np.load(filepath)
            for x in range(len(l)):
                ring = ogr.Geometry(ogr.wkbLinearRing)
                for x2 in l[x]:
                    ring.AddPoint_2D(x2[0], x2[1])
                polygon = ogr.Geometry(ogr.wkbPolygon)
                polygon.AddGeometry(ring)

                # -----------------------------------
                # Associate Metadata with Polygon.
                # -----------------------------------

                featureDefn = layer.GetLayerDefn()
                feature = ogr.Feature(featureDefn)

                feature.SetGeometry(polygon)
                feature.SetField("Shape *", "Polyline")
                feature.SetField("Fire_Type", self.expanding_fire)
                feature.SetField("Month", 5)
                feature.SetField("Day", 21)
                feature.SetField("Hour", 10)
                feature.SetField("Elapsed_Mi", self.elapsed_time)

                layer.CreateFeature(feature)

                multipolygon.AddGeometry(polygon)

            self.elapsed_time = self.elapsed_time + 10

            print("----------------------------NEW FILE-------------------------------------------")

    def main(self):

        # --------------------------------
        # Shapefile.
        # --------------------------------

        driver = ogr.GetDriverByName("Esri Shapefile")
        ds = driver.CreateDataSource(self.output_file)

        # --------------------------------
        # Geo Reference.
        # --------------------------------

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(self.spatial_reference)

        self.create_layer_and_metadata(ds, srs)


if __name__ == '__main__':
    Shape_Creation_DAO().main()
