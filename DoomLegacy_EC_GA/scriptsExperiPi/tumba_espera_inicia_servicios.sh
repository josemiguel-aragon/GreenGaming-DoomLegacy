#!/bin/bash

helpFunction()
{
   echo ""
   echo "Uso: $0 -t parameterT"
   echo -e "\t-t Tiempo de espera entre que se tumban y levantan los servicios"
}

while getopts "t:" opt
do
   case "$opt" in
      t ) time="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

if [ -z "$time" ]
then
   echo "No se ha dado el parámetro de tiempo.";
   helpFunction
fi

# Begin script in case all parameters are correct

time=$((time+10))
echo "$time"

./experimentos/tumbarServicios6.sh
read -t $time
./experimentos/iniciarServicios.sh
