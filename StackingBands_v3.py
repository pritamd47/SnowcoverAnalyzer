# Run this file inside arcgis

import arcpy
import os
import logging
from sys import argv

arcpy.env.workspace = r"H:\Projects\SnowcoverAnalyzer\UsefulData"
arcpy.env.overwriteOutput = True

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

srcdir = r"H:\Projects\SnowcoverAnalyzer\UsefulData" + os.sep
directories = os.listdir(srcdir)
directories = filter(lambda x: os.path.isdir(srcdir + x), directories)

DEMbasin = [r"H:\Projects\SnowcoverAnalyzer\DEM\Brahmaputra\Brahmaputra_lowres_sinu.tif",
            r"H:\Projects\SnowcoverAnalyzer\DEM\Indus\Indus_lowres_sinu.tif",
            r"H:\Projects\SnowcoverAnalyzer\DEM\UpperGanga\UpperGanga_lowres_sinu.tif"]
Snowbasin = ["Brahmaputra", "Indus", "UpperGanga"]
LSTbasin = ["Brahmputra", "Indus", "Upper_Ganga"]

missingDIR = set()

dirind = 0

for directory in directories:
    for index in range(3):         # selecting basin
        for time in ("Day", "Night"):
            skp_exec = 0            # Set to 1 if current iteration to be skipped
            logger.info(": ".join(("[+] Working with", directory, str(dirind), DEMbasin[index], time)))
            b1 = srcdir + directory + os.sep + Snowbasin[index] + ".tif"
            b2 = srcdir + directory + os.sep + LSTbasin[index] + "_LST_" + time + ".tif"
            b3 = DEMbasin[index]

            dst = srcdir + directory + os.sep + Snowbasin[index] + "_" + time + "_composite.tif"

            if not os.path.exists(b1):
                logger.warning(": ".join(("FILE MISSING", b1)))
                missingDIR.add(directory)
                skp_exec = 1

            if not os.path.exists(b2):
                logger.warning(": ".join(("FILE MISSING", b2)))
                missingDIR.add(directory)
                skp_exec = 1

            if skp_exec:
                logger.warning(": ".join(("Skipping directory", directory)))
                continue

            try:
                s = ";".join((b1,b2,b3))
                inRast = [b1, b2, b3]
                logger.info(": ".join(("String", s, dst)))
                arcpy.CompositeBands_management(inRast, dst)
                logger.info(": ".join(("File created", dst)))
            except Exception as e:
                logger.error("Error compositing bands: %s", e, exc_info=1)
    dirind += 1

