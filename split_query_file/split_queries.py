import csv
import sys

INPUT_FILE=sys.argv[1]
FILE_PREFIX=sys.argv[2]
NUM_QUERIES_PER_FILE=int(sys.argv[3])

infile=open(INPUT_FILE)
counter=0;
fcounter=0;
inquery=False
query_lines=list()
query_lines.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
query_lines.append("\t<kbpslotfill>\n")
for line in infile:
	parts=line.strip()
	parts=parts.split(' ')
	#print parts[0]
	if parts[0] == "<?xml" or parts[0]=="<kbpslotfill>":
		continue
	elif parts[0]=="<query":
		#start of query
		inquery=True
		query_lines.append(line)
	elif parts[0]=="</query>":
		#end of query
		counter+=1
		query_lines.append(line)
		if counter==NUM_QUERIES_PER_FILE:
			counter=0
			inquery=False
			query_lines.append("</kbpslotfill>")
			outfile=open(FILE_PREFIX+str(fcounter),'w')
			for lin in query_lines:
				outfile.write("%s" % lin)
			fcounter+=1
			outfile.close()
			query_lines=list()
			query_lines.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
			query_lines.append("\t<kbpslotfill>\n")
	elif parts[0] == "</kbpslotfill>":
		query_lines.append(line)
		outfile=open(FILE_PREFIX+str(fcounter),'w')
		for lin in query_lines:
			outfile.write("%s" % lin)
		fcounter+=1
		outfile.close()
		sys.exit("done")
	elif inquery==True:
		query_lines.append(line)