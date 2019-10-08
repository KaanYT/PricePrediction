#!/bin/bash
#
# Unpack all the zipped twitter archive in same directory from:
# https://archive.org/details/twitterstream
#
files=`ls *.tar`
for t in ${files} ; do
	filename=$(basename -- "$t")
	extension="${filename##*.}"
	filename="${filename%.*}"
	bn="$filename"
	mkdir -p "$bn"
	tar -xvf "$t" -C "$bn"
	mv "$t" "$bn"
done