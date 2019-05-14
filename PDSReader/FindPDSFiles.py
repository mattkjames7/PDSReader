import numpy as np
import os
from .SearchForFile import SearchForFile
from .SearchForFilePattern import SearchForFilePattern

def FindPDSFiles(InPath,FMTname,FilePattern):
	'''
	Searches a directory (InPath) for a .fmt file and for all of the 
	data files.
	
	Inputs:
		InPath: An absolute path to the folder which contains both the
				.fmt file and all of the data. If you have downloaded an
				entire PDS repository, then use the root of that folder.
		FMTname: Either provide the name of the file as a string, or the
				name and absolute path of the .fmt file.
		FilePattern: This is the pattern which will be used to search 
				for the data files, this requires the use of wildcards
				(*) e.g. FilePattern = 'FIPS_R*EDR*.DAT'. It's best to
				be as specific as possible, in case there are multiple 
				different data types with very similar names within the 
				same folder.
				
	Returns:
		(fmtfile,datafiles)
		fmtfile = path and file name of .fmt file to read
		datafiles = array containing all the names of the data files
			which were found.
	
	'''
	#find the fmt file first
	if os.path.isfile(FMTname):
		fmtfile = FMTname
	else:
		fmtfile = SearchForFile(InPath,FMTname)[0]
		
	#find the list of data files
	datafiles = SearchForFilePattern(InPath,FilePattern)
		

	return fmtfile,datafiles
