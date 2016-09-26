import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pyhdf.SD import SD, SDC, SD


hdffile = SD(r"data\MOD10A1.A2013177.h25v06.006.2016143122733.hdf", SDC.READ)

print hdffile.datasets()

DATAFIELD_NAME = "NDSI_Snow_Cover"

data_mesh = hdffile.select(DATAFIELD_NAME)
data = data_mesh[:,:].astype(np.int64)

istart = 0
ifinish = 10

jstart = 0
jfinish = 5
#
#for j in range(0, 2400, 10):
#    jstart = j
#    jfinish = jstart + 10
#    print "sec" + str(j/10) + ": "
    #print data[istart:ifinish, jstart:jfinish]
plt.imshow(data[:,:], interpolation='nearest')
plt.show()


# Code doesn't reach here
#with open("Data/NDSI_Snow_Cover (dimension).txt", 'r') as txtfile:
#    data = numpy.loadtxt(txtfile, dtype=int)
#    imgplot = plt.imshow(data)
#    plt.show()