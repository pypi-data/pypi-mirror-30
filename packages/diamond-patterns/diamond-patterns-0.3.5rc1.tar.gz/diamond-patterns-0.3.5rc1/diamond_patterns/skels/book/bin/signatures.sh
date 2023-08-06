#!/bin/bash

# create print signatures
# 4-page imposition, meaning 4 pages on a single double-sided sheet of paper
# 4 sheets (16 pages) per booklet
# This is not a 16-page signature, per se, but a 4x4-page signature
# create the number of 4x4-page signatures required to print the entire book

# from https://www.designersinsights.com/designer-resources/understanding-and-working-with-print/
# "a signature is a group of pages that are printed on both sides of a single sheet of paper"

PRODUCT=$1

cd .build
rm -rf signatures
mkdir signatures

# TODO: this process is not flexible enough to handle books above or below 160 pages.

echo "split original PDF into 16-page segments"
pdfjam ${PRODUCT}.pdf '1-16'       --outfile signatures/${PRODUCT}-01.pdf
pdfjam ${PRODUCT}.pdf '17-32'      --outfile signatures/${PRODUCT}-02.pdf
pdfjam ${PRODUCT}.pdf '33-48'      --outfile signatures/${PRODUCT}-03.pdf
pdfjam ${PRODUCT}.pdf '49-64'      --outfile signatures/${PRODUCT}-04.pdf
pdfjam ${PRODUCT}.pdf '65-80'      --outfile signatures/${PRODUCT}-05.pdf
pdfjam ${PRODUCT}.pdf '81-96'      --outfile signatures/${PRODUCT}-06.pdf
pdfjam ${PRODUCT}.pdf '97-112'     --outfile signatures/${PRODUCT}-07.pdf
pdfjam ${PRODUCT}.pdf '113-128'    --outfile signatures/${PRODUCT}-08.pdf
pdfjam ${PRODUCT}.pdf '129-144'    --outfile signatures/${PRODUCT}-09.pdf
pdfjam ${PRODUCT}.pdf '145-'       --outfile signatures/${PRODUCT}-10.pdf
# pdfjam ${PRODUCT}.pdf '145-160'    --outfile signatures/${PRODUCT}-10.pdf
# pdfjam ${PRODUCT}.pdf '161-'       --outfile signatures/${PRODUCT}-11.pdf

echo "convert 16-page segments into 4-page, 4-up signatures"
for i in 01 02 03 04 05 06 07 08 09 10; do
    pdfbook "signatures/${PRODUCT}-$i.pdf"
done
mv *-book.pdf signatures

echo "recombine PDFs"
pdfjoin signatures/${PRODUCT}-??-book.pdf
mv ${PRODUCT}-??-book-joined.pdf signatures/${PRODUCT}-book-joined.pdf

echo "split the PDF signatures into odd-page and even-page"
pdftk A=signatures/${PRODUCT}-book-joined.pdf \
    cat 'AoddDown' output ${PRODUCT}-book-odd.pdf

pdftk A=signatures/${PRODUCT}-book-joined.pdf \
    cat Aeven output ${PRODUCT}-book-even.pdf
