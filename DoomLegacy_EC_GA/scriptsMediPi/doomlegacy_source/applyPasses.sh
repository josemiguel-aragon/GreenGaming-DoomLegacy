#!/bin/bash
rm -r "~/experimentos/doomlegacy_optimized"
cd "~/experimentos/doomlegacy_source"
make clean
sed -i "s/OPTLEV=.*/OPTLEV=-O0/" src/Makefile
sed -i "s/OPTLEV=.*/OPTLEV=-O0/" Makefile
export LLVM_COMPILER=clang
make
cd "./bin"
extract-bc doomlegacy
opt-9 $1 doomlegacy.bc -o doomlegacy.bc
llc-9 -filetype=obj doomlegacy.bc
rm doomlegacy
clang-9 doomlegacy.o -lm -Wl,--export-dynamic -lpthread -lpcre -lSDL -lz  -lSDL_mixer -lOpenGL  -lglut -lGLU -lGL -lzip -o doomlegacy
cd "../"
make install_user
cp -r "~/games/doomlegacy/" "~/experimentos/doomlegacy_optimized"
cp -r "~/experimentos/common_files/*" "~/experimentos/doomlegacy_optimized/"
rm -r "~/games/doomlegacy/"
cd "~/"

