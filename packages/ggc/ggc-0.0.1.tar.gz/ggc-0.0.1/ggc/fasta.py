# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: methods for FASTA manipulation.
'''

# DEPENDENCIES =================================================================

from Bio.SeqIO.FastaIO import SimpleFastaParser
from tqdm import tqdm

# CONSTANTS ====================================================================

tqdm.monitor_interval = 0

# FUNCTIONS ====================================================================

def count_records(fpath):
    '''Quickly count headers in FASTA file.

    Args:
        fpath (str): path to input FASTA file.
    
    Returns:
        int: number of headers (lines starting with ">")
    '''
    rc = 0
    with open(fpath, "r") as IH:
        for line in IH:
            if ">" == line[0]:
                rc += 1
    return(rc)

def read_seq(ipath, opath = None, n = None):
    '''Converts a FASTA file into a header-less fasta file with one sequence
    per line.

    Args:
        ipath (str): path to input FASTA.
        opath (str): path to output header-less FASTA.
        n (int): number of sequences in input file for progress bar.
    
    Returns:
        list: sequences from the input FASTA.
        None: writes to disk.
    '''
    if type(None) == type(opath):
        l = []
        with open(ipath, 'r') as IH:
            seqgen = SimpleFastaParser(IH)
            if type(None) != type(n): seqgen = tqdm(seqgen, total = n)

            for record in seqgen: l.append(record[1])
        return(l)
    else:
        with open(opath, 'w+') as OH:
            with open(ipath, 'r') as IH:
                seqgen = SimpleFastaParser(IH)
                if type(None) != type(n): seqgen = tqdm(seqgen, total = n)

                for record in seqgen:
                    if 0 != len(record[1]):
                        OH.write("%s\n" % record[1])

# END ==========================================================================

################################################################################
