import os
import shutil
from arcpy.sa import *
import arcpy
from numpy import ma

def MoveObsolete(srcDir, dstDir, files):
    """
    Moves obsolete files to a temp folder
    :srcDir: Source directory
    :dstDir: Destination directory.
    :files: List of file names that are to be moved
    """

    if not os.path.exists(dstDir):
        os.mkdir(dstDir)

    for f in files:
        src = srcDir + os.sep + f
        dst = dstDir + os.sep + f
        if os.path.exists(src):
            print "[+] Moving file: ", src, " -> ", dst
            shutil.move(src, dst)
            print "[!] Moved file successfully"
        else:
            print "[-] File ", f, " not present"

def fixTemp(src, dst):
    res = Raster(src) * 0.02 - 273
    try:
        res.save(dst)
    except Exception as e:
        print "[-] Error: ", e.args

def main():
    path = "UsefulData" + os.sep

    dstRoot = "ObsoleteData" + os.sep
    directories = os.listdir(path)
    directories = filter(lambda x: os.path.isdir(path + x), directories)

    # files = ["Brahmaputra_composite_Day.tif",
    #          "Brahmaputra_composite_Night.tif",
    #          "Brahmaputra_processed.tif",
    #          "Brahmaputra_withDEM.tif",
    #          "Indus_composite_Day.tif",
    #          "Indus_composite_Night.tif",
    #          "UpperGanga_composite_Day.tif",
    #          "UpperGanga_composite_Night.tif",
    #          "Brahmputra_LST_Day.tif",
    #          "Brahmputra_LST_Night.tif",
    #          "Indus_LST_Day.tif",
    #          "Indus_LST_Night.tif",
    #          "Lower_Ganga_LST_Day.tif",
    #          "Lower_Ganga_LST_Night.tif",
    #          "Upper_Ganga_LST_Day.tif",
    #          "Upper_Ganga_LST_Night.tif"]

    files = [
        "Brahmputra_LST_Day",
        "Brahmputra_LST_Night",
        "Indus_LST_Day",
        "Indus_LST_Night",
        "Lower_Ganga_LST_Day",
        "Lower_Ganga_LST_Night",
        "Upper_Ganga_LST_Day",
        "Upper_Ganga_LST_Night"
    ]

    arcpy.env.workspace = r"H:\Projects\SnowcoverAnalyzer\TempWS"
    arcpy.geoprocessing.env.overwriteOutput = True

    i = 495
    for directory in directories[495:]:
        print "[+] Working in Dir: ", directory, i
        i+=1
        for f in files:
            src = path + directory + os.sep + f + "_resampled.tif"
            dst = path + directory + os.sep + f + ".tif"
            if not os.path.exists(src):
                print "[-] ERROR: File not found", src
                continue
            try:
                fixTemp(src, dst)
            except Exception as e:
                print "[-] ERROR: ", e.args
                continue

    #    MoveObsolete(srcDir, dstDir, files)


if __name__ == "__main__":
    main()