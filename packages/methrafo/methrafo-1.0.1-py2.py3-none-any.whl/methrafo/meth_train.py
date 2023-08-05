#!/usr/bin/env python
"""
methrafo.train <reference genomes><input MeDIP-Seq bigWig> <input Bisulfite-Seq bigWig> <output model prefix>
e.g.
methrafo.train hg19 example_MeDIP.bw example_Bisulfite.bw trained_model

"""


import pdb,sys,os
import gzip
from File import *
import re
import pyBigWig
from scipy.stats import pearsonr
from sklearn.ensemble import RandomForestRegressor
import math
import cPickle as pickle


#-----------------------------------------------------------------------
def fetchGenome(chrom_id,gref):
	with gzip.open(gref+'/'+chrom_id+'.fa.gz','rb') as f:
			lf=f.read()
			lf=lf.split("\n")
			chrom_id=lf[0].split('>')[1]
			chrom_seq="".join(lf[1:])
			chrom_seq=chrom_seq.upper()
	return [chrom_id,chrom_seq]
 
def cgVector(chrom):
	chrom_seq=chrom[1]
	cgV=[m.start() for m in re.finditer('CG',chrom_seq)]
	return cgV
	
def scoreVector1(chrom,cgv,bwFile):
	bw=pyBigWig.open(bwFile)
	chrom_name=chrom[0]
	sv=[]
	for i in cgv:
		si=bw.stats(chrom_name,i,i+1)[0]
		si=0 if si==None else si
		sv.append(si)
	return sv
	
def scoreVector(chrom,cgv,bwFile):
	bw=pyBigWig.open(bwFile)
	chrom_name=chrom[0]
	sc=bw.values(chrom_name,0,len(chrom[1]))
	sv=[0 if math.isnan(sc[item]) else sc[item]  for item in cgv ]
	return sv
	
	
def nearbyCGVector(cgv,nearbycut):
	nearcgs=[]
	for i in range(len(cgv)):
		j=i-1
		leftcgs=[]
		rightcgs=[]
		while (j>0):
			if abs(cgv[j]-cgv[i])>nearbycut:
				break 
			else:
				leftcgs.append(j)
			j=j-1
		
		j=i+1
		while (j<len(cgv)):
			if abs(cgv[j]-cgv[i])>nearbycut:
				break
			else:
				rightcgs.append(j)
			j=j+1
		inearcgs=leftcgs+rightcgs
		nearcgs.append(inearcgs)
	return nearcgs
	
def nearbyCGScoreVector(chrom,bwFile,cgv,nearcgs):
	# the contribution of nearby CGs on current CG
	nearcgsS=[]
	bw=pyBigWig.open(bwFile)
	chrom_name=chrom[0]
	k=5 # distance weight parameter
	for i in range(len(nearcgs)):
		cgi=nearcgs[i]
		si=0
		for j in cgi:
			dij=abs(cgv[j]-cgv[i])
			sj=bw.stats(chrom_name,cgv[j],cgv[j]+1)[0]
			sj=0 if sj==None else sj
			si+=(sj/dij)*k
		nearcgsS.append(si)
	return nearcgsS
			
#----------------------------------------------------------------------

def main():
	if len(sys.argv[1:])!=4:
		print(__doc__)
		sys.exit(0)
		
	# reference genomes
	gref=sys.argv[1]
	# bigwig file-MeDIP-seq
	bwFile=sys.argv[2]
	
	# bigwig file bisulfite
	bwBSFile=sys.argv[3]
	output=sys.argv[4]
	rfregressor=RandomForestRegressor(random_state=0)
	chroms=os.listdir(gref)
	dchrom={}

	nearbycut=90
	rfregressor=RandomForestRegressor(random_state=0)
	#----------------------------------------------------------------------
	F=[]
	T=[]

	print("training...")
	cut=0.5
	for i in chroms:
		if i[0:3]=='chr':
			iid=i.split('.')[0]
			try:
				chromi=fetchGenome(iid,gref)
				cgv=cgVector(chromi)
				sv=scoreVector(chromi,cgv,bwFile)
				nearcgs=nearbyCGVector(cgv,nearbycut)   # number of cgs nearby
				tsv=scoreVector(chromi,cgv,bwBSFile)
				FI=[]
				for j in range(len(cgv)):
					fij=[sv[j],len(nearcgs[j])]
					FI.append(fij)
				FIX=FI[:int(len(FI)*cut)]
				tsvX=tsv[:int(len(tsv)*cut)]
				F+=FIX
				T+=tsvX
				print(iid)
			except:
				pass 
	rfregressor.fit(F,T)		
	with open(output+'.pkl','w') as f:
			pickle.dump(rfregressor,f)
		
		
if __name__=="__main__":
	main()
	
		
		


