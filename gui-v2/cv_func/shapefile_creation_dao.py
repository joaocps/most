import numpy as np

import shapefile as shp

from osgeo import ogr
from osgeo import osr

import glob
import os


class Shape_Creation_DAO(object):

    def __init__(self):
        self.layer_name = "Fire Propagation"
        self.output_file = "DisperSHP"
        self.spatial_reference = 32629
        self.enclave_fire = "Enclave Fire"
        self.expanding_fire = "Expanding Fire"
        self.directory = ""

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
            # print(filepath)
            l = np.load(filepath, allow_pickle=True)
            self.simple_shapefile(l, filepath, self.elapsed_time)
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

            self.elapsed_time = self.elapsed_time + 60

            # print("----------------------------NEW FILE-------------------------------------------")

    def simple_shapefile(self, npy, output, time):
        w = shp.Writer(output.split(".")[0], shp.POLYGON)

        w.poly(npy)
        w.field('F_FLD', 'C', '40')
        w.field('S_FLD', 'C', '40')
        w.field('Time', 'C', '40')
        w.record('First', 'Polygon', time)

    def main(self, directory, o):
        self.directory = directory

        if o == 'win':
            f_path = self.directory + "\\" + self.output_file + "\\"
            if os.path.exists(os.path.normpath(f_path)) is False:
                os.mkdir(f_path)
            f_path = f_path + "\\shape_output.shp"
        else:
            f_path = self.directory + "/" + self.output_file + "/"
            if os.path.exists(f_path) is False:
                os.mkdir(f_path)
            f_path = f_path + "/shape_output.shp"

        # --------------------------------
        # Shapefile.
        # --------------------------------

        driver = ogr.GetDriverByName("Esri Shapefile")
        ds = driver.CreateDataSource(f_path)

        # --------------------------------
        # Geo Reference.
        # --------------------------------

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(self.spatial_reference)

        self.create_layer_and_metadata(ds, srs)


# if __name__ == '__main__':
#     Shape_Creation_DAO().main()
