#!/usr/bin/env python
"""
methrafo.predict <genome_index><RPKM bigwig><model><output_prefix>
eg.
methrafo.precit hg19 example.bw trained_model.pkl example_out
"""

import pdb,sys,os
import gzip
from File import *
import re
import pyBigWig
from scipy.stats import pearsonr
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
import math
import cPickle as pickle
import gc
import numpy as np

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
	
""""
def scoreVector1(chrom,cgv,bwFile):
	bw=pyBigWig.open(bwFile)
	chrom_name=chrom[0]
	sc=bw.values(chrom_name,0,len(chrom[1]))
	sv=[0 if math.isnan(sc[item]) else sc[item]  for item in cgv ]
	return sv
"""	

def scoreVector(chrom,cgv,bwFile):
	bw=pyBigWig.open(bwFile)
	chrom_name=chrom[0]
	N=10 # split large list to reduce RAM usage
	cgvL=np.array_split(cgv,N)
	sv=[]
	for l in cgvL:
		sc=bw.values(chrom_name,l[0],l[-1]+1)
		sv+=[0 if math.isnan(sc[item-l[0]]) else sc[item-l[0]]  for item in l]
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
		nearcgs.append(len(inearcgs))
	return nearcgs
			
def Vector2Wig(chri,cgv,rv,f):
	wigString="variableStep chrom="+chri+" span=2"
	f.write(wigString+'\n')
	for i in range(len(cgv)):
		f.write(str(cgv[i])+' '+str(rv[i])+'\n')
	
	
	
def getFeature(iid,gref,nearbycut,bwFile):
	chromi=fetchGenome(iid,gref)
	cgv=cgVector(chromi)
	sv=scoreVector(chromi,cgv,bwFile)
	
	if (sum(sv)==0):
		return None
	nearcgs=nearbyCGVector(cgv,nearbycut)
	FI=[]
	for j in range(len(cgv)):
		fij=[sv[j],nearcgs[j]]
		FI.append(fij)
	return [cgv,FI]
		
#----------------------------------------------------------------------


def main():
	# reference genomes
	
	if len(sys.argv[1:])!=4:
		print(__doc__)
		sys.exit(0)
		
	gref=sys.argv[1]
	chroms=os.listdir(gref)

	# bigwig file-MeDIP-seq
	bwFile=sys.argv[2]
	
	f=open(sys.argv[3],'rb')
	rfregressor=pickle.load(f)
	f.close()
	
	nearbycut=90
	output=sys.argv[4]
	
	#----------------------------------------------------------------------
	print("predicting...")
	wig_track="track type=wiggle_0  visibility=full"
	f=open(output+'.wig','a')
	f.write(wig_track+'\n')
	for i in chroms:
		if i[0:3]=='chr':
			iid=i.split('.')[0]
			print(iid)
			try:
				[cgv,FI]=getFeature(iid,gref,nearbycut,bwFile)
				rv=list(rfregressor.predict(FI))
				#rv=[rv[k] if sv[k]>0 else 0 for k in range(len(rv))]
				Vector2Wig(iid,cgv,rv,f)	
			except:
				pass 
	f.close()


if __name__=="__main__":
	main()
	
	
		
		


