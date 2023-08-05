import os, csv
from Bio import SeqIO

def execute(input_file, output_file):
	f = csv.writer(open(output_file, "w"))
	f.writerow(['name', 'fraction'])

	for seq_record in SeqIO.parse(input_file, "fasta"):
		f.writerow([seq_record.description.split()[0]+"_"+seq_record.description.split()[1], 
			float(seq_record.seq.count("C")+seq_record.seq.count("G"))/len(seq_record.seq)])
