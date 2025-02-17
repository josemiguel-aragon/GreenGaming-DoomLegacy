# Main que orquesta toda la ejecución, así como transferencia de archivos y creación de directorios.

# Configuración del archivo al final del mismo

from os import mkdir, listdir, system
from os.path import isdir,isfile
#from re import I

from jmetal.core.problem import IntegerProblem
from jmetal.core.solution import IntegerSolution
from jmetal.algorithm.singleobjective import GeneticAlgorithm

from jmetal.operator.mutation import IntegerPolynomialMutation
from jmetal.operator.selection import BestSolutionSelection, RouletteWheelSelection
from jmetal.operator.crossover import IntegerSBXCrossover
from jmetal.util.termination_criterion import StoppingByEvaluations

from math import ceil

import csv

from jmetal.util.generator import Generator

from random import randint

from datetime import datetime

from typing import TypeVar, List

from numpy import mean, count_nonzero
from numpy.core.defchararray import upper

import requests

import getopt, sys

from create_file_all_c_bc import create_file_all_c_bc

from subprocess import call

__autor__="Jesús Morales Millán"
__contact__="jesus.morales@uca.es"

class Suite_Execution_Problem(IntegerProblem):

	def get_name(self) -> str:
		return 'Suite_Execution_Problem'

	def __init__(self, _bool_minimize, _objective_time, _route_bench, _flags=[], _rate_max_solutions=0.3):

		super(Suite_Execution_Problem, self).__init__()

		self.number_of_objectives=1
		
		self.number_of_constraints=0

		self.list_bench=[]
		self.list_bench_w_route=[]

		for f_ in listdir(_route_bench):
			if not isfile(_route_bench+f_):
				for f in listdir(_route_bench+f_):
					if not isfile(_route_bench+f_+'/'+f):
						self.list_bench+=[f]
						self.list_bench_w_route+=[_route_bench+f_+'/'+f]

		self.power=dict()
		self.time=dict()

		self.objective_time=_objective_time
		
		print('Calculando el consumo de los benchmarks...')

		for i in listdir('./experimentos/mediciones/'):
			if i[:len("mean-std-and-time-seconds-")]=="mean-std-and-time-seconds-":
				name_benchmark=i.index("mean-std-and-time-seconds-")+len("mean-std-and-time-seconds-")
				name_benchmark=i[name_benchmark:name_benchmark+i[name_benchmark:].index('-')]
				with open('./experimentos/mediciones/'+i,'r') as file:
					reader=csv.reader(file)
					num_rows=0
					for row in reader:
						num_rows+=1
						self.power[name_benchmark]+=float(row[5])
						self.time[name_benchmark]+=float(row[2])
					self.power[name_benchmark]/=num_rows
					self.time[name_benchmark]/=num_rows

		print('Consumo del basal calculado como una constante')
		self.basal_consumption=(0.13*1670*self.objective_time)*(5/(1670*self.objective_time))*self.objective_time

		print('')

		print('Inicializando variables adicionales...')

		self.number_of_variables=len(self.list_bench_w_route)

		self.bool_minimize=_bool_minimize
		self.objective_direction=self.MINIMIZE

		if type(_flags)==list:
			self.list_str_flags=_flags
		else:
			if type(_flags)==str:
				self.list_str_flags=_flags.split(' ')

		self.rate_max_solutions=_rate_max_solutions

		if not isdir('./experimentos/genetic_data'):
			mkdir('./experimentos/genetic_data')

		self.lower_bound=[]
		self.upper_bound=[]
		for bench in self.list_bench:
			self.lower_bound+=[0]
			self.upper_bound+=[int(self.objective_time/self.time[bench])]
		self.max_possible_power=sum([self.power[bench]*self.upper_bound[i]\
			for i,bench in enumerate(self.list_bench)])

		self.max_possible_time=sum([self.time[bench]*self.upper_bound[i]\
			for i,bench in enumerate(self.list_bench)])

		self.min_time=0

	def normalize_time_distance_from_objective(self,time):
		#		distancia al objetivo - 0   /max(distancia del máximo tiempo al objetivo,distancia del objetivo al 0) - 0
		return abs(time-self.objective_time)/max(self.max_possible_time-self.objective_time,self.objective_time)

	def normalize_power_consumption(self,power):
		return (power-self.basal_consumption)/(self.max_possible_power-self.basal_consumption)
		#return power/self.max_possible_power
	
	def create_solution(self) -> IntegerSolution:
		solution=IntegerSolution(lower_bound=self.lower_bound,upper_bound=self.upper_bound,\
			number_of_objectives=self.number_of_objectives,number_of_constraints=self.number_of_constraints)
		
		solution.variables=[randint(self.lower_bound[i],self.upper_bound[i]) for i,_ in enumerate(self.list_bench)]
		return solution

	def evaluate(self, solution: IntegerSolution) -> IntegerSolution:
		sum_time=0
		sum_power=0
		fitness=0
		
		#str_aux=[]

		# Calculo el tiempo y potencia de la solución
		for iterations,bench in zip(solution.variables,self.list_bench):
			sum_time+=self.time[bench]*iterations
			sum_power+=self.power[bench]*iterations
		
		fitness+=self.normalize_time_distance_from_objective(sum_time)
			# ^^^ Cuánto tiempo ha tardado con respecto del objetivo
		
		#str_aux+=[self.normalize_time_distance_from_objective(sum_time)]

		fitness+=((len(solution.variables)-count_nonzero(solution.variables))/solution.number_of_variables)
			# ^^^ Cuánta variabilidad tiene
		
		#str_aux+=[((len(solution.variables)-count_nonzero(solution.variables))/solution.number_of_variables)]

		# La distancia con respecto del consumo, afectando de una manera u otra al fitness
		# en función de si se desea acercase al consumo basal o alejarse de este. En otras
		# palabras, minimizar o maximizar el consumo, respectivamente.

		if sum_power<self.basal_consumption:
			# Alternativa 1:
			# Normalizamos la distancia al basal en un rango [0-basal], para luego multiplicarla por 3,
			# quedando el resultado en un rango [0-3], que penalizará la solución
			#fitness+=((sum_power-self.basal_consumption)/self.basal_consumption)*3
			
			# Alternativa 2: Sumamos una constante para asegurarnos de que se penaliza lo suficiente 
			# (el fitness considera 3 criterios, incluyendo este, que valora en un rango 0 a 1).
			fitness+=4

			#str_aux+=[4]
		else:
			if self.bool_minimize:
				#str_aux+=[self.normalize_power_consumption(sum_power)]
				fitness+=self.normalize_power_consumption(sum_power)
			else:
				#str_aux+=[1-self.normalize_power_consumption(sum_power)]
				fitness+=1-self.normalize_power_consumption(sum_power)
		
		#print(solution.variables,'\t'.join(str_aux))

		solution.objectives[0]=fitness


S = TypeVar('S')

class Suite_Execution_Genetic(GeneticAlgorithm):

	def create_initial_solutions(self) -> list:
		population=[self.problem.create_solution() for _ in range(self.population_size)]
		
		return population

	def replacement(self, population: List[S], offspring_population: List[S]) -> List[S]:
		population.extend(offspring_population)
		#print(len(offspring_population))
		#print(self.evaluations)
		
		#print('Población:')
		#for e in population:
			#print('\t\t',e.variables,'\t\t Evaluación: ',e.objectives[0])
		#print('')
		#print('')
		progreso=(self.evaluations/self.termination_criterion.__getattribute__("max_evaluations"))
		print('Progreso del algoritmo:')
		print('['+'='*ceil(progreso*20)+' '*(20-ceil(progreso*20))+'] '+str(progreso*100)+'%')
		print('')

		population.sort(key=lambda s: s.objectives[0])
		
		mod_population=[]
		for i in range(0,len(population)):
			mod_population+=[population[i].variables]
		
		limit_size=int(len(population)*self.problem.rate_max_solutions)
		
		i=0
		while i!=len(population):
			if mod_population.count(mod_population[i])>limit_size:
				population.pop(i)
				mod_population.pop(i)
			else:
				i+=1
		
		if not isfile('./experimentos/genetic_data/population_ga.csv'):
			with open('./experimentos/genetic_data/population-ga.csv', 'w', newline='') as file:
				csv.writer(file).writerows([\
					['N Iteración','Resultado consumo','Iteraciones'],\
					['Benchmarks, en el mismo orden que el vector individuo:']+self.problem.list_bench,\
				])

		n_iters=self.termination_criterion.__getattribute__("max_evaluations")/self.population_size
		with open('./experimentos/genetic_data/population-ga.csv', 'a', newline='') as file:
			writer=csv.writer(file)
			
			for solution in population:
				writer.writerow([progreso*n_iters,solution.objectives[0]]+solution.variables)

		return population[:self.population_size]    

	def stopping_condition_is_met(self) -> bool:
		return super().stopping_condition_is_met()

if __name__=="__main__":


	# Configuración de variables

	population_size=100			# Tamaño de la población del algoritmo

	prob_mutation=0.1			# Probabilidad de mutación, con valor de 0 a 1
	prob_cross=0.2				# Probabilidad de cruce, con valor de 0 a 1

	n_iters=50					# Número de iteraciones que se realiza el algoritmo genético.
								# Se define este valor como criterio de parada del mismo.

	bool_minimize=True			# Booleano que indica si se desea maximizar o minimizar el consumo
								# con respecto del basal.

	seconds_time_objective=120	# Tiempo de ejecución que se persigue como objetivo dentro del algoritmo,
								# el cual debe pretender acercarse en el intento de buscar la solución ideal.


	flags=[]					# Passes o flags de compilación LLVM.

	# ---------------------------------
		
	bool_uploadDrive=False      # Si se especifica a True, sube los archivos a Google Drive al finalizar

	route_bench="./experimentos/EEMBC_benchmark_suites/" 
								# Ruta al benchmark. pc_launch siempre lo envía a la misma
								# ruta, por lo que no se necesita modificar.

	# ---------------------------------

	# ---------------------------------

	if route_bench[-1]!='/':
		route_bench+='/'

	if not isdir('./experimentos/genetic_data'):
		mkdir('./experimentos/genetic_data')
	
	print('Inicializando objeto que representa al problema...')
	problem=Suite_Execution_Problem(_bool_minimize=bool_minimize,\
		_objective_time=seconds_time_objective,_route_bench=route_bench)

	print('Inicilizado objeto que representa al problema.')
	algorithm = Suite_Execution_Genetic(
	problem=problem,
	population_size=population_size,
	offspring_population_size=population_size,
	#mutation=IntegerPolynomialMutation(1.0 / problem.number_of_variables, 20.0),
	mutation=IntegerPolynomialMutation(prob_mutation),
	crossover=IntegerSBXCrossover(prob_cross),
	selection=RouletteWheelSelection(),
	#termination_criterion=StoppingByEvaluations(max_evaluations=population_size*n_iters)
	termination_criterion=StoppingByEvaluations(max_evaluations=population_size*n_iters)
	)

	print('Se inicia el algoritmo genético...')
	print('')
	print('-----------------------------------')
	algorithm.run()

	result = algorithm.get_result()

	print('')
	print('-----------------------------------')
	print('')
	
	print('Algoritmo genético terminado. Imprimiendo resultados:')
	print('Algoritmo: {}'.format(algorithm.get_name()))
	print('Problema	: {}'.format(problem.get_name()))
	print('Solución	: {}'.format(result.variables))
	print('Fitness 	: {}'.format(result.objectives[0]))
	print('T. ejec	: {}'.format(algorithm.total_computing_time))

	with open('./experimentos/genetic_data/final-population-ga.csv', 'a', newline='') as file:
		writer=csv.writer(file)
		for solution in algorithm.solutions:
			writer.writerow([solution.objectives[0]]+solution.variables)

	create_file_all_c_bc(route_bench=route_bench,iteraciones=result.variables,flags=flags,
	list_benchmarks=problem.list_bench,list_benchmarks_with_route=problem.list_bench_w_route)

	call(["cp",route_bench+'benchmarks_all/all.c','./experimentos/genetic_data/'],shell=False)

	call(["cp",route_bench+'binaries/benchmarks_all/all','./experimentos/genetic_data/'],shell=False)

	call(["cp",route_bench+'bc/benchmarks_all/all.bc','./experimentos/genetic_data/'],shell=False)

	if bool_uploadDrive:
		url = "https://www.google.es"
		try:
			requests.get(url)
			print("Subiendo archivos a Drive")
			system('rclone copy -P ~/experimentos/genetic_data/ gdrive:genetic_`date +%Y.%m.%d`')
			system('rclone copy -P ~/experimentos/mediciones/ gdrive:genetic_`date +%Y.%m.%d`')
			print('Subida completada en ' + str(datetime.now()))
		except:
			print('No Internet connection found')