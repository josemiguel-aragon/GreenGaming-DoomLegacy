from os import system,listdir
from os.path import isdir
from time import sleep,time

from Measurer import Measurer

from sys import exit

import getopt, sys

from os import system
from os.path import isdir

from socket import gethostname

from datetime import datetime

from EEMBC_benchmark_suites.compile_all_v3_2 import compile_all, apply_flags_and_recompile_already_compiled_benchmark

__autor__="Jesús Morales Millán"
__contact__="jesus.morales@uca.es"

def printBold (str):
	print('\033[1m' + str + '\033[0m')

class benchmark_measurer(Measurer):

	def send_and_compile_file(self,send_compile_data=[]):
		"""
		Se compilan UN programa, usando los datos del parámetro recibido, send_compile_data.

		send_compile_data puede estar vacío o no. Si lo está, no tendrá ningún comportamiento.
		Si lo está, envía el binario especificado en la primera posición de la lista 
		"send_compile_data" al dispositivo de experimentación. La segunda posición de la lista
		puede contener una lista o string de passes que aplicar al benchmark.

		Valores de entrada:
		- send_compile_data: Lista que modifica el comportamiento de esta función. Si está vacía, no se hace nada.
		En caso contrario, debe de almacenar los siguientes valores:
			Posición 0 (send_compile_data[0]): Cadena de caracteres que indica del benchmark a enviar
				dentro de la carpeta de las suites.
				
				Ejemplo: 'benchmarks_suiteA/benchmark_de_ejemplo/benchmark_de_ejemplo'

			Posición 1 (send_compile_data[1]): Flags de compilación, ya sea como string o como lista, que se aplican
			 	al benchmark. En caso de que no se deseen compilar con flags, se deja esta posición como una lista vacía.
		"""

		# Si el parámetro no es una lista vacía...
		if send_compile_data!=[]:
			# Si hay passes que aplicar...
			if len(send_compile_data)>1:
				apply_flags_and_recompile_already_compiled_benchmark(\
				'./experimentos/EEMBC_benchmark_suites/',\
				send_compile_data[0],send_compile_data[1],'',True)
			
			# Se envía el archivo
			#system('rsync -r ./experimentos/EEMBC_benchmark_suites/binaries/ '+self.usuario_IP_experimentacion+':~/experimentos/binaries/')
			system('rsync -r ./experimentos/EEMBC_benchmark_suites/binaries/'+send_compile_data[0]+' '+self.usuario_IP_experimentacion+':~/experimentos/binaries/'+send_compile_data[0])

			# Se le da permisos
			system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "chmod SPACE +x SPACE ./experimentos/binaries/'+send_compile_data[0]+' ENTER"')

			# Se realiza una pequeña espera para asegurar su correcto funcionamiento.
			self.custom_sleep(0.01)

	def doom_send_and_compile_file(self,send_compile_data=[]):			
			# Se envía el archivo
			#system('rsync -r ./experimentos/EEMBC_benchmark_suites/binaries/ '+self.usuario_IP_experimentacion+':~/experimentos/binaries/')
			system('scp -Q -r ./experimentos/doomlegacy_optimized/ '+self.usuario_IP_experimentacion+':~/experimentos/')

			# Se le da permisos
			system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "chmod SPACE +x SPACE ./experimentos/doomlegacy_optimized/doomlegacy ENTER"')

			# Se realiza una pequeña espera para asegurar su correcto funcionamiento.
			self.custom_sleep(0.01)
	
	def execute_file(self,exec_data=[]):
		"""
		Se envía la orden de ejecución de un binario correspondiente a un benchmark, usando los datos en exec_data.

		Valor de entrada:
		- exec_data: Lista que contiene:
			Posición 0 (exec_data[0]): Cadena de caracteres que indica del benchmark a ejecutar
				dentro de la carpeta de las suites.
				
				Ejemplo: 'benchmarks_suiteA/benchmark_de_ejemplo/benchmark_de_ejemplo'
			
			Posición 1 (exec_data[1]): Número de iteraciones a ejecutar del benchmark.
			Posición 2 (exec_data[2]): Tiempo durante el que se desea que se ejecute el benchmark.
			Posición 3 (exec_data[3]): Tiempo durante el que se espera antes de la ejecución de cada iteración 
				del benchmark.
		"""

		system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "python3 SPACE ~/experimentos/main_experipi.py\
			SPACE -n SPACE '+exec_data[0]+' SPACE -i SPACE '+str(exec_data[1])+' SPACE -t SPACE '+str(exec_data[2])+' SPACE -w SPACE '+str(exec_data[3])+' ENTER"')

	def cep_execute_file(self,exec_data=[]):
		"""
		Se envía la orden de ejecución de un binario correspondiente a un benchmark, usando los datos en exec_data.

		Valor de entrada:
		- exec_data: Lista que contiene:
			Posición 0 (exec_data[0]): Cadena de caracteres que indica del benchmark a ejecutar
				dentro de la carpeta de las suites.
				
				Ejemplo: 'benchmarks_suiteA/benchmark_de_ejemplo/benchmark_de_ejemplo'
			
			Posición 1 (exec_data[1]): Número de iteraciones a ejecutar del benchmark.
			Posición 2 (exec_data[2]): Tiempo durante el que se desea que se ejecute el benchmark.
			Posición 3 (exec_data[3]): Tiempo durante el que se espera antes de la ejecución de cada iteración 
				del benchmark.
		"""

		system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "python3 SPACE ~/experimentos/main_experipi_CEP.py\
			SPACE -n SPACE '+exec_data[0]+' SPACE -i SPACE '+str(exec_data[1])+' SPACE -t SPACE '+str(exec_data[2])+' SPACE -w SPACE '+str(exec_data[3])+' ENTER"')

	def doom_execute_file(self,exec_data=[]):
		"""
		Se envía la orden de ejecución de un binario correspondiente a un benchmark, usando los datos en exec_data.

		Valor de entrada:
		- exec_data: Lista que contiene:
			Posición 0 (exec_data[0]): Cadena de caracteres que indica del benchmark a ejecutar
				dentro de la carpeta de las suites.
				
				Ejemplo: 'benchmarks_suiteA/benchmark_de_ejemplo/benchmark_de_ejemplo'
			
			Posición 1 (exec_data[1]): Número de iteraciones a ejecutar del benchmark.
			Posición 2 (exec_data[2]): Tiempo durante el que se desea que se ejecute el benchmark.
			Posición 3 (exec_data[3]): Tiempo durante el que se espera antes de la ejecución de cada iteración 
				del benchmark.
		"""

		system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "python3 SPACE ~/experimentos/main_experipi_doom.py\
			SPACE -n SPACE '+exec_data[0]+' SPACE -i SPACE '+str(exec_data[1])+' SPACE -t SPACE '+str(exec_data[2])+' SPACE -w SPACE '+str(exec_data[3])+' ENTER"')

	def compile_send_all(self,aux_data=[]):
		"""
		Método ejecutado en el constructor de clase.
		Compila todos los benchmarks de todas las suites de la carpeta "./experimentos/EEMBC_benchmarks_suites/"
		Almacena los binarios generados en el atributo "aux_list".
		
		Valores de entrada:
		- aux_data: Flags de compilación, ya sea como string o como lista, que se aplican
			a cada uno de los benchmark. En caso de que no se deseen compilar con flags, 
			se deja esta posición como una lista vacía.
		"""

		# Se compilan los benchmarks en la ruta usando los flags de compilación, si procede.
		compile_all('./experimentos/EEMBC_benchmark_suites/',aux_data)
		
		# Se crea una lista con la ruta a todos los programas compilados. Se almacena en self.aux_data. Mediante estos,
		# se pueden usar los otros dos métodos de esta clase.

		# Formato en el que se guarda:
			# benchmarks_suiteA/benchmark_ejemplo_uno/benchmark_ejemplo_uno
			# benchmarks_suiteA/benchmark_ejemplo_dos/benchmark_ejemplo_dos
			# ...
			# benchmarks_suiteZ/benchmark_ejemplo_n_menos_uno/benchmark_ejemplo_n_menos_uno
			# benchmarks_suiteZ/benchmark_ejemplo_n/benchmark_ejemplo_n

		aux_list=[]
		for f_ in listdir("./experimentos/EEMBC_benchmark_suites/binaries"):
			aux_list+=[f_+'/'+f+'/'+f for f in listdir("./experimentos/EEMBC_benchmark_suites/binaries/"+f_) \
				if isdir('./experimentos/EEMBC_benchmark_suites/binaries/'+f_+'/'+f)]
		aux_list.sort()

		self.aux_data=aux_list

		# Se envían los archivos compilados, así como otros que necesiten, y se les da permiso de ejecución.
		system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "mkdir SPACE ./experimentos/binaries ENTER"')
		system('rsync -r ./experimentos/EEMBC_benchmark_suites/binaries/ '+self.usuario_IP_experimentacion+':~/experimentos/binaries/')
		for f_ in aux_list:
			system('ssh -t '+self.usuario_IP_experimentacion+' tmux send -t mySession "chmod SPACE +x SPACE ./experimentos/binaries/'+f_+' ENTER"')
			self.custom_sleep(0.001)


# Main que controla la ejecución a nivel de la MediPi.
if __name__=="__main__":
	bool_uploadDrive=False

	# ---------------------------------
	# Configuración de variables
	flags=[]					# Passes o flags de compilación LLVM.
	# ---------------------------------
	try:
		opts, args = getopt.getopt(sys.argv[1:],"he:i:f:t:w:u:",[])
	except getopt.GetoptError:
		print('Error: benchmark_measurer.py')
		print('\t-h <Ayuda>')
		print('\t-e <usuario e IP usados para conexión ssh con el dispositivo de experimentación, con formato usuario@IP>')
		print('\t-i <número de iteraciones desde el que se empieza a ejecutar, que incrementa al multiplicar por 2>')
		print('\t-f <número de iteraciones en el que se para a ejecutar>')
		print('\t-t <tiempo que se ejecuta cada iteración, en segundos (entero)>')
		print('\t-u <Si se especifica a True, sube los archivos a Google Drive al finalizar>')
		print('\t-w <tiempo de espera tras cada ejecución, en segundos (flotante)>')
		print('')
		print('Se recuerda que se debe de ejecutar tras 15 min de haber encendido los dispositivos, en caso contrario,')
		print('pueden aparecer irregularidades.')

	for opt, arg in opts:
		if opt == '-h':
			print('Ayuda: benchmark_measurer.py')
			print('\t-h <Ayuda>')
			print('\t-e <usuario e IP usados para conexión ssh con el dispositivo de experimentación, con formato usuario@IP>')
			print('\t-i <número de iteraciones desde el que se empieza a ejecutar, que incrementa al multiplicar por 2>')
			print('\t-f <número de iteraciones en el que se para a ejecutar>')
			print('\t-t <tiempo que se ejecuta cada iteración, en segundos>')
			print('\t-u <Si se especifica a True, sube los archivos a Google Drive al finalizar>')
			print('\t-w <tiempo de espera tras cada ejecución, en segundos (flotante)>')
			print('--------------------------------')
			print('Si no se desea ejecutar en un intervalo, se puede poner -f igual a i. De igual forma, si')
			print('no se desea ejecutar un tiempo determinado, se puede poner -t a 0.')
			print('')
			print('Se recuerda que se debe de ejecutar tras 15 min de haber encendido los dispositivos, en caso contrario,')
			print('pueden aparecer irregularidades.')
			exit(0)
			
		if opt == '-e':
			_IP_experimentacion=str(arg)
		if opt == '-i':
			iteraciones_ini=int(arg)
		if opt == '-f':
			iteraciones_fin=int(arg)
		if opt == '-t':
			tiempo=int(arg)
		if opt == '-u':
			bool_uploadDrive = str(arg) == 'True'
		if opt == '-w':
			wait=float(arg)

	# Se inicializa una instancia de la clase benchmark_measurer. Al instanciar, se compilan
	# los programas usando los flags, si procede, e inicializan las variables necesarias para
	# la medición.
	m=benchmark_measurer(_usuario_IP_experimentacion=_IP_experimentacion,_aux_data=flags)

	m.custom_sleep(5)

	printBold("Variable objeto ya inicializada.")

	# Se hace una copia de las rutas a los benchmarks compilados.
	binaries=m.aux_data

	binaries.sort()

	printBold("Binarios:")
	print(binaries)
	
	# Para cada uno de los binarios...
	for i in binaries:
		iters=iteraciones_ini
		# Desde iters=iteraciones_ini hasta iteraciones_fin, en incrementos de iters*=2...
		while iters<=iteraciones_fin:
			printBold('Ejecutando: '+i)
			printBold('Número de iteraciones: '+str(iters))

			# Si la variable tiempo ha sido definida...
			if tiempo>0:
				# Se inicializa la variable que da nombre al archivo CSV guardado.
				title=i.split('/')[-1]+'-'+gethostname()+'-'+str(tiempo)+'s-total-iter-'+str(iters)
				
				# Se ejecuta "iters" veces mediciones de "tiempo" segundos, donde se ejecutan tantas iteraciones
				# como sean necesarias hasta que el tiempo de ejecución de ellas sea igual al de "tiempo".
				iter_aux=0
				while iter_aux<iters:
					printBold(i.split('/')[-1]+" - Iter="+str(iter_aux+1)+"/"+str(iters)+" "+str(datetime.now()))
					m.main_speedup([],[i,iters,tiempo,wait],title+'-iter-num-'+str(iter_aux))
					#m.main([],[i,iters,tiempo,wait],title+'-iter-num-'+str(iter_aux))
					iter_aux+=1
			else:
				# Se ejecuta "iters" iteraciones del benchmark.
				title=i.split('/')[-1]+'-'+gethostname()+'-iters-'+str(iters)
				m.main([],[i,iters,tiempo,wait],title)
			
			# Se hace una espera de 10 segundos, para asegurar el aislamiento entre ejecuciones, de forma que
			# no existan posibles influencias de ejecuciones previas.
			m.custom_sleep(10)

			iters*=2

	# A la función de ejecución, main o main_speedup según corresponda, se le pasa, según lo definido
	# en la clase benchmark_measurer como podemos ver en la parte superior de este mismo archivo, 
	# como segundo parámetro, una lista con los siguientes elementos:
		# - Ruta al binario a ejecutar 
		# - Número de iteraciones
		# - Tiempo de ejecución
		# - Tiempo de espera
	# El tercer parámetro es el que da nombre al CSV, además de los elementos ya incluidos en el nombre.

	m.shutdown()	# Indicamos que no vamos a seguir midiendo

	printBold('He acabado en ' + str(datetime.now()))

	# Se suben los archivos a Google Drive, si procede.
	if bool_uploadDrive:
		import requests
		url = "https://www.google.es"
		try:
			requests.get(url)
			printBold("Subiendo archivos a Drive")
			system('rclone copy -P ~/experimentos/mediciones/ gdrive:`date +%Y.%m.%d`')
			printBold('Subida completada en ' + str(datetime.now()))
		except:
			printBold('No Internet connection found')

	printBold('Ta lue ;D')

	if m.data_file!=[]:
		printBold('Muestras/s:'+str(sum([e[4] for e in m.data_file[1:]])/sum([e[2] for e in m.data_file[1:]])))