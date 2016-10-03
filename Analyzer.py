import numpy as np
import matplotlib.pyplot as plt
import threading
from pyhdf.SD import SD, SDC
import os
import time



path = "Data" + os.sep

directories = os.listdir(path)
directories = filter(lambda x: os.path.isdir(path+x), directories)

os.chdir(path)        # Changed directory to Path
cwd = os.getcwd()
snowcov = []
date = []

cover = []


class analyzerthread(threading.Thread):
    def __init__(self, dataset):
        threading.Thread.__init__(self)

        self.dataset = dataset

    def run(self):
        #self.calcsnow()
        pass

def calcsnow(dataset):
    snow = 0.0
    global cover

    #print dataset[:10, :10]
    for i in range(dataset.shape[0]):
        for j in range(dataset.shape[1]):
            if dataset[i, j] in (200, 100):
                snow += 1

    snowcover = (snow/ dataset.shape[0]**2) * 100
    cover.append(snowcover * 1.0/256.0)



start = time.time()


for i in range(1, 6):
    dirstart = time.time()
    cover = []    # Global
    date.append(directories[i])

    hdffile = SD(directories[i] + os.sep + "h25v06.hdf")
    DATASET_NAME = "Maximum_Snow_Extent"
    data_mesh = hdffile.select(DATASET_NAME)

    print "[+] Working on {0}".format(directories[i])

    data = data_mesh[:,:].astype(np.int64)    # This is stored in array form
    snow = 0
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if data[i, j] in (100, 200):
                snow += 1

    snowcov.append((snow / 5670000.0) * 100)
    print "[+] Finished working in directory with result {0}".format(snowcov[-1])
    print "[!] Time taken: {0}".format(time.time()-dirstart)

print time.time() - start
plot = plt.plot(snowcov)

plt.show()