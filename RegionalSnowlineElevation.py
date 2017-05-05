import numpy as np
from osgeo import gdal
import os
from matplotlib import pyplot as plt
import time


def findsnowliveelev(snowdata, demdata, step=10):
    min_elev = demdata.min()
    max_elev = demdata.max()

    elevs = []
    func = []    # Sum of Land pixels above {Elevation} and Snow pixels below {Elevation}

    for elev in range(int(min_elev), int(max_elev), step):
        landcount = np.count_nonzero((demdata > (elev-step)) & (snowdata == 25))    # count of land pixels above elev
        snowcount = np.count_nonzero((demdata <= elev) & (snowdata == 200))          # count of snow pixels below elev
        elevs.append(elev)
        func.append((float(landcount + snowcount)/(snowdata.shape[0] * snowdata.shape[1]))* 100)

    RSLE = elevs[func.index(min(func))]

    return RSLE, elevs, func

def main():
    src = "UsefulData" + os.sep

    directories = os.listdir(src)
    directories = filter(lambda x: os.path.isdir(src + x), directories)

    cloud_cover = 0

    for directory in directories[3:]:
        start = time.time()
        print "[+] Working in directory: " + directory
        dst_file = src + directory + os.sep + "Res.png"
        src_file = src + directory + os.sep + "Brahmaputra_withDEM.tif"
        try:
            im = gdal.Open(src_file)
        except Exception as e:
            print "[-] Error: " + str(e.args)
            continue
        snow_band = im.GetRasterBand(1)
        DEM_band = im.GetRasterBand(2)

        snow = snow_band.ReadAsArray()
        DEM = DEM_band.ReadAsArray()

        clouds = snow == 50
        percentage_clouds = float(np.count_nonzero(clouds)) / (snow.shape[0] * snow.shape[1])
        print "[+] Percentage Cloud: {0}%".format(percentage_clouds)
        cloud_cover += percentage_clouds

        if percentage_clouds > 0.1:
            continue

        findsnowliveelev(snow, DEM)
        print "[+] Finished working: {0}s".format(time.time() - start)

    print "[=] Mean cloud cover: " + str((cloud_cover/(len(directories)-3)))


if __name__ == "__main__":
    main()
