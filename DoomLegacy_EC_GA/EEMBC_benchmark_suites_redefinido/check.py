from os import listdir, system
from os.path import isfile,isdir

__autor__="Jesús Morales Millán"
__contact__="jesus.morales@uca.es"

def check_correctness_files_and_folders(str_directory):
	"""
	
	Comprueba que los directorios de la carpeta especificada tiene nombres adecuados según nuestros criterios:
	- No se hace uso de "-".
	- No se hace uso de "."
	- No existen varios benchmarks con el mismo nombre. En tal caso, se añade "benchmark_nombre-suite" al
	final del nombre del benchmark, donde "nombre-suite" es el nombre dado a la suite en la que se encuentra
	el benchmark en concreto.
	"""
	if str_directory[-1]!='/':
		str_directory+='/'
	
	list_benchmarks=[]
	for f_ in listdir(str_directory):
		if isdir(str_directory+f_) and ('bc' not in f_ or 'binaries' not in f_):
			if f_!=f_.replace('.','_').replace('-','_'):
				print('Se cambia el directorio', str_directory+f_,'por',str_directory+f_.replace('.','_').replace('-','_'))
				system("mv "+str_directory+f_+" "+str_directory+f_.replace('.','_').replace('-','_'))
				f_=f_.replace('.','_').replace('-','_')
			for f in listdir(str_directory+f_):
				if isdir(str_directory+f_+"/"+f):
					if f not in list_benchmarks:
						list_benchmarks += [f]
					else:
						print('Se reemplaza el benchmark ' +str_directory +f_+'/'+f+' por ' +str_directory +f_ +'/' +f +'_' +f_)
						print('')
						system("mv " +str_directory +f_ +"/" +f+" "+str_directory +f_ +"/"+ f+"_" +f_)
						if isfile(str_directory +f_ +"/"+ f+"_" +f_+"/"+f+".c "):
							system("mv " +str_directory +f_ +"/"+ f+"_" +f_+"/"+f+".c "+str_directory +f_ +"/"+ f+"_" +f_+"/"+f+"_"+f_+".c")
							print('Se reemplaza',str_directory +f_ +"/"+ f+"_" +f_+"/"+f+".c ",'por',str_directory +f_ +"/"+ f+"_" +f_+"/"+f+"_"+f_+".c")
						#print("mv " +str_directory +f_ +"/"+ f+"_" +f_+"/"+f+".c "+str_directory +f_ +"/"+ f+"_" +f_+"/"+f+"_"+f_+".c")
						list_benchmarks+=[f+'_'+f_]

#if __name__=="__main__":
	#print('')
	#check_correctness_files_and_folders('./')