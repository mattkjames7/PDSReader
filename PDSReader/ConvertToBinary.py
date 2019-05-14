import numpy as np
from .FindPDSFiles import FindPDSFiles
from .ReadPDSFile import ReadPDSFile
import RecarrayTools as RT
from .PDSFMTtodtype import PDSFMTtodtype
import DateTimeTools as TT
import os
import re
	
def ConvertToBinary(InPath,OutPath,FilePattern,FMTname,OutDict=None,DateRegex=None):
	'''
	This will convert the data files within a directory to a simple 
	binary format which can be ready quickly using the RecarrayTools
	package.
	
	Inputs:
		InPath: The path to the folder which contains the data files and
			the .fmt file.
		OutPath: The full path where the converted files will be saved.
			The files in this path will be saved with names in the format
			yyyymmdd.bin, where yyyy, mm and dd are the year, month and
			day, respectively.
		FilePattern: This is the pattern which will be used to search 
			for the data files, this requires the use of wildcards
			(*) e.g. FilePattern = 'FIPS_R*EDR*.DAT'. It's best to
			be as specific as possible, in case there are multiple 
			different data types with very similar names within the 
			same folder.
		FMTname: Either provide the name of the file as a string, or the
			name and absolute path of the .fmt file.
		OutDict: This is a dict object which would map the names of the 
			fields defined in the .fmt file to whatever you want to name 
			them e.g.:
			OutDict = {	'MET':				'MET',
						'FIPS_SCANTYPE':	'ScanType',
						'PROTON_RATE':		'ProtonRate',}		
			which maps the original name on the left, to the new name on 
			the right (i.e. PROTON_RATE becomes ProtonRate). This is 
			mostly cosmetic, but can be useful in converting dates too e.g.
			
					{	'UTC_TIME':		('Date','ut'),
						'CMD_UTC_DATE':	('Date',),
						'CMD_UTC_TIME':	('ut',)}
			where ('Date','ut') tells the function to expect dates and 
			times with the format YYYY-MM-DDThh:mm:ss.sss(s...), or 
			('Date',) mean the function will expect and ascii date in 
			the format YYYY-MM-DD, or ('ut',) tells the function to 
			convert times from the format hh:mm:ss.sss...
		DateRegex: Use this to define the regex pattern for the date as
			is appears on the file name (if possible). If left equal to
			None, then by default it should try to locate the date in
			either the yyyymmdd or yyyyddd format.
		
	'''
	#search for the PDS files
	fmt,files = FindPDSFiles(InPath,FMTname,FilePattern)
	
	#check that the output directory exists, mkdir if not
	if not os.path.isdir(OutPath):
		os.system('mkdir -pv '+OutPath)
		
	#now convert them
	_ConvBinary(fmt,files,OutPath,FilePattern,OutDict,DateRegex)
	


		
def _NewDtype(pdsdata,fields):
	
	oldfields = list(fields.keys())
	
	newdtype = []
	for f in oldfields:
		sh = pdsdata[f].shape
		if isinstance(fields[f],tuple):
			#this is some date and or time
			if len(fields[f]) == 2:
				newdtype.append(('Date','>i4'))
				newdtype.append(('ut','>f4'))
			elif fields[f][0] == 'Date':	
				newdtype.append(('Date','>i4'))
			else:
				newdtype.append(('ut','>f4'))
		else:
			if len(sh) == 1:
				tmp = (fields[f],pdsdata[f].dtype.str)
			else:
				tmp = (fields[f],pdsdata[f].dtype.str,pdsdata[f].shape[1:])
			newdtype.append(tmp)
	return newdtype
		
		

def _ConvBinary(fmt,files,outpath,fpatt,fields,DateRegex):

	#check the outpath has '/' at the end
	if outpath[-1] != '/':
		outpath = outpath + '/'

	#get fmt data
	fmtdata = PDSFMTtodtype(fmt)
	
	#if fields is None the we need to copy the original ones
	if fields is None:
		fields = {}
		ff = fmtdata[0]
		for i in range(0,len(ff)):
			fld = ff[i][0]
			fields[fld] = fld
			
	
	oldfields = list(fields.keys())
	newfields = [fields[f] for f in oldfields]

	#create regex patterns
	dp7 = re.compile('\d\d\d\d\d\d\d')
	dp8 = re.compile('\d\d\d\d\d\d\d\d')
	if not DateRegex is None:
		dre = re.compile(DateRegex)
	else:
		dre = None

	
	
	#loop through files
	nf = np.size(files)
	for i in range(0,nf):
		#get the date from the file name
		fsplit = files[i].split('/')
		flast = fsplit[-1]
		#see if either regex patterns match
		match7 = dp7.search(flast)
		match8 = dp8.search(flast)
		if not dre is None:
			matchc = dre.search(flast)
		else:
			matchc = None
		
		if not matchc is None:
			#this will take a custom Regex match, strip non-numeric 
			#characters and try to assume a date format
			datestr = matchc.group()
			datestr = re.sub("[^0-9]","",datestr)
			if len(datestr) == 7:
				#assume yyyyddd
				year = np.int32(datestr[:4])
				doy = np.int32(datestr[4:7])
				Date = TT.DayNotoDate(year,doy)
				fname = outpath + '{:08d}.bin'.format(Date)				
			elif len(datestr) >= 8:
				#assume yyyymmdd
				Date = np.int32(datestr) 
				fname = outpath + '{:08d}.bin'.format(Date)				
			else:
				#fuck it, use the original name
				fname = outpath + flast
		
		elif not match8 is None:
			#in this case the date might be in the format yyyymmdd
			Date = np.int32(match8.group()) 
			fname = outpath + '{:08d}.bin'.format(Date)
		elif not match7 is None:
			#in this case we assume a format of yyyyddd
			datestr = match7.group()
			year = np.int32(datestr[:4])
			doy = np.int32(datestr[4:7])
			Date = TT.DayNotoDate(year,doy)
			fname = outpath + '{:08d}.bin'.format(Date)
		else:
			#use original name
			fname = outpath + flast
		

		
		#read the file first
		data,_ = ReadPDSFile(files[i],fmtdata)
		
		
		
		#get the new dtype if needed
		if i == 0:
			dtype = _NewDtype(data,fields)
			print('dtype: ',dtype)
			print(data.dtype)
			#save the dtype to a file 
			f = open(outpath+'dtype','w')
			f.write('dtype = '+str(dtype))
			f.close()
			print('dtype saved to '+outpath+'dtype')
			
		print('\rConverting file {:d} of {:d}'.format(i+1,nf),end='')
		#get the output recarray
		out = np.recarray(data.size,dtype=dtype)
		
		#move data to new recarray
		for f in oldfields:
			
			
			if isinstance(fields[f],tuple):
				#probably a date, time or date and time combination
				if len(fields[f]) == 2:
					x = data[f][0]
					out.Date = [TT.DayNotoDate(np.int32(x[0:4]),np.int32(x[5:8])) for x in data[f]]
					out.ut = [np.float32(x[9:11])+np.float32(x[12:14])/60.0+np.float32(x[15:])/3600.0 for x in data[f]]
				elif len(fields[f]) == 1 and fields[f] == 'Date':
					out.Date = [np.int32(x[0:4]+x[5:7]+x[8:10]) for x in data[f]]
				elif len(fields[f]) == 1 and fields[f] == 'ut':
					out.ut = [np.float32(x[0:2]) + np.float32(x[3:5])/60.0 + np.float32(x[6:])/3600.0 for x in data[f]]

			else:
				out[fields[f]] = data[f]

		#save the file
		RT.SaveRecarray(out,fname)
		
	print()
	

