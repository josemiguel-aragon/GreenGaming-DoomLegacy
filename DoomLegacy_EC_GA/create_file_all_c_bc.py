from os import listdir,mkdir, system
from os.path import isfile,isdir

from subprocess import call

from EEMBC_benchmark_suites_redefinido.compile_all_v3_2 import onebyone,allinone, apply_passes

__autor__="Jesús Morales Millán"
__contact__="jesus.morales@uca.es"

#def create_file_all_c_bc(route_bench,iterations_benchmarks,flags=[]):
def create_file_all_c_bc(route_bench,list_benchmarks=[],\
    list_benchmarks_with_route=[],iterations_benchmarks=[],flags=[]):

    """
    Genera "all.c", un archivo que llama a todos los benchmarks especificados el número de iteraciones que
    se especifique. Además, se genera el archivo binario y bc del mismo, usando los flags que se deseen.

    Valores de entrada:
    - route_bench=Ruta donde se encuentran todas las suites de todos los benchmarks.
    - list_benchmarks=Lista de los nombres de los benchmarks.
    - list_benchmarks_with_route=Lista de las rutas a las benchmarks, dentro del directorio "route_bench".
    - iterations_benchmarks=Lista de cuántas veces ejecutar cada benchmark.
    - flags=Flags con los que compilar los archivos utilizados.

    Ejemplo de los tres primeros parámetros:
            route_bench:
                'ruta/carpeta_de_benchmarks'

            list_benchmarks_with_route en una posición x:
                'benchmarks_suiteA/benchmark_de_ejemplo/benchmark_de_ejemplo'
            
            list_benchmarks en la posición x:
                'benchmark_de_ejemplo'

            La ruta completa estaría formada por route_bench+'/'+list_benchmarks_with_route[x]
    """
    
    if route_bench[-1]!='/':
        route_bench+='/'
    
    # Elimina la carpeta "bc", "benchmarks_all" y "binaries".
    call(["rm","-rf",route_bench+"bc",route_bench+"benchmarks_all",route_bench+"binaries"],shell=False)
    
    # Si list_benchmarks_with_route, list_benchmarks y iterations_benchmarks están vacíos, 
    # se rellenan con la información de route_bench.
    if len(list_benchmarks_with_route)==0 and len(list_benchmarks)==0\
    and len(iterations_benchmarks)==0:
        for f_ in sorted(listdir(route_bench)):
            if not isfile(route_bench+f_):
                for f in sorted(listdir(route_bench+f_)):
                    if not isfile(route_bench+f_+'/'+f): #and (f!="qos" and f!="mp4encode" and f!="mp4decode" and f!="rotate01"):
                        list_benchmarks+=[f]
                        list_benchmarks_with_route+=[route_bench+f_+'/'+f]
                        iterations_benchmarks+=[1]
    
    # Si list_benchmarks_with_route está vacío pero iterations_benchmarks no, se lanza
    # una excepción.
    if len(list_benchmarks_with_route)==0 and len(iterations_benchmarks)!=0:
        raise ValueError
    
    # Si iterations_benchmarks está vacío, se rellena con tantos 1 como benchmarks
    # haya en list_benchmarks_with_route.
    if iterations_benchmarks==[]:
        iterations_benchmarks=[1 for _ in list_benchmarks_with_route]

    # Si list_benchmarks está vacío, se rellena a partir de list_benchmarks_with_route.
    if list_benchmarks==[]:
        list_benchmarks=[e.split('/')[-1] for e in list_benchmarks_with_route]

    # Se crea el archivo "all.c" en una lista de listas, que representa al archivo como tal.
    result_file=["#include <stdio.h>\n"]
    
    for file in list_benchmarks:
        result_file+=["extern int benchmark_"+file+"_main(int argc, const char* argv[]);\n"]
    
    result_file+=["int main(int argc, const char* argv[]){\n"]
    result_file+=["int i=0;\n"]
    
    for file,iterations in zip(list_benchmarks,iterations_benchmarks):
        result_file+=['printf("\\n\\nEjecutando benchmark: '+file+'\\n\\n");\n']
        if iterations>1:
            result_file+=["while(i<"+str(iterations)+"){benchmark_"+file+"_main(argc,argv); i++;} i=0;\n"]
        else:
            if iterations==1:
                result_file+=["benchmark_"+file+"_main(argc,argv);\n"]
    
    result_file+=["}"]


    # Se crean los distintos directorios.
    if not isdir(route_bench+'benchmarks_all'):
        mkdir(route_bench+'benchmarks_all')

    if not isdir(route_bench+'bc'):
        mkdir(route_bench+'bc')
    if not isdir(route_bench+'bc/benchmarks_all'):
        mkdir(route_bench+'bc/benchmarks_all')

    if not isdir(route_bench+"binaries"):
        mkdir(route_bench+"binaries")
    if not isdir(route_bench+"binaries/benchmarks_all"):
        mkdir(route_bench+"binaries/benchmarks_all")

    with open(route_bench+"benchmarks_all/all.c", "w") as f:
        f.writelines(result_file)


    # Se compila el archivo "all.c", creando "all.bc".
    call(["clang-9","-c","-O0","-lm","-Xclang","-disable-O0-optnone","-w","-emit-llvm"]+flags+[\
        route_bench+"benchmarks_all/all.c","-o",route_bench+"bc/benchmarks_all/all.bc"],shell=False)

    # Se renombran los main de todos los benchmarks involucrados en "all.c", teniendo como nuevo
    # nombre "benchmark_nombrebenchmark_main". Estas son las funciones a las que "all.c" llama.
    # Debido a que el nombre del benchmark es usado para renombrar el main, y dado que existen
    # ciertas reglas con la nomenclatura de funciones en C, el nombre del benchmark no puede ser
    # cualquiera, de ahí la insistencia en la nomenclatura.
    for file,file_w_route in zip(list_benchmarks,list_benchmarks_with_route):
        if isfile(file_w_route+"/bmark_lite.c"):
            main_file_name="bmark_lite.c"
        else:
            main_file_name=file+".c"

        with open(file_w_route+"/"+main_file_name, "r") as f:
            lines=f.readlines()

        for i,_ in enumerate(lines):
            if " main(" in lines[i] and not "extern" in lines[i]:
                lines[i]=lines[i].replace(" main("," benchmark_"+file+"_main(")

        with open(file_w_route+"/"+main_file_name, "w") as f:
            f.writelines(lines)

    # Se recoge la información de cada benchmark de todos sus archivos ".c", ".h" 
    # y los distintos de ".c" y ".h". Esta información es guardada en listas, 
    # que serán utilizadas en la compilación.

    list_h_files_w_route_benchmarks=[]
    list_h_files_names_benchmarks=[]
    
    list_c_files_w_route_benchmarks=[]
    list_c_files_names_benchmarks=[]

    list_bc_to_compile=[route_bench+'bc/benchmarks_all/all.bc']
    list_bc_benchmarks=[]

    for file,file_w_route in zip(list_benchmarks,list_benchmarks_with_route):
        list_h_files_w_route_benchmarks+=[[file_w_route+"/"+f for f in listdir(file_w_route) \
            if isfile(file_w_route+"/"+f) and f[-2:]==".h"]]
        list_h_files_names_benchmarks+=[[f for f in listdir(file_w_route) \
            if isfile(file_w_route+"/"+f) and f[-2:]==".h"]]

        list_c_files_w_route_benchmarks+=[[file_w_route+"/"+f for f in listdir(file_w_route) \
            if isfile(file_w_route+"/"+f) and f[-2:]==".c"]]
        list_c_files_names_benchmarks+=[[f for f in listdir(file_w_route) \
            if isfile(file_w_route+"/"+f) and f[-2:]==".c"]]      

        list_bc_benchmarks+=[[f[:-2]+'.bc' for f in listdir(file_w_route) \
            if isfile(file_w_route+"/"+f) and f[-2:]==".c"]]
        
        list_bc_to_compile+=[route_bench+'bc/benchmarks_all/'+file+'.bc']

        other_files=[file_w_route+'/'+f for f in listdir(file_w_route)\
            if (f[-2:]!='.c' and f[-2:]!='.h' and f[-4:]!='.cpp' and f[-4:]!='.hpp'\
            and isfile(file_w_route+'/'+f) and f[-5:]!='.cold' and "README" not in f) or (isdir(file_w_route+'/'+f))]

        for other_file in other_files:
            call(["cp","-r",other_file,route_bench+'bc/benchmarks_all/'],shell=False)
            call(["cp","-r",other_file,route_bench+'binaries/benchmarks_all/'],shell=False)

    # Para cada uno de los benchmarks involucrados...
    for benchmark_name,list_c,list_bc in zip(list_benchmarks,\
    list_c_files_w_route_benchmarks,list_bc_benchmarks):
        
        # Se compilan todos los archivos ".c" del benchmark, generando archivos ".bc" para
        # cada uno de ellos.
        call(["clang-9","-c","-O0","-lm","-Xclang","-disable-O0-optnone","-w","-emit-llvm"]+\
        list_c,shell=False)

        # Se enlazan todos los "bc" como uno solo, cuyo nombre es el nombre del benchmark.
        call(["llvm-link-9"]+list_bc+["-o",\
            route_bench+"bc/benchmarks_all/"+benchmark_name+".bc"],shell=False)

        # Se eliminan todos los "bc" excepto el que acabamos de crear.
        call(["rm"]+list_bc,shell=False)

        # Se aplican los passes sobre el "bc" correspondiente al benchmark.
        apply_passes(passes=flags,source_bc=route_bench+"bc/benchmarks_all/"+benchmark_name+".bc",
        target_bc=route_bench+"bc/benchmarks_all/"+benchmark_name+".bc",
        target_as_source_with_prefix_mod=False)

    # Se enlazan todos los "bc" de todos los benchmarks y "all.bc" como un solo "bc", de nombre "all.bc".
    call(["llvm-link-9"]+list_bc_to_compile+["-o",route_bench+"bc/benchmarks_all/all.bc"],shell=False)
    
    # Se le aplican los passes al archivo "all.bc"
    apply_passes(passes=flags,source_bc=route_bench+"bc/benchmarks_all/all.bc",
    target_bc=route_bench+"bc/benchmarks_all/all.bc",
    target_as_source_with_prefix_mod=False)
    
    # Se genera el binario correspondiente a "all.bc"
    call(["clang-9","-lm","-O0"]+flags+[route_bench+"bc/benchmarks_all/all.bc","-o",route_bench+"binaries/benchmarks_all/all"],shell=False)
    
    print('Compilación exitosa')
    
    # Se deshace el renombrado de la función "main" de los benchmarks.
    for file,file_w_route in zip(list_benchmarks,list_benchmarks_with_route):
        if isfile(file_w_route+"/bmark_lite.c"):
            main_file_name="bmark_lite.c"
        else:
            main_file_name=file+".c"

        with open(file_w_route+"/"+main_file_name, "r") as f:
            lines=f.readlines()

        for i,_ in enumerate(lines):
            if " benchmark_"+file+"_main(" in lines[i] and not "extern" in lines[i]:
                lines[i]=lines[i].replace(" benchmark_"+file+"_main("," main(",)

        with open(file_w_route+"/"+main_file_name, "w") as f:
            f.writelines(lines)


# Ejemplos de mains para ejecutar este script
"""
if __name__=="__main__":

    list_benchmarks=[]
    list_benchmarks_with_route=[]
    iterations=[]
    route_bench="./EEMBC_benchmark_suites/"
    for f_ in listdir(route_bench):
        if not isfile(route_bench+f_):
            for f in listdir(route_bench+f_):
                if not isfile(route_bench+f_+'/'+f):
                    list_benchmarks+=[f]
                    list_benchmarks_with_route+=[route_bench+f_+'/'+f]
                    iterations+=[1]

    create_file_all_c_bc(route_bench=route_bench,iterations_benchmarks=iterations)
"""

"""
if __name__=="__main__":
    create_file_all_c_bc(route_bench='./EEMBC_benchmark_suites_redefinido/',
    list_benchmarks_with_route=\
    [\
        'benchmark_automotive/bitmnp01',
        'benchmark_consumer/rgbhpg01',
        'benchmark_embench/libminver',
        'benchmarks_digital_entertainment/rgbcmykv2'
    ])
"""