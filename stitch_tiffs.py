import os
import sys
sys.path.append(r'C:\OSGeo4W64\bin')

import gdal_merge

path = "Data" + os.sep
directories = os.listdir(path)
directories = filter(lambda x: os.path.isdir(path+x), directories)
outputfile = 'Brahmaputra_uncut.tif'
os.chdir(path)

for directory in directories[:52]:
    workspace = directory + os.sep
    os.chdir(workspace)
    files = os.listdir(os.getcwd())
    sys.argv[1:] = ['-n','0','-o', outputfile]
    if 'h26v06.tif' in files:
        sys.argv.append('h24v06.tif')
    if 'h25v06.tif' in files:
        sys.argv.append('h25v06.tif')
    if len(sys.argv) < 6:
        sys.argv.append('FILENOTFOUND.intentionalerror')
    print sys.argv
    try:
        print "[+] Current directory: " + directory
        gdal_merge.main()

    except Exception as e:
        print "[-] ERROR: " + str(e.args)

    os.chdir('..')
