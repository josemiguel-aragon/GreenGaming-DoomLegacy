import sys

from jmetal.core.problem import IntegerProblem
from jmetal.core.solution import IntegerSolution
import os

from LlvmUtilsV5 import LlvmUtils

class llvmIntegerProblem(IntegerProblem):

    def __init__(self, is_minimization: bool = True, max_evaluations: int = 25000,
                 from_file: bool = False, filename: str = None, solution_length: int = 100,
                 population_size = int, offspring_population_size = int, verbose: bool = True,
                 upper_bound : int = 86, assambly_lines: bool = True, ec: bool = False, jobid: str = "0",
                 dictionary_preloaded: bool = True, dictionary_name: str = 'dictionarys/llvm_dict_runtimes.data',
                 useinterval: bool = False, n_iterations: int = 500, significance_level: int = 5,
                 multiobjective: bool = False, custom: bool = False, usedelay: bool = False, usenuma: bool = False,
                 useworstcase: bool = False, worstruns: int = 5, runs: int = 5):

        self.jobid = jobid
        self.useinterval = useinterval
        self.llvm = LlvmUtils(jobid = self.jobid, runs = runs, worstruns = worstruns, useinterval = useinterval, n_iterations = n_iterations,
                              significance_level = significance_level, usedelay = usedelay, usenuma = usenuma, useworstcase = useworstcase)
        self.number_of_variables = solution_length
        self.lower_bound = [0 for _ in range(self.number_of_variables)]
        self.upper_bound = [upper_bound for _ in range(self.number_of_variables)]
        self.obj_directions = [self.MINIMIZE if is_minimization else self.MAXIMIZE]
        self.custom = custom

        if multiobjective:
            self.number_of_objectives = 2
        else:
            self.number_of_objectives = 1

        self.number_of_constraints = 0
        self.is_minimization = is_minimization
        self.max_evaluations = max_evaluations
        self.evaluations = 0
        self.epoch = 1
        print('epoch {}'.format(self.epoch))
        self.phenotype = 0
        self.population_size = population_size
        self.offspring_population_size = offspring_population_size
        self.assambly_lines = assambly_lines # True means fitness = code lines
        self.ec = ec # True means fitness = ec
        self.dictionary = dict()
        self.verbose = verbose
        self.multiobjective = multiobjective
        if dictionary_preloaded:
            LlvmUtils.fileToDictionary(dictionary_name,self.dictionary)
        
        # Generate doomlegacy binary file
        os.system("bash /home/pi/experimentos/doomlegacy_source/genBinary.sh")


    def get_name(self):
        return 'Llvm Integer Problem Version 3'

    def evaluate(self, solution: IntegerSolution) -> IntegerSolution:
        self.phenotype +=1
        limit = [self.offspring_population_size if self.epoch != 1 else self.population_size]
        if self.phenotype%(limit[0]+1) == 0:
            self.epoch += 1
            self.phenotype = 1
            print("epoch {}".format(self.epoch))
        key = "{}".format(solution.variables)
        value = self.dictionary.get(key)
        if value == None: # When the key is not in dictionary
            # Decode
            passes = ""
            for i in range(self.number_of_variables):
                passes += " {}".format(LlvmUtils.get_passes()[solution.variables[i]])
            # Fitness
            if self.assambly_lines:
                solution.objectives[0] = self.llvm.get_codelines(passes=passes)
            elif self.ec:
                if self.multiobjective and self.useinterval:
                    if not self.custom:
                        interval, _ = self.llvm.get_energy_consumption_doom(passes=passes)

                        solution.objectives[0] = interval.upper_bound
                        solution.objectives[1] = interval.center()
                    else:
                        interval, desviation = self.llvm.get_energy_consumption_doom(passes=passes)

                        solution.objectives[0] = interval
                        solution.objectives[1] = desviation
                else:
                    solution.objectives[0], _ = self.llvm.get_energy_consumption_doom(passes=passes)
            else:
                if self.multiobjective and self.useinterval:
                    if not self.custom:
                        interval, _ = self.llvm.get_runtime(passes=passes)

                        solution.objectives[0] = interval.upper_bound
                        solution.objectives[1] = interval.center()
                    else:
                        interval, desviation = self.llvm.get_runtime(passes=passes)

                        solution.objectives[0] = interval
                        solution.objectives[1] = desviation
                else:
                    solution.objectives[0], _ = self.llvm.get_runtime(passes=passes)
            self.dictionary.update({key: solution.objectives[0]})
        else: # When the key is in dictionary
            solution.objectives[0] = value
        if self.verbose:
            #print("evaluated solution {:3} from epoch {:3} : variables = {}, fitness = {:>7}"\
            #       .format(self.phenotype,self.epoch,solution.variables,solution.objectives[0]))
            if self.phenotype == 1 and self.epoch == 1 :
                with open(f"solutions_{self.population_size}_{self.offspring_population_size}_{self.jobid}.data","w") as file:
                    file.write("{} {} {} {}\n".format("epoch","iter","variables","fitness"))
            with open(f"solutions_{self.population_size}_{self.offspring_population_size}_{self.jobid}.data","a") as file:
                file.write("{:03} {:03} {} {}\n"\
                   .format(self.epoch,self.phenotype,solution.variables,-solution.objectives[0]))
        return solution

    def get_onebyone(self):
        return self.llvm.get_onebyone()

    ### FOR TERMINATION CRITERION ###
    def update(self, *args, **kwargs):
        self.evaluations = kwargs['EVALUATIONS']

    ### FOR TERMINATION CRITERION ###
    @property
    def is_met(self):
        met = self.evaluations >= self.max_evaluations
        if self.phenotype*self.epoch % 100 == 0 or met:
            if met:
                filename = "new_dictionary_{}_{}_{}_{}.data".format(self.population_size,
                            self.offspring_population_size, self.phenotype*self.epoch,
                            self.jobid)
            elif self.phenotype*self.epoch % 500 == 0:
                filename = "tmp_solutions_{}_{}_{}_{}.data".format(self.population_size,
                            self.offspring_population_size, self.phenotype*self.epoch,
                            self.jobid)
            LlvmUtils.dictionaryToFile(filename,self.dictionary)
        return met
