#!/bin/bash

UIDIR="pyflies/gui/ui"

for f in `find $UIDIR -iname *.ui`; do
	pyuic4 --from-imports "$f" -o "${f%ui}py"
done

for f in `find  $UIDIR -iname *.qrc`; do
	pyrcc4 -py3 "$f" -o "${f%.qrc}_rc.py"
done
