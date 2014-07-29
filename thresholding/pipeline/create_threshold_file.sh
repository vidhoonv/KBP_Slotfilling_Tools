#!/bin/bash

THRESHOLD_VALUE=$1
RELATION_TYPE=$2
THRESHOLD_FILE=$3

relations[0]="per:alternate_names"
relations[1]="per:date_of_birth"
relations[2]="per:age"
relations[3]="per:country_of_birth"
relations[4]="per:stateorprovince_of_birth"
relations[5]="per:city_of_birth"
relations[6]="per:origin"
relations[7]="per:date_of_death"
relations[8]="per:country_of_death"
relations[9]="per:stateorprovince_of_death"
relations[10]="per:city_of_death"
relations[11]="per:cause_of_death"
relations[12]="per:countries_of_residence"

relations[13]="per:statesorprovinces_of_residence"
relations[14]="per:cities_of_residence"
relations[15]="per:schools_attended"
relations[16]="per:title"
relations[17]="per:employee_or_member_of"
relations[18]="per:religion"
relations[19]="per:spouse"
relations[20]="per:children"
relations[21]="per:parents"
relations[22]="per:siblings"
relations[23]="per:other_family"
relations[24]="per:charges"

relations[25]="org:alternate_names"
relations[26]="org:political_religious_affiliation"
relations[27]="org:top_members_employees"
relations[28]="org:number_of_employees_members"
relations[29]="org:members"
relations[30]="org:member_of"
relations[31]="org:subsidiaries"
relations[32]="org:parents"
relations[33]="org:founded_by"
relations[34]="org:date_founded"
relations[35]="org:date_dissolved"
relations[36]="org:country_of_headquarters"
relations[37]="org:stateorprovince_of_headquarters"
relations[38]="org:city_of_headquarters"
relations[39]="org:shareholders"
relations[40]="org:website"



slot_type[0]="list"
slot_type[1]="single"
slot_type[2]="single"
slot_type[3]="single"
slot_type[4]="single"
slot_type[5]="single"
slot_type[6]="list"
slot_type[7]="single"
slot_type[8]="single"
slot_type[9]="single"
slot_type[10]="single"
slot_type[11]="single"
slot_type[12]="list"
slot_type[13]="list"
slot_type[14]="list"
slot_type[15]="list"
slot_type[16]="list"
slot_type[17]="list"
slot_type[18]="single"
slot_type[19]="list"
slot_type[20]="list"
slot_type[21]="list"
slot_type[22]="list"
slot_type[23]="list"
slot_type[24]="list"

slot_type[25]="list"
slot_type[26]="list"
slot_type[27]="list"
slot_type[28]="single"
slot_type[29]="list"
slot_type[30]="list"
slot_type[31]="list"
slot_type[32]="list"
slot_type[33]="list"
slot_type[34]="single"
slot_type[35]="single"
slot_type[36]="single"
slot_type[37]="single"
slot_type[38]="single"
slot_type[39]="list"
slot_type[40]="single"


touch $THRESHOLD_FILE

for i in `seq 0 40`;
do
#	echo " $RELATION_TYPE => ${relations[$i]}"
	if [ $RELATION_TYPE == ${relations[$i]} ]
	then
		echo "${relations[$i]} ${slot_type[$i]} $THRESHOLD_VALUE" >> $THRESHOLD_FILE
	else
		echo "${relations[$i]} ${slot_type[$i]} 0.0" >> $THRESHOLD_FILE
	fi
done


