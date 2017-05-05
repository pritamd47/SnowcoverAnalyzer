import os
import subprocess

#-----------------------------------------------------------------------------------------------------------------------
# batch_convert_hdf2gtiff.py will convert all the .hdf files in 2 levels of hierarchy to .tif files
# Variables:
#       1. path => This is path to the folder where all the hdf files are
#       2. TranslatePath => Path to gdal_translate.exe
#       3. filename => Name of the file to convert (Here, it is the block of sinusoidal projection which corresponds to
#                      required tile)
#       4. command => The command which is passed to gdal_translate
#-----------------------------------------------------------------------------------------------------------------------

def run_command(command):
    p = subprocess.Popen(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    p.wait()
    return iter(p.stdout.readline, b'')

path = "Data" + os.sep
directories = os.listdir(path)
directories = filter(lambda x: os.path.isdir(path+x), directories)

TranslatePath = r'C:\OSGeo4W64\bin'
app = "gdal_translate.exe"
os.chdir(TranslatePath)

for directory in directories[:70]:

    path = r'F:/Projects/SnowcoverAnalyzer/Data/' + directory
    for file in os.listdir(path):

        if file in ('h24v06.hdf', 'h25v06.hdf','h25v05.hdf','h26v06.hdf','h26v05.hdf'):
            filename = file.split(".")[0]
            command = TranslatePath + os.sep + app + ' -a_nodata 0 -of GTiff HDF4_EOS:EOS_GRID:\"'+ path + '/' + filename + '.hdf\":MOD_Grid_Snow_500m:Maximum_Snow_Extent ' + path +"/"+ filename + '.tif'
            try:

                print "[+] Converting " + directory + "/" + filename
                run_command(command)
                for line in run_command(command):
                    print line
                print "[!] Converted " + directory + "/" + filename
            except Exception as e:
                print str(e.args)
                break