####################################################################################
#                                       Atención
#
#   El uso de esta clase es la de ser heredada por otra, donde a su vez, se deben de 
#   definir los métodos "compile_send_all", "send_and_compile_file" y "execute_file".
#
#   Entre los dos primeros métodos, se debe de conseguir la funcionalidad de compilar 
#   los ficheros que sean necesarios, que estos sean enviados al dispositivo de experimentación.
#   El último, "execute_file", manda a la de experimentación a ejecutar un archivo.
#
#   "compile_send_all" se llama una única vez en el constructor, mientras que los otros
#   se llaman posteriormente al ejecutar la función "main". 
# 
#   "compile_send_all" recibe la variable "_aux_data" por parámetro, por si fuese necesario. 
#   Del mismo modo, "send_and_compile_file" y "execute_file" reciben una variable por parámetro.
#
#   Por si fuese necesario, se define un atributo en el constructor llamada "aux_data", 
#   para que se le de el uso que se considere necesario, en caso de que se necesite de forma externa
#   en el objeto creado o interna.
#   
#   El dispositivo de experimentación debe de tumbar los servicios, cambiar el valor de
#   pin_ejecucion_general a alto, y hacer un bucle de n iteraciones,
#   donde se pone en alto el pin_ejecucion antes de cada ejecución, para luego ponerlo en bajo.
#   Deben de haber al menos 4 segundos entre que se tumban y se levantan los servicios.
#   Es estrictamente necesario esperar estos.
#
#   Métodos a usar:
#   - Constructor: Se inicializa un objeto de la clase Measurer.
#   - main: Se manda a medir un determinado programa dado por el valor de sus variables.
#	- main speedup: Se manda a medir un determinado programa dado por el valor de sus variables,
# 	almacenando el resultado al final de la ejecución y en memoria, en los atributos "measures_file"
#	y "data_file".
#	- main basal: Se manda a medir el consumo del sistema operativo inactivo.
#   - shutdown: Se finaliza la lectura del INA y almacenaje en el buffer, indicando así
#       que no se van a realizar más mediciones. Es NECESARIO que este se ejecute una vez.
#      
####################################################################################

# Autor: Jesús Morales
# Implementación hecha en Python 3.6.9

# Enlaces usados:

# https://python-forum.io/thread-27644.html

# https://docs.python.org/3.6/library/concurrent.futures.html

# https://www.tecmint.com/ssh-passwordless-login-using-ssh-keygen-in-5-easy-steps/

# https://stackoverflow.com/questions/44576167/force-child-class-to-override-parents-methods/44576235

# Inclusión de librerías

#from time import time

from time import monotonic as time

import digitalio, board

from ina219 import INA219 as INAClass

#import threading

from os import system, nice

#from os import system,mkdir
#from os.path import isdir

#from os import chdir,listdir
#from os.path import isfile, join

import csv

from abc import abstractmethod, ABC

from numpy import mean, std, sum
#from math import sqrt

__autor__="Jesús Morales Millán"
__contact__="jesus.morales@uca.es"

def printBold (str):
	print('\033[1m' + str + '\033[0m')

# Definición de clase

class Measurer(ABC):
	
	def __init__(self, _usuario_IP_experimentacion,voltage_ina=16,current_ina=2400, ina_address=0x40, _aux_data=[]):

		"""
		Variables de entrada:
		 - _usuario_IP_experimentacion = usuario e IP del equipo de experimentación, usado para conectar
		       con la misma mediante ssh.
		       Ejemplo: _usuario_IP_experimentacion = "pi@192.168.3.14"

		 - voltage_ina,current_ina= Valores de voltaje y amperaje del INA. Estos valores dependen 
		       estrechamente del driver del INA, no se pueden asignar de forma arbitraria.
		
		 - ina_address= Dirección del INA a usar.
		
		 - _aux_data= Estructura de datos usada por el método "compile_send_all".
		"""

		printBold("Inicializando...")

		# Lanzar sesión
		self.usuario_IP_experimentacion=_usuario_IP_experimentacion
		try:
			system("ssh -t "+self.usuario_IP_experimentacion+" tmux new -d -s mySession")
		except:
			printBold("Fallo al iniciar sesión")
			raise Exception

		# Pin de ejecución - iteración
		self.pin_ejecucion=digitalio.DigitalInOut(board.D26)

		# Pin de escritura
		self.pin_escritura_disco=digitalio.DigitalInOut(board.D19)

		#Pin de ejecución - general
		self.pin_ejecucion_general=digitalio.DigitalInOut(board.D13)

		# Inicializar pines
		self.iniciar_pines()

		# Inicialización de variables a usar
			# Creación de un buffer donde se almacenan las lecturas del INA.
			# Creación de un buffer donde se almacenan los timestamps correspondientes 
			# a las lecturas.
		self.buffer=[]
		self.buffer_time=[]

		# Variable que controla que se haga la obtención de valores del INA
		#self.condition=True

		# Variable auxiliar que ayuda al control de los datos necesarios.
		self.aux_data=[]

		# Inicialización de INA219
		self.ina1=INAClass(i2c_bus=1, i2c_addr=ina_address)
		self.ina1.set_mode(newMode=self.ina1.MODE_SVOLT_CONTINUOUS)
		self.ina1.set_bus_adc_resolution(self.ina1.ADCRES_12BIT_1S)
		self.ina1.set_shunt_adc_resolution(self.ina1.ADCRES_12BIT_1S)
		self.ina1.set_config()
		
		#self.ina1.set_rshunt(0.1) # Configuración de los ohmios
		
		# Voltios con los que se presupone que el dispositivo funciona.
		self.volts=5

		# Archivo que guarda las lecturas de intensidad. En disco, tendrá un nombre de
		# "consumption-". Esta variable es una lista de listas, donde cada lista corresponde
		# a una iteración del programa que se desee medir.
		self.measures_file=[]
		
		# Archivo que guarda información relevante procesada mediante las lecturas de 
		# intensidad tomadas. En disco, tendrá un nombre de "data-". Esta variable es una 
		# lista de listas, donde cada lista corresponde a una iteración del programa que se desee medir.
		self.data_file=[]

		# Archivo que guarda las tomas de tiempo correspondiente a las lecturas de intensidad. 
		# En disco, tendrá un nombre de "timestamps-". Esta variable es una lista de listas, 
		# donde cada lista corresponde a una iteración del programa que se desee medir.
		self.timestamps_file=[]
		
		# Se compilan todos los programas, utilizando la variable _aux_data recibida como hiperparámetro.
		printBold("Compilando...")
		self.aux_data=[]

		self.compile_send_all(_aux_data)

		printBold("Inicializado.")

	@abstractmethod
	def compile_send_all(self,aux_data=[]):
		"""
		Compila y envía todos los archivos necesarios para la ejecución
		"""
		pass
	
	@abstractmethod
	def send_and_compile_file(self,send_compile_data=[]):
		"""
		Compila y envía un solo archivo
		"""
		pass

	@abstractmethod
	def execute_file(self,exec_data=[]):
		"""
		Ordena al dispositivo de experimentación a ejecutar un archivo
		"""
		pass
	
	def custom_sleep(self,seconds):
		"""
		Método de espera personalizado mediante espera ocupada.
		"""
		t__=time()+seconds

		while time()<t__:
			pass

	def checkPin(self,pin,updownstate):
		"""
		Comprueba que un pin GPIO tiene el valor dado por updownstate, ya sea alto (1) o bajo (0).
		La espera introducida asegura que no se puedan producir rebotes.
		"""
		# Comprueba que el valor es el deseado
		if pin.value == updownstate:
			# Se realiza una espera
			self.custom_sleep(0.001)
			#self.custom_sleep(0.003)

			# Si el valor sigue siendo así, se devuelve "True"
			if pin.value == updownstate:
				return True
				
		return False

	def iniciar_pines(self):
		"""
		Se inicializan los pines GPIO.
		"""
		# Pin de ejecución
		# Controlado por el dispositivo de experimentación.
		# Indica si se está haciendo una iteración (alto) o no (bajo) de un determinado programa.
		self.pin_ejecucion.direction=digitalio.Direction.INPUT
		self.pin_ejecucion.pull=digitalio.Pull.UP

		#Pin de ejecución - general
		# Controlado por el dispositivo de experimentación.
		# Indica si se ha finalizado la ejecución de todos los programas.
		self.pin_ejecucion_general.direction=digitalio.Direction.INPUT
		self.pin_ejecucion_general.pull=digitalio.Pull.UP

		#Pin de escritura
		# Controlado por el dispositivo de medición.
		# Indica si se está realizando una escritura en disco.
		self.pin_escritura_disco.direction = digitalio.Direction.OUTPUT
		self.pin_escritura_disco.value = True

		# Damos una pequeña espera para dar tiempo a que los pines se inicialicen correctamente,
		# evitando posibles valores incorrectos por rebote.
		self.custom_sleep(0.01)
	
	def synchronizer(self,send_compile_data,exec_data,file_name="file"):
		"""
		Método principal, llamado por main, que se encarga de compilar, mandar los archivos necesarios al
		dispositivo de ejecución, realizar la ejecución y almacenar los valores resultantes.
		"""

		# Se compilan los programas necesarios, usando el parámetro de datos de compilación.
		self.send_and_compile_file(send_compile_data)

		# Se inicializa el archivo "data" donde se almacenan los datos relevantes procesados.
		# La primera fila contiene una etiqueta del significado de cada columna.
		with open('./experimentos/mediciones/data-'+file_name+'.csv','a') as file:
			csv.writer(file).writerow(['Mean measures (mA)','std measures',
				'execution time (seconds)', 'Total miliamps measured', 'Number of measures','Energy consumption (mWs)'])

		#system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "python3 SPACE ./experimentos/pin_initialization_experipi.py ENTER"')

		#self.custom_sleep(0.1)

		# Se ejecuta el archivo correspondiente.
		self.execute_file(exec_data)

		# Se realiza una espera para dar tiempo al dispositivo de experimentación a realizar las inicializaciones necesarias.
		self.custom_sleep(0.5)

		init_variables=True
		
		# Si hay ejecuciones de programas pendientes aún...
		while self.checkPin(self.pin_ejecucion_general,True):

			# Inicializa las variables
			if init_variables:
				# Inicializamos las variables a utilizar y se baja el semáforo, permitiendo que el 
				# dispositivo de experimentación ejecute.
				self.buffer=[]
				self.buffer_time=[]
				init_variables=False

				self.pin_escritura_disco.value=False

			# Si está ejecutando algo... (lo sabemos porque pin_ejecucion, pin que indica la ejecución de una
			# iteración de un programa, está en alto)
			if self.checkPin(self.pin_ejecucion,True):
				# Tomamos el tiempo de inicio y se baja el semáforo, impidiendo el paso a futuras ejecuciones
				# aparte de la actual.
				t_init=time()
				self.pin_escritura_disco.value=True
				
				# Mientras no se finaliza la ejecución, se toman los valores de intensidad y tiempo.
				while not self.checkPin(self.pin_ejecucion,False):
					self.buffer+=[round(self.ina1.check_conv_bit_and_return_current_ma(),6)]
					self.buffer_time+=[time()]

				# Tomamos el tiempo de finalización de la ejecución.
				t_end=time()

				# Indicamos que, más adelante, se deben de reinicializar las variables, y que se debe 
				# de bajar el semáforo para dejar que se continue ejecutando.
				init_variables=True
				
				# Guardamos las lecturas tomadas de intensidad.
				with open('./experimentos/mediciones/consumption-'+file_name+'.csv','a') as file:
					csv.writer(file).writerow(self.buffer)
				
				# Calculamos el consumo energético
				energy=0
				for i in range(0,len(self.buffer)-1):
					energy+=self.buffer[i]*(self.buffer_time[i+1]-self.buffer_time[i])*self.volts

				# Se guarda en disco los datos de análisis calculados a partir de las lecturas.
				sum_=sum(self.buffer,axis=0)
				with open('./experimentos/mediciones/data-'+file_name+'.csv','a') as file:
					csv.writer(file).writerow([\
						mean(self.buffer,axis=0), #mean
						std(self.buffer,axis=0),  # std
						t_end-t_init,  # execution time (seconds)
						sum_, # Total miliamps measured
						len(self.buffer), # Number of measures
						energy # Power consumption in mWs
						#(sum_)*(self.volts/len(self.buffer))*(t_end-t_init) # Quick power consumption in mWs
							# Con este método, se supone que el tiempo entre muestras es constante.
					])
				
				# Se guarda en disco los datos de las tomas de tiempo correspondientes a las lecturas
				# de intensidad tomadas.
				with open('./experimentos/mediciones/timestamps-'+file_name+'.csv','a') as file:
					csv.writer(file).writerow(self.buffer_time)
				
				self.aux_buffer = self.buffer


		# Se reinializan las variables que guardan las lecturas.	
		self.buffer=[]
		self.buffer_time=[]

	def doom_synchronizer_speedup(self,send_compile_data,exec_data,file_name="file"):
		# Se compilan los programas necesarios, usando el parámetro de datos de compilación.
		self.doom_send_and_compile_file(send_compile_data)

		#system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "python3 SPACE ./experimentos/pin_initialization_experipi.py ENTER"')
		
		#self.custom_sleep(0.1)

		# Se ejecuta el archivo correspondiente.
		self.doom_execute_file(exec_data)

		# Se realiza una espera para dar tiempo al dispositivo de experimentación a realizar las inicializaciones necesarias.
		self.custom_sleep(0.5)

		init_variables=True
		

		# Archivo que guarda las lecturas de intensidad. En disco, tendrá un nombre de
		# "consumption-". Esta variable es una lista de listas, donde cada lista corresponde
		# a una iteración del programa que se desee medir.
		self.measures_file=[]
		
		# Archivo que guarda información relevante procesada mediante las lecturas de 
		# intensidad tomadas. En disco, tendrá un nombre de "data-". Esta variable es una 
		# lista de listas, donde cada lista corresponde a una iteración del programa que se desee medir.
		self.data_file=[['Mean measures (mA)','std measures',
			'execution time (seconds)', 'Total miliamps measured', 'Number of measures','Energy consumption (mWs)']]

		# Archivo que guarda las tomas de tiempo correspondiente a las lecturas de intensidad. 
		# En disco, tendrá un nombre de "timestamps-". Esta variable es una lista de listas, 
		# donde cada lista corresponde a una iteración del programa que se desee medir.
		self.timestamps_file=[]

		# Si hay ejecuciones de programas pendientes aún...
		while self.checkPin(self.pin_ejecucion_general,True):

			# Inicializa las variables
			if init_variables:
				# Inicializamos las variables a utilizar y se baja el semáforo, permitiendo que el 
				# dispositivo de experimentación ejecute.
				self.buffer=[]
				self.buffer_time=[]
				init_variables=False

				self.pin_escritura_disco.value=False

			# Si está ejecutando algo... (lo sabemos porque pin_ejecucion, pin que indica la ejecución de una
			# iteración de un programa, está en alto)
			if self.checkPin(self.pin_ejecucion,True):
				# Tomamos el tiempo de inicio y se baja el semáforo, impidiendo el paso a futuras ejecuciones
				# aparte de la actual.
				t_init=time()
				self.pin_escritura_disco.value=True
				
				# Mientras no se finaliza la ejecución, se toman los valores de intensidad y tiempo.
				while not self.checkPin(self.pin_ejecucion,False):
					self.buffer+=[round(self.ina1.check_conv_bit_and_return_current_ma(),6)]
					self.buffer_time+=[time()]
				
				# Tomamos el tiempo de finalización de la ejecución.
				t_end=time()

				# Indicamos que, más adelante, se deben de reinicializar las variables, y que se debe 
				# de bajar el semáforo para dejar que se continue ejecutando.
				init_variables=True

				# Se almacenan las lecturas de intensidad tomadas.
				self.measures_file+=[self.buffer]
				
				# Calculamos el consumo energético
				energy=0
				for i in range(0,len(self.buffer)-1):
					energy+=self.buffer[i]*(self.buffer_time[i+1]-self.buffer_time[i])*self.volts

				# Almacenamos los datos calculados a partir de las lecturas.
				sum_=sum(self.buffer,axis=0)
				self.data_file+=[[\
					mean(self.buffer,axis=0), #mean
					std(self.buffer,axis=0),  # std
					t_end-t_init,  # execution time (seconds)
					sum_, # Total miliamps measured
					len(self.buffer), # Number of measures
					energy # Power consumption in mWs
					#(sum_)*(self.volts/len(self.buffer))*(t_end-t_init) # Quick power consumption in mWs
						# Con este método, se supone que el tiempo entre muestras es constante.
				]]

				# Se almacenan las lecturas de tiempo corespondiente a las lecturas intensidad tomadas.
				self.timestamps_file+=[self.buffer_time]

				self.aux_buffer = self.buffer


		# Tras finalizar, se guardan las lecturas en disco.
		with open('./experimentos/mediciones/consumption-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.measures_file)

		with open('./experimentos/mediciones/data-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.data_file)

		with open('./experimentos/mediciones/timestamps-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.timestamps_file)

		# Se reinializan las variables que guardan las lecturas.
		self.buffer=[]
		self.buffer_time=[]	

	def synchronizer_speedup(self,send_compile_data,exec_data,file_name="file"):
		"""
		Método principal, llamado por main_speedup, que se encarga de compilar, mandar los 
		archivos necesarios al dispositivo de ejecución, realizar la ejecución y almacenar los 
		valores resultantes.

		A diferencia de "synchronizer", almacena la información del fichero escrito en memoria, en los
		atributos "measures_file" y "data_file", haciendo más fácil la recuperación de información.
		Únicamente se almacena la información al final del método, no cada iteración.
		"""

		# Se compilan los programas necesarios, usando el parámetro de datos de compilación.
		self.send_and_compile_file(send_compile_data)

		#system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "python3 SPACE ./experimentos/pin_initialization_experipi.py ENTER"')
		
		#self.custom_sleep(0.1)

		# Se ejecuta el archivo correspondiente.
		self.execute_file(exec_data)

		# Se realiza una espera para dar tiempo al dispositivo de experimentación a realizar las inicializaciones necesarias.
		self.custom_sleep(0.5)

		init_variables=True
		

		# Archivo que guarda las lecturas de intensidad. En disco, tendrá un nombre de
		# "consumption-". Esta variable es una lista de listas, donde cada lista corresponde
		# a una iteración del programa que se desee medir.
		self.measures_file=[]
		
		# Archivo que guarda información relevante procesada mediante las lecturas de 
		# intensidad tomadas. En disco, tendrá un nombre de "data-". Esta variable es una 
		# lista de listas, donde cada lista corresponde a una iteración del programa que se desee medir.
		self.data_file=[['Mean measures (mA)','std measures',
			'execution time (seconds)', 'Total miliamps measured', 'Number of measures','Energy consumption (mWs)']]

		# Archivo que guarda las tomas de tiempo correspondiente a las lecturas de intensidad. 
		# En disco, tendrá un nombre de "timestamps-". Esta variable es una lista de listas, 
		# donde cada lista corresponde a una iteración del programa que se desee medir.
		self.timestamps_file=[]

		# Si hay ejecuciones de programas pendientes aún...
		while self.checkPin(self.pin_ejecucion_general,True):

			# Inicializa las variables
			if init_variables:
				# Inicializamos las variables a utilizar y se baja el semáforo, permitiendo que el 
				# dispositivo de experimentación ejecute.
				self.buffer=[]
				self.buffer_time=[]
				init_variables=False

				self.pin_escritura_disco.value=False

			# Si está ejecutando algo... (lo sabemos porque pin_ejecucion, pin que indica la ejecución de una
			# iteración de un programa, está en alto)
			if self.checkPin(self.pin_ejecucion,True):
				# Tomamos el tiempo de inicio y se baja el semáforo, impidiendo el paso a futuras ejecuciones
				# aparte de la actual.
				t_init=time()
				self.pin_escritura_disco.value=True
				
				# Mientras no se finaliza la ejecución, se toman los valores de intensidad y tiempo.
				while not self.checkPin(self.pin_ejecucion,False):
					self.buffer+=[round(self.ina1.check_conv_bit_and_return_current_ma(),6)]
					self.buffer_time+=[time()]
				
				# Tomamos el tiempo de finalización de la ejecución.
				t_end=time()

				# Indicamos que, más adelante, se deben de reinicializar las variables, y que se debe 
				# de bajar el semáforo para dejar que se continue ejecutando.
				init_variables=True

				# Se almacenan las lecturas de intensidad tomadas.
				self.measures_file+=[self.buffer]
				
				# Calculamos el consumo energético
				energy=0
				for i in range(0,len(self.buffer)-1):
					energy+=self.buffer[i]*(self.buffer_time[i+1]-self.buffer_time[i])*self.volts

				# Almacenamos los datos calculados a partir de las lecturas.
				sum_=sum(self.buffer,axis=0)
				self.data_file+=[[\
					mean(self.buffer,axis=0), #mean
					std(self.buffer,axis=0),  # std
					t_end-t_init,  # execution time (seconds)
					sum_, # Total miliamps measured
					len(self.buffer), # Number of measures
					energy # Power consumption in mWs
					#(sum_)*(self.volts/len(self.buffer))*(t_end-t_init) # Quick power consumption in mWs
						# Con este método, se supone que el tiempo entre muestras es constante.
				]]

				# Se almacenan las lecturas de tiempo corespondiente a las lecturas intensidad tomadas.
				self.timestamps_file+=[self.buffer_time]

				self.aux_buffer = self.buffer


		# Tras finalizar, se guardan las lecturas en disco.
		with open('./experimentos/mediciones/consumption-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.measures_file)

		with open('./experimentos/mediciones/data-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.data_file)

		with open('./experimentos/mediciones/timestamps-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.timestamps_file)

		# Se reinializan las variables que guardan las lecturas.
		self.buffer=[]
		self.buffer_time=[]

	def simple_synchronizer_speedup(self,send_compile_data,exec_data,file_name="file"):
		"""
		Método principal, llamado por main_speedup, que se encarga de compilar, mandar los 
		archivos necesarios al dispositivo de ejecución, realizar la ejecución y almacenar los 
		valores resultantes.

		A diferencia de "synchronizer", almacena la información del fichero escrito en memoria, en los
		atributos "measures_file" y "data_file", haciendo más fácil la recuperación de información.
		Únicamente se almacena la información al final del método, no cada iteración.
		"""

		# Se compilan los programas necesarios, usando el parámetro de datos de compilación.
		#self.send_and_compile_file(send_compile_data)

		#system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "python3 SPACE ./experimentos/pin_initialization_experipi.py ENTER"')
		
		#self.custom_sleep(0.1)

		# Se ejecuta el archivo correspondiente.
		self.doom_execute_file(exec_data)

		# Se realiza una espera para dar tiempo al dispositivo de experimentación a realizar las inicializaciones necesarias.
		self.custom_sleep(0.5)

		init_variables=True
		

		# Archivo que guarda las lecturas de intensidad. En disco, tendrá un nombre de
		# "consumption-". Esta variable es una lista de listas, donde cada lista corresponde
		# a una iteración del programa que se desee medir.
		self.measures_file=[]
		
		# Archivo que guarda información relevante procesada mediante las lecturas de 
		# intensidad tomadas. En disco, tendrá un nombre de "data-". Esta variable es una 
		# lista de listas, donde cada lista corresponde a una iteración del programa que se desee medir.
		self.data_file=[['Mean measures (mA)','std measures',
			'execution time (seconds)', 'Total miliamps measured', 'Number of measures','Energy consumption (mWs)']]

		# Archivo que guarda las tomas de tiempo correspondiente a las lecturas de intensidad. 
		# En disco, tendrá un nombre de "timestamps-". Esta variable es una lista de listas, 
		# donde cada lista corresponde a una iteración del programa que se desee medir.
		self.timestamps_file=[]

		# Si hay ejecuciones de programas pendientes aún...
		while self.checkPin(self.pin_ejecucion_general,True):

			# Inicializa las variables
			if init_variables:
				# Inicializamos las variables a utilizar y se baja el semáforo, permitiendo que el 
				# dispositivo de experimentación ejecute.
				self.buffer=[]
				self.buffer_time=[]
				init_variables=False

				self.pin_escritura_disco.value=False

			# Si está ejecutando algo... (lo sabemos porque pin_ejecucion, pin que indica la ejecución de una
			# iteración de un programa, está en alto)
			if self.checkPin(self.pin_ejecucion,True):
				# Tomamos el tiempo de inicio y se baja el semáforo, impidiendo el paso a futuras ejecuciones
				# aparte de la actual.
				t_init=time()
				self.pin_escritura_disco.value=True
				
				# Mientras no se finaliza la ejecución, se toman los valores de intensidad y tiempo.
				while not self.checkPin(self.pin_ejecucion,False):
					self.buffer+=[round(self.ina1.check_conv_bit_and_return_current_ma(),6)]
					self.buffer_time+=[time()]
				
				# Tomamos el tiempo de finalización de la ejecución.
				t_end=time()

				# Indicamos que, más adelante, se deben de reinicializar las variables, y que se debe 
				# de bajar el semáforo para dejar que se continue ejecutando.
				init_variables=True

				# Se almacenan las lecturas de intensidad tomadas.
				self.measures_file+=[self.buffer]
				
				# Calculamos el consumo energético
				energy=0
				for i in range(0,len(self.buffer)-1):
					energy+=self.buffer[i]*(self.buffer_time[i+1]-self.buffer_time[i])*self.volts

				# Almacenamos los datos calculados a partir de las lecturas.
				sum_=sum(self.buffer,axis=0)
				self.data_file+=[[\
					mean(self.buffer,axis=0), #mean
					std(self.buffer,axis=0),  # std
					t_end-t_init,  # execution time (seconds)
					sum_, # Total miliamps measured
					len(self.buffer), # Number of measures
					energy # Power consumption in mWs
					#(sum_)*(self.volts/len(self.buffer))*(t_end-t_init) # Quick power consumption in mWs
						# Con este método, se supone que el tiempo entre muestras es constante.
				]]

				# Se almacenan las lecturas de tiempo corespondiente a las lecturas intensidad tomadas.
				self.timestamps_file+=[self.buffer_time]

				self.aux_buffer = self.buffer


		# Tras finalizar, se guardan las lecturas en disco.
		with open('./experimentos/mediciones/consumption-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.measures_file)

		with open('./experimentos/mediciones/data-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.data_file)

		with open('./experimentos/mediciones/timestamps-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.timestamps_file)

		# Se reinializan las variables que guardan las lecturas.
		self.buffer=[]
		self.buffer_time=[]

	def synchronizer_basal(self,measured_time,tumbarServicios,file_name="file"):
		"""
		Método principal, llamado por main_basal, que se encarga de medir el consumo basal del
		equipo de experimentación, tirando o no los servicios en función de lo que se desee.
		"""

		# Archivo que guarda las lecturas de intensidad. En disco, tendrá un nombre de
		# "consumption-". Esta variable es una lista de listas, donde cada lista corresponde
		# a una iteración del programa que se desee medir.
		self.measures_file=[]
		
		# Archivo que guarda información relevante procesada mediante las lecturas de 
		# intensidad tomadas. En disco, tendrá un nombre de "data-". Esta variable es una 
		# lista de listas, donde cada lista corresponde a una iteración del programa que se desee medir.
		self.data_file=[['Mean measures (mA)','std measures',
			'execution time (seconds)', 'Total miliamps measured', 'Number of measures','Energy consumption (mWs)']]

		# Archivo que guarda las tomas de tiempo correspondiente a las lecturas de intensidad. 
		# En disco, tendrá un nombre de "timestamps-". Esta variable es una lista de listas, 
		# donde cada lista corresponde a una iteración del programa que se desee medir.
		self.timestamps_file=[]

		# Inicializamos las variables a utilizar.
		self.buffer=[]
		self.buffer_time=[]

		# Si se desea tumbar los servicios...
		if tumbarServicios:
			# La ExperiPi tumba los servicios durante el tiempo que se va a medir + 1 minuto y 10 segundos
			system('ssh -t '+self.usuario_IP_experimentacion+\
			' tmux send -t mySession "sudo SPACE ./experimentos/tumba_espera_inicia_servicios.sh'+\
			' SPACE -t SPACE '+str(60+10+measured_time)+' SPACE ENTER"')
			
			
			#' tmux send -t mySession "sudo SPACE ./experimentos/tumbarServicios6.sh SPACE && SPACE '+\
			#' read SPACE -t SPACE '+str(70+measured_time)+' SPACE && SPACE '+\
			#' sudo SPACE ./experimentos/iniciarServicios.sh SPACE ENTER"')

			#' tmux send -t mySession "sudo SPACE ./experimentos/tumbarServicios6.sh ENTER"')
			

			# Se espera un minuto (de esta forma, los servicios quedan tumbados durante el tiempo que se
			# va a medir + 10 segundos).
			self.custom_sleep(60)
		
		# Tomamos el tiempo de inicio.
		t_init=time()

		# Mientras no haya transcurrido el tiempo determinado, se toman los valores de intensidad y tiempo.
		t_objective=t_init+measured_time
		while time()<t_objective:

			self.buffer+=[round(self.ina1.check_conv_bit_and_return_current_ma(),6)]
			self.buffer_time+=[time()]

		# Tomamos el tiempo de finalización de la ejecución.
		t_end=time()
		
		# Se almacenan las lecturas de intensidad tomadas.
		self.measures_file+=[self.buffer]
		
		# Calculamos el consumo energético
		energy=0
		for i in range(0,len(self.buffer)-1):
			energy+=self.buffer[i]*(self.buffer_time[i+1]-self.buffer_time[i])*self.volts

		# Almacenamos los datos calculados a partir de las lecturas.
		sum_=sum(self.buffer,axis=0)
		self.data_file+=[[\
			mean(self.buffer,axis=0), #mean
			std(self.buffer,axis=0),  # std
			t_end-t_init,  # execution time (seconds)
			sum_, # Total miliamps measured
			len(self.buffer), # Number of measures
			energy # Power consumption in mWs
			#(sum_)*(self.volts/len(self.buffer))*(t_end-t_init) # Quick power consumption in mWs
				# Con este método, se supone que el tiempo entre muestras es constante.
		]]

		self.aux_buffer = self.buffer

		# Se almacenan las lecturas de tiempo corespondiente a las lecturas intensidad tomadas.
		self.timestamps_file+=[self.buffer_time]
		
		# Tras finalizar, se guardan las lecturas en disco.
		with open('./experimentos/mediciones/consumption-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.measures_file)
		
		with open('./experimentos/mediciones/data-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.data_file)

		with open('./experimentos/mediciones/timestamps-'+file_name+'.csv','w') as file:
			csv.writer(file).writerows(self.timestamps_file)

		# Se reinializan las variables que guardan las lecturas.
		self.buffer=[]
		self.buffer_time=[]
					
	def shutdown(self):
		printBold('Bye bye!')

	def main_speedup(self,send_compile_data,exec_data, file_name="medicion"):
		"""
		Método principal que se encarga de compilar, mandar los archivos necesarios al dispositivo 
		de ejecución, realizar la ejecución y almacenar los valores resultantes.

		A diferencia de "main", almacena la información del fichero escrito en memoria, en los
		atributos "measures_file", "data_file" y "timestamps_file", haciendo más fácil la recuperación de información.
		Únicamente se almacena la información al final del método, no cada iteración.

		Valores de entrada:
		 - send_compile_data= Estructura usada por send_and_compile_file
		 - exec_data= Estructura usada por execute_file
		 - file_name= Cadena de texto que refleja el nombre con el que se guardan los CSV
		       con las mediciones hechas.
		"""

		printBold('Inicio main speedup...')
		self.iniciar_pines()

		print('Cambiando valor de prioridad...')
		nice(19-nice(0))

		printBold('Lanzo ejecución') 
		self.synchronizer_speedup(send_compile_data,exec_data,file_name)
		printBold('Fin de main')

	def simple_main_speedup(self,send_compile_data,exec_data, file_name="medicion"):
		"""
		Método principal que se encarga de compilar, mandar los archivos necesarios al dispositivo 
		de ejecución, realizar la ejecución y almacenar los valores resultantes.

		A diferencia de "main", almacena la información del fichero escrito en memoria, en los
		atributos "measures_file", "data_file" y "timestamps_file", haciendo más fácil la recuperación de información.
		Únicamente se almacena la información al final del método, no cada iteración.

		Valores de entrada:
		 - send_compile_data= Estructura usada por send_and_compile_file
		 - exec_data= Estructura usada por execute_file
		 - file_name= Cadena de texto que refleja el nombre con el que se guardan los CSV
		       con las mediciones hechas.
		"""

		printBold('Inicio main speedup...')
		self.iniciar_pines()

		print('Cambiando valor de prioridad...')
		nice(19-nice(0))

		printBold('Lanzo ejecución') 
		self.simple_synchronizer_speedup(send_compile_data,exec_data,file_name)
		printBold('Fin de main')

	
	def doom_main_speedup(self,send_compile_data,exec_data, file_name="medicion"):
		"""
		Método principal que se encarga de compilar, mandar los archivos necesarios al dispositivo 
		de ejecución, realizar la ejecución y almacenar los valores resultantes.

		A diferencia de "main", almacena la información del fichero escrito en memoria, en los
		atributos "measures_file", "data_file" y "timestamps_file", haciendo más fácil la recuperación de información.
		Únicamente se almacena la información al final del método, no cada iteración.

		Valores de entrada:
		 - send_compile_data= Estructura usada por send_and_compile_file
		 - exec_data= Estructura usada por execute_file
		 - file_name= Cadena de texto que refleja el nombre con el que se guardan los CSV
		       con las mediciones hechas.
		"""

		printBold('Inicio main speedup...')
		self.iniciar_pines()

		print('Cambiando valor de prioridad...')
		nice(19-nice(0))

		printBold('Lanzo ejecución') 
		self.doom_synchronizer_speedup(send_compile_data,exec_data,file_name)
		printBold('Fin de main')
	

	def main(self,send_compile_data,exec_data, file_name="medicion"):
		"""
		Método principal que se encarga de compilar, mandar los archivos necesarios al dispositivo 
		de ejecución, realizar la ejecución y almacenar los valores resultantes.

		Valores de entrada:
		 - send_compile_data= Estructura usada por send_and_compile_file
		 - exec_data= Estructura usada por execute_file
		 - file_name= Cadena de texto que refleja el nombre con el que se guardan los CSV
		       con las mediciones hechas.
		"""

		printBold('Inicio main...')
		self.iniciar_pines()

		print('Cambiando valor de prioridad...')
		nice(19-nice(0))

		printBold('Lanzo ejecución')
		self.synchronizer(send_compile_data,exec_data,file_name)
		printBold('Fin de main')

	def main_basal(self,measured_time,tumbarServicios,file_name="medicion"):
		""" 
		Método principal, llamado por main_basal, que se encarga de medir el consumo basal del
		equipo de experimentación, tirando o no los servicios en función de lo que se desee.
		
		Valores de entrada:
		 - measured_time= Tiempo de ejecución que se mide el basal
		 - tumbarServicios= Booleano que indica si se tumban o no los servicios.
		 - file_name= Cadena de texto que refleja el nombre con el que se guardan los CSV
		       con las mediciones hechas.
		"""

		print('Cambiando valor de prioridad...')
		nice(19-nice(0))

		print('Lanzo ejecución')
		
		self.synchronizer_basal(measured_time,tumbarServicios,file_name)
		
		print('Fin de basal')