from osgeo import gdal
import numpy as np
import os
import arcpy
from arcpy.sa import *
from matplotlib import pyplot as plt
from matplotlib import cm

def saveLike(refRaster, array, dst):
    yPx, xPx = array.shape
    Raster = gdal.Open(refRaster, gdal.GA_ReadOnly)

    geotransform = Raster.GetGeoTransform()
    sr = Raster.GetProjection()

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
    print "[+] Saving: ", dst

    dataset.SetGeoTransform((geotransform))
    dataset.SetProjection(sr)
    dataset.GetRasterBand(1).WriteArray(nonMAarray)
    dataset.GetRasterBand(1).SetNoDataValue(nodata)
    dataset.FlushCache()
    dataset = None
    del nonMAarray
    Raster = None
    print "[+] Saving successful"

def calcDev(meanRaster, monthMean, dst):
    meanRasterArr = meanRaster.ReadAsArray()
    band1 = meanRaster.GetRasterBand(1)
    nodata1 = band1.GetNoDataValue()
    monthRasterArr = monthMean.ReadAsArray()
    band2 = monthMean.GetRasterBand(1)
    nodata2 = band2.GetNoDataValue()

    meanRasterMasked = np.ma.masked_values(meanRasterArr, nodata1)
    monthRasterMasked = np.ma.masked_values(monthRasterArr, nodata2)

    if not meanRasterArr.shape == monthRasterArr.shape:
        print "[-] Inequal shapes", meanRasterArr.shape, monthRasterArr.shape
        return None

    res = monthRasterMasked - meanRasterMasked

    saveLike(meanRaster, res, dst)

def mean(stackedRasters):
    # Code here

    shp = stackedRasters[0].shape
    for raster in stackedRasters:
        if shp[0] > raster.shape[0] or shp[1] > raster.shape[1]:
            shp = raster.shape

    sumFactor = np.zeros(shp, float)
    dividingFactor = sumFactor

    for raster in stackedRasters:
        mask = np.ma.getmask(raster)[0:shp[0], 0:shp[1]]
        sumFactor = sumFactor + raster.filled(0)[0:shp[0], 0:shp[1]]
        dividingFactor = dividingFactor + np.ma.masked_array(np.ones_like(dividingFactor), mask=mask).filled(0)[:shp[0], :shp[1]]

    dividingFactorMasked = np.ma.masked_values(dividingFactor, 0)
    sumFactorMasked = np.ma.masked_values(sumFactor, 0)

    resArr = sumFactorMasked / dividingFactorMasked
    return resArr

def calcStandardDev(stackedRasters):
    print "[+] Calculating mean"
    rasterMean = mean(stackedRasters)

    dev = []                    # Deviations
    print "[+] Calculating deviations"
    for raster in stackedRasters:
        dev.append(np.ma.power(rasterMean - raster, 2))

    print "[+] Calculating standard deviations"
    stdDev = np.sqrt(mean(dev))
    return stdDev

def createMasked(rasterPath):
    raster = gdal.Open(rasterPath)
    band = raster.GetRasterBand(1)

    arr = band.ReadAsArray()
    nodata = band.GetNoDataValue()
    mask = arr == nodata
    errorCells = np.count_nonzero(mask)
    error = (errorCells / float(mask.size)) * 100.0

    maArr = np.ma.masked_array(arr, mask, float)

    band = None
    del arr
    del mask
    raster = None

    return maArr, error

def anomalyStdDev(mainDir, filename):
    directories = os.listdir(mainDir)
    directories = filter(lambda x: os.path.isdir(mainDir + x), directories)

    years = [
        '2001', '2002', '2003', '2004',
        '2005', '2006', '2007', '2008',
        '2009', '2010', '2011', '2012',
        '2013', '2014', '2015', '2016'
    ]

    files = []
    refRaster = ""
    for directory in directories:
        devPath = mainDir + directory + os.sep + filename
        if os.path.exists(devPath):
            refRaster = devPath
            maskedDev, _ = createMasked(devPath)
            files.append(maskedDev)
            print "[!] ", devPath
        else:
            print "[-] File not present: ", devPath

    dst = mainDir + os.sep + "MAIN_" + filename + "_stdOfDeviations.tif"

    std_raster = calcStandardDev(files)
    saveLike(refRaster, std_raster, dst)

def createStackedrasters(files):
    stack = []
    for f in files:
        raster, _ = createMasked(f)
        stack.append(raster)

    return stack

def main():
    stackedlayers = [
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp200507281.tif",
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp200607281.tif",
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp200707281.tif",
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp200807271.tif",
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp200907281.tif",
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp201007281.tif",
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp201107281.tif",
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp201207271.tif",
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp201307281.tif",
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp201407281.tif",
        r"C:\Users\hp\Documents\tiff_T-20170118T164159Z\tiff_T\temp201507281.tif"
    ]

    layers = createStackedrasters(stackedlayers)
    m = mean(layers)
    saveLike(stackedlayers[0], m, r"H:\mean.tif")

    # path = r"H:\Projects\SnowcoverAnalyzer\Results\StdDev_new" + os.sep
    # directories = os.listdir(path)
    # directories = filter(lambda x: os.path.isdir(path + x), directories)
    # masterMean = r"H:\Projects\SnowcoverAnalyzer\Results\Upper_Ganga_LST_Day.tif_gdalMean.tif"
    #
    # MeanRaster = gdal.Open(masterMean)
    #
    # files = [
    #     "Brahmputra_LST_Day_dev.tif",
    #     "Brahmputra_LST_Night_dev.tif",
    #     "Indus_LST_Day_dev.tif",
    #     "Indus_LST_Night_dev.tif",
    #     "Upper_Ganga_LST_Day_dev.tif"
    # ]
    #
    # for f in files:
    #     anomalyStdDev(path, f)
    #
    # for directory in directories:
    #     src = path + directory + os.sep + f
    #     if not os.path.exists(src):
    #         print "[-] File not present: ", src
    #         continue
    #     individual = f.split('_')
    #     dst = path + directory + os.sep + "_".join((individual[0], individual[1], individual[2], "dev.tif"))
    #     monthRaster = gdal.Open(src)
    #     print "[!]", src
    #     calcDev(MeanRaster, monthRaster, dst)


if __name__ == "__main__":
    main()