# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: methods for arguments manipulation.
'''

# DEPENDENCIES =================================================================

import multiprocessing

# CONSTANTS ====================================================================

# FUNCTIONS ====================================================================

def check_threads(threads):
    # Check thread count
    if threads <= 0: return(1)
    if threads > multiprocessing.cpu_count():
        return(multiprocessing.cpu_count())
    return(threads)

# END ==========================================================================

################################################################################
