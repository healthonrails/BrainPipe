#!/bin/env bash
#
#SBATCH -p all                # partition (queue)
#SBATCH -c 8                      # number of cores
#SBATCH -t 20                # time (minutes)
#SBATCH -o logs/cnn_step0_%j.out        # STDOUT #add _%a to see each array job
#SBATCH -e logs/cnn_step0_%j.err        # STDERR #add _%a to see each array job
#SBATCH --contiguous #used to try and get cpu mem to be contigous
#SBATCH --mem 25000 #25 gbs

echo "In the directory: `pwd` "
echo "As the user: `whoami` "
echo "on host: `hostname` "

cat /proc/$$/status | grep Cpus_allowed_list

module load anacondapy/2020.11
. activate brainpipe

echo "Experiment name:" "`pwd`"

python cell_detect.py 0 0 "`pwd`"

