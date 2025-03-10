#!/bin/env bash
#
#SBATCH -p all                # partition (queue)
#SBATCH -c 1                      # number of cores
#SBATCH -t 20                 # time (minutes)
#SBATCH -o logs/step0.out        # STDOUT
#SBATCH -e logs/step0.err        # STDERR

module load anacondapy/2020.11
module load elastix/4.8
. activate brainpipe

echo "Starting step 0"

python main.py 0 #update dictionary and pickle

# HOW TO USE:
# sbatch --array=0-20 sub_arrayjob.sh 

