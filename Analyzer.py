import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from datetime import datetime
import os
import time


def counterror(raster, percentage = True):
    global snow_area
    ysnow, xsnow = np.where(raster == 100)
    for i in range(xsnow.shape[0]):
        coords = (ysnow[i], xsnow[i])
        snow_area[coords] = True

    ycloud, xcloud = np.where(raster == 50)
    errtile = 0
    for i in range(xcloud.shape[0]):
        coords = (ycloud[i], xcloud[i])
        if snow_area[coords]:
            errtile += 1

    if percentage:
        return (errtile / 5670000.0) * 100

    return errtile * 0.214658673298

def ret_area(raster):
    '''

    :param raster: Numpy array
    :return: area of basin
    '''
    nodatatiles = np.count_nonzero(raster)
    totalarea = raster.shape[0] * raster.shape[1]

    return totalarea - nodatatiles

def count(raster, percentage = True):
    # From here counting of snow area is done
    '''
    :param raster: array of mod10a2
    :param percentage: to write in form of percentage or only area
    :return: returns either percentage of snow cover or area of snow cover (km2)
    '''
    area =  ret_area(raster)
    unique, counts = np.unique(raster, return_counts=True)
    values = dict(zip(unique, counts))

    snow = values.get(100, 0) + values.get(200, 0)

    if percentage:
        snow = (snow / area) * 100
        return snow
    # counting finished

    return snow * 0.214658673298

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

def analyze(directories, outputfilename, filename, percentage = True):
    global snow_area
    tempraster = readimage(directories[100] + os.sep + filename)
    snow_area = np.full(tempraster.shape, False)

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

            error = counterror(raster, percentage)
            snow = count(raster, percentage)
            print "[+] Printing data to file: {0} {1} {2}".format(directory, snow, error)
            outputfile.write("{directory},{snow},{error}\n".format(directory=directory, snow=snow, error=error))
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
        analyze(directories,outputfile, filename, percentage=False)
        print "[!] Total time taken: " + str(time.time() - start)

        os.chdir('..')

    #minivisualize(outputfile, "Upper Ganga")

if __name__ == '__main__':
    main()