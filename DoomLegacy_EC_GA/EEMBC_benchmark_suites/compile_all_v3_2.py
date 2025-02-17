from distutils.errors import CompileError
from os import listdir,mkdir
from os.path import isfile,isdir
from os import getcwd
import subprocess

__autor__="Jesús Morales Millán"
__contact__="jesus.morales@uca.es"

def allinone(route:str,source_bench_bc:str,passes, target_bench_bc='') -> bool:
    result = True

    if isinstance(passes,list):
        passes = ' '.join(passes)

    if target_bench_bc=='':
        target_bench_bc=source_bench_bc

    cmd = subprocess.Popen("{}opt-9 {} {} -o {}".format(\
        route,passes,source_bench_bc,target_bench_bc),\
        shell=True,stdout=subprocess.DEVNULL,\
        stderr=subprocess.DEVNULL)
    try:
        cmd.wait(timeout=20)
    except:
        if cmd.returncode != 0:
            cmd.kill()
            result = False

    if result and cmd.returncode != 0:
        result = False

    return result

def onebyone(route:str, source_bench_bc:str,passes, target_bench_bc='') -> bool:
    result = True

    if isinstance(passes,str):
        passes = passes.split(' ')

    if target_bench_bc=='':
        target_bench_bc=source_bench_bc

    for llvm_pass in passes:
        cmd = subprocess.Popen("{}opt-9 {} {} -o {}".format(
            route,llvm_pass,source_bench_bc,target_bench_bc),
            shell=True,stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        try:
            cmd.wait(timeout=10)
        except:
            if cmd.returncode != 0:
                cmd.kill()
                result = False

    if result and cmd.returncode != 0:
        result = False

    return result

def apply_passes(passes, source_bc:str, target_bc:str, target_as_source_with_prefix_mod: bool):
    """
    Función para la aplicación de passes, o transformaciones LLVM, sobre un archivo de extensión bc.

    Parámetros:
    - passes: Cadena de caracteres o lista de transformaciones. En caso de ser una cadena de
    caracteres, esta debe de ir separada por espacios.

    - source_bc: Cadena de caracteres que reflejan la ruta al archivo bc que se toma como
    fuente sobre la que alterar. Este queda no alterado.

    - target_bc: Cadena de caracteres que reflejan la ruta donde se encontrará el archivo bc
    sobre el que quedarán reflejados los passes, teniendo source_bc como base. Si source_bc
    y target_bc tienen el mismo valor, deseando aplicar unos passes sobre un bc y que quede
    reflejado en el mismo, se gestionará realizando una copia del mismo.

    - target_as_source_with_prefix_mod: Booleano que indica que el archivo target_bc debe de tener
    el nombre de source_bc precedido por "mod_". En caso de que este booleano tenga un valor de
    True, se ignorará el valor de target_bc.
    """

    if not isinstance(passes,str) and not isinstance(passes,list):
        raise ValueError("Los passes tienen un valor incorrecto")

    if passes!=[]:

        if target_as_source_with_prefix_mod:
            target_bc='/'.join(source_bc.split('/')[:-1])+'/mod_'+source_bc.split('/')[-1]

        copy_bc=False
        if source_bc==target_bc:
            copy_bc=True
            source_bc='/'.join(source_bc.split('/')[:-1])+'/copy_'+source_bc.split('/')[-1]
            subprocess.call(["cp",target_bc,source_bc],shell=False)
        else:
            subprocess.call(["cp",source_bc,target_bc],shell=False)

        result=allinone("",target_bc,passes)
        if not result:
            subprocess.call(["cp", source_bc, target_bc],shell=False)

            result=onebyone("",target_bc,passes)

            if not result:
                raise CompileError("Error al aplicar passes")

        if copy_bc:
            subprocess.call(["rm",source_bc],shell=False)

def compile_all(route_bench,flags=[]):
    """
    Compila todos los benchmarks de todas las suites de la carpeta route_bench usando los
    passes LLVM especificados en flags.

    Genera unas carpetas de nombre "bc" y "binaries" dentro de route_bench, donde se tienen
    las mismas carpetas que en route_bench. En ellas, se guardan los archivos bc correspondientes
    a la compilación, y sus respectivos archivos binarios generados. Se genera un archivo "bc" y
    un binario por cada benchmark, donde ambos tienen los nombres "nombre_de_bench.bc" y
    "nombre_de_bench", respectivamente.

    Parámetros:

    - route_bench: Cadena de caracteres que indican la ruta a la carpeta de suites de
    benchmarks, siguiendo el formato especificado en la documentación.

    - flags: Cadena de caracteres o lista de transformaciones. En caso de ser una cadena de
    caracteres, esta debe de ir separada por espacios.
    """

    if route_bench[-1]!='/':
        route_bench+='/'

    suite_dir=[]
    bench_dir=[]
    for f in listdir(route_bench):
        if isdir(route_bench+f) and 'bc' not in f and 'binaries' not in f:
            suite_dir+=[f]
            bench_dir+=[f+'/'+f_ for f_ in listdir(route_bench+f) if isdir(route_bench+f+'/'+f_)]

    if not isdir(route_bench+'binaries'):
        mkdir(route_bench+'binaries')

    if not isdir(route_bench+'bc'):
        mkdir(route_bench+'bc')

    for aux_dir in suite_dir:
        if not isdir(route_bench+'binaries/'+aux_dir):
            mkdir(route_bench+'binaries/'+aux_dir)
        if not isdir(route_bench+'bc/'+aux_dir):
            mkdir(route_bench+'bc/'+aux_dir)

    for aux_dir in bench_dir:
        files_c_=[route_bench+aux_dir+'/'+f for f in listdir(route_bench+aux_dir) if f[-2:]=='.c']

        other_files=[route_bench+aux_dir+'/'+f for f in listdir(route_bench+aux_dir)\
            if (f[-2:]!='.c' and f[-2:]!='.h' and f[-4:]!='.cpp' and f[-4:]!='.hpp'\
            and isfile(route_bench+aux_dir+'/'+f) and f[-5:]!='.cold' and "README" not in f) or (isdir(route_bench+aux_dir+'/'+f))]

        if not isdir(route_bench+'binaries/'+aux_dir):
            mkdir(route_bench+'binaries/'+aux_dir)
        if not isdir(route_bench+'bc/'+aux_dir):
            mkdir(route_bench+'bc/'+aux_dir)


        subprocess.call(["clang-9","-c","-O0","-lm","-Xclang","-disable-O0-optnone","-w","-emit-llvm"]\
            +files_c_,shell=False)

        list_bc=[f.split('/')[-1][:-2]+'.bc' for f in files_c_]

        subprocess.call(["llvm-link-9"]+list_bc+["-o",route_bench+"bc/"+aux_dir+'/'+\
            aux_dir.split('/')[-1]+'.bc']\
            ,shell=False)

        subprocess.call(["rm"]+list_bc,shell=False)


        apply_passes(passes=flags,\
        source_bc=route_bench+"bc/"+aux_dir+'/'+aux_dir.split('/')[-1]+'.bc',\
        target_bc=route_bench+"bc/"+aux_dir+'/'+aux_dir.split('/')[-1]+'.bc',\
        target_as_source_with_prefix_mod=False)

        subprocess.call(["clang-9","-lm","-w","-O0",\
            route_bench+"bc/"+aux_dir+'/'+aux_dir.split('/')[-1]+'.bc',\
            "-o",\
            route_bench+"binaries/"+aux_dir+'/'+aux_dir.split('/')[-1]],shell=False)

        if other_files!=[]:
            for other_file in other_files:
                subprocess.call(["cp","-r",other_file,route_bench+"binaries/"+aux_dir],shell=False)
                subprocess.call(["cp","-r",other_file,route_bench+"bc/"+aux_dir],shell=False)

def compile_one_bench(route_bench,route_single_bench,flags=[]):
    """
    Compila el benchmarks de la carpeta route_single_bench dentro de route_bench usando los
    passes LLVM especificados en flags.

    Genera unas carpetas de nombre "bc" y "binaries" dentro de route_bench, donde se tienen
    las mismas carpetas que en route_bench. En ellas, se guardan los archivos bc correspondientes
    a la compilación, y sus respectivos archivos binarios generados. Se genera un archivo "bc" y
    un binario por cada benchmark, donde ambos tienen los nombres "nombre_de_bench.bc" y
    "nombre_de_bench", respectivamente.

    Parámetros:

    - route_bench: Cadena de caracteres que indican la ruta a la carpeta de suites de
    benchmarks, siguiendo el formato especificado en la documentación.

    - route_single_bench: Cadena de caracteres que indica la ruta al benchmark que queremos
    compilar dentro de route_bench, la carpeta de las suites.

		Ejemplo:
            route_bench:
                'ruta/carpeta_de_benchmarks'
            route_single_bench:
                'benchmarks_suiteA/benchmark_de_ejemplo/benchmark_de_ejemplo'

            La ruta completa estaría formada por route_bench+'/'+route_single_bench

    - flags: Cadena de caracteres o lista de transformaciones. En caso de ser una cadena de
    caracteres, esta debe de ir separada por espacios.
    """

    if route_bench[-1]!='/':
        route_bench+='/'

    if route_single_bench[-1]=='/':
        route_single_bench=route_single_bench[:-1]

    split_route=route_single_bench.split('/')

    if len(split_route)!=2 and len(split_route)!=3:
        raise ValueError('Ruta del benchmark no definida correctamente.')

    if len(split_route)==3:
        route_single_bench='/'.join(split_route[:-1])

    if not isdir(route_bench+'binaries'):
        mkdir(route_bench+'binaries')

    if not isdir(route_bench+'bc'):
        mkdir(route_bench+'bc')

    for aux_dir in [split_route[0],route_single_bench]:
        if not isdir(route_bench+'binaries/'+aux_dir):
            mkdir(route_bench+'binaries/'+aux_dir)
        if not isdir(route_bench+'bc/'+aux_dir):
            mkdir(route_bench+'bc/'+aux_dir)

    files_c_=[route_bench+route_single_bench+'/'+f for f in listdir(route_bench+route_single_bench) if f[-2:]=='.c']

    other_files=[route_bench+route_single_bench+'/'+f for f in listdir(route_bench+route_single_bench)\
        if (f[-2:]!='.c' and f[-2:]!='.h' and f[-4:]!='.cpp' and f[-4:]!='.hpp'\
        and isfile(route_bench+route_single_bench+'/'+f) and f[-5:]!='.cold' and "README" not in f) or (isdir(route_bench+route_single_bench+'/'+f))]

    if not isdir(route_bench+'binaries/'+route_single_bench):
        mkdir(route_bench+'binaries/'+route_single_bench)
    if not isdir(route_bench+'bc/'+route_single_bench):
        mkdir(route_bench+'bc/'+route_single_bench)

    subprocess.call(["clang-9","-c","-O0","-lm","-Xclang","-disable-O0-optnone","-w","-emit-llvm"]\
        +files_c_,shell=False)

    list_bc=[f.split('/')[-1][:-2]+'.bc' for f in files_c_]

    subprocess.call(["llvm-link-9"]+list_bc+["-o",route_bench+"bc/"+route_single_bench+'/'+\
        route_single_bench.split('/')[-1]+'.bc']\
        ,shell=False)

    subprocess.call(["rm"]+list_bc,shell=False)


    apply_passes(passes=flags,\
        source_bc=route_bench+"bc/"+route_single_bench+'/'+route_single_bench.split('/')[-1]+'.bc',\
        target_bc=route_bench+"bc/"+route_single_bench+'/'+route_single_bench.split('/')[-1]+'.bc',\
        target_as_source_with_prefix_mod=False)

    subprocess.call(["clang-9","-lm","-w","-O0",\
        route_bench+"bc/"+route_single_bench+'/'+route_single_bench.split('/')[-1]+'.bc',\
        "-o",\
        route_bench+"binaries/"+route_single_bench+'/'+route_single_bench.split('/')[-1]],shell=False)

    if other_files!=[]:
        for other_file in other_files:
            subprocess.call(["cp","-r",other_file,route_bench+"binaries/"+route_single_bench],shell=False)
            subprocess.call(["cp","-r",other_file,route_bench+"bc/"+route_single_bench],shell=False)


def apply_flags_and_recompile_already_compiled_benchmark(route_bench,route_single_bench,flags,route_target_bench,\
    target_as_source_with_prefix_mod):
    """
    Aplica las transformaciones indicadas en flags al archivo guardado en la carpeta
    route_single_bench.

    Parámetros:

    - route_bench: Cadena de caracteres que indican la ruta a la carpeta de suites de
    benchmarks, siguiendo el formato especificado en la documentación.

    - route_single_bench: Cadena de caracteres que indica la ruta al benchmark que queremos
    aplicar las transformaciones dentro de route_bench, la carpeta de las suites.

		Ejemplo:
            route_bench:
                'ruta/carpeta_de_benchmarks'
            route_single_bench:
                'benchmarks_suiteA/benchmark_de_ejemplo/benchmark_de_ejemplo'

            La ruta completa estaría formada por route_bench+'/'+route_single_bench

            Las transformaciones, en este caso, se aplicarían sobre el archivo:

            ruta/carpeta_de_benchmarks/benchmarks_suiteA/benchmark_de_ejemplo/benchmark_de_ejemplo.bc

    - flags: Cadena de caracteres o lista de transformaciones. En caso de ser una cadena de
    caracteres, esta debe de ir separada por espacios.

    - route_target_bench: Cadena de caracteres que reflejan la ruta donde se encontrará el archivo bc
    sobre el que quedarán reflejados los passes, teniendo el ubicado en route_single_bench como base.
    Si el route_single_bench y route_target_bench tienen el mismo valor, deseando aplicar unos passes
    sobre un bc y que quede reflejado en el mismo, se gestionará realizando una copia del mismo.

    - target_as_source_with_prefix_mod: Booleano que indica que el archivo del directorio
    route_target_bench debe de tener el nombre de source_bc precedido por "mod_". En caso de que este
    booleano tenga un valor de  True, se ignorará el valor de route_target_bench. De esta manera, se
    encontrará en el mismo directorio que route_target_bench pero con nombre cambiado.
    """

    if route_bench[-1]!='/':
        route_bench+='/'

    if route_single_bench[-1]=='/':
        route_single_bench=route_single_bench[:-1]

    split_route=route_single_bench.split('/')

    if len(split_route)!=2 and len(split_route)!=3:
        raise ValueError('Ruta del benchmark no definida correctamente.')

    if len(split_route)==2:
        route_single_bench+='/'+split_route[-1]

    if target_as_source_with_prefix_mod:
        route_target_bench='/'.join(route_single_bench.split('/')[:-1])+'/mod_'+route_single_bench.split('/')[-1]
    else:
        if route_target_bench=='':
            route_target_bench=route_single_bench


    apply_passes(passes=flags,\
        source_bc=route_bench+"bc/"+route_single_bench+'.bc',\
        target_bc=route_bench+"bc/"+route_target_bench+'.bc',\
        target_as_source_with_prefix_mod=target_as_source_with_prefix_mod)

    subprocess.call(["clang-9","-lm","-w","-O0",\
        route_bench+"bc/"+route_target_bench+'.bc',\
        "-o",\
        route_bench+"binaries/"+route_single_bench],shell=False)

def get_benchmarks_available_in_requested_format(route_bench):
    """
    Devuelve una lista de benchmarks ubicados en el directorio route_bench en el formato
    que el resto de métodos utilizan. Esto es, la ruta hasta los directorios de los
    benchmarks partiendo de route_bench.

    Ejemplo:
        route_bench:
            'ruta/carpeta_de_benchmarks'
        Ruta a un benchmark (de ejemplo):
            'benchmarks_suiteA/benchmark_de_ejemplo/benchmark_de_ejemplo'

        La ruta al benchmark de ejemplocompleta estaría formada por
        route_bench+'/'+route_single_bench.
    """
    if route_bench[-1]!='/':
        route_bench+='/'

    bench_list=[]
    for f_ in listdir(route_bench):
        bench_list+=[f_+'/'+f for f in listdir(route_bench+f_) if isdir(route_bench+f_+'/'+f)]
    return bench_list
