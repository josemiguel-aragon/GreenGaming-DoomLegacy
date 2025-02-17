# v5 version
# energy consumption function added


import os
import subprocess
import time
import random
import sys
import numpy as np

from shutil import copy as copyfile
from socket import gethostname
from typing import Union

from IntervalValueV1 import IntervalValue
from IntervalUtilsV1 import IntervalUtils
from benchmark_measurer import benchmark_measurer



class LlvmUtils():
    '''
    llvmpath = llvm path
    basepath = work path
    bechmark = benchmark folder name, has to be in work path
    generator = script to merge all benchmark suite
    source = name for benchmark IR code
    runs = how many times should the benchmark be run
    jobid = job identifier code
    '''

    def __init__(self, llvmpath: str = "", basepath: str = "/home/pi/experimentos/", benchmark: str = "polybench_small",
                 generator: str = "original_merged_generator.sh", source: str = "polybench_small_original.bc",
                 runs: int = 1, worstruns: int = 1, jobid: str = "", useperf : bool = True, useinterval: bool = False, n_iterations: int = 500,
                 significance_level: int = 5, usedelay: bool = False, usenuma: bool = False, useworstcase: bool = False):
        self.llvmpath = llvmpath
        self.basepath = basepath
        self.benchmark = benchmark
        self.generator = generator
        self.source = source
        self.runs = runs
        self.worstruns = worstruns
        self.jobid = jobid
        self.onebyones = 0
        self.useperf = useperf
        self.useinterval = useinterval
        self.n_iterations = n_iterations
        self.significance_level = significance_level
        self.usedelay = usedelay
        self.useworstcase = useworstcase
        if usenuma:
            self.usenuma = "taskset -c 72-95"
        else:
            self.usenuma = ""

    @staticmethod
    def get_passes() -> list:
        all_passes = ["-tti","-tbaa","-scoped-noalias","-assumption-cache-tracker","-targetlibinfo","-verify",
                      "-ee-instrument","-simplifycfg","-domtree","-sroa","-early-cse","-lower-expect",
                      "-profile-summary-info","-forceattrs","-inferattrs","-callsite-splitting","-ipsccp",
                      "-called-value-propagation","-attributor","-globalopt","-mem2reg","-deadargelim",
                      "-basicaa","-aa","-loops","-lazy-branch-prob","-lazy-block-freq","-opt-remark-emitter",
                      "-instcombine","-basiccg","-globals-aa","-prune-eh","-inline","-functionattrs",
                      "-argpromotion","-memoryssa","-speculative-execution","-lazy-value-info",
                      "-jump-threading","-correlated-propagation","-aggressive-instcombine","-libcalls-shrinkwrap",
                      "-branch-prob","-block-freq","-pgo-memop-opt","-tailcallelim","-reassociate",
                      "-loop-simplify","-lcssa-verification","-lcssa","-scalar-evolution","-loop-rotate","-licm",
                      "-loop-unswitch","-indvars","-loop-idiom","-loop-deletion","-loop-unroll","-mldst-motion",
                      "-phi-values","-memdep","-gvn","-memcpyopt","-sccp","-demanded-bits","-bdce","-dse",
                      "-postdomtree","-adce","-barrier","-elim-avail-extern","-rpo-functionattrs","-globaldce",
                      "-float2int","-loop-accesses","-loop-distribute","-loop-vectorize","-loop-load-elim",
                      "-slp-vectorizer","-transform-warning","-alignment-from-assumptions","-strip-dead-prototypes",
                      "-constmerge","-loop-sink","-instsimplify","-div-rem-pairs",""]
        return all_passes

    # To convert the original benchmark into LLVM IR
    def benchmark_link(self) -> None:
        os.chdir("{}{}/".format(self.basepath,self.benchmark))
        os.system("./{} {}".format(self.generator,self.llvmpath))
        copyfile("{}".format(self.source),"../{}".format(self.source))
        os.chdir("../")

    # To get the runtime
    def get_runtime(self,passes: str = "-O3") -> Union[float, IntervalValue]:
        if (os.path.exists("{}optimized_{}.bc".format(self.basepath,self.jobid))):
            os.remove("{}optimized_{}.bc".format(self.basepath,self.jobid))
        copyfile("{}{}".format(self.basepath,self.source),"{}optimized_{}.bc".format(self.basepath,self.jobid))
        # os.system("ls")
        median = 0.0
        desviation = None
        if self.toIR(passes):
            os.system("{}clang-9 -lm -O0 -Wno-everything -disable-llvm-optzns -disable-llvm-passes {}".format(
                       self.llvmpath,"-Xclang -disable-O0-optnone {}optimized_{}.bc -o {}exec_{}.o".format(
                       self.basepath,self.jobid,self.basepath,self.jobid)))
            if self.useperf:
                runtimes = []
                if self.usedelay:
                    for i in range(self.runs):
                        cmd = subprocess.check_output("{} {}runtimes.sh {}exec_{}.o 1".format(
                                self.usenuma, self.basepath,self.basepath,self.jobid),shell=True)
                        if i==0:
                            runtimes = np.array(cmd.decode("utf-8")[:-1].split(","),dtype=float)
                        else:
                            runtimes = np.concatenate((runtimes,np.array(cmd.decode("utf-8")[:-1].split(","),dtype=float)),axis=0)

                        time.sleep(random.randint(1,3))
                else:
                    cmd = subprocess.check_output("{} {}runtimes.sh {}exec_{}.o {}".format(
                            self.usenuma, self.basepath,self.basepath,self.jobid,self.runs),shell=True)
                    runtimes = np.array(cmd.decode("utf-8")[:-1].split(","),dtype=float)
                if self.useinterval:
                    if self.useworstcase:
                        sorted_runtimes = runtimes[np.argsort(runtimes)]
                        median = IntervalUtils.make_interval(runtimes = sorted_runtimes[-self.worstruns:], n_iterations = self.n_iterations
                         ,significance_level = self.significance_level)
                    else:
                        median = IntervalUtils.make_interval(runtimes = runtimes, n_iterations = self.n_iterations
                             ,significance_level = self.significance_level)
                        desviation = np.std(runtimes)
                elif self.useworstcase:
                    median = np.amax(runtimes)
                    deviation = np.std(runtimes)
                else:
                    median = np.median(runtimes)
                    desviation = np.std(runtimes)
                    #print("median : {}".format(median))
                    #exit(1)
            else:
                array = []
                if self.usedelay:
                    for _ in range(self.runs):
                        start_time = time.time()
                        os.system("{} {}exec_{}.o".format(self.usenuma, self.basepath,self.jobid))
                        array.append(time.time() - start_time)
                        time.sleep(random.randint(1,3))
                else:
                    for _ in range(self.runs):
                        start_time = time.time()
                        os.system("{} {}exec_{}.o".format(self.usenuma, self.basepath,self.jobid))
                        array.append(time.time() - start_time)
                if self.useinterval:
                    if self.worstcase:
                        runtimes = np.array(array)
                        sorted_runtimes = runtimes[np.argsort(runtimes)]
                        median = IntervalUtils.make_interval(runtimes = sorted_runtimes[-self.worstruns:], n_iterations = self.n_iterations
                         ,significance_level = self.significance_level)
                    else:
                        median = IntervalUtils.make_interval(runtimes = np.array(array), n_iterations = self.n_iterations
                             ,significance_level = self.significance_level)
                        desviation = np.std(np.array(array))
                elif self.useworstcase:
                    median = np.amax(np.array(array))
                    desviation = np.std(np.array(array))
                else:
                    median = np.median(np.array(array))
                    desviation = np.std(np.array(array))
        else:
            median = sys.maxsize
        return median, desviation

    # To get the runtime
    def get_runtime_doom(self,passes: str = "-O3") -> Union[float, IntervalValue]:
        if (os.path.exists("{}optimized_{}.bc".format(self.basepath,self.jobid))):
            os.remove("{}optimized_{}.bc".format(self.basepath,self.jobid))
        copyfile("{}{}".format(self.basepath,self.source),"{}optimized_{}.bc".format(self.basepath,self.jobid))
        # os.system("ls")
        median = 0.0
        desviation = None
        if self.toIR(passes):
            os.system("bash ./doomlegacy/applyPassesTime.sh \"{}\"".format(passes))
            if self.useperf:
                runtimes = []
                if self.usedelay:
                    for i in range(self.runs):
                        cmd = subprocess.check_output("{} {}runtimesDoom.sh doomlegacy_optimized/doomlegacy 1".format(
                                self.usenuma, self.basepath),shell=True)
                        if i==0:
                            runtimes = np.array(cmd.decode("utf-8")[:-1].split(","),dtype=float)
                        else:
                            runtimes = np.concatenate((runtimes,np.array(cmd.decode("utf-8")[:-1].split(","),dtype=float)),axis=0)

                        time.sleep(random.randint(1,3))
                else:
                    cmd = subprocess.check_output("{} {}runtimesDoom.sh doomlegacy_optimized/doomlegacy {}".format(
                            self.usenuma, self.basepath,self.runs),shell=True)
                    runtimes = np.array(cmd.decode("utf-8")[:-1].split(","),dtype=float)
                if self.useinterval:
                    if self.useworstcase:
                        sorted_runtimes = runtimes[np.argsort(runtimes)]
                        median = IntervalUtils.make_interval(runtimes = sorted_runtimes[-self.worstruns:], n_iterations = self.n_iterations
                         ,significance_level = self.significance_level)
                    else:
                        median = IntervalUtils.make_interval(runtimes = runtimes, n_iterations = self.n_iterations
                             ,significance_level = self.significance_level)
                        desviation = np.std(runtimes)
                elif self.useworstcase:
                    median = np.amax(runtimes)
                    deviation = np.std(runtimes)
                else:
                    median = np.median(runtimes)
                    desviation = np.std(runtimes)
                    #print("median : {}".format(median))
                    #exit(1)
            else:
                array = []
                if self.usedelay:
                    for _ in range(self.runs):
                        start_time = time.time()
                        os.system("{} {}exec_{}.o".format(self.usenuma, self.basepath,self.jobid))
                        array.append(time.time() - start_time)
                        time.sleep(random.randint(1,3))
                else:
                    for _ in range(self.runs):
                        start_time = time.time()
                        os.system("{} {}exec_{}.o".format(self.usenuma, self.basepath,self.jobid))
                        array.append(time.time() - start_time)
                if self.useinterval:
                    if self.worstcase:
                        runtimes = np.array(array)
                        sorted_runtimes = runtimes[np.argsort(runtimes)]
                        median = IntervalUtils.make_interval(runtimes = sorted_runtimes[-self.worstruns:], n_iterations = self.n_iterations
                         ,significance_level = self.significance_level)
                    else:
                        median = IntervalUtils.make_interval(runtimes = np.array(array), n_iterations = self.n_iterations
                             ,significance_level = self.significance_level)
                        desviation = np.std(np.array(array))
                elif self.useworstcase:
                    median = np.amax(np.array(array))
                    desviation = np.std(np.array(array))
                else:
                    median = np.median(np.array(array))
                    desviation = np.std(np.array(array))
        else:
            median = sys.maxsize
        return median, desviation


    
    def get_energy_consumption(self, passes: str = "-O3") -> Union[float, IntervalValue]:
        array = []
        measurer = \
            benchmark_measurer(_usuario_IP_experimentacion = "pi@192.168.3." + str(int(gethostname().split('-')[1]) + 1))

        if self.usedelay:
            measurer.main_speedup(send_compile_data = [measurer.aux_data[0], passes.split(" ")],            
            exec_data = [measurer.aux_data[0], self.runs, 0, random.randint(1, 3)],
            file_name = measurer.aux_data[0].split('/')[-1])

        else:
            measurer.main_speedup(send_compile_data = [measurer.aux_data[0], passes.split(" ")],
            exec_data = [measurer.aux_data[0], self.runs, 0, 0],
            file_name = measurer.aux_data[0].split('/')[-1])

        for i, data_iter in enumerate(measurer.data_file):
            if i != 0:
                array.append(data_iter[-1])
            
        if self.useinterval:
            if self.useworstcase:
                consumptions = np.array(array)
                sorted_consumptions = consumptions[np.argsort(consumptions)]
                median = IntervalUtils.make_interval(runtimes = sorted_consumptions[-self.worstruns:], n_iterations = self.n_iterations
                    ,significance_level = self.significance_level)
                desviation = np.std(np.array(array))
            else:
                median = IntervalUtils.make_interval(runtimes = np.array(array), n_iterations = self.n_iterations
                        ,significance_level = self.significance_level)
                desviation = np.std(np.array(array))
        elif self.useworstcase:
            median = np.amax(np.array(array))
            desviation = np.std(np.array(array))
        else:
            median = np.median(np.array(array))
            desviation = np.std(np.array(array))

        return median, desviation
    
    def get_energy_consumption_doom(self, passes: str = "-O3") -> Union[float, IntervalValue]:
        array = []
        if (os.path.exists("{}doomlegacy_optimized.bc".format(self.basepath))):
            os.remove("{}doomlegacy_optimized.bc".format(self.basepath))
        copyfile("{}doomlegacy_source/bin/doomlegacy_original.bc".format(self.basepath),"{}doomlegacy_optimized.bc".format(self.basepath))
        if self.toIR_doom(passes):
            os.system("bash {}doomlegacy_source/genGame.sh".format(self.basepath))


            measurer = \
                benchmark_measurer(_usuario_IP_experimentacion = "pi@192.168.3." + str(int(gethostname().split('-')[1]) + 1))

            if self.usedelay:
                measurer.doom_main_speedup(send_compile_data = ["doomlegacy_opt", passes.split(" ")],            
                exec_data = ["doomlegacy_opt", self.runs, 0, random.randint(1, 3)],
                file_name = "doomlegacy_opt")

            else:
                measurer.doom_main_speedup(send_compile_data = ["doomlegacy_opt", passes.split(" ")],
                exec_data = ["doomlegacy_opt", self.runs, 0, 0],
                file_name = "doomlegacy_opt")

            for i, data_iter in enumerate(measurer.data_file):
                if i != 0:
                    array.append(data_iter[-1])
                
            if self.useinterval:
                if self.useworstcase:
                    consumptions = np.array(array)
                    sorted_consumptions = consumptions[np.argsort(consumptions)]
                    median = IntervalUtils.make_interval(runtimes = sorted_consumptions[-self.worstruns:], n_iterations = self.n_iterations
                        ,significance_level = self.significance_level)
                    desviation = np.std(np.array(array))
                else:
                    median = IntervalUtils.make_interval(runtimes = np.array(array), n_iterations = self.n_iterations
                            ,significance_level = self.significance_level)
                    desviation = np.std(np.array(array))
            elif self.useworstcase:
                median = np.amax(np.array(array))
                desviation = np.std(np.array(array))
            else:
                median = np.median(np.array(array))
                desviation = np.std(np.array(array))
        else:
            median = sys.maxsize

        return median, desviation
    

    # To get the number of lines of code
    def get_codelines(self,passes: str = '-O3',source: str = "optimized.bc",
                  output: str = "optimized.ll") -> int:
        source = "{}{}".format(self.basepath,source.replace(".bc","_{}.bc".format(self.jobid)))
        output = "{}{}".format(self.basepath,output.replace(".bc","_{}.bc".format(self.jobid)))
        if self.toIR(passes):
            self.toAssembly()
            with open("{}optimized_{}.ll".format(self.basepath,self.jobid),'r') as file:
                result = -len(file.readlines())
        else:
            result = 0
        return result

    # To apply transformations
    def toIR(self, passes: str = '-O3') -> bool:
        if (os.path.exists("{}optimized_{}.bc".format(self.basepath,self.jobid))):
            os.remove("{}optimized_{}.bc".format(self.basepath,self.jobid))
        copyfile("{}{}".format(self.basepath,self.source),"{}optimized_{}.bc".format(self.basepath,self.jobid))
        result = self.allinone(passes)
        if not result:
            copyfile("{}{}".format(self.basepath,self.source),"{}optimized_{}.bc".format(self.basepath,self.jobid))
            result = self.onebyone(passes)
        return result

    # To apply transformations
    def toIR_doom(self, passes: str = '-O3') -> bool:
        if (os.path.exists("{}doomlegacy_optimized.bc".format(self.basepath))):
            os.remove("{}doomlegacy_optimized.bc".format(self.basepath))
        copyfile("{}doomlegacy_source/bin/doomlegacy_original.bc".format(self.basepath),"{}doomlegacy_optimized.bc".format(self.basepath))
        
        result = self.allinone_doom(passes)
        if not result:
            copyfile("{}doomlegacy_source/bin/doomlegacy_original.bc".format(self.basepath),"{}doomlegacy_optimized.bc".format(self.basepath))
            result = self.onebyone_doom(passes)
        return result

    # To transform from LLVM IR to assembly code
    def toAssembly(self, source: str = "optimized.bc", output: str = "optimized.ll"):
        source = "{}{}".format(self.basepath,source.replace(".bc","_{}.bc".format(self.jobid)))
        output = "{}{}".format(self.basepath,output.replace(".ll","_{}.ll".format(self.jobid)))
        os.system("{}llc {}{} -o {}{}".format(self.llvmpath,
                  self.basepath,source,self.basepath,output))

    # To apply transformations in one line
    def allinone(self, passes: str = '-O3') -> bool:
        result = True
        cmd = subprocess.Popen("{}opt-9 {} {}optimized_{}.bc -o {}optimized_{}.bc".format(
                                self.llvmpath,passes,self.basepath,self.jobid,self.basepath,
                                self.jobid),shell=True, stderr = subprocess.PIPE)
        try:
            cmd.wait(timeout=20)
            if cmd.returncode != 0:
                result = False
        except subprocess.TimeoutExpired as e:
            cmd.kill()
            print('Error {}'.format(e),file=sys.stderr)
            print('Sentence: {}'.format(passes),file=sys.stderr)
            result = False
        return result
    
    # To apply transformations in one line
    def allinone_doom(self, passes: str = '-O3') -> bool:
        result = True
        cmd = subprocess.Popen("{}opt-9 {} {}doomlegacy_optimized.bc -o {}doomlegacy_optimized.bc".format(
                                self.llvmpath,passes,self.basepath,self.basepath),shell=True, stderr = subprocess.PIPE)
        try:
            cmd.wait(timeout=120)
            if cmd.returncode != 0:
                result = False
        except subprocess.TimeoutExpired as e:
            cmd.kill()
            print('Error {}'.format(e),file=sys.stderr)
            print('Sentence: {}'.format(passes),file=sys.stderr)
            result = False
        return result
    
    # To apply transformations one by one
    def onebyone_doom(self, passes: str = '-O3') -> bool:
        result = True
        passeslist = passes.split(' ')
        self.onebyones += 1
        for llvm_pass in passeslist:
            cmd = subprocess.Popen("{}opt-9 {} {}doomlegacy_optimized.bc -o {}doomlegacy_optimized.bc".format(
                                    self.llvmpath,llvm_pass, self.basepath,
                                    self.basepath),shell=True)
            try:
                cmd.wait(timeout=20)
            except subprocess.TimeoutExpired as e:
                cmd.kill()
                print('Error {}'.format(e),file=sys.stderr)
                print('Sentence: {}'.format(passes),file=sys.stderr)
                result = False
        return result


    # To apply transformations one by one
    def onebyone(self, passes: str = '-O3') -> bool:
        result = True
        passeslist = passes.split(' ')
        self.onebyones += 1
        for llvm_pass in passeslist:
            cmd = subprocess.Popen("{}opt-9 {} {}optimized_{}.bc -o {}optimized_{}.bc".format(
                                    self.llvmpath,llvm_pass, self.basepath,self.jobid,
                                    self.basepath,self.jobid),shell=True)
            try:
                cmd.wait(timeout=20)
            except subprocess.TimeoutExpired as e:
                cmd.kill()
                print('Error {}'.format(e),file=sys.stderr)
                print('Sentence: {}'.format(passes),file=sys.stderr)
                result = False
        return result

    # To get the number of time onebyone is run
    def get_onebyone(self):
        return self.onebyones

    # To add a file to the output file
    @staticmethod
    def mergeDict(input_: str,output_: str):
        dic = dict()
        LlvmUtils.fileToDictionary(input_,dic)
        LlvmUtils.fileToDictionary(output_,dic)
        LlvmUtils.dictionaryToFile(output_,dic)

    # File to dictionary
    @staticmethod
    def fileToDictionary(input_: str, dic: list):
        with open(input_,"r") as file:
                lines = file.readlines()
                for line in lines:
                    index = line.rfind(',')
                    key = "["+"{}".format(line[:index])+"]"
                    value = "{}".format(line[index+1:])[:-1]
                    dic.update({key: value})

    # Dictionary to file
    @staticmethod
    def dictionaryToFile(filename: str, dic: list):
        with open(filename,"w") as file:
                for keys,values in dic.items():
                    key = '{}'.format(keys).replace("[","").replace("]","")
                    key = '{}'.format(key).replace(", ",",")
                    file.write('{},{}\n'.format(key,values))

    # To encode file from passes to integers
    @staticmethod
    def encode(input_: str, output_: str):
        with open(input_,'r') as inputfile:
            lines = inputfile.readlines()
            with open(output_,'w') as ouputfile:
                for line in lines:
                    index = line.rfind(',')
                    keys = "{}".format(line[:index]).split(",")
                    value = "{}".format(line[index+1:])[:-1]
                    newkey = ""
                    for key in keys:
                        newkey += '{},'.format(LlvmUtils.get_passes().index(key))
                    ouputfile.write('{}{}\n'.format(newkey,value))

    # To decode file from integers to passes
    @staticmethod
    def decode(input_: str,output_: str):
        with open(input_,'r') as inputfile:
            lines = inputfile.readlines()
            with open(output_,'w') as ouputfile:
                for line in lines:
                    index = line.rfind(',')
                    keys = "{}".format(line[:index]).split(",")
                    value = "{}".format(line[index+1:])[:-1]
                    newkey = ""
                    for key in keys:
                        newkey += '{},'.format(LlvmUtils.get_passes()[int(key)])
                    ouputfile.write('{}{}\n'.format(newkey,value))
