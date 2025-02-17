#!/bin/bash
rm -r ~/experimentos/doomlegacy_optimized
cd ~/experimentos/doomlegacy_source
make clean
sed -i "s/OPTLEV=.*/OPTLEV=-O0/" ~/experimentos/doomlegacy_source/src/Makefile
sed -i "s/OPTLEV=.*/OPTLEV=-O0/" ~/experimentos/doomlegacy_source/Makefile
export LLVM_COMPILER=clang
make -s
cd "./bin"
extract-bc doomlegacy
mv doomlegacy.bc doomlegacy_original.bc
cp doomlegacy_original.bc ../
rm doomlegacy
cd ~/
