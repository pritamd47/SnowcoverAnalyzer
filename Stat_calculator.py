from Visualise import visualize   #Local file
import numpy as np
from datetime import datetime

def extremes(data, std_dev, mean):
    highs = []
    lows = []
    for i in range(data.shape[0]):
        if data[i][1] > mean + std_dev:
            highs.append(data[i])
        elif data[i][1] < mean - std_dev:
            lows.append(data[i])
    return highs, lows

def ret_limitedarr(arr, start, finish):
    lims = calc_limits(arr['x'], start, finish)
    return arr[lims[0] : lims[1]]

def yearwise(arr, start, finish, filename):
    iyear, imonth, iday = start.split('.')
    fyear, fmonth, fday = finish.split('.')

    outfile = open(filename, 'w')

    start_time = datetime(int(iyear), int(imonth), int(iday))
    finish_time = datetime(int(fyear), int(fmonth), int(fday))

    i = start_time

    while i <= finish_time:
        year = i.year
        startdate = "{0}.{1}.{2}".format(year,1,1)
        enddate = "{0}.{1}.{2}".format(year+1,1,1)

        year_data = ret_limitedarr(arr, startdate, enddate)

        mean, std_dev, maxdate, max, mindate, min =compute_stats(year_data)
        outfile.write("{year},{maxdate},{max},{mindate}{min},{change}\n".format(year=year, maxdate=maxdate, max=max, mindate=mindate, min=min, change=max-min))
        i = datetime(1+i.year, i.month, i.day)

def compute_stats(data, limits=(None, None)):
    data = data[limits[0]:limits[1]]

    mean = np.average(data['y'])
    std_dev = np.std(data['y'])

    max_index = np.argmax(data['y'])
    min_index = np.argmin(data['y'])

    maxdate, max, _ = data[max_index]
    mindate, min, _ = data[min_index]

    return mean, std_dev, maxdate, max, mindate, min

def calc_limits(arr, start, finish):
    iyear, imonth, iday = start.split('.')
    fyear, fmonth, fday = finish.split('.')

    start_time = datetime(int(iyear), int(imonth), int(iday))
    finish_time = datetime(int(fyear), int(fmonth), int(fday))

    i = 0
    while start_time > arr[i]:
        i += 1
    j = len(arr) -1
    while finish_time < arr[j]:
        j -= 1

    return (i, j)

def main():
    infile = 'Brahmaputra'
    infilename = r'F:\Projects\SnowcoverAnalyzer\Results\{0}.csv'.format(infile)

    outfile = 'Brahmaputra_maxmin'
    outfilename = r'F:\Projects\SnowcoverAnalyzer\Results\{0}.csv'.format(outfile)

    convert_datetime = lambda x: datetime.strptime(str(x), "%Y.%m.%d")
    data = np.genfromtxt(infilename, delimiter=",",
                         dtype=[('x', datetime), ('y', np.float), ('z', np.float)],
                         converters={0: convert_datetime})

    #lims = calc_limits(data['x'], '2009.1.1', '2010.1.1')
    #compute_stats(data, lims)
    yearwise(data,'2001.1.1', '2016.11.1', outfilename)

if __name__=='__main__':
    main()