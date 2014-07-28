#
# AUTHOR: Vidhoon Viswanathan (for UT Austin KBP SF system)
#
#
import csv
import sys


#USAGE:
#python extract_secondset_queries.py <OUTPUT_OF_ORIGINAL_QUERIES> <NEW_QUERIES_FILE.XML> <YEAR> <PREFIX_FOR_QUERYID>
INFILE=sys.argv[1]
OUTFILE=sys.argv[2]
YEAR=int(sys.argv[3])
PREFIX=sys.argv[4]

relationsOfInterest=list()
etypes={}
relationsOfInterest.append("org:founded_by")
etypes["org:founded_by"]="PER"

relationsOfInterest.append("org:members")
etypes["org:members"]="ORG"


relationsOfInterest.append("org:parents")
etypes["org:parents"]="ORG"


relationsOfInterest.append("org:shareholders")
etypes["org:shareholders"]="ORG"
#etypes.append("ORG")

relationsOfInterest.append("org:subsidiaries")
etypes["org:subsidiaries"]="ORG"
#etypes.append("ORG")

relationsOfInterest.append("org:top_members_employees")
etypes["org:top_members_employees"]="PER"
#etypes.append("PER")

relationsOfInterest.append("per:children")
etypes["per:children"]="PER"
#etypes.append("PER")

relationsOfInterest.append("per:employee_or_member_of")
etypes["per:employee_or_member_of"]="ORG"
#etypes.append("ORG")

relationsOfInterest.append("per:other_family")
etypes["per:other_family"]="PER"
#etypes.append("PER")

relationsOfInterest.append("per:parents")
etypes["per:parents"]="PER"
#etypes.append("PER")

relationsOfInterest.append("per:schools_attended")
etypes["per:schools_attended"]="ORG"
#etypes.append("ORG")

relationsOfInterest.append("per:siblings")
etypes["per:siblings"]="PER"
#etypes.append("PER")

relationsOfInterest.append("per:spouse")
etypes["per:spouse"]="PER"
#etypes.append("PER")





newQueries=list()
docids=list()
spans=list()
quert_entity_types=list()

#the column number of LSV system output
if YEAR==2013:
	RELATIONTYPE_FIELD_ID=1
	SLOTVALUE_FIELD_ID=4
	DOCID_FIELD_ID=3
	SPAN_FIELD_ID=5
elif YEAR==2014:
	RELATIONTYPE_FIELD_ID=1
	SLOTVALUE_FIELD_ID=4
	DOCID_FIELD_ID=5
else:
	sys.exit("Year undefined!!")

rel_file = open(INFILE)
outfile=open(OUTFILE,'w')

rel_reader=csv.reader(rel_file,delimiter="\t")

for row in rel_reader:
	if len(row)==4:
		continue
	elif row[RELATIONTYPE_FIELD_ID] in relationsOfInterest:
		if YEAR==2013:
			newQueries.append(row[SLOTVALUE_FIELD_ID])
			doc_id=row[DOCID_FIELD_ID]
			span=row[SPAN_FIELD_ID]
			spans.append(span)
			docids.append(doc_id)
			quert_entity_types.append(etypes[row[RELATIONTYPE_FIELD_ID]])
		elif YEAR==2014:
			newQueries.append(row[SLOTVALUE_FIELD_ID])
			doc_id=row[DOCID_FIELD_ID].split(':')[0]
			span=row[DOCID_FIELD_ID].split(':')[1]
			spans.append(span)
			docids.append(doc_id)
			quert_entity_types.append(etypes[row[RELATIONTYPE_FIELD_ID]])
		else:
			sys.exit("Year undefined!!")			
	else:
		continue	

# <?xml version="1.0" encoding="UTF-8"?>
# <kbpslotfill>
#   <query id="SF14_ENG_001">
#     <name>Ahmed Rashid</name>
#     <enttype>PER</enttype>
#     <docid>eng-NG-31-100600-11180231</docid>
#     <beg>21904</beg>
#     <end>21915</end>
#   </query>

counter=1
id_prefix=PREFIX #"SF14_ENG_SECRUN"
list_of_lines=list()
list_of_lines.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
list_of_lines.append("\t<kbpslotfill>")

for query,did,sp,etype in zip(newQueries,docids,spans,quert_entity_types):
	padded_counter='%03d' % counter
	query_id=id_prefix + padded_counter
	rang=sp.split("-")
	if YEAR==2013:
		list_of_lines.append("\t\t<query id=\""+query_id+"\">")
		list_of_lines.append("\t\t\t<name>"+query+"</name>")
		list_of_lines.append("\t\t\t<docid>"+did+"</docid>")
		list_of_lines.append("\t\t\t<beg>"+rang[0]+"</beg>")
		list_of_lines.append("\t\t\t<end>"+rang[1]+"</end>")
		list_of_lines.append("\t\t\t<enttype>"+etype+"</enttype>")
		list_of_lines.append("\t\t\t<nodeid>NIL</nodeid>")
		list_of_lines.append("\t\t</query>")		
	elif YEAR==2014:
		list_of_lines.append("\t\t<query id=\""+query_id+"\">")
		list_of_lines.append("\t\t\t<name>"+query+"</name>")
		list_of_lines.append("\t\t\t<enttype>"+etype+"</enttype>")
		list_of_lines.append("\t\t\t<docid>"+did+"</docid>")
		list_of_lines.append("\t\t\t<beg>"+rang[0]+"</beg>")
		list_of_lines.append("\t\t\t<end>"+rang[1]+"</end>")
		list_of_lines.append("\t\t</query>")
	else:
		sys.exit("YEAR undefined")	
	counter+=1

list_of_lines.append("\t</kbpslotfill>")

for line in list_of_lines:
  outfile.write("%s\n" % line)

outfile.close()
print "Number of second set queries generated: ",len(newQueries)