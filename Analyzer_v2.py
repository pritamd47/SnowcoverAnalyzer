from matplotlib import pyplot as plt
from osgeo import gdal
import os
from numpy import ma
import RegionalSnowlineElevation
import numpy as np
import logging
from sys import argv


# Setting up logger
logger = logging.getLogger(argv[0].split('/')[-1])
logger.setLevel(logging.DEBUG)

# File handler
fh = logging.FileHandler(r'Logs/' + logger.name + '.log', mode = 'a')
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


def ret_ma_array(array):
    nodata = array[0,0]     # First value is nodata for all the basins
    # Load as array
    raster = array
    masked_raster = ma.masked_values(raster, nodata, copy=False)
    masked_raster.fill_value = nodata

    return masked_raster

def dumpDeepResults(Snow, LST, DEM, dst, step = 100):
    #outFile = open(dst, mode='w')
    minElev = 0
    maxElev = int(DEM.max())

    logger.info("Opening file: "+ dst)
    csvFile = open(dst, mode='w')
    header = ','.join((
        'lowElev',
        'highElev',
        'RSLE',
        'totalPixels',
        'snowPixels',
        'landPixels',
        'cloudPixels',
        'totalLSTPixels',
        'minimumLST',
        'maximumLST',
        'missingLST'
    ))
    csvFile.write(header + "\n")

    #logger.info("Calculating RSLE")
    #RSLE = RegionalSnowlineElevation.findsnowliveelev(Snow, DEM, step=10)[0]
    RSLE = np.nan
    #logger.info("RSLE: " + str(RSLE))

    for elev in range(minElev, maxElev + 1, step):
        lowElev = elev                  # Lower limit elevation
        highElev = elev + step          # Higher limit elevation

        mask = (DEM >= lowElev) & (DEM < highElev)      # Mask according to elevation

        req_LST_mask = LST == mask                      # np.ma object, required LST mask (note: mask, not array)
        req_LST_mask[mask] = True
        req_LST = LST[mask]                             # required LST array / Raster
        req_Snow = Snow[mask]                           # required Snow array / Raster

        totalPixels = int(req_Snow.shape[0])            # Total pixels in elevation ranfe
        snowPixels = np.count_nonzero(req_Snow == 200)  # Total pixels categorized as Snow
        landPixels = np.count_nonzero(req_Snow == 25)   # Total pixels categorized as Land
        cloudPixels = np.count_nonzero(req_Snow == 50)  # Total pixels categorized as Cloud

        totalLSTPixels = np.size(req_LST)               # Total LST pixels in elevation range
        if totalLSTPixels == 0:
            minimumLST = np.nan
            maximumLST = np.nan
        else:
            minimumLST = np.min(req_LST)                # Min LST
            maximumLST = np.max(req_LST)                # Max LST


        arrDiff = mask != req_LST_mask
        missingLST = np.count_nonzero(arrDiff)          # For some reason, the missing LST has a base maximum value.
                                                        # In image form, it is seen that there are some extra pixels classified as TRUE in arrDiff
                                                        # To get correct number of missing data, just subtract the value from maximum base missing values seen that day
        res = (
            lowElev,
            highElev,
            RSLE,
            totalPixels,
            snowPixels,
            landPixels,
            cloudPixels,
            totalLSTPixels,
            minimumLST,
            maximumLST,
            missingLST
        )
        resString = ','.join(str(x) for x in res)

        csvFile.write(resString + "\n")

    logger.info("Writing to file complete")
    csvFile.close()


def main():
    srcdir = "UsefulData" + os.sep
    basins = (
        "Brahmaputra",
        "Indus",
        "UpperGanga"
    )
    times = ("Day", "Night")
    dstdir = "Results" + os.sep + "DeepRes" + os.sep

    directories = os.listdir(srcdir)
    directories = filter(lambda x: os.path.isdir(srcdir + x), directories)

    i = 350

    for directory in directories[350:]:
        for basin in basins:
            for time in times:
                logger.info("Working in directory: " + directory + ", " + str(i) )
                src = srcdir + directory + os.sep + basin + "_" + time + "_composite" + ".tif"
                if not os.path.exists(src):
                    logger.error("File not present: " + src)
                    continue
                dst = dstdir + directory + os.sep

                # Create directory if it doesn't exist
                if not os.path.isdir(dst):
                    logger.info("Making directory" + dst)
                    os.mkdir(dst)

                dstCSV = dst + basin + "_" + time + ".csv"

                composite_im = gdal.Open(src)

                try:
                    Snow = composite_im.GetRasterBand(1)
                    LST = composite_im.GetRasterBand(2)
                    DEM = composite_im.GetRasterBand(3)

                except Exception as e:
                    logger.error("ERROR: " + str(e.args))
                    continue

                if not (Snow == None or LST == None or DEM == None):
                    SnowRaster = ret_ma_array(Snow.ReadAsArray())
                    LSTRaster = ret_ma_array(LST.ReadAsArray())
                    DEMRaster = ret_ma_array(DEM.ReadAsArray())

                    logger.info("Dumping results of dir: " + directory)
                    dumpDeepResults(SnowRaster, LSTRaster, DEMRaster, dstCSV)
                else:
                    if Snow == None:
                        logger.error("Band missing: Snow")
                    if LST == None:
                        logger.error("Band missing: LST")
        i += 1

if __name__ == "__main__":
    main()