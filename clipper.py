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

    basin = "Brahmaputra"
    shapefilepath = r'F:\Projects\SnowcoverAnalyzer\Basinss\{0}.shp'.format(basin.upper())  #
    inputfile = r'Brahmaputra_SRTM_Sinu_full.tif'                        #   Change these variables to clip and finalize
    outputfile = r'Indus.tif'                                            #
    inputpixelsize = '463.312716528'   # extracted from qgis; Dont change
    directories = os.listdir(localpath)
    directories = filter(lambda x: os.path.isdir(localpath+x), directories)

    for directory in directories[50:56]:
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
            command = "gdalwarp -dstnodata 25 -q -cutline " + shapefilepath + " -crop_to_cutline -of GTiff " + inputfilepath + " " + outputfilepath
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