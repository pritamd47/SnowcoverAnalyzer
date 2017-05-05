"""
This code can only be ran inside QGis, due to some dumb restrictions -_-
"""


from qgis.core import *
from qgis.analysis import *
from PyQt4.QtCore import *
import os

def resample_lst(lst, snow, dst):
    lst_fileInfo = QFileInfo(lst)
    lst_baseName = lst_fileInfo.baseName()
    lst_layer = QgsRasterLayer(lst, lst_baseName)

    snow_fileInfo = QFileInfo(snow)
    snow_baseName = snow_fileInfo.baseName()
    snow_layer = QgsRasterLayer(snow, snow_baseName)

    entries = []

    # Define reference raster
    ref = QgsRasterCalculatorEntry()
    ref.ref = 'snow@1'
    ref.raster = snow_layer
    ref.bandNumber = 1
    entries.append(ref)

    # Define LST raster
    temp = QgsRasterCalculatorEntry()
    temp.ref = 'lst@1'
    temp.raster = lst_layer
    temp.bandNumber = 1
    entries.append(temp)
    print "[+] Resampling.."
    calc = QgsRasterCalculator('lst@1', dst, 'GTiff', snow_layer.extent(), snow_layer.crs(), snow_layer.width(), snow_layer.height(), entries)
    calc.processCalculation()
    print "[+] Successfully resampled"

def main():
    print "here"
    snow = r"F:\Projects\SnowcoverAnalyzer\UsefulData\{date}\{basin}.tif"
    lst = r"F:\Projects\SnowcoverAnalyzer\Snow_LST\{date}\{basin}_LST_{time}.tif"
    dst = r"F:\Projects\SnowcoverAnalyzer\Snow_LST\{date}\{basin}_LST_{time}_resampled.tif"
    
    path = r"F:\Projects\SnowcoverAnalyzer\Snow_LST" + os.sep
    directories = os.listdir(path)
    directories = filter(lambda x: os.path.isdir(path+x), directories)
    
    # Variables
    basin_lst = ("Indus","Indus"), ("Upper_Ganga", "UpperGanga"), ("Lower_Ganga", "LowerGanga")
    time = ("Day", "Night")
    
    for directory in directories[0:2]:
        for b in basin_lst:
            for t in time:
                snow_param = snow.format(date = directory, basin=b[1])
                lst_param = lst.format(date = directory, basin = b[0], time = t)
                dst_param = dst.format(date=directory, basin = b[0], time = t)

                print "[+] Working in: {0} ->{2}-> {1}".format(directory, t, b)
                try:
                    resample_lst(lst_param, snow_param, dst_param)
                except Exception as e:
                    print "[-] Something went wrong: " + str(e.args)
                    break

main()