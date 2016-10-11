import sys
import os
import subprocess

def run_command(command):
    p = subprocess.Popen(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    p.wait()
    return iter(p.stdout.readline, b'')

def main():
    gdalwarppath = r'C:\OSGeo4W64\bin'
    localpath = r'F:\Projects\SnowcoverAnalyzer\Data\\'
    os.chdir(gdalwarppath)

    shapefilepath = r'F:\Projects\SnowcoverAnalyzer\Basinss\BRAHMPUTRA.shp'  #
    inputfile = r'Brahmaputra_uncut.tif'                                       #   Change these variables to clip and finalize
    outputfile = r'Brahmaputra.tif'                                            #
    inputpixelsize = '463.312716528'   # extracted from qgis; Dont change
    directories = os.listdir(localpath)
    directories = filter(lambda x: os.path.isdir(localpath+x), directories)

    for directory in directories[:52]:
        print "[+] Working in directory: "+ directory
        files = os.listdir(localpath+directory)
        inputfilepath = localpath + directory + os.sep + inputfile

        outputfilepath = localpath + directory + os.sep + outputfile
        command = str()

        try:
            os.remove(outputfilepath)
        except OSError:
            pass

        if inputfile in files:
            command = "gdalwarp -dstnodata 0 -q -cutline " + shapefilepath + " -crop_to_cutline -tr " + inputpixelsize + " " + inputpixelsize\
                        + " -of GTiff " + inputfilepath + " " + outputfilepath
            try:
                for line in run_command(command):
                    print line
                print "[+] Successfully finished clipping@ " + directory
            except Exception as e:
                print "[-] ERROR: " + str(e.args)
        else:
            print "[-] Not found@ " + directory

if __name__ == '__main__':
    main()