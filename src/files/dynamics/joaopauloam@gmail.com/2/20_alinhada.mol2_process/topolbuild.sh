#!/bin/bash
export topo=~/topolbuild1_2_1
echo -n " Enter mol2 path (do not put file extension): "
read filemol2
cp $topo/src/topolbuild $PWD
./topolbuild -n $filemol2 -dir $topo -ff gaff
rm $PWD/topolbuild
