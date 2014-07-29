#!/bin/bash

INPUT_FILE=$1
RELATION_NAME=$2
OUTFILE=$3
echo "Creating relation extractor file $OUTFILE"
grep $RELATION_NAME $INPUT_FILE > $OUTFILE
