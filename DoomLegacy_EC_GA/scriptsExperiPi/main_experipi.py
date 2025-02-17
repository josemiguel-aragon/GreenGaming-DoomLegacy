from os import system, chdir, getenv
import sys, getopt

#from time import time
from time import monotonic as time

import csv

import board
from digitalio import DigitalInOut, Direction, Pull

__autor__="Jesús Morales Millán"
__contact__="jesus.morales@uca.es"

def custom_sleep(seconds):
    t__=time()+seconds

    while time()<t__:
        pass

def checkPin(pin,updownstate):
    """
    Comprueba que un pin GPIO tiene el valor dado por updownstate, ya sea alto (1) o bajo (0).
    La espera introducida asegura que no se puedan producir rebotes.
    """
    if pin.value == updownstate:
        custom_sleep(0.001)
        #custom_sleep(0.003)

        if pin.value == updownstate:
            return True
    return False
    
if __name__=="__main__":

    pin_ejecucion_general = DigitalInOut(board.D13)
    pin_ejecucion_general.direction = Direction.OUTPUT
    pin_ejecucion_general.value = True

    pin_ejecucion = DigitalInOut(board.D26)
    pin_ejecucion.direction = Direction.OUTPUT
    pin_ejecucion.value = False

    pin_escritura_disco=DigitalInOut(board.D19)
    pin_escritura_disco.direction = Direction.INPUT
    pin_escritura_disco.pull = Pull.UP


    try:
        opts, args = getopt.getopt(sys.argv[1:],"n:i:t:w:",[])
    except getopt.GetoptError:
        print('Error: main_experipi.py')
        sys.exit(2)

    for opt, arg in opts:
        if opt=='-n':
            name=str(arg)
        if opt=='-i':
            iters=int(arg)
        if opt=='-t':
            tiempo_ej=int(arg)
        if opt=='-w':
            wait_time=float(arg)

    total_wait_time=0.002+wait_time


    system('sudo ./experimentos/tumbarServicios6.sh')

    total_elapsed_time=time()

    #list_t=[]

    chdir('./experimentos/binaries/'+name[:name.rfind('/')])
    
    name=name[name.rfind('/')+1:]

    #aux=2+name.count('/')

    if tiempo_ej==0:        
        for i in range(0,iters):
            while checkPin(pin_escritura_disco,True):
                pass

            custom_sleep(total_wait_time)
            
            pin_ejecucion.value=True

            #custom_sleep(0.002)

            system('./'+name)

            pin_ejecucion.value=False

            #custom_sleep(total_wait_time)

    else:
        t_acum=0
        while t_acum<tiempo_ej:
            while checkPin(pin_escritura_disco,True):
                pass

            custom_sleep(total_wait_time)

            t_aux=time()
            
            pin_ejecucion.value=True
            
            #custom_sleep(0.002)

            system('./'+name)
            
            pin_ejecucion.value=False

            t_acum+=time()-t_aux
            
            #t_aux=time()-t_aux
            #list_t+=[[t_aux]]
            #t_acum+=t_aux

            #custom_sleep(total_wait_time)

    total_elapsed_time=time()-total_elapsed_time
    
    if total_elapsed_time<5:
        custom_sleep(5-total_elapsed_time)

    """route=''
    for _ in range(0,aux):
        route+='../'
    chdir(route)"""


    chdir(getenv("HOME"))

    system('sudo ./experimentos/iniciarServicios.sh')

    #with open('./experimentos/times_'+name+'.csv','w') as file:
        #csv.writer(file).writerows(list_t)

    pin_ejecucion_general.value=False