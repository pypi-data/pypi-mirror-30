# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: methods for file manipulation.
'''

# DEPENDENCIES =================================================================

# CONSTANTS ====================================================================

# FUNCTIONS ====================================================================

def count_lines(ipath):
    '''Quickly count lines in a file.

    Args:
        ipath (str): path to input file.
    
    Returns:
        int: number of lines
    '''
    rc = 0
    with open(ipath, "r") as IH:
        for line in IH: rc += 1
    return(rc)

# END ==========================================================================

################################################################################
