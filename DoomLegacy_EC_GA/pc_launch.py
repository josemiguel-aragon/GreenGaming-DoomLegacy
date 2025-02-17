# Main que orquesta toda la ejecución, así como transferencia de archivos y creación de directorios.

# Configuración del archivo al final del mismo

from os import system
from time import sleep

#from os import listdir
#from os.path import isdir

from EEMBC_benchmark_suites_redefinido.check import check_correctness_files_and_folders

from save_and_fix_multiple_definitions_v4_7 import save_and_fix_multiple_definitions

__autor__="Jesús Morales Millán"
__contact__="jesus.morales@uca.es"

def printBold (str):
	print('\033[1m' + str + '\033[0m')


# class Measure_tuple: Clase que abstrae la comunicación entre una tupla MediPi y ExperiPi
# Param:
# 	(str/int) id_host_medipi 	Espera el identificador de host local del sistema MediPi,   si tiene la IP 192.168.3.12, será '12'
# 	(str/int) id_host_exprpi 	Espera el identificador de host local del sistema ExperiPi, si tiene la IP 192.168.3.13, será '13'
# 	(str)	 ip_wan 			Espera la dirección de red del router al que se encuentran conectados los sistemas, por ejemplo '10.142.154.43'
# 								Nota: El router tiene que tener implementado el reenvio de puertos del 22xx al 22 en el rango de direcciones ip local,
# 									  siendo xx el identificador de host de los sistemas, por ejemplo '12' para la ip local '192.168.3.12'.
#								Nota2: Si no se especifica ninguna dirección IP se asumirá que la conexión es local y se usará la IP LAN para las comunicaciones.
#
# 	(str)	 id_lan 			Espera el identificador de red de la red local a la que se encuentran conectadas las raspberrys, por ejemplo: '192.168.3.0'
# 	(str)	 user_medipi 		Espera el nombre de usuario del sistema MediPi,   por defecto, 'pi'
# 	(str)	 user_exprpi 		Espera el nombre de usuario del sistema ExperiPi, por defecto, 'pi'
#
class Measure_tuple:
	"""
	Clase auxiliar para la conexión con los dispositivos.
	"""
	def __init__ (self, id_host_medipi, id_host_exprpi, ip_wan=None, id_lan='192.168.3.0', user_medipi='pi', user_exprpi='pi'):
		"""
		Crea un objeto de la clase Measure_tuple, auxiliar para la conexión con los dispositivos.

		- (str/int) id_host_medipi 	Espera el identificador de host local del sistema MediPi,   si tiene la IP 192.168.3.12, será '12'.
		- (str/int) id_host_exprpi 	Espera el identificador de host local del sistema ExperiPi, si tiene la IP 192.168.3.13, será '13.
		- (str)	 ip_wan 			Espera la dirección de red del router al que se encuentran conectados los sistemas, por ejemplo '10.142.154.43'.
	 								Nota: El router tiene que tener implementado el reenvio de puertos del 22xx al 22 en el rango de direcciones ip local,
	 									  siendo xx el identificador de host de los sistemas, por ejemplo '12' para la ip local '192.168.3.12'.
									Nota 2: Si no se especifica ninguna dirección IP se asumirá que la conexión es local y se usará la IP LAN para las comunicaciones.

	 	- (str)	 id_lan 			Espera el identificador de red de la red local a la que se encuentran conectadas las raspberrys, por ejemplo: '192.168.3.0'.
	 	- (str)	 user_medipi 		Espera el nombre de usuario del sistema MediPi,   por defecto, 'pi'.
	 	- (str)	 user_exprpi 		Espera el nombre de usuario del sistema ExperiPi, por defecto, 'pi'.
		"""
		self.id_host_medipi = str(id_host_medipi)
		self.id_host_exprpi = str(id_host_exprpi)
		self.user_medipi	= str(user_medipi)
		self.user_exprpi	= str(user_exprpi)
		self.id_lan		 = ".".join(str(id_lan).split(".", 3)[:-1]) + '.' # Removes the last octect: 192.168.3.
		self.ip_wan		 = str(ip_wan)
		self.cmd_ssh   = 'ssh -t -p 22'
		self.cmd_scp   = 'scp -r -P 22'
		self.cmd_rsync = 'rsync -aP'

		self.login_medipi_lan = self.user_medipi +'@'+ self.id_lan + self.id_host_medipi 	# pi@192.168.3.3
		self.login_exprpi_lan = self.user_exprpi +'@'+ self.id_lan + self.id_host_exprpi 	# pi@192.168.3.4

		if (self.ip_wan == 'None'):
			self.login_medipi = self.login_medipi_lan						# pi@192.168.3.3
			self.login_exprpi = self.login_exprpi_lan 						# pi@192.168.3.4

			self.cmd_ssh_medipi = self.cmd_ssh + " "  						# 'ssh -t -p 22 '
			self.cmd_ssh_exprpi = self.cmd_ssh + " "  						# 'ssh -t -p 22 '

			self.cmd_scp_medipi = self.cmd_scp + " "  						# 'scp	-P 22 '
			self.cmd_scp_exprpi = self.cmd_scp + " "  						# 'scp	-P 22 '

			self.cmd_rsync_medipi = self.cmd_rsync + " "  					# 'rsync -ar '
			self.cmd_rsync_exprpi = self.cmd_rsync + " "  					# 'rsync -ar '

		else:
			self.id_host_medipi = str(id_host_medipi).zfill(2)
			self.id_host_exprpi = str(id_host_exprpi).zfill(2)
			self.login_medipi = self.user_medipi +'@'+ self.ip_wan  	# pi@10.142.154.43
			self.login_exprpi = self.user_exprpi +'@'+ self.ip_wan  	# pi@10.142.154.43

			self.cmd_ssh_medipi = self.cmd_ssh + self.id_host_medipi + " "  # 'ssh -t -p 2212 '
			self.cmd_ssh_exprpi = self.cmd_ssh + self.id_host_exprpi + " "  # 'ssh -t -p 2213 '

			self.cmd_scp_medipi = self.cmd_scp + self.id_host_medipi + " "  # 'scp	-P 2212 '
			self.cmd_scp_exprpi = self.cmd_scp + self.id_host_exprpi + " "  # 'scp	-P 2213 '

			self.cmd_rsync_medipi = self.cmd_rsync + ' -e \''+self.cmd_ssh_medipi+'\'' + " " # 'rsync -ar -e \'ssh -t -p 2212\' '
			self.cmd_rsync_exprpi = self.cmd_rsync + ' -e \''+self.cmd_ssh_exprpi+'\'' + " " # 'rsync -ar -e \'ssh -t -p 2213\' '


	def send_cmd_ssh (self, str_host, str_cmd):
		str_host = str(str_host).upper()
		if (str_host == "MEDIPI"):
			system(self.cmd_ssh_medipi + " " + self.login_medipi + " " + str_cmd) # 'ssh -t -p 22 '   + 'pi@192.168.3.3'   + 'ls -la'
		if (str_host == "EXPERIPI"):
			system(self.cmd_ssh_exprpi + " " + self.login_exprpi + " " + str_cmd) # 'ssh -t -p 2204 ' + 'pi@10.142.153.43' + 'ls -la'

	def send_cmd_scp (self, str_source, str_host, str_destination):
		str_host = str(str_host).upper()
		if (str_host == "MEDIPI"):
			system(self.cmd_scp_medipi + str_source + " " + self.login_medipi + ":" + str_destination) # 'scp -P 22   ./EEMBC_benchmark_suites pi@192.168.3.3:~/'
		if (str_host == "EXPERIPI"):
			system(self.cmd_scp_exprpi + str_source + " " + self.login_exprpi + ":" + str_destination) # 'scp -P 2204 ./EEMBC_benchmark_suites pi@10.142.154.43:~/'

	def recv_cmd_scp (self, str_host, str_source, str_destination):
		str_host = str(str_host).upper()
		if (str_host == "MEDIPI"):
			system(self.cmd_scp_medipi + self.login_medipi + ":" + str_source + " " + str_destination) # 'scp -P 22   pi@192.168.3.3:~/EEMBC_benchmark_suites ./'
		if (str_host == "EXPERIPI"):
			system(self.cmd_scp_exprpi + self.login_exprpi + ":" + str_source + " " + str_destination) # 'scp -P 2204 pi@10.142.154.43:~/EEMBC_benchmark_suites ./'

	def send_cmd_rsync (self, str_source, str_host, str_destination):
		str_host = str(str_host).upper()
		if (str_host == "MEDIPI"):
			system(self.cmd_rsync_medipi + str_source + " " + self.login_medipi + ":" + str_destination) # 'rsync -ar					   ./EEMBC_benchmark_suites pi@192.168.3.3:~/'
		if (str_host == "EXPERIPI"):
			system(self.cmd_rsync_exprpi + str_source + " " + self.login_exprpi + ":" + str_destination) # 'rsync -ar -e \'ssh -t -p 2204\' ./EEMBC_benchmark_suites pi@10.142.154.43:~/'

	def recv_cmd_rsync (self, str_host, str_source, str_destination):
		str_host = str(str_host).upper()
		if (str_host == "MEDIPI"):
			system(self.cmd_rsync_medipi + self.login_medipi + ":" + str_source + " " + str_destination) # 'rsync -ar						pi@192.168.3.3:~/EEMBC_benchmark_suites ./'
		if (str_host == "EXPERIPI"):
			system(self.cmd_rsync_exprpi + self.login_exprpi + ":" + str_source + " " +  str_destination) # 'rsync -ar -e \'ssh -t -p 2204\' pi@10.142.154.43:~/EEMBC_benchmark_suites ./'


def send_files_and_create_session(tupla, str_benchmarks_suites_directory):
	"""
	Crea sesiones tmux en cada uno de los dispositivos y les envía los archivos que son necesarios, siguiendo
	la estructura de directorios creada.
	"""
	try:
		# Eliminar sesiones anteriores
		printBold('Eliminando sesiones antiguas...')
		tupla.send_cmd_ssh("MEDIPI",   'tmux kill-session -t mySession')
		tupla.send_cmd_ssh("EXPERIPI", 'tmux kill-session -t mySession')

		# Se crea una sesión en las raspberries
		printBold('Creando sesión actual...')
		tupla.send_cmd_ssh("MEDIPI",   'tmux new -d -s mySession')
		tupla.send_cmd_ssh("EXPERIPI", 'tmux new -d -s mySession')

		sleep(0.1)

		# Borrando archivos previos...
		printBold('Borrando archivos previos...')
		tupla.send_cmd_ssh("MEDIPI",   'tmux send -t mySession "rm SPACE -rf SPACE ~/experimentos ENTER"')
		tupla.send_cmd_ssh("EXPERIPI", 'tmux send -t mySession "rm SPACE -rf SPACE ~/experimentos ENTER"')

		# Creando directorios
		printBold('Creando directorios...')
		tupla.send_cmd_ssh("MEDIPI",  'tmux send -t mySession "mkdir SPACE -p SPACE ~/experimentos/mediciones ENTER"')
		tupla.send_cmd_ssh("EXPERIPI",'tmux send -t mySession "mkdir SPACE -p SPACE ~/experimentos ENTER"')

		# Envío del benchmark a Medipi
		printBold('Enviado suites...')
		tupla.send_cmd_ssh("MEDIPI",  'tmux send -t mySession "mkdir SPACE -p SPACE ~/experimentos/EEMBC_benchmark_suites ENTER"')
		tupla.send_cmd_rsync(str_benchmarks_suites_directory+'/*', "MEDIPI", "~/experimentos/EEMBC_benchmark_suites")

		# Envío de scripts a las raspberries
		printBold('Enviando scripts a MediPi...')
		tupla.send_cmd_rsync("./scriptsMediPi/*",   "MEDIPI",   "~/experimentos/")

		printBold('Enviando scripts a ExperiPi...')
		tupla.send_cmd_rsync("./scriptsExperiPi/*", "EXPERIPI", "~/experimentos/")

		# Damos permiso a los bash de iniciar y tumbar servicios
		printBold('Dando permisos...')
		tupla.send_cmd_ssh("MEDIPI",  'tmux send -t mySession "chmod SPACE +x SPACE ~/experimentos/\*.sh ENTER"')
		tupla.send_cmd_ssh("EXPERIPI",'tmux send -t mySession "chmod SPACE +x SPACE ~/experimentos/\*.sh ENTER"')

		sleep(0.1)

	except:
		printBold('Fallo ethernet')

def lanzar_medicion(tupla,iteraciones_ini,iteraciones_fin,tiempo,tiempo_de_espera,subir_a_drive):
	"""
	Se ejecuta el script de Python de la MediPi que mide todos los benchmarks de todas las suites
	del directorio especificado.

	Parámetros:

	- tupla = objeto de la clase Measure_tuple que abstrae la comunicación de dos Raspberries Pi.

	- iteraciones_ini= Número de iteraciones que se empieza a ejecutar. Este número va a aumentando, siendo multiplicado
	por dos cada vez que se ejecuta x*2^i veces.
	- iteraciones_fin = Número de iteraciones que se ejecutan por última vez

	Ejemplo de funcionamiento de estos dos parámetros:
	Si ajustamos los parámetros a iteraciones_ini=5, iteraciones_fin=40, nuestros benchmarks se ejecutarán
	primero 5 veces, luego 10, más tarde 20, y finalmente 40.

	Para cada uno de estos pasos, se guarda un CSV por separado, donde cada línea es una iteración del programa

	- tiempo: Si la variable tiempo tiene un menor o igual que 0, el comportamiento será el anterior.
	En caso contrario, si la variable tiempo está definida con un valor mayor que 0, el funcionamiento será el siguiente:

	Se itera el programa tantas veces como sea necesario hasta que su tiempo de ejecución sea igual o superior al definido
	en esta variable. Este proceso se repetirá tantas veces como vengan dado por el número de iteraciones actual, en el rango
	definido por iteraciones_ini e iteraciones_fin.

	Ejemplo: Si se define tiempo=1, iteraciones_ini=5, iteraciones_fin=40, el comportamiento será medir un benchmark
	tantas iteraciones como sea necesario hasta llegar a que el tiempo de ejecución total de las iteraciones
	sea mayor o igual a 1 segundo, y repetir esto 5 veces. Más tarde se repite con 10, 20, y finalmente 40.

	La diferencia con este es el resultado en disco, ya que cada vez que se llega al tiempo de ejecución, se guarda un archivo.
	De esta manera, siguiendo con el ejemplo anterior, tendremos 10 archivos para iteraciones=10 donde cada archivo tiene
	tantas iteraciones comos sea necesario, más tarde 20 archivos para iteraciones=20, y así.

	- tiempo de espera: Tiempo, en segundos, que la ExperiPi espera tras cada iteración.
	Este valor debe ser el suficiente como para asegurar que las iteraciones sean independientes.
	"""
	try:

		printBold('Se lanza la ejecución')

		tupla.send_cmd_ssh("MEDIPI", 'tmux send -t mySession "python3 SPACE ~/experimentos/benchmark_measurer.py '+\
			'SPACE -e SPACE '+tupla.login_exprpi_lan+' SPACE -i SPACE '+str(iteraciones_ini)+' SPACE -f SPACE '+str(iteraciones_fin)+' '+\
			'SPACE -t SPACE '+str(tiempo)+' SPACE -w SPACE '+str(tiempo_de_espera)+' SPACE -u SPACE '+str(subir_a_drive)+' ENTER"')

	except Exception as exception:
		printBold(exception)
		printBold('Fallo ethernet')


def lanzar_genetico(tupla,tiempo_de_espera,subir_a_drive):
	"""
	Se ejecuta el script de Python de la MediPi que mide el genético.

	Parámetros:
	- tupla = objeto de la clase Measure_tuple que abstrae la comunicación de dos Raspberries Pi.

	- tiempo_de_espera: Tiempo, en segundos, que la ExperiPi espera tras cada iteración.
	Este valor debe ser el suficiente como para asegurar que las iteraciones sean independientes.

	- subir_a_drive: Booleano que indica si se sube o no a Google Drive el archivo, según la configuración
	hecha en el dispositivo de experimentación.
	"""
	try:
		printBold('Se lanza la ejecución')

		tupla.send_cmd_ssh("MEDIPI", 'tmux send -t mySession "python3 SPACE ~/experimentos/genetico_ejecucion_suite_v1_3.py '+\
			'SPACE -e SPACE '+tupla.login_exprpi_lan+' SPACE -w SPACE '+str(tiempo_de_espera)+' SPACE -u SPACE '+str(subir_a_drive)+' ENTER"')
	except Exception as exception:
		printBold(exception)
		printBold('Fallo ethernet')


def lanzar_basal(tupla,tiempo_ejecucion,tumbarServicios,subir_a_drive):
	"""
	Se ejecuta el script de Python de la MediPi que mide el consumo basal.

	Parámetros:
	- tupla = objeto de la clase Measure_tuple que abstrae la comunicación de dos Raspberries Pi.

	- tiempo_ejecucion: Tiempo, en segundos, que se mide el consumo basal.

	- tumbarServicios: Booleano que indica si se tumban o no los servicios del dispositivo de experimentación.
	Debido a que se desea la menor interferencia posible, y sumado al hecho de que uno de los servicios tumbados
	es el de la conexión, esta se pierde hasta que se reinicie manualmente el dispositivo, desenchufándolo de corriente.
	Se podría añadir un programa que esperase durante tantos segundos como indique "tiempo_de_ejecucion", pero eso
	afectaría al consumo.

	- subir_a_drive: Booleano que indica si se sube o no a Google Drive el archivo, según la configuración
	hecha en el dispositivo de experimentación.
	"""
	try:
		printBold('Se lanza la ejecución')

		tupla.send_cmd_ssh("MEDIPI", 'tmux send -t mySession "python3 SPACE ~/experimentos/measure_basal.py '+\
			'SPACE -e SPACE '+tupla.login_exprpi_lan+' SPACE -t SPACE '+str(tiempo_ejecucion)+' SPACE -u SPACE '+str(subir_a_drive)+\
			' SPACE -x SPACE '+str(tumbarServicios)+' ENTER"')

	except Exception as exception:
		printBold(exception)
		printBold('Fallo ethernet')


# ------------------------

if __name__=="__main__":

	# Variables para la inicialización de la clase Measure_tuple, que abstrae del conexionado con los
	# dispositivos.
	id_host_medipi  = 18
	id_host_exprpi  = 19
	ip_red_wan 		= '10.142.155.18'
	id_red_lan		= '192.168.3.0'

	tupla = Measure_tuple(id_host_medipi, id_host_exprpi, ip_red_wan, id_red_lan)

	# Variable que indica la ruta donde se encuentra el directorio de suites de benchmarks.

	#str_benchmarks_suites_directory = "./EEMBC_benchmark_suites"
	str_benchmarks_suites_directory="./EEMBC_benchmark_suites_redefinido"
	#str_benchmarks_suites_directory="./bench_prueba"

	# Funciones necesarias previas a la ejecución:

	# Si el último caracter de str_benchmarks_suites_directory es una '/', se elimina.
	# Debido al funcionamiento de los métodos y funciones usadas, este no debe aparecer.

	if str_benchmarks_suites_directory[-1]=='/':
		str_benchmarks_suites_directory=str_benchmarks_suites_directory[:-1]

	# Se comprueba la corrección de la nomenclatura y organización.
	#check_correctness_files_and_folders(str_benchmarks_suites_directory)

	# Opcional: Comprueba si se producen redefiniciones en los benchmarks.
	# Únicamente es necesario hacerlo si se ejecuta el algoritmo genético.
	#save_and_fix_multiple_definitions(route_bench=str_benchmarks_suites_directory)

	# Envía archivos y crea sesiones.
	send_files_and_create_session(tupla, str_benchmarks_suites_directory)

	# Lanza las funciones que desees. A continuación se muestran varios ejemplos:

	# Mediciones:

	#lanzar_medicion(tupla=tupla,
	#iteraciones_ini=100, iteraciones_fin=100,
	#tiempo=0, tiempo_de_espera=0,
	#subir_a_drive=False)

	#lanzar_medicion(tupla=tupla,
	#iteraciones_ini=1, iteraciones_fin=1,
	#tiempo=0, tiempo_de_espera=0,
	#subir_a_drive=True)

	#lanzar_medicion(tupla=tupla,
	#iteraciones_ini=15, iteraciones_fin=15,
	#tiempo=3600, tiempo_de_espera=0,
	#subir_a_drive=False)

	# Genético:

	#lanzar_genetico(tupla=tupla,
	#tiempo_de_espera=0,
	#subir_a_drive=False)

	# Basal:
	#lanzar_basal(tupla=tupla,
	#tiempo_ejecucion=60,
	#tumbarServicios=True,
	#subir_a_drive=False)

	#lanzar_basal(tupla=tupla,
	#tiempo_ejecucion=1,
	#tumbarServicios=False,
	#subir_a_drive=False)
