import sys

INFILE=sys.argv[1]
OUTFILE=sys.argv[2]

infile=open(INFILE)
outfile=open(OUTFILE,'w')

lines=infile.readlines()

relations=list()


relations.append("per:alternate_names")
relations.append("per:date_of_birth")
relations.append("per:age")
relations.append("per:country_of_birth")
relations.append("per:stateorprovince_of_birth")
relations.append("per:city_of_birth")
relations.append("per:origin")
relations.append("per:date_of_death")
relations.append("per:country_of_death")
relations.append("per:stateorprovince_of_death")
relations.append("per:city_of_death")
relations.append("per:cause_of_death")
relations.append("per:countries_of_residence")
relations.append("per:statesorprovinces_of_residence")
relations.append("per:cities_of_residence")
relations.append("per:schools_attended")
relations.append("per:title")
relations.append("per:employee_or_member_of")
relations.append("per:religion")
relations.append("per:spouse")
relations.append("per:children")
relations.append("per:parents")
relations.append("per:siblings")
relations.append("per:other_family")
relations.append("per:charges")
relations.append("org:alternate_names")
relations.append("org:political_religious_affiliation")
relations.append("org:top_members_employees")
relations.append("org:number_of_employees_members")
relations.append("org:members")
relations.append("org:member_of")
relations.append("org:subsidiaries")
relations.append("org:parents")
relations.append("org:founded_by")
relations.append("org:date_founded")
relations.append("org:date_dissolved")
relations.append("org:country_of_headquarters")
relations.append("org:stateorprovince_of_headquarters")
relations.append("org:city_of_headquarters")
relations.append("org:shareholders")
relations.append("org:website")

fill_type = {}
thresholds = {}

fill_type["per:alternate_names"]="list"
fill_type["per:date_of_birth"]="single"
fill_type["per:age"]="single"
fill_type["per:country_of_birth"]="single"
fill_type["per:stateorprovince_of_birth"]="single"
fill_type["per:city_of_birth"]="single"
fill_type["per:origin"]="list"
fill_type["per:date_of_death"]="single"
fill_type["per:country_of_death"]="single"
fill_type["per:stateorprovince_of_death"]="single"
fill_type["per:city_of_death"]="single"
fill_type["per:cause_of_death"]="single"
fill_type["per:countries_of_residence"]="list"
fill_type["per:statesorprovinces_of_residence"]="list"
fill_type["per:cities_of_residence"]="list"
fill_type["per:schools_attended"]="list"
fill_type["per:title"]="list"
fill_type["per:employee_or_member_of"]="list"
fill_type["per:religion"]="single"
fill_type["per:spouse"]="list"
fill_type["per:children"]="list"
fill_type["per:parents"]="list"
fill_type["per:siblings"]="list"
fill_type["per:other_family"]="list"
fill_type["per:charges"]="list"
fill_type["org:alternate_names"]="list"
fill_type["org:political_religious_affiliation"]="list"
fill_type["org:top_members_employees"]="list"
fill_type["org:number_of_employees_members"]="single"
fill_type["org:members"]="list"
fill_type["org:member_of"]="list"
fill_type["org:subsidiaries"]="list"
fill_type["org:parents"]="list"
fill_type["org:founded_by"]="list"
fill_type["org:date_founded"]="single"
fill_type["org:date_dissolved"]="single"
fill_type["org:country_of_headquarters"]="single"
fill_type["org:stateorprovince_of_headquarters"]="single"
fill_type["org:city_of_headquarters"]="single"
fill_type["org:shareholders"]="list"
fill_type["org:website"]="single"


for line in lines:
	parts=line.split(' ')
	if parts[3]=="NIL":
		thresholds[parts[0]] = 1.0
	else:
		thresholds[parts[0]] = parts[3]

for relation in relations:
	if relation in thresholds:
		newline=relation+" "+fill_type[relation]+" "+str(thresholds[relation])
		outfile.write("%s\n" % newline)
	else:
		print "key not found in thresholds: "+relation

outfile.close()
