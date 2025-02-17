from LlvmUtilsV5 import LlvmUtils
from socket import gethostname
from benchmark_measurer import benchmark_measurer

import numpy as np
import subprocess
import os
import sys

if len(sys.argv) < 2:
    config_type = '1toma'
else:
    config_type = sys.argv[1]

config_filename = "resultados_raspberry_uncertainty/results_{}.data".format(config_type)
config_jobid = 1
config_runs = 1000

if __name__=='__main__':
    solution = None
    solution_length = None
    llvm = LlvmUtils(jobid = config_jobid, runs = 1)
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

    print('Data:')
    print('Solution: {}'.format(passes))
    print('Solution length: {}'.format(solution_length))
    print('Result type: {}'.format(config_type))

    measurer = \
        benchmark_measurer(_usuario_IP_experimentacion = "pi@192.168.3." + str(int(gethostname().split('-')[1]) + 1))
    
    measurer.main_speedup(send_compile_data = [measurer.aux_data[0], passes.split(" ")],            
        exec_data = [measurer.aux_data[0], 1000, 0, 0],
        file_name = measurer.aux_data[0].split('/')[-1])

    ec_array = []
    for i, data_iter in enumerate(measurer.data_file):
        if i != 0:
            ec_array.append(data_iter[-1])

    # Save times in a csv file
    np.array(ec_array).tofile('solutions_ec_fitness_{}.csv'.format(config_type), sep = ',')
