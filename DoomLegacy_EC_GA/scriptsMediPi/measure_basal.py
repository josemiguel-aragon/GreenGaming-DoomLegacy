import getopt
import sys

from os import system

from time import sleep

from Measurer import Measurer

from datetime import datetime

from socket import gethostname

__autor__="Jesús Morales Millán"
__contact__="jesus.morales@uca.es"

def printBold(str):
	print('\033[1m' + str + '\033[0m')

class basal_measurer(Measurer):

	def send_and_compile_file(self,send_compile_data=[]):
		pass

	def execute_file(self,exec_data=[]):
		pass

	def compile_send_all(self,aux_data=[]):
		pass

# Main que controla la ejecución a nivel de la MediPi.
if __name__ == "__main__":

	bool_uploadDrive = False

	try:
		opts, args = getopt.getopt(sys.argv[1:], "he:t:u:x:", [])
	except getopt.GetoptError:
		print('Error: benchmark_measurer.py')
		print('\t-h <Ayuda>')
		print('\t-e <usuario e IP usados para conexión ssh con el dispositivo de experimentación, con formato usuario@IP>')
		print('\t-t <tiempo que se ejecuta cada iteración, en segundos (entero)>')
		print('\t-u <Si se especifica a True, sube los archivos a Google Drive al finalizar>')
		print('\t-x <Si se especifica a True, se tumban los servicios. Estos no se levantan, se ruega precaución.>')
		print('')
		print('Se recuerda que se debe de ejecutar tras 15 min de haber encendido los dispositivos, en caso contrario,')
		print('pueden aparecer irregularidades.')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print('Ayuda: benchmark_measurer.py')
			print('\t-h <Ayuda>')
			print('\t-e <usuario e IP usados para conexión ssh con el dispositivo de experimentación, con formato usuario@IP>')
			print('\t-t <tiempo que se ejecuta cada iteración, en segundos>')
			print('\t-u <Si se especifica a True, sube los archivos a Google Drive al finalizar>')
			print('\t-x <Si se especifica a True, se tumban los servicios. Estos no se levantan, se ruega precaución.>')
			print('')
			print('Se recuerda que se debe de ejecutar tras 15 min de haber encendido los dispositivos, en caso contrario,')
			print('pueden aparecer irregularidades.')
		if opt == '-e':
			_IP_experimentacion = str(arg)
		if opt == '-t':
			tiempo = int(arg)
		if opt == '-u':
			bool_uploadDrive = str(arg) == 'True'
		if opt == '-x':
			tumbarServicios	= str(arg) == 'True'

	# Se inicializa una instancia de la clase basal_measurer. Al instanciar, se 
	# inicializan las variables necesarias para la medición.
	m = basal_measurer(_IP_experimentacion)

	m.custom_sleep(5)
	
	printBold('He empezado en ' + str(datetime.now()))

	# Se realiza la medición basal, indicando el tiempo que se va a realizar (measured_time=tiempo),
	# si se tumban los servicios (tumbarServicios=tumbarServicios) y el nombre del archivo que se guarda
	# en disco.
	m.main_basal(measured_time=tiempo,tumbarServicios=tumbarServicios,\
		file_name="basal-"+gethostname()+'-'+str(datetime.now()))


	m.shutdown()	# Se indica que no se va a realizar otra medida.

		
	printBold('He acabado en ' + str(datetime.now()))

	printBold('Muestras/s:'+str(sum([e[4] for e in m.data_file[1:]])/sum([e[2] for e in m.data_file[1:]])))
	printBold('Media mA:'+str(m.data_file[1][0]))
	
	# Se guarda en disco, si procede.
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

	printBold('ta lueh ;D')
