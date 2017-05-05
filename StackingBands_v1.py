from osgeo import gdal
import os
from numpy import ma
import math
from matplotlib import pyplot as plt

def ret_ma_array(path):
    dataset = gdal.Open(path)
    band = dataset.GetRasterBand(1)
    # Store nodata value, for masking
    nodata = band.GetNoDataValue()
    # Load as array
    raster = band.ReadAsArray(0, 0, band.XSize, band.YSize)
    masked_raster = ma.masked_values(raster, nodata, copy=False)
    masked_raster.fill_value = nodata

    return masked_raster

def addDEMBand(dstpath, refraster, *args):
    """
    Creates a file with path dstpath with 2 bands, DEM and snow
    :param dstpath: Output path
    :param mainraster: Raster from which metadata is to be copied
    :param DEMarray: Array containing DEM data (goes to 2nd band)
    :param Snowarray: Array containing Snoe Cover data (goes to 1st band)
    """
    print "[+] Getting metadata..."
    x_size = refraster.RasterXSize
    y_size = refraster.RasterYSize
    pixel_size = refraster.GetGeoTransform()[1]
    x_origin = refraster.GetGeoTransform()[0]
    y_origin = refraster.GetGeoTransform()[3]
    wkt_proj = refraster.GetProjection()

    driver = gdal.GetDriverByName("GTiff")

    dataset = driver.Create(
        dstpath,
        x_size,
        y_size,
        len(args[0]),
        gdal.GDT_Float32,
    )

    dataset.SetGeoTransform((
        x_origin,
        pixel_size,
        0,
        y_origin,
        0,
        -pixel_size
    ))
    print "[+] Metadata obatined"
    print "[+] Creating file: {0}".format(dstpath)
    dataset.SetProjection(wkt_proj)

    i = 1

    for array in args[0]:
        print "[+] Writing array: {0}".format(i)
        dataset.GetRasterBand(i).SetNoDataValue(0)
        dataset.GetRasterBand(i).WriteArray(ma.filled(array, 0))
        i+=1
    dataset.FlushCache()    # Writes to file
    print "[+] File created!"

def coordToPixel(gt, pt):
    """
    Converts a given coordinate to pixel
    :param gt: Geotransform of the raster
    :param pt: Coordinates of the point
    :return:
    """
    x = -(gt[0] - pt[0]) / gt[1]
    y = (gt[3] - pt[1]) / gt[1]
    return (int(math.floor(x)), int(math.floor(y)))

def pixelToCoord(gt, pt):
    """
    converts given array index to coordinates, returned coordinate is the coordinate of the centre of the array cell
    :param gt: Geotransform
    :param pt: Pixel point
    :return:
    """
    x = gt[0] + pt[0] * gt[1] + gt[1]/2
    y = gt[3] + pt[1] * gt[5] + gt[5]/2
    return x, y

def main():
    dem_path = "DEM/Brahmaputra_lowres_sinu.tif"
    src_dir = "UsefulData" + os.sep
    basin = "Brahmaputra"
    directories = os.listdir(src_dir)
    directories = filter(lambda x: os.path.isdir(src_dir + x), directories)

    lims = [(0,1000),(1000,2000),(2000,3000),(3000,4000),(4000,5000),(5000,6000),(6000,7000),(7000,8000)] #b1, b2, b3, b4, b5, b6, b7, b8 respectively
    DEM = ret_ma_array(dem_path)
    for directory in directories[413:]:
        print "[+] Working in: " + directory
        src_path = src_dir + directory + os.sep + basin + ".tif"
        dst_path = src_dir + directory + os.sep + basin + "_processed.tif"
        elevs = []
        if not os.path.isfile(src_path):
            continue
        refRaster = gdal.Open(src_path)

        SnowCover = ret_ma_array(src_path)
        for lim in lims:
            condition = (DEM < lim[0]) | (DEM >= lim[1])

            SnowCover_elev_masked = ma.masked_where(condition, SnowCover)    # Workes like charm, applies mask where condition is true
            elevs.append(SnowCover_elev_masked)
        print "[+] Writing Arrays into: " + dst_path
        addDEMBand(dst_path, refRaster, elevs)
        refRaster = None    # Closing file


if __name__ == '__main__':
    main()