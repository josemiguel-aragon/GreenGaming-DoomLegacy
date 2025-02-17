#!/bin/bash
rm -r ~/experimentos/doomlegacy_optimized/
cp ~/experimentos/doomlegacy_optimized.bc ~/experimentos/doomlegacy_source/bin/doomlegacy.bc
cd ~/experimentos/doomlegacy_source/bin
llc-9 -filetype=obj doomlegacy.bc
clang-9 doomlegacy.o -lm -Wl,--export-dynamic -lpthread -lpcre -lSDL -lz  -lSDL_mixer -lglut -lGLU -lGL -lzip -o doomlegacy
rm doomlegacy.bc
cd "../"
make -s install_user
cd ~/
cp -r ~/games/doomlegacy/ ~/experimentos/doomlegacy_optimized
cp -r ~/experimentos/common_files/* ~/experimentos/doomlegacy_optimized/
rm -r ~/games/doomlegacy/