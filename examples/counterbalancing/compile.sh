#!/bin/sh

# group A
textx generate counterbalancing.pf --target psychopy --overwrite --group A -o houses.py
textx generate counterbalancing.pf --target log --overwrite --group A -o houses.pflog

# group B
textx generate counterbalancing.pf --target psychopy --overwrite -o faces.py
textx generate counterbalancing.pf --target log --overwrite -o faces.pflog
