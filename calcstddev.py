import numpy as np
import os
from osgeo import gdal
from matplotlib import pyplot as plt

path = "H:\\Projects\\SnowcoverAnalyzer\\"

def saveLike(refRaster, array, dst):
    yPx, xPx = array.shape
    Raster = gdal.Open(refRaster, gdal.GA_ReadOnly)
    band = Raster.GetRasterBand(1)

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

    dataset.SetGeoTransform((geotransform))
    dataset.SetProjection(sr)
    dataset.GetRasterBand(1).WriteArray(nonMAarray)
    dataset.GetRasterBand(1).SetNoDataValue(nodata)
    dataset.FlushCache()

def createMasked(rasterPath):
    raster = gdal.Open(rasterPath)
    band = raster.GetRasterBand(1)

    arr = band.ReadAsArray()
    nodata = band.GetNoDataValue()
    mask = arr == nodata
    errorCells = np.count_nonzero(mask)
    error = (errorCells / float(mask.size)) * 100.0

    maArr = np.ma.masked_array(arr, mask, float)

    return maArr, error

def calcStats(inRasters, dst):
    # try:
    #     dev = CellStatistics(inRasters, "MEAN", "DATA")
    # except Exception as e:
    #     raise e
    # dev.save(dst)



    refRaster = gdal.Open(inRasters[0])
    arr = refRaster.ReadAsArray()

    sumFactor = np.zeros_like(arr, float)
    dividingFactor = sumFactor

    errorThreshold = 75.0    # About 5% missing data

    for raster in inRasters:
        currRaster, error = createMasked(raster)

        print raster, ": ", error
        # plt.imshow(currRaster)
        # plt.show()

        if error > errorThreshold:
            print "[-] Too much missing data: ", error - 71               # 76% is the optimum / 100% data
            continue
        elif not sumFactor.shape == currRaster.shape:
            print "[-] Different shapes"
            continue
        else:
            mask = np.ma.getmask(currRaster)
            sumFactor = sumFactor + currRaster.filled(0)
            dividingFactor = dividingFactor + np.ma.masked_array(np.ones_like(dividingFactor), mask=mask).filled(0)

    dividingFactorMasked = np.ma.masked_values(dividingFactor, 0)
    sumFactorMasked = np.ma.masked_values(sumFactor, 0)

    resArr = sumFactorMasked / dividingFactorMasked

    saveLike(inRasters[0], resArr, dst)

def main():
    dataPath = path + "UsefulData" + os.sep
    directories = os.listdir(dataPath)
    directories = filter(lambda x: os.path.isdir(dataPath + x), directories)

    files = [
        "Brahmputra_LST_Day.tif",
        "Brahmputra_LST_Night.tif",
        "Indus_LST_Day.tif",
        "Indus_LST_Night.tif",
        "Upper_Ganga_LST_Day.tif"
    ]

    # monthNames = [
    #     "Jan",
    #     "Feb",
    #     "March",
    #     "April",
    #     "May",
    #     "June",
    #     "July",
    #     "Aug",
    #     "Sept",
    #     "Oct",
    #     "Nov",
    #     "Dec"
    # ]


    sources = []
    # currentMonth = directories[0].split(".")[1]

    f = files[4]

    for directory in directories:
        srcDir = dataPath + directory + os.sep
        src = srcDir + f

        if not os.path.exists(src):
            print "[-] Missing data: ", directory + "/" + f
            continue

        sources.append(src)
        print "[!] src: ", src

    dst = path + "Results" + os.sep + f + "_gdalMean.tif"
    print "[+] Calculating stats\n\n\n"
    calcStats(sources, dst)

    sources = []

        # year, month, day = directory.split(".")
        # monthName = monthNames[int(currentMonth) - 1]
        #
        #
        #
        # if month == currentMonth:
        #     srcFile = path +"UsefulData" + os.sep + directory + os.sep + f
        #     if os.path.exists(srcFile):                         # If srcFile exists, append srcFile
        #         sources.append(srcFile)
        #         print "[!]", srcFile
        #     else:
        #         print "[-] File doesn't exist: ", srcFile
        # else:
        #     print "[+] Calculating statistics for month: ", monthName
        #     yearPath = path + "Results" + os.sep + "StdDev_new" + os.sep + year
        #     if not os.path.exists(yearPath):
        #         os.mkdir(yearPath)
        #     monthPath = yearPath + "_" + monthName
        #     if not os.path.exists(monthPath):
        #         os.mkdir(monthPath)
        #     dst = monthPath + os.sep + f.split(".")[0] +"_std.tif"
        #     try:
        #         calcStats(sources, dst)
        #         print "[+] Calculated mean successfully: ", dst            # calculate statistics for the rasters
        #     except Exception as e:
        #         print "[-] Error: ", e.args
        #
        #     currentMonth = month
        #     srcFile = path + "UsefulData" + os.sep + directory + os.sep + f
        #     if os.path.exists(srcFile):
        #         sources = [srcFile]                             # Add the file where the execution stopped if it exists
        #     else:
        #         print "[-] File doesn't exist: ", srcFile
        #         sources = []



if __name__ == "__main__":
    main()