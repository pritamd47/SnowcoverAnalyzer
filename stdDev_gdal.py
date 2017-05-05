from osgeo import gdal
import numpy as np
import numpy.ma as ma
import os
from matplotlib import pyplot as plt

def calcDev(meanPath, tempPath, dst):
    """
    Calculates the deviation and saves in dst
    :param meanPath: path to mean raster
    :param tempPath: path to temperature raster
    :param dst: destination of deviation array
    """
    meanRaster = gdal.Open(meanPath)
    tempRaster = gdal.Open(tempPath)

    meanArray = meanRaster.ReadAsArray()
    arr = tempRaster.ReadAsArray()
    band = tempRaster.GetRasterBand(1)
    nodata = band.GetNoDataValue()

    mask = arr == nodata
    tArray = ma.masked_array(arr, mask, float)

    meanRaster = None
    tempRaster = None

    print "[+] Finding deviation: ", dst
    try:
        dev = np.square(meanArray - tArray)
        np.save(dst, dev.filled(np.nan))
    except ValueError:
        print "[-] Shapes different"

def _calcDev(meanPath, src,  dirLst, fl):
    for directory in dirLst:
        tempPath = src + directory + os.sep + fl
        dst = src + directory + os.sep + fl.split(".")[0] + "_dev.npy"

        if not os.path.exists(tempPath):
            print "[-] File not present"
            continue
        if os.path.exists(dst):
            print "[+] File already present: ", dst

        calcDev(meanPath, tempPath, dst)

def calcStdDev(f, directories, path, resPath):
    months = ["Jan",
              "Feb",
              "March",
              "April",
              "May",
              "June",
              "July",
              "Aug",
              "Sept",
              "Oct",
              "Nov",
              "Dec"]

    currentMonth = directories[0].split(".")[1]
    monthList = []

    fl = f[0]

    for directory in directories[325:]:
        year, month, date = directory.split(".")
        monthName = months[int(month) - 1]

        if month == currentMonth:
            monthList.append(directory)
        else:
            meanRaster = resPath + year + os.sep + monthName + os.sep + fl
            if not os.path.exists(meanRaster):              # check is mean raster is present
                print "Error: meanraster not present: ", year, monthName
                currentMonth = month
                monthList = [directory]
                continue
            temperatureSrc = path + directory + os.sep + fl

            _calcDev(meanRaster, path, monthList, fl)
            currentMonth = month
            monthList = [directory]

def main():
    path = r"H:\Projects\SnowcoverAnalyzer\UsefulData" + os.sep
    resPath = r"H:\Projects\SnowcoverAnalyzer\Results" + os.sep + "StdDev" + os.sep

    directories = os.listdir(path)
    directories = filter(lambda x: os.path.isdir(path + x), directories)

    f = ["Brahmputra_LST_Day.tif",
         "Brahmputra_LST_Night.tif",
         "Indus_LST_Day.tif",
         "Indus_LST_Night.tif",
         "Upper_Ganga_LST_Day.tif"]

    calcStdDev(f, directories, path, resPath)

if __name__ == '__main__':
    main()