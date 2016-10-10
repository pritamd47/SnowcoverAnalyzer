import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from datetime import datetime
from threading import Thread, activeCount
import collections
import Queue
from pyhdf.SD import SD
from pyhdf import error
import os
import time

def analyzer(directories, isitathread=False, filename = None, outfile = None):
    global date, snowcov
    date = []
    snowcov = []
    cloudcov = []
    for i in range(len(directories)):
        dirstart = time.time()
        try:
            hdffile = SD(directories[i] + os.sep + filename)
        except error.HDF4Error as e:
            print "[-] Error: " + str(e.args)
            continue
        DATASET_NAME = "Maximum_Snow_Extent"
        data_mesh = hdffile.select(DATASET_NAME)

        print "[+] Working on {0}".format(directories[i])
        data = data_mesh[:, :].astype(np.int32)  # This is stored in array form
        snow = 0
        cloud = 0

        condition = lambda x: True if x in (100, 200) else False

        unique, counts = np.unique(data, return_counts=True)
        values = dict(zip(unique, counts))
        snow = values.get(100, 0) + values.get(100, 0)
        cloud = values.get(100, 0)
        # for i_loc in range(data.shape[0]):
        #     for j_loc in range(data.shape[1]):
        #         if data[i_loc, j_loc] in {100, 200}:
        #             snow += 1
        #         elif data[i_loc, j_loc] == 50:
        #             cloud += 1
        snow = (snow / 5670000.0) * 100
        cloud = (cloud / 5670000.0) * 100
        snowcov.append(snow)
        cloudcov.append(cloud)
        date.append(directories[i])

        if not outfile == None and not isitathread:
            outfile.write("{0},{1},{2}\n".format(date[-1], snow, cloud))

        print "[+] Finished working in directory with result {0}".format(snowcov[-1])
        print "[!] Time taken: {0}".format(time.time() - dirstart)

    if isitathread:
        global dat_queue
        dat_queue = Queue.Queue()
        l = len(snowcov)
        for i in range(l):
            dat_queue.put((date[i], snowcov[i]))


def threadhandler(directories, dirperthread = 20):    # dirperthread = Directories per thread
    length = len(directories)
    global dat_queue
    dat_queue = Queue.Queue()
    i = 0
    dirranges = []
    while i <= length:
        dirranges.append((i, i+dirperthread))
        i += dirperthread

    #for dirs in dirranges:
    t = Thread(target=analyzer, args=(directories[dirranges[0][0]:dirranges[0][1]], True, None))
    t.start()

    while activeCount() > 1:
        continue

    dat_list = []
    while dat_queue.qsize() > 0:
        dat_list.append(dat_queue.get())

    return list(sorted(list(dat_list)))

def visualize(infile):
    # Reading data
    convert_datetime = lambda x: datetime.strptime(str(x), "%Y.%m.%d")
    data = np.genfromtxt(infile, delimiter=",", dtype=[('x', datetime), ('y', np.float)], converters = {0: convert_datetime})

    # showing graphs
    years = YearLocator()
    months = MonthLocator()
    yearsFmt = DateFormatter("%Y")

    fig , ax1 = plt.subplots()
    ax1.plot_date(data['x'], data['y'],'-', linestyle = 'solid', color = 'r', linewidth = 0.5, fillstyle='bottom')
    ax1.xaxis.set_major_locator(years)
    ax1.xaxis.set_major_formatter(yearsFmt)
    ax1.xaxis.set_minor_locator(months)
    ax1.autoscale_view()
    ax1.grid(True)

    plt.xlabel("Years")
    plt.ylabel("Percentage snow cover over h24v06")
    fig.autofmt_xdate()
    plt.show()

def main():
    path = "Data" + os.sep
    filename = "h26v06"
    directories = os.listdir(path)
    directories = filter(lambda x: os.path.isdir(path+x), directories)

    os.chdir(path)        # Changed directory to Path
    os.getcwd()

    outfile = open("data_"+filename+".csv", "w")
    analyzer(directories[:], filename = filename+".hdf", outfile=outfile)
    outfile.close()

    infile = open("data_"+filename+".csv", "r")
    visualize(infile)
    infile.close()
    # MODIS data must be citied!

if __name__ == '__main__':
    main()