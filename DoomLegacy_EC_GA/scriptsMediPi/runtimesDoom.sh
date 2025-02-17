#!/bin/bash

# param1    : executable to run 
# param2    : iters


declare -a runtimes=()

#/llvm/bin/opt $1 polybench_small.bc -o output.bc
#/llvm/bin/clang -lm output.bc -o output.out

if [ [$2 = "0"] ]; then
    outputPerf=$( { perf stat ./${1} ;} 2>&1)
    #echo $outputPerf
    if [[ "$outputPerf" =~ ([0-9]+.[0-9]+)\ seconds\ time\ elapsed ]] ; then
        outputPerf=${BASH_REMATCH[1]}
        #echo $outputPerf
    else
        outputPerf="NULL"
        echo $ouputPerf 2>&1
        exit 1
    fi
    outputPerf=${outputPerf//,/.}
    echo $outputPerf
else
    for i in `seq 1 ${2}`; do
        outputPerf=$( { perf stat ./${1} ;} 2>&1)
        if [[ "$outputPerf" =~ ([0-9]+.[0-9]+)\ seconds\ time\ elapsed ]] ; then
            outputPerf=${BASH_REMATCH[1]}
            #echo $outputPerf
        else
            outputPerf="NULL"
            echo $ouputPerf 2>&1
            exit 1
        fi
        runtimes=(${runtimes[@]} $outputPerf)
        #echo "${#runtimes[*]}"
    done
    line=${runtimes[@]}
    line=${line//,/.}
    line=${line// /,}
    echo "$line"
    #echo "$line" > runtimes.csv
fi
