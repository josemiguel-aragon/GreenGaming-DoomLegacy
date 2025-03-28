import warnings
with warnings.catch_warnings():
	warnings.simplefilter('ignore', SyntaxWarning)

import pickle
import sys
import math
#sys.path.append("..")

from jmetal.core.problem import IntegerProblem
from jmetal.core.solution import IntegerSolution
from jmetal.algorithm.singleobjective import CellularGeneticAlgorithm
from jmetal.algorithm.multiobjective import NSGAII

from jmetal.operator.mutation import IntegerSimpleRandomMutation
from jmetal.operator.selection import BestSolutionSelection, RouletteWheelSelection
from jmetal.operator.crossover import IntegerTPXCrossover
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.util.neighborhood import L5

from llvmIntegerProblemV3doom import llvmIntegerProblem


### SETTINGS
config_max_evaluations = 10000 # Maximum number of evaluations for the GA
config_population_size = 100 # Total population size of the GA
config_offspring_population_size = 100 # Total offspring population size of the GA
config_probability_mutation = 1. / 300. # Mutation probability for the GA
config_probability_crossover = 1 # Crossover probability for the GA
config_solution_length = 300 # Sequence of passes length
config_assambly_lines = False # True means fitness = code lines
config_ec = True # True means fitness = energy consumption
config_dictionary_preloaded = False # True for load an initial dictionary
config_dictionary_name = 'dictionarys/llvm_dict_runtimes.data' # Path to the initial dictionary file
config_verbose = False # True enable logging output
config_jobid = "1" # Jobid for managing multiple process without race conditions
config_useinterval = False # True enable interval uncertainty treatment method
config_bootstrap_iterations = 500 # Total number of bootstrap replications to build the confidence interval
config_significance_level = 5 # Significance level of the confidence interval
config_multiobjective = False # True enable MO-GA usage
config_usedelay = False # True introduce a random delay between 1-3 seconds between execution time measurements
config_usenuma = False # True launch evaluations in a different NUMA unit than the GA
config_useworstcase = True # True enable worstcase uncertainty treatment method
config_custom = False # True enable our own MO uncertainty treatment approach
config_runs = 5 # Number of measurements to calculate the evaluation method
config_worstruns = 5 # Number of the worst runs used in the Interval + Worstcase uncertainty treatment method

if __name__ == '__main__':

    # Problem set
    problem = llvmIntegerProblem(max_evaluations = config_max_evaluations,
                                 population_size = config_population_size,
                                 offspring_population_size = config_offspring_population_size,
                                 solution_length = config_solution_length,
                                 dictionary_preloaded = config_dictionary_preloaded,
                                 dictionary_name = config_dictionary_name,
                                 assambly_lines = config_assambly_lines,
                                 ec = config_ec,
                                 verbose = config_verbose,
                                 jobid = config_jobid,
								 runs = config_runs,
                                 useinterval = config_useinterval,
                                 n_iterations = config_bootstrap_iterations,
                                 significance_level = config_significance_level,
                                 multiobjective = config_multiobjective,
								 custom = config_custom,
								 usedelay = config_usedelay,
								 usenuma = config_usenuma,
								 useworstcase = config_useworstcase,
								 worstruns = config_worstruns)

    algorithm = None
    if config_multiobjective:
        # Multiobjective Algorithm set
        algorithm = NSGAII(
            problem=problem,
            population_size=config_population_size,
            offspring_population_size=config_offspring_population_size,
            mutation=IntegerSimpleRandomMutation(config_probability_mutation),
            crossover=IntegerTPXCrossover(config_probability_crossover),
            termination_criterion=StoppingByEvaluations(max_evaluations=config_max_evaluations)
        )

    else:
        # Monoobjective Algorithm set
        algorithm = CellularGeneticAlgorithm(
            problem=problem,
            population_size=config_population_size,
            neighborhood=L5(int(math.sqrt(config_population_size)), int(math.sqrt(config_population_size))),
            mutation=IntegerSimpleRandomMutation(config_probability_mutation),
            crossover=IntegerTPXCrossover(config_probability_crossover),
            termination_criterion=StoppingByEvaluations(max_evaluations=config_max_evaluations)
        )

    algorithm.run()

    with open("results.data","w") as file:
        #Outputs
        file.write('\nSettings:')
        file.write(f'\n\tAlgorithm: {algorithm.get_name()}')
        file.write(f'\n\tProblem: {problem.get_name()}')
        file.write(f'\n\tComputing time: {algorithm.total_computing_time} seconds')
        file.write(f'\n\tMax evaluations: {config_max_evaluations}')
        file.write(f'\n\tPopulation size: {config_population_size}')
        file.write(f'\n\tOffspring population size: {config_offspring_population_size}')
        file.write(f'\n\tProbability mutation: {config_probability_mutation}')
        file.write(f'\n\tProbability crossover: {config_probability_crossover}')
        file.write(f'\n\tSolution length: {config_solution_length}')
        file.write(f'\n\tInterval values: {config_useinterval}')
        file.write(f'\n\tBootstrap iterations: {config_bootstrap_iterations}')
        file.write(f'\n\tSignificance level: {config_significance_level}')
        file.write(f'\n\tOpt executed one by one: {problem.get_onebyone()} times')
        file.write('\nResults:')
        if config_multiobjective:
            for solution in algorithm.get_result():
                file.write(f'\n\tBest solution: {solution.variables}')
                file.write(f'\n\tFitness: [{solution.objectives[0]}, {solution.objectives[1]}]')
        else:
            file.write(f'\n\tBest solution: {algorithm.get_result().variables}')
            file.write(f'\n\tFitness: {algorithm.get_result().objectives[0]}')


    with open("solutions.data","wb") as solution_file:
        pickle.dump(algorithm.solutions, solution_file)

    print('\nSettings:')
    print(f'\tAlgorithm: {algorithm.get_name()}')
    print(f'\tProblem: {problem.get_name()}')
    print(f'\tComputing time: {algorithm.total_computing_time} seconds')
    print(f'\tMax evaluations: {config_max_evaluations}')
    print(f'\tPopulation size: {config_population_size}')
    print(f'\tOffspring population size: {config_offspring_population_size}')
    print(f'\tProbability mutation: {config_probability_mutation}')
    print(f'\tProbability crossover: {config_probability_crossover}')
    print(f'\tSolution length: {config_solution_length}')
    print(f'\tInterval values: {config_useinterval}')
    print(f'\tBootstrap iterations: {config_bootstrap_iterations}')
    print(f'\tSignificance level: {config_significance_level}')
    print(f'\tOpt executed one by one: {problem.get_onebyone()} times')
    print('\nResults:')
    if config_multiobjective:
        for solution in algorithm.get_result():
            print(f'\tBest solution: {solution.variables}')
            print(f'\tFitness: [{solution.objectives[0]}, {solution.objectives[1]}]')
    else:
        print(f'\tBest solution: {algorithm.get_result().variables}')
        print(f'\tFitness: {algorithm.get_result().objectives[0]}')
