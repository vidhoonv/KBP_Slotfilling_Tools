#!/bin/bash
# provenance invariant scorer for 2013 data
response=$1
key=$2
#optargs="${@:3}"


java -cp /scratch/cluster/vidhoon/kbp/KBP_Slotfilling_Tools/thresholding/pipeline/evaluator SFScore $response $key anydoc \
| grep -P '\tF1:'

