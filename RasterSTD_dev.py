#!C:/Anaconda_32bit/

import os
from sys import path, argv
import numpy as np

p = ['C:\\Python27\\ArcGIS10.2\\lib\\site-packages\\setuptools-18.1-py2.7.egg',
 u'c:\\program files (x86)\\arcgis\\desktop10.2\\arcpy',
 'C:\\Python27\\ArcGIS10.2\\lib\\site-packages\\pip-7.1.0-py2.7.egg',
 'C:\\WINDOWS\\SYSTEM32\\python27.zip',
 'C:\\Anaconda2\\Lib',
 'C:\\Anaconda2\\DLLs',
 'C:\\Python27\\ArcGIS10.2\\Lib',
 'C:\\Python27\\ArcGIS10.2\\DLLs',
 'C:\\Python27\\ArcGIS10.2\\Lib\\lib-tk',
 'C:\\WINDOWS\\system32',
 'C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\bin',
 'C:\\Python27\\ArcGIS10.2',
 'C:\\Python27\\ArcGIS10.2\\lib\\site-packages',
 'C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\arcpy',
 'C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\ArcToolbox\\Scripts']

path.extend(p)

import arcpy
from arcpy.sa import *
import logging

arcpy.env.workspace = "H:\\Projects\\SnowcoverAnalyzer\\arcpyWorkspace" + os.sep
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")


# Setting up logger
logger = logging.getLogger(argv[0].split('/')[-1])
logger.setLevel(logging.DEBUG)

# File handler
fh = logging.FileHandler(r'Logs/' + logger.name + '.log')
fh.setLevel(logging.DEBUG)

# Console Handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Formatter
fileFormatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
fh.setFormatter(fileFormatter)

chFormatter = logging.Formatter('%(levelname)s: %(message)s')
ch.setFormatter(chFormatter)

logger.addHandler(fh)
logger.addHandler(ch)

logger.info("----------------NEW RUN----------------")

def calcmean(inputRaster, dst):
    """
    Calculates the mean of given number of rasters in inputRaster keeping in account missing data
    :param refRaster:
    :param inputRaster:
    :param dst:
    :return:
    """
    read = False
    for raster in inputRaster:
        try:
            refRaster = arcpy.Raster(raster)
            read = True
            break
        except:
            continue

    if not read:
        raise

    desc = arcpy.Describe(refRaster)

    cell_size = desc.children[0].meanCellHeight
    extent = desc.children[0].extent
    nodata = desc.children[0].noDataValue
    sr = desc.SpatialReference

    temp = CreateConstantRaster(0, cell_size=cell_size, extent=extent)
    dividingFactor = arcpy.RasterToNumPyArray(temp)
    dividingFactor = np.array(dividingFactor, dtype=np.float)
    sumRaster = dividingFactor
    dividingFactor = dividingFactor + 1

    for raster in inputRaster:
        logger.info("Raster: " + raster)

        if not os.path.exists(raster):
            logger.error("File doesn't exist: " + raster)
            continue

        raster = arcpy.Raster(raster)

        desc = arcpy.Describe(raster)
        nodata = desc.children[0].noDataValue
        npRaster_nonma = arcpy.RasterToNumPyArray(raster)

        arcpy.Delete_management(raster)

        ma_mask = npRaster_nonma == nodata
        mask = npRaster_nonma > nodata
        print "1"
        npRaster = np.ma.masked_array(npRaster_nonma, mask=ma_mask, dtype=float)
        try:
            dividingFactor[mask] = dividingFactor[mask] + 1
            sumRaster = sumRaster + npRaster.filled(0.0)
        except Exception as e:
            logger.error(e.args)

    ll = Point(desc.Extent.XMin, desc.Extent.YMin)
    dividingFactor[dividingFactor == 0] = None
    if not bool(np.count_nonzero(dividingFactor)):
        logger.error("Dividing raster is empty")
        raise
    try:
        print "2"
        mean = sumRaster / dividingFactor
        del dividingFactor
        del sumRaster
    except Exception as e:
        logger.error(e.args)
        raise
    print "3"
    meanRaster = arcpy.NumPyArrayToRaster(mean, ll, cell_size, cell_size, nodata)
    del mean
    print "4"
    arcpy.DefineProjection_management(meanRaster, sr)               # Defining spatial reference
    meanRaster.save(dst)

    arcpy.Delete_management(temp)
    arcpy.Delete_management(meanRaster)
    arcpy.Delete_management(refRaster)

    return dst

def calcDev(mean, monthLST):
    meanRast = arcpy.Raster(mean)
    monthLSTRast = arcpy.Raster(monthLST)
    dev = Power((meanRast - monthLSTRast), 2)
    dev.save("Results\\Dev.tif")

def main():
    path = r"H:\Projects\SnowcoverAnalyzer\UsefulData" + os.sep
    resPath = r"H:\Projects\SnowcoverAnalyzer\Results" + os.sep + "StdDev" + os.sep

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

    directories = os.listdir(path)
    directories = filter(lambda x: os.path.isdir(path + x), directories)

    f = ["Brahmputra_LST_Day.tif",
         "Brahmputra_LST_Night.tif",
         "Indus_LST_Day.tif",
         "Indus_LST_Night.tif",
         "Upper_Ganga_LST_Day.tif",
         "Upper_Ganga_LST_Night.tif"]

    # fl = f[5]
    #
    # currentMonth = None
    # monthList = None
    # lastMonth = ''
    # i = 0
    # for directory in directories[i:]:
    #     year, month, day = directory.split(".")
    #     logger.info("Working in dir: "+directory+", "+str(i))
    #
    #     if not month == currentMonth:
    #         currentMonth = month
    #         monthName = months[int(month) - 1]
    #         yearDst = resPath + year + os.sep
    #         monthDst = yearDst + lastMonth
    #
    #
    #         if not os.path.exists(yearDst):
    #             os.mkdir(yearDst)
    #         if not os.path.exists(monthDst):
    #             os.mkdir(monthDst)
    #
    #         if not monthList == None:
    #             try:
    #                 d = calcmean(monthList, monthDst + fl)
    #                 logger.info(d)
    #             except Exception as e:
    #                 logger.error(e.args)
    #                 continue
    #         filePath = path + directory + os.sep + fl
    #         if not os.path.exists(filePath):
    #             monthList = []
    #         else:
    #             monthList = [filePath]
    #
    #         lastMonth = monthName
    #     else:
    #         filePath = path + directory + os.sep + fl
    #         if os.path.exists(filePath):
    #             monthList.append(filePath)
    #
    #     i += 1



if __name__ == '__main__':
    main()