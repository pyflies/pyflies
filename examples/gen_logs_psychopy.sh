#!/bin/sh

for model in HelloWorld/HelloWorld.pf EriksenFlanker/EriksenFlanker.pf Simon/Simon.pf PosnerCueing/PosnerCueing.pf Parity/Parity.pf blocking/blocking.pf
do
    textx generate $model --target log --overwrite
    textx generate $model --target psychopy --overwrite
done

cd counterbalancing
./compile.sh
