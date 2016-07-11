Scripts
=======

A selection of scripts used for benchmarking VASP on the University of Bath's [Balena](http://www.bath.ac.uk/bucs/services/hpc/facilities/) HPC cluster.


Contents
--------

- `CPUTest.py` : *A script for benchmarking the CPU version of VASP by sweeping the `KPAR`, `NPAR` and/or `NSIM` parameters.*

- `GPUTest.py` : *A script for benchmarking the GPU version of VASP by sweeping the number of MPI processes and the `NSIM` parameter.*

- `GetTimings.py` : *A command-line script for quickly extracting timing information from the files in VASP job folders.*

- `Shared.py` : *A module containing functions for extracting information from VASP output files; imported by `CPUTest.py`, `GPUTest.py` and `GetTimings.py`.*

- `PadCSVs.py` : *Rewrites CSV files to pad rows to a consistent length; required for the "pretty" display on the GitHub website.*


Usage
-----

`CPUTest.py` and `GPUTest.py` are configured through parameters set at the top of the scripts; these are annotated with explanatory comments and fairly self explanatory.

These scripts are designed to be run from the scheduler - see the example SLURM scripts `CPUTest.balena.slm` and `GPUTest.balena.slm` for running on Balena.

`GetTimings.py` is called from the command line:

```
python GetTimings.py CPU-GeTe_256/vasp_gam

Analysing "CPU-GeTe_256/vasp_gam"...
  -> # SCF steps: 32
  -> Avgerage t_SCF [s]: 21.93
  -> Elapsed time [s]: 745.55
  -> Final E_0 [eV]: -670.88396000
```

The optional `--skip_scf_cycles=N` argument can be used to exclude the first *N* SCF steps from the average cycle time.

`PadCSV.py` is a utility script, again called from the command line; type `PadCSV.py -h` for usage instructions.

N.B. The default `python` on Balena does not have the `argparse` module imported by `GetTimings.py` - use the distribution provided by the `python/2.7.8` module instead.


Acknowledgements
----------------

The CUDA setup in `GPUTest.balena.slm` is based on the notes from Peter Larsson's blog post, [Running VASP on Nvidia GPUs](https://www.nsc.liu.se/~pla/blog/2015/11/16/vaspgpu/).
