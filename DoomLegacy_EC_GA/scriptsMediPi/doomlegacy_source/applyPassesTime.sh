#!/bin/bash
rm -r "./doomlegacy_optimized"
cd "./doomlegacy_source"
make clean
sed -i "s/OPTLEV=.*/OPTLEV=${1}/" src/Makefile
sed -i "s/OPTLEV=.*/OPTLEV=${1}/" Makefile
make
make install_user
cd "../"
cp -r "~/games/doomlegacy/" "./doomlegacy_optimized"
cp -r "./common_files/*" "./doomlegacy_optimized/"
rm -r "~/games/doomlegacy/"

