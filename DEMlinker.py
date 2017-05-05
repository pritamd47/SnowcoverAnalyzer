
"""
At this point, I realised, creating new files with 2 bands will take a lot of time. FML. Read the dem raster once, and try to correlate with elevation data
"""


from osgeo import gdal
import os
from numpy import ma
import math

def createMaskedArray(path):
    """
    Returns a masked array and the geotransform of the raster after reading the given raster
    :param path: Path to raster file
    :return:
        masked_raster: Raster with missing values replaced by nodata value (0)
        geotransform: Top-Left coordinate of raster and cell size
    """

    print "[+] Creating masked array for: {0}".format(path)
    dataset = gdal.Open(path)

    if dataset is None:
        raise Exception()

    # Get geotransform data { top-left point coordinates and cell size }
    geotransform = dataset.GetGeoTransform()

    # Working on the first band
    band = dataset.GetRasterBand(1)
    #Store nodata value, for masking
    nodata = band.GetNoDataValue()
    # Load as array
    raster = band.ReadAsArray(0, 0, band.XSize, band.YSize)
    # Closing database
    dataset = None
    masked_raster = ma.masked_values(raster, nodata, copy=False)
    masked_raster.fill_value = nodata
    print "[+] Returning masked raster"
    return masked_raster, geotransform

def ret_dataset(path):
    dataset = gdal.Open(path)
    return dataset

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

def addDEMBand(dstpath, mainraster, DEMarray, Snowarray):
    """
    Creates a file with path dstpath with 2 bands, DEM and snow
    :param dstpath: Output path
    :param mainraster: Raster from which metadata is to be copied
    :param DEMarray: Array containing DEM data (goes to 2nd band)
    :param Snowarray: Array containing Snoe Cover data (goes to 1st band)
    """
    print "[+] Getting metadata..."
    x_size = mainraster.RasterXSize
    y_size = mainraster.RasterYSize
    pixel_size = mainraster.GetGeoTransform()[1]
    x_origin = mainraster.GetGeoTransform()[0]
    y_origin = mainraster.GetGeoTransform()[3]
    wkt_proj = mainraster.GetProjection()

    driver = gdal.GetDriverByName("GTiff")

    dataset = driver.Create(
        dstpath,
        x_size,
        y_size,
        2,
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
    dataset.GetRasterBand(1).SetNoDataValue(0)
    dataset.GetRasterBand(1).WriteArray(ma.filled(Snowarray,0))  # First band contains MODIS Snowcover data

    dataset.GetRasterBand(2).SetNoDataValue(0)
    dataset.GetRasterBand(2).WriteArray(ma.filled(DEMarray, 0))
    dataset.FlushCache()    # Writes to file
    print "[+] File created!"

def main():
    src_dir = "UsefulData" + os.sep

    directories = os.listdir(src_dir)
    directories = filter(lambda x: os.path.isdir(src_dir + x), directories)
    directories = directories[3:]    # Hardcoded to ignore 2000 data

    basin = "Brahmaputra"

    for directory in directories[414:]:
        print "[+] Working with: {0}/{1}.tif".format(directory, basin)
        src = src_dir + directory + os.sep + basin + ".tif"
        if not os.path.isfile(src):
            continue
        dst = src_dir + directory + os.sep + basin + "_withDEM.tif"
        dem = "DEM\\Brahmaputra_lowres_sinu.tif"
        demraster, dem_gt = createMaskedArray(dem)
        mainraster = ret_dataset(src)
        snowarray, gt = createMaskedArray(src)

        addDEMBand(dst, mainraster, demraster, snowarray)
        print "[+] Finished working with: {0}/{1}.tif".format(directory, basin)
    """
    mainraster= ret_dataset("2003.08.13/Brahmaputra.tif")
    demraster, dem_gt = createMaskedArray("Brahmaputra_lowres_sinu.tif")

    snowarray, gt = createMaskedArray("2003.08.13/Brahmaputra.tif")
    demarray = linkDEM(gt, snowarray, demraster)

    dstpath = "2003.08.13/Br_withdem.tif"
    addDEMBand(dstpath, mainraster, demarray, snowarray)
    """
if __name__ == '__main__':
    main()