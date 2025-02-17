Uso:

- Ejecute compile-all-v3.py para crear los archivos binarios y bc de todos los benchmarks, almacenados en las carpetas "binaries" y "bc" respectivamente.

- Ejecute "check.py" para comprobar que los archivos y carpetas están correctamente definidas según la metodología definida.


Problemas encontrados:

- thcfg.h
	#define USE_TH_FILEIO (FALSE)
	esta macros debe ser puesta a false. En valor TRUE, lo que hace es usar las librerías del benchmark para gestionar la creación, lectura y escritura
	de archivos, para evitar el uso de el tipo FILE de C (por si no se encuentra disponible). Sin embargo, este funciona mal.

- init_files llama a una función void init_nombrearchivo_extensión que no existe:
	Se implementa esa función como void init_nombrearchivo_extensión(){return;}

- función ee_FILE *pathfind_file(const char *filename, const char *filemode,char *outname)

	Esta función incluye una variable "path", que es la que se encarga de comprobar si los archivos que se leen están en los directorios especificados en
	la misma. Sin embargo, por alguna razón, no está incluído el directorio en el que se está ejecutando (pwd, "./"). Por esta razón, se sustituye de la
	siguiente manera:

	char	*path[] = {"",...,NULL};

	char	*path[] = {"./",NULL};


Muchos otros más problemas específicos de cada benchmark han sido encontrados. 
Algunos de ellos han sido documentados en archivos README.txt dentro de directorio correspondiente.


Configuración:

En cada directorio de cada benchmark, hay un archivo bmark_lite.c que contiene el main. El main, a su vez, se encarga de llamar a otra función llamada t_run_test,
que es la encargada de ejecutar el benchmark como tal. Esta recibe por parámetro una estructura que, entre otras cosas, contiene el número de iteraciones
que se ejecuta el benchmark. Puede ser modificado mediante:

the_tcdef.rec_iterations=100;

En el código de "aes", de suite digital entertainment, se encuentra un ejemplo comentado, que no afecta a la ejecución.


Además, existe un parámetro llamado "repetitions" en el script encargado de la ejecución de los binarios, exec-all-v2, que controla el número de ejecuciones que se
hacen de cada uno de estos.
