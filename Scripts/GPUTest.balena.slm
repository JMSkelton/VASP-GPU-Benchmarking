#!/bin/sh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --time=6:00:00

#SBATCH --job-name=GPU-Test
#SBATCH --account=free

#SBATCH --partition=batch-acc

# Request a node w/ 1 k20x card.

#SBATCH --gres=gpu:1
#SBATCH --constraint=k20x

# Request a node w/ 4 k20x cards.

##SBATCH --gres=gpu:4
##SBATCH --constraint=k20x

#SBATCH --output=%j.out
#SBATCH --error=%j.err

. /etc/profile.d/modules.sh

module purge
module load slurm

module load intel/compiler/64/15.0.0.090
module load intel/mkl/64/11.2
module load openmpi/intel/1.8.4
module load cuda/toolkit/7.5.18

# As part of the setup, we need to create some folders in /tmp for the NVIDIA MPS (= "Multi Process Service"), and start the daemon.

if [ ! -d "/tmp/nvidia-mps" ] ; then
    mkdir "/tmp/nvidia-mps"
fi

export CUDA_MPS_PIPE_DIRECTORY="/tmp/nvidia-mps"

if [ ! -d "/tmp/nvidia-log" ] ; then
    mkdir "/tmp/nvidia-log"
fi

export CUDA_MPS_LOG_DIRECTORY="/tmp/nvidia-log"

nvidia-cuda-mps-control -d

# The -u ("unbuffered") flag stops Python buffering std out, so the (minimal) output from the script is written to the .out file as soon as it's printed.

python -u GPUTest.py
