# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfon.luu@mines-paristech.fr>
License: MIT
"""

import numpy as np
import os, sys, time
from argparse import ArgumentParser
from copy import deepcopy
try:
    from mpi4py import MPI
    mpi_exist = True
except ImportError:
    mpi_exist = False
try:
    from evodcinv import DispersionCurve, LayeredModel, progress
except ImportError:
    sys.path.append("../")
    from evodcinv import DispersionCurve, LayeredModel, progress
    

if __name__ == "__main__":
    # Initialize MPI
    if mpi_exist:
        mpi_comm = MPI.COMM_WORLD
        mpi_rank = mpi_comm.Get_rank()
    else:
        mpi_rank = 0
        
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument("-n", "--num_threads", type = int, default = 8)
    args = parser.parse_args()
        
    # Parameters
    ny = 200                        # Number of velocity discretization points
    max_run = 10                    # Number of runs
    outdir = "output"               # Output directory
    
    # Inversion boundaries
    beta = np.array([ [ 100., 1000. ], [ 500., 2000. ], [ 500., 2000. ] ])
    thickness = np.array([ [ 100., 1000. ], [ 100., 500. ], [ 99999., 99999. ] ])
    
    # Initialize dispersion curves
    disp_param = [
        ( "data/rayleigh_mode0.txt", "rayleigh", 0 ),
        ( "data/rayleigh_mode1.txt", "rayleigh", 1 ),
        ( "data/love_mode0.txt", "love", 0 ),
        ( "data/love_mode1.txt", "love", 1 ),
        ]
    
    dcurves = []
    for param in disp_param:
        filename, wtype, mode = param
        faxis, disp = np.loadtxt(filename, unpack = True)
        dc = DispersionCurve(disp, faxis, mode, wtype)
        dcurves.append(dc)

    # Evolutionary optimizer parameters
    evo_kws = dict(popsize = 20, max_iter = 200, constrain = True, mpi = mpi_exist)
    opt_kws = dict(solver = "cpso")
        
    # Multiple inversions
    if mpi_rank == 0:
        starttime = time.time()
        os.makedirs(outdir, exist_ok = True)
        progress(-1, max_run, "perc", prefix = "Inverting dispersion curves: ")
        
    models = []
    for i in range(max_run):
        lm = LayeredModel()
        lm.invert(dcurves, beta, thickness, ny = ny, n_threads = args.num_threads,
                  evo_kws = evo_kws, opt_kws = opt_kws)
        if mpi_rank == 0:
            lm.save("%s/run%d.pickle" % (outdir, i+1))
            models.append(deepcopy(lm))
            progress(i, max_run, "perc", prefix = "Inverting dispersion curves: ")
        
    if mpi_rank == 0:
        print("\n")
        misfits = [ m.misfit for m in models ]
        print(models[np.argmin(misfits)])
        print("Elapsed time: %.2f seconds\n" % (time.time() - starttime))