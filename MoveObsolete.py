import os
import shutil
import logging
from sys import argv


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

def moveMetadata(srcDir, dstDir, exts):
    files = os.listdir(srcDir)

    for f in files:
        for ext in exts:
            if ext in f:
                src = srcDir + os.sep + f
                dst = dstDir + os.sep + f
                logger.info("Moving file: " + src + "->" + dst)
                shutil.move(src, dst)


def MoveObsolete(srcDir, dstDir, files):
    """
    Moves obsolete files to a temp folder
    :srcDir: Source directory
    :dstDir: Destination directory.
    :files: List of file names that are to be moved
    """

    if not os.path.exists(dstDir):
        os.mkdir(dstDir)

    # exts = [
    #     ".tfw",
    #     ".xml",
    #     ".ovr"
    # ]
    # moveMetadata(srcDir, dstDir, exts)

    for f in files:
        src = srcDir + os.sep + f
        dst = dstDir + os.sep + f
        if os.path.exists(src):
            logger.info("Moving file: " + src + "->" + dst)
            shutil.move(src, dst)
            logger.info("Moved file successfully")
        else:
            logger.warning("File not present: " + f)

def main():
    path = "ObsoleteData" + os.sep

    dstRoot = "UsefulData" + os.sep
    directories = os.listdir(path)
    directories = filter(lambda x: os.path.isdir(path + x), directories)

    # files = ["Brahmaputra_composite_Day.tif",
    #          "Brahmaputra_composite_Night.tif",
    #          "Brahmaputra_processed.tif",
    #          "Brahmaputra_withDEM.tif",
    #          "Indus_composite_Day.tif",
    #          "Indus_composite_Night.tif",
    #          "UpperGanga_composite_Day.tif",
    #          "UpperGanga_composite_Night.tif",            Old files
    #          "Brahmputra_LST_Day.tif",
    #          "Brahmputra_LST_Night.tif",
    #          "Indus_LST_Day.tif",
    #          "Indus_LST_Night.tif",
    #          "LowerGanga_LST_Day.tif",
    #          "LowerGanga_LST_Night.tif",
    #          "UpperGanga_LST_Day.tif",
    #          "UpperGanga_LST_Night.tif"]

    files = [
        "Brahmputra_LST_Day.tif",
        "Brahmputra_LST_Night.tif",
        "Indus_LST_Day.tif",
        "Indus_LST_Night.tif",
        "Lower_Ganga_LST_Day.tif",
        "Lower_Ganga_LST_Night.tif",
        "Upper_Ganga_LST_Day.tif",
        "Upper_Ganga_LST_Night.tif",
    ]
    i = 0

    for directory in directories:
        logger.info("Working in dir: " + directory + ": " + str(i))
        i+=1

        srcDir = path + directory
        dstDir = dstRoot + directory

        MoveObsolete(srcDir, dstDir, files)

if __name__ == '__main__':
    main()