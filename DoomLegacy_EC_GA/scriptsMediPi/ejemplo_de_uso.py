from socket import gethostname # Te da el nombre del host del sistema. Este es, por ejemplo: "Medipi-12".

from benchmark_measurer import benchmark_measurer

m=benchmark_measurer(_usuario_IP_experimentacion="pi@192.168.3."+str(int(gethostname().split('-')[1])+1))
	# Obtengo el número de mi dispositivo de medición y le sumo 1, ya que por ahora, con la
	# organización actual, los dispositivos de experimentación tienen como IP la de medición + 1.

	# Se inicializa una instancia de la clase benchmark_measurer. Al instanciar, se compilan
	# los programas usando los flags, si procede.

binaries=m.aux_data	# Ruta a los programas compilados dentro de la carpeta de suites de benchmarks.
					# Esta variable es usada para compilar, enviar y ejecutar benchmarks.

iteraciones=10		# Iteraciones a realizar de cada benchmark.

tiempo=0 			# Variable de tiempo que indica durante cuánto tiempo se ejecuta cada programa.
					# Al estar a 0, no se hace uso de este. Para más detalle, consulta la documentación
					# interna correspondiente.

tiempo_espera=0		# Tiempo de espera entre iteraciones de cada programa.

for binary in binaries:
	print('Ejecutando',binary)
	# Se ejecuta el benchmark de la ruta "binary", aplicando los passes '-aa' y '-aa'.
	# A los archivos que se producen como resultado de la medida, se les añade el nombre del binario 
	# (binary.split('/')[-1]).
	m.main_speedup(\
		send_compile_data=[binary,['-aa','-aa']], \
		exec_data=[binary,iteraciones,tiempo,tiempo_espera], \
		file_name=binary.split('/')[-1]\
	)
	
	# Se imprimen los resultados conseguidos mediante el acceso a los datos en memoria de las lecturas.
	for i,data_iter in enumerate(m.data_file):
		# La primera fila corresponde a qué significado tiene cada columna del archivo.
		if i==0:
			print(data_iter[-1])
		else:
			print('Consumo de',binary.split('/')[-1],'=',data_iter[-1])
