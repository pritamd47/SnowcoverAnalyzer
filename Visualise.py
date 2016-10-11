import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from datetime import datetime

def visualize(infile, basin, percentage = True):
    # Reading data
    convert_datetime = lambda x: datetime.strptime(str(x), "%Y.%m.%d")
    data = np.genfromtxt(infile, delimiter=",", dtype=[('x', datetime), ('y', np.float), ('z', np.float)], converters = {0: convert_datetime}, skip_header=52)

    # showing graphs
    years = YearLocator()
    months = MonthLocator()
    yearsFmt = DateFormatter("%Y")

    fig , ax1 = plt.subplots(2, sharex=True)
    ax1[0].plot_date(data['x'], savitzky_golay(data['y'], 51, 2),'.', linestyle = 'solid', color = 'r', linewidth = 0.5)
    # remove savitzky_golay if want actual percentages
    ax1[0].xaxis.set_major_locator(years)
    ax1[0].xaxis.set_major_formatter(yearsFmt)
    ax1[0].xaxis.set_minor_locator(months)
    ax1[0].autoscale_view()
    ax1[0].grid(True)

    ax1[1].plot_date(data['x'], savitzky_golay(data['z'], 51, 2), '-', linestyle = 'solid', color = 'b', linewidth = 0.5)
    ax1[1].xaxis.set_major_locator(years)
    ax1[1].xaxis.set_major_formatter(yearsFmt)
    ax1[1].xaxis.set_minor_locator(months)
    ax1[1].autoscale_view()
    ax1[1].grid(True)

    plt.xlabel("Years")
    plt.ylabel("Percentage snow cover over " + basin)
    fig.autofmt_xdate()
    plt.show()


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    import numpy as np
    from math import factorial

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate ** deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')

def main():
    filename = r'F:\Projects\SnowcoverAnalyzer\Results\Indus.csv'
    visualize(filename, 'Indus')

if __name__ == "__main__":
    main()