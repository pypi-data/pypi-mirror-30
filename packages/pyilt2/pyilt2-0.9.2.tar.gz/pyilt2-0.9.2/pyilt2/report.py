#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple example for a search & report tool using the pyILT2 library.

(c) 2018 Frank Roemer; see http://wgserve.de/pyilt2
Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
from __future__ import print_function

from . import (properties, query, __version__)

import argparse
import datetime
import sys
import time
import threading
import os


# version of the search & report tool
__prgversion__ = '0.9'


def printPropAbbrList():
    """
    Print a table, showing the physical properties which can be addressed in a query,
    and the respective *abbreviation* which is used in the :func:`pyilt2.query` function, to *stdout*::

         Abbr.  Property
        ------  -----------------------------------------
         Dself  Self-diffusion coefficient
         Dterm  Thermal diffusivity
         Dtrac  Tracer diffusion coefficient
             H  Enthalpy
           Hap  Apparent enthalpy
           ...  ...

    """
    print ( "%6s  %s" % ('Abbr.','Property') )
    print ('------  -----------------------------------------')
    for key in sorted(properties):
        print ( "%6s  %s" % (key, properties[key][1]) )


def writeReport(listOfDsets):
    dtnow = datetime.datetime.now()
    dname = 'pilt2report_' + dtnow.strftime("%Y-%m-%d_%H:%M:%S")
    os.mkdir(dname)
    rep = open(dname + '/report.txt', 'w')
    rep.write(dtnow.strftime("%d. %b. %Y (%H:%M:%S)") + '\n')
    rep.write('-' * 24 + '\n')
    for i in range(0, len(listOfDsets)):
        rep.write('\nRef. #{0:d}\n'.format(i, listOfDsets[i].setid))
        rep.write('=' * 10 + '\n')
        rep.write(str(listOfDsets[i]))
        listOfDsets[i].write('{0:s}/ref{1:d}.dat'.format(dname, i))
    rep.close()
    return dname


class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)

# create a spinner object for he following functions
spinner = Spinner()


def cliQuery(comp='', numOfComp=0, year='', author='', keywords='', prop='', verbose=False):
    resObj=None
    if verbose:
        print('Make query to NIST... ', end='')
        spinner.start()
    try:
        resObj = query(comp=comp,
                              numOfComp=numOfComp,
                              year=year,
                              author=author,
                              keywords=keywords,
                              prop=prop)
    except:
        if verbose:
            spinner.stop()
        e = sys.exc_info()[1]
        print('Error: {0:s}'.format(e))
        exit(1)
    else:
        if verbose:
            spinner.stop()
            print('\b done! ({0:d} hits)'.format(len(resObj)))
    return resObj


def getAllData(resObj, verbose=False):
    dataSets = []
    if verbose:
        print('\nRequest data sets from NIST:')
    for i in range(0, len(resObj)):
        if verbose:
            print(' >> {0:s} [{1:s}] ... '.format(resObj[i].ref, resObj[i].setid), end='')
            spinner.start()
        try:
            dataSets.append(resObj[i].get())
        except:
            if verbose:
                spinner.stop()
            e = sys.exc_info()[1]
            print('Error: {0:s}'.format(e))
            exit(1)
        else:
            if verbose:
                spinner.stop()
                print('\b done!')
    return dataSets


# ===============================================================================
# run
# ===============================================================================
def run():
    """CLI main entry point."""

    parser = argparse.ArgumentParser(description='A search and report tool for ILThermo v2.0')
    parser.add_argument('-c', type=str, metavar='str',
                        help='chemical formula, CAS registry number, or name (part or full)', default='')
    parser.add_argument('-n', type=int, metavar='0',
                        help='number of mixture components. Default: 0 = any number.', default=0)
    parser.add_argument('-y', type=str, metavar='2018',
                        help='publication year', default='')
    parser.add_argument('-a', type=str, metavar='name',
                        help='author’s last name', default='')
    parser.add_argument('-k', type=str, metavar='str',
                        help='keyword(s)', default='')
    parser.add_argument('-p', type=str, metavar='prop',
                        help='physical property by abbreviation. Default unspecified.', default=None)
    parser.add_argument('--props', action='store_true',
                        help='show properties abbreviations and exit', default=False)
    parser.add_argument('--version', action='version',
                        version="%(prog)s " + __prgversion__ + " (pyilt2 " + __version__ + ")")
    args = parser.parse_args()

    if args.props:
        printPropAbbrList()
        exit(0)

    # check the 'phys. property' search option
    sprop = ''
    if args.p:
        if args.p not in properties.keys():
            print('Error! Invalid abbreviation "{0:s}" for physical property.'.format(args.p))
            exit(1)
        else:
            sprop = args.p

    # makes the request to the NIST database
    res = cliQuery(comp=args.c, numOfComp=args.n, year=args.y,
                   author=args.a, keywords=args.k, prop=sprop, verbose=True)

    # show results and ask if to proceed
    res.printResultTable()
    print('\nProceed? [Y]/n  ', end='')
    answ = sys.stdin.readline().strip()
    if answ not in ['', 'y', 'Y']:
        print('Abort by user!')
        exit(0)

    # get full data sets for _all_ references
    dataSets = getAllData(res, verbose=True)

    # write report
    dname = writeReport(dataSets)
    print('\nReport written to ' + dname)


# Script entry point
if __name__ == "__main__":
    run()