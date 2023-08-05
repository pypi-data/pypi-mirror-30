#!/usr/bin/env python
"""Some random utility functions.

Import this file as
    import utils.utilities as utl

@author: Federico Tomasi
@email:  fdtomasi@gmail.com
"""
import sys
import time
import numpy as np
from datetime import datetime as dt


def find_TP(true_l, empirical_l):
    """Binary format only; 1 positive, 0 negative."""
    l1, l2 = np.array(true_l), np.array(empirical_l)
    res = l1 + l2 - 1
    res[res < 1] = 0
    return res


def find_FP(true_l, empirical_l):
    """Binary format only; 1 positive, 0 negative."""
    l1, l2 = np.array(true_l), np.array(empirical_l)
    res = l1 - l2
    res[res < 1] = 0
    return res


def find_FN(true_l, empirical_l):
    """Binary format only; 1 positive, 0 negative."""
    l1, l2 = np.array(true_l), np.array(empirical_l)
    res = l2 - l1
    res[res < 1] = 0
    return res


def perc_var(mic, mid):
    """Percentual variations.

    To better compare DMI results, we can consider percentual variation between
    mutual information of control cases (mic) and mutual information of
    disease cases (mid).
    """
    try:
        return 1. * abs(mic - mid) / (mic + mid)
    except ZeroDivisionError:
        return 0.


def progressbar(i, maxv, title=''):
    """Progress bar."""
    sys.stdout.write(
        "\r[%-20s] %.2f%% (%3d/%3d) -- %s" % ('=' * int(i * 20. / maxv),
                                              i * 100. / maxv, i, maxv,
                                              title[:20]))
    sys.stdout.flush()


def sec_to_time(seconds):
    """Transform seconds into formatted time string."""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d.%02d.%02d" % (h, m, s)


def get_time():
    """Get time."""
    return dt.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H.%M.%S')


def file_len(fname):
    """Find the number of lines in a file."""
    with open(fname, 'r') as f:
        for i, l in enumerate(f):
            pass
    return i + 1
