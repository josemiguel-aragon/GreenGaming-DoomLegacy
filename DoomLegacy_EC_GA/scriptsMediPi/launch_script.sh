#!/bin/bash
benchmarks="uncertainty"
for bench in $benchmarks
do
  echo $bench
  cp -r "experimentos/using_benchmarks/benchmarks_${bench}" "experimentos/EEMBC_benchmark_suites/"
  python3 experimentos/tomaMuestrasBench.py "benchmarks_${bench}"
  rm -r "experimentos/EEMBC_benchmark_suites/benchmarks_${bench}"
  rm -r "experimentos/EEMBC_benchmark_suites/binaries/benchmarks_${bench}"
  rm -r "experimentos/EEMBC_benchmark_suites/bc/benchmarks_${bench}"
done
