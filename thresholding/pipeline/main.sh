#!/bin/bash

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

for relation in ${relations[@]}
do
	echo "Submitting threshold generation job for relation :  $relation"
	./generate_threshold.sh $relation  0 0.01 1 2013-lsv-with-ut-inference-setthresholds.txt ../../../lsv/relationfactory-master/evaluation/queries/queries-2013.xml  key_file_2013 lsv_inference_thresholds.txt
done

echo "All jobs submitted"
