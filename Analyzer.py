import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from datetime import datetime
from threading import Thread, activeCount
import Queue
import os
import time

def count(raster, percentage = True):
    # From here counting of cloud area and snow area is done
    unique, counts = np.unique(raster, return_counts=True)
    values = dict(zip(unique, counts))
    snow = values.get(100, 0) + values.get(100, 0)
    cloud = values.get(50, 0)

    if percentage:
        snow = (snow / 5670000.0) * 100
        cloud = (cloud / 5670000.0) * 100
    # countind finished

    return snow, cloud

def minivisualize(infile, basin, percentage = True):
    # Reading data
    convert_datetime = lambda x: datetime.strptime(str(x), "%Y.%m.%d")
    data = np.genfromtxt(infile, delimiter=",", dtype=[('x', datetime), ('y', np.float), ('z', np.float)], converters = {0: convert_datetime}, skip_header=52)

    # showing graphs
    years = YearLocator()
    months = MonthLocator()
    yearsFmt = DateFormatter("%Y")

    fig , ax1 = plt.subplots(sharex=True, sharey=True)
    ax1.plot_date(data['x'], data['y'],'-', linestyle = 'solid', color = 'r', linewidth = 0.5)
    ax1.xaxis.set_major_locator(years)
    ax1.xaxis.set_major_formatter(yearsFmt)
    ax1.xaxis.set_minor_locator(months)
    ax1.autoscale_view()
    ax1.grid(True)

    ax1.plot_date(data['x'], data['z'], '-', linestyle = 'solid', color = 'b', linewidth = 0.5)

    plt.xlabel("Years")
    plt.ylabel("Percentage snow cover over " + basin)
    fig.autofmt_xdate()
    plt.show()

def readimage(path):
    from PIL import Image
    raster = Image.open(path)
    return np.array(raster)

def analyze(directories, outputfilename, filename):
    try:
        outputfile = open(outputfilename, mode='w')
        for directory in directories:
            start = time.time()
            os.chdir(directory)
            print "[+] Working in directory " + directory
            try:
                raster = readimage(filename)
            except IOError:
                print "[-] File not found"
                os.chdir('..')
                continue

            snow, cloud = count(raster)
            print "[+] Printing data to file: {0} {1} {2}".format(directory, snow, cloud)
            outputfile.write("{directory},{snow},{cloud}\n".format(directory=directory, snow=snow, cloud=cloud))
            print "[+] Time taken: {0}".format(str(time.time()-start))
            os.chdir('..')
        outputfile.close()
    except:
        raise


def main():
    path = r"Data" + os.sep
    for filename in ("Brahmaputra.tif", "Indus.tif", "UpperGanga.tif", "LowerGanga.tif"):
        outputfile = "F:\Projects\SnowcoverAnalyzer\Results" + os.sep + filename.split('.')[0] + ".csv"
        directories = os.listdir(path)
        directories = filter(lambda x: os.path.isdir(path+x), directories)

        os.chdir(path)        # Changed directory to Path
        os.getcwd()

        start = time.time()
        analyze(directories,outputfile, filename)
        print "[!] Total time taken: " + str(time.time() - start)

        os.chdir('..')

    minivisualize(outputfile, "Upper Ganga")

if __name__ == '__main__':
    main()