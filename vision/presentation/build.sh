#!/bin/bash
pandoc --slide-level 2 --template=custom.beamer --toc -t beamer presentation.md -o presentation.pdf
pdfnup presentation.pdf --nup 2x3 --no-landscape --keepinfo --paper A4 --frame true --scale 0.9 --suffix "nup"