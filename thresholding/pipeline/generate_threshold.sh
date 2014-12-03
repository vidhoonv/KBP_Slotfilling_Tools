#!/bin/bash

# USAGE:
#
#./main.sh "per:title" 0 0.01 1 lsv_output_2013.txt ../../../lsv/relationfactory-master/evaluation/queries/queries-2013.xml key_file_2013 outputfile

RELATION_TYPE=$1
THRESHOLD_BEGIN=$2
STEP_SIZE=$3
THRESHOLD_END=$4
RE_FILE=$5
QUERIES_FILE=$6
KEY_FILE=$7
OUTFILE=$8

declare -a scores
declare -a threshold
#create RE out file for the relation
./create_RE_outfile.sh $RE_FILE $RELATION_TYPE "$RELATION_TYPE-RE_output.txt"
k=0
for i in `seq $THRESHOLD_BEGIN $STEP_SIZE $THRESHOLD_END`;
do
	#create threshold file
	./create_threshold_file.sh $i $RELATION_TYPE  "thresholds/threshold_file_$RELATION_TYPE-$i.txt"
	#karl's post process
	./karl_postprocess2014/postprocess.py \
  		--queries=$QUERIES_FILE \
  		--infile="$RELATION_TYPE-RE_output.txt" \
  		--thresholds="thresholds/threshold_file_$RELATION_TYPE-$i.txt" \
  		--outfile="relations/pp_$RELATION_TYPE-$i.txt"
	#run evaluator on output file and get F1 score
	score_out=`./evaluator/score2013.sh "relations/pp_$RELATION_TYPE-$i.txt.postprocessed" $KEY_FILE`
	#echo $score_out
	IFS=' '	read -ra parts <<< $score_out
	#echo "k is $k"
	scores[$k]=${parts[1]}
	threshold[$k]=$i
	k=$((k + 1))
done

echo "${scores[*]}"
index=-1
maxval=-1000
k=0
for i in "${scores[@]}"
do
	if [ $i == "NaN" ];
	then
#		echo "NaN detected"
		continue
	fi
#	echo "here $i"
	#echo "$i > $maxval" | bc
	res=$(bc <<< "$i > $maxval")
#	echo $res
	if [ $res -eq 1 ];
	then
		maxval=$i
		index=$k
	fi
	k=$((k + 1))
done

if [ ! -f $OUTFILE ];
then
	echo "creating new outfile"
	touch $OUTFILE
fi

if [ $index -eq -1 ]
then
	#all NaN case
	echo "$RELATION_TYPE  threshold: NIL F1Score: NaN" >> $OUTFILE	
else
	echo "$RELATION_TYPE  threshold: ${threshold[$index]} F1Score: ${scores[$index]}" >> $OUTFILE
fi

