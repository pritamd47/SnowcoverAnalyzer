from osgeo import gdal
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import numpy as np
import os

def plot_errors(dates, percentages):
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    fig, ax = plt.subplots()
    arr = np.array(percentages)
    m = arr.max()
    arr = -(arr - m)

    avg = np.average(arr)
    median = np.median(arr)

    m_new = arr.max()

    ax.axhline(y=median, color='r', linestyle = '--', linewidth=0.5)
    ax.axhline(y=m_new, color='black', linestyle='--', linewidth=0.5)
    ax.axhline(y=avg, color = 'g', linestyle = '--', linewidth = 0.5)
    ax.plot(dates, arr, color = 'b', linewidth = 0.5)


    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)

    ax.format_xdata = mdates.DateFormatter('%Y.%m.%d')
    ax.grid(True)

    fig.autofmt_xdate()

    plt.show()

def main():
    path = "Snow_LST" + os.sep
    basin = "Brahmputra"
    time = "Night"

    directories = os.listdir(path)
    directories = filter(lambda x: os.path.isdir(path + x), directories)

    dates = []
    percentages = []

    for directory in directories:
        src = path + directory + os.sep + basin + "_LST_" + time + "_resampled.tif"
        print "[+] Working in dir: " + directory
        if not os.path.exists(src):
            continue
        im = gdal.Open(src)
        band = im.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        raster = band.ReadAsArray()

        im = None

        total_pixels = np.size(raster)
        raster[raster==nodata] = 0
        nodata_count = np.count_nonzero(raster)
        percentage = (float(nodata_count) / total_pixels) * 100
        print percentage

        percentages.append(percentage)
        dt_date = dt.datetime.strptime(directory, "%Y.%m.%d")
        dates.append(dt_date)

    plot_errors(dates, percentages)

if __name__ == "__main__":
    main()