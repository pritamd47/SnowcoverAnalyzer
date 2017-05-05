import os
from osgeo import gdal
import numpy as np
from matplotlib import pyplot as plt


def saveLike(refRaster, array, dst):
    yPx, xPx = array.shape
    Raster = refRaster #gdal.Open(refRaster, gdal.GA_ReadOnly)
    band = Raster.GetRasterBand(1)

    geotransform = Raster.GetGeoTransform()
    sr = Raster.GetProjection()
    print "[+] Saving in: ", dst
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(
        dst,
        xPx,
        yPx,
        1,
        gdal.GDT_Float32
    )

    nodata = -9999.0
    nonMAarray = array.filled(nodata)

    dataset.SetGeoTransform(geotransform)
    dataset.SetProjection(sr)
    dataset.GetRasterBand(1).WriteArray(nonMAarray)
    dataset.GetRasterBand(1).SetNoDataValue(nodata)
    dataset.FlushCache()

def createMasked(rasterPath, bandNo):
    raster = gdal.Open(rasterPath)
    band = raster.GetRasterBand(bandNo)

    arr = band.ReadAsArray()
    nodata = band.GetNoDataValue()
    mask = arr == nodata
    errorCells = np.count_nonzero(mask)
    error = (errorCells / float(mask.size)) * 100.0

    maArr = np.ma.masked_array(arr, mask, float)

    return maArr, error

def createAvgRaster(filePaths, dst):
    refRaster, _ = createMasked(filePaths[0], 1)
    dem, _ = createMasked(filePaths[0], 3)
    refRasterGDAL = gdal.Open(filePaths[0])
    count = np.zeros_like(refRaster, float)

    for filename in filePaths:
        raster, error = createMasked(filename, 1)
        print "[+] ", filename

        snowMask = (raster == 200) | ((raster == 50) & (dem > 3500))
        count += snowMask

    totalfiles = len(filePaths)
    reqCount = 0.60 * totalfiles

    res = count.filled(0) > reqCount
    res_zeros = np.zeros(res.shape)
    np.place(res_zeros, res, [200])
    print res_zeros
    res = np.ma.masked_values(res_zeros, 0)

    saveLike(refRasterGDAL, res, dst)


def handleRasters(path):
    basins = [
        #"Indus",
        "Brahmaputra",
        "UpperGanga"
    ]
    time = ["Day"]

    dataPath = path + "UsefulData" + os.sep
    directories = os.listdir(dataPath)
    directories = filter(lambda x: os.path.isdir(dataPath+x), directories)

    for basin in basins:
        for t in time:

            files = []
            for directory in directories:
                src = path + "UsefulData" + os.sep + directory + os.sep + "_".join((basin, t, "composite.tif"))
                if os.path.exists(src):
                    files.append(src)
                    print "[!] ", src

            dst = path + "Results\\" + basin + "_" + t + "_snowAvg.tif"
            createAvgRaster(files, dst)

def main():
    path = r"H:\Projects\SnowcoverAnalyzer" + os.sep
    handleRasters(path)

if __name__ == "__main__":
    main()