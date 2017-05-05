import subprocess
import os


def run_command(command):
    p = subprocess.Popen(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    p.wait()
    return iter(p.stdout.readline, b'')

def StackBands(merge_path, Snow, LST, DEM, Dest):
    command = "python " + merge_path + os.sep + "gdal_merge.py -seperate -of GTiff -ot Int32 -o " + Dest + " " + Snow + " "\
                + LST + " " + DEM

    for response in run_command(command):
        print "[+] \t" + response

def main():
    path = "UsefulData" + os.sep
    directories = os.listdir(path)
    directories = filter(lambda x: os.path.isdir(path + x), directories)

    merge_path = "C:\\OSGeo4W64\\bin"
    DEM = r"H:\Projects\SnowcoverAnalyzer\DEM\Brahmaputra_lowres_sinu.tif"

    time = ("Day", "Night")

    for directory in directories[0:1]:
        for t in time:
            print directory
            #input()
            Dest = path + "{0}\\Brahmaputra_composite_{1}.tif".format(directory, t)
            Snow = path + "{0}\\Brahmaputra.tif".format(directory)
            LST = path + "{0}\\Brahmaputra_LST_{1}_resampled.tif".format(directory, t)

            if not (os.path.isfile(Snow) or os.path.isfile(LST)):
                print "[-] File not found"
                continue

            print "[+] Working with {0} data in {1}".format(t.upper(), directory)

            StackBands(merge_path, Snow, LST, DEM, Dest)

if __name__ == "__main__":
    main()