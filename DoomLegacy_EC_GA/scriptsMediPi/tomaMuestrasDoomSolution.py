from LlvmUtilsV5 import LlvmUtils
from socket import gethostname
from benchmark_measurer import benchmark_measurer
from shutil import copy as copyfile

import numpy as np
import subprocess
import os
import sys

if len(sys.argv) < 2:
    config_type = "ga_doom"
else:
    config_type = sys.argv[1]

config_program = 'doomlegacy'
config_jobid = 1
config_runs = 1000

if __name__=='__main__':
    solution = None
    solution_length = None
    llvm = LlvmUtils(jobid = config_jobid, runs = 1)

    # Generate doomlegacy binary file
    basepath = "./experimentos/"
    os.system("bash /home/pi/experimentos/doomlegacy_source/genBinary.sh")

    if (os.path.exists("{}doomlegacy_optimized.bc".format(basepath))):
        os.remove("{}doomlegacy_optimized.bc".format(basepath))
    copyfile("{}doomlegacy_source/bin/doomlegacy_original.bc".format(basepath),"{}doomlegacy_optimized.bc".format(basepath))

    config_filename = f"results_{config_type}.data"
    with open(config_filename, 'r') as filestr:
        for line in filestr.readlines():
            if "Best solution:" in line:
                solution = line.split(':')[1].strip().replace('[','').replace(']','').split(',')
            elif "Solution length" in line:
                solution_length = int(line.split(':')[1].strip())

    if solution_length == None:
        solution_length = len(solution)
    
    # Decode
    passes = ""
    for i in range(solution_length):
        passes += " {}".format(LlvmUtils.get_passes()[int(solution[i])])

    llvm.toIR_doom(passes)

    os.system("bash {}doomlegacy_source/genGame.sh".format(basepath))

    print('Data:')
    print('Solution: {}'.format(solution))
    print('Solution length: {}'.format(solution_length))
    print('Result type: {}'.format(passes))

    measurer = \
        benchmark_measurer(_usuario_IP_experimentacion = "pi@192.168.3." + str(int(gethostname().split('-')[1]) + 1))

    measurer.doom_main_speedup(send_compile_data = [f"{config_program}_{config_type}", passes.split(" ")],
        exec_data = [f"{config_program}_{config_type}", 1000, 0, 0],
        file_name = f"{config_program}_{config_type}")

    ec_array = []
    for i, data_iter in enumerate(measurer.data_file):
        if i != 0:
            ec_array.append(data_iter[-1])

    # Save times in a csv file
    np.array(ec_array).tofile('solutions_ec_fitness_{}_{}.csv'.format(config_type,config_program), sep = ',')
