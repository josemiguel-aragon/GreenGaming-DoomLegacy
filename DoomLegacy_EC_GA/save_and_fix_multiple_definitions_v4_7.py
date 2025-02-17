from datetime import datetime
from os import listdir,mkdir, system
from os.path import isfile,isdir

from datetime import datetime

from subprocess import call,getoutput

#from filecmp import cmp

#from numpy import where

#from re import match

from re import search,sub

from EEMBC_benchmark_suites_redefinido.check import check_correctness_files_and_folders

import csv

__autor__="Jesús Morales Millán"
__contact__="jesus.morales@uca.es"

def save_and_fix_multiple_definitions(route_bench):
    """
    Comprueba que los benchmarks del directorio route_bench no tengan ninguna función, parámetro,
    o estructura redefinida entre sí. Renombra los elementos necesarios, de manera que pasa de
    "nombre-elemento" a "benchmark_nombre-benchmark_nombre-elemento" (siendo "nombre-elemento"
    el nombre del elemento redefinido, y "nombre-benchmark" el nombre del benchmark).
    """
    if route_bench[-1]!='/':
        route_bench+='/'
    
    # Se comprueba la corrección de los directorios de route_bench.
    check_correctness_files_and_folders(str_directory=route_bench)

    # Se almacena la información de todos los benchmarks en route_bench.
    list_benchmarks=[]
    list_benchmarks_with_route=[]
    iterations_benchmarks=[]
    for f_ in listdir(route_bench):
        if not isfile(route_bench+f_):
            for f in listdir(route_bench+f_):
                if not isfile(route_bench+f_+'/'+f):
                    list_benchmarks+=[f]
                    list_benchmarks_with_route+=[route_bench+f_+'/'+f]
                    iterations_benchmarks+=[1]

    # Se crea el archivo "all.c" en una lista de listas, que representa al archivo como tal.
    result_file=[]
    
    for file in list_benchmarks:
        result_file+=["extern int benchmark_"+file+"_main(int argc, const char* argv[]);\n"]
    
    result_file+=["int main(int argc, const char* argv[]){\n"]
    result_file+=["int i=0;\n"]
    
    for file,iterations in zip(list_benchmarks,iterations_benchmarks):
        result_file+=["while(i<="+str(iterations)+"){benchmark_"+file+"_main(argc,argv); i++;} i=0;\n"]
    
    result_file+=["}"]

    # Se crean los distintos directorios.
    if not isdir(route_bench+'bc_all'):
        mkdir(route_bench+'bc_all')
    
    # Si se encuentra algún archivo ".bc" en el directorio actual, se elimina.
    i=['./'+f for f in listdir('./') if f[-3:]=='.bc']
    if len(i)!=0:
        call(["rm"]+i,shell=False)

    # Se crea el archivo "all.c".
    with open(route_bench+"bc_all/all.c", "w") as f:
        f.writelines(result_file)

    # Se compila el archivo "all.c", creando "temp_all.bc".
    call(["clang-9","-c","-O0","-lm","-Xclang","-disable-O0-optnone","-w","-emit-llvm"]+[\
        route_bench+"bc_all/all.c","-o",route_bench+"bc_all/temp_all.bc"],shell=False)

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

    list_hc_files_w_route_benchmarks=[]
    #list_hc_files_names_benchmarks=[]

    list_bc_to_compile=[route_bench+'bc_all/temp_all.bc']
    list_bc_benchmarks=[]

    redefiniciones=[]

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
        
        list_bc_to_compile+=[route_bench+'bc_all/'+file+'.bc']

    for i,_ in enumerate(list_h_files_w_route_benchmarks):
        list_hc_files_w_route_benchmarks+=[list_h_files_w_route_benchmarks[i]+\
            list_c_files_w_route_benchmarks[i]]
        
    # Reemplazando las inclusiones de guarda (inclusion guards)
    """for file,file_w_route, h_files_w_route, h_files_name\
    in zip(list_benchmarks,list_benchmarks_with_route,list_h_files_w_route_benchmarks,\
    list_h_files_names_benchmarks):
        for h_file_w_route,h_file_name in zip(h_files_w_route,h_files_name):
            with open(h_file_w_route, "r") as f:
                lines=f.readlines()
            replace=False
            string_to_compare=h_file_name.replace('.','_').upper()
            for i,_ in enumerate(lines):
                if ("#ifndef" in lines[i] or "#define" in lines[i]) \
                and string_to_compare in lines[i] \
                and string_to_compare+'_'+file.upper() not in lines[i]:
                    lines[i]=lines[i].replace(string_to_compare,string_to_compare+'_'+file.upper())
                    replace=True
            if replace:
                with open(h_file_w_route, "w") as f:
                    f.writelines(lines)
    """
    
    # Para cada uno de los benchmarks involucrados...
    for benchmark_name,list_c,list_bc in zip(list_benchmarks,\
    list_c_files_w_route_benchmarks,list_bc_benchmarks):
        # Se compilan todos los archivos ".c" del benchmark, generando archivos ".bc" para
        # cada uno de ellos.
        call(["clang-9","-c","-O0","-lm","-Xclang","-disable-O0-optnone","-w","-emit-llvm"]+\
        list_c,shell=False)

        # Se enlazan todos los "bc" como uno solo, cuyo nombre es el nombre del benchmark.
        call(["llvm-link-9"]+list_bc+["-o",\
        route_bench+"bc_all/"+benchmark_name+".bc"],shell=False)

        # Se eliminan todos los "bc" excepto el que acabamos de crear.
        call(["rm"]+list_bc,shell=False)

    sucess=False
    
    # Hasta que no tengamos éxito en la compilación...
    while not sucess:

        # Se enlazan todos los "bc" de todos los benchmarks y "all.bc" como un solo "bc", de nombre "all.bc".
        error=getoutput("llvm-link-9 "+" ".join(list_bc_to_compile)+" -o "+route_bench+"bc_all/all.bc")
        
        # Se aplica la expresión regular (aunque esté escrita en inglés es mía, antes comentaba
        # en inglés)
        #
        # Regular expression:
        # (?<![\"_a-z])(name)[^a-z_]+ 
        # (?<![\"_a-z])(name)([^a-z_]+)
        #
        # Check if name is a name variable or name function not followed or preceded by
        # something

        # Se comprueba si en la salida del enlazado hay algún error en el enlazado. En concreto,
        # el error capturado son las redefiniciones, si varios elementos tienen nombres repetidos.
        if "multiply defined!" in error:
            # Se captura el nombre redefinido.
            start_index=error.index("Linking globals named '")+len("Linking globals named '")
            name=error[start_index:error.index("'",start_index+1)]
            print('Redefinición detectada:',name)
            print('\t Detección en tiempo: ',datetime.now())
            print('')
            print('')

            redefiniciones+=[[name]]

            # Se sustituye y recompilan los benchmarks con redefiniciones.
            for file,file_w_route,list_hc,list_c,list_bc\
            in zip(list_benchmarks,list_benchmarks_with_route,list_hc_files_w_route_benchmarks,\
            list_c_files_w_route_benchmarks,list_bc_benchmarks):
                recompile=False
                for hc_file_w_route in list_hc:
                    with open(hc_file_w_route, "r") as f:
                        lines=f.readlines()
                    string_lines=''.join(lines)

                    if name in string_lines:
                        recompile=True
                        for i,_ in enumerate(lines):
                            while search('(?<![\\"_a-z])('+name+')[^a-z_]+',lines[i])!=None:
                                lines[i]=sub('(?<![\\"_a-z])('+name+')([^a-z_]+)',\
                                'benchmark_'+file+'_\\1\\2',lines[i])
                    
                    with open(hc_file_w_route, "w") as f:
                        f.writelines(lines)
                    
                if recompile:
                    call(["clang-9","-c","-O0","-lm","-Xclang","-disable-O0-optnone","-w","-emit-llvm"]+\
                    list_c,shell=False)

                    call(["llvm-link-9"]+list_bc+["-o",\
                    route_bench+"bc_all/"+file+".bc"],shell=False)

                    call(["rm"]+list_bc,shell=False)
        else:
            sucess=True
    
    print('Compilación exitosa')
    
    # Se guardan las redefiniciones aparecidas en un CSV.
    with open(route_bench+'nuevas_redefiniciones.csv','w') as file:
        csv.writer(file).writerows(redefiniciones)

    # Se elimina la carpeta usada para arreglar las redefiniciones.
    call(["rm","-r",route_bench+'bc_all/'])
    
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



# Main de ejemplo

#if __name__=="__main__":

    #route_bench="./EEMBC_benchmark_suites_redefinido/"

    #check_correctness_files_and_folders(route_bench)
    
    #save_and_fix_multiple_definitions(route_bench)
    