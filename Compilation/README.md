Building `vasp-gpu` on Balena
=============================

These instructions are for building VASP 5.4.1 (05Feb16 revision) on the University of Bath's [Balena](http://www.bath.ac.uk/bucs/services/hpc/facilities/) HPC cluster.


Modules
-------

VASP 5.4.1 was build with the following modules:

- `intel/compiler/64/15.0.0.090`
- `intel/mkl/64/11.2`
- `openmpi/intel/1.8.4`
- `cuda/toolkit/7.5.18`


Compilation
-----------

- Prepare a suitable `makefile.include` in the top-level directory; `makefile.include.balena` is based on the `makefile.include.linux_intel_cuda` template distributed with the source code.

- Compile the binaries, including the `gpu` and `gpu_ncl` targets: `make std gam ncl gpu gpu_ncl`.


Running Jobs
------------

Running jobs with the GPU-enabled versions of VASP requires a modified SLURM script to request a GPU-equipped node and to perform some setup tasks.
See the sample submission script in [Scripts](../Scripts) for an example.
