"""
methrafo.download  <genome_index><output_directory>
e.g. 
methrafo.download hg19 hg19
"""
import pdb,sys,os
import gzip
import ftplib
from ftplib import FTP

def main():
	if len(sys.argv[1:])!=2:
		print(__doc__)
		sys.exit(0)
		
	gref=sys.argv[1]
	outputdir=sys.argv[2]
	if os.path.exists(outputdir)==False:
		os.mkdir(outputdir)
	ucscftp="hgdownload.cse.ucsc.edu"
	ftp=FTP(ucscftp)
	
	#download chrome sizes
	
	ftp.login()
	
	ftp.cwd("/goldenPath/%s/bigZips/"%(gref))
	ftp.retrbinary("RETR "+"%s.chrom.sizes"%(gref),open(outputdir+'/'+"%s.chrom.sizes"%(gref),"wb").write)
	print("%s.chrom.sizes downloaded"%(gref))
	
	#download chromes
	ftp.cwd("/goldenPath/%s/chromosomes/"%(gref))
	filenames=ftp.nlst()
	for f in filenames:
		if f!="." and f!="..":
			ftp.retrbinary("RETR "+f, open(outputdir+'/'+f,"wb").write)
			print(f+" downloaded")
	
	ftp.close()
	
if __name__=='__main__':
	main()
	
	


