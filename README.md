# PDSReader
A simple module for reading NASA PDS repositories.

## Installation

Use `pip3` e.g.

`pip3 install packagename.whl --user` for installing a compiled wheel 

 or 

`pip3 install PDSReader --user` when I get around to uploading to PyPI.

## Basic usage

This package assumes that you have downloaded the PDS data to some folder
on your computer and will scan it for the relevant files. If you keep
the original directory structure it should work fine.

### Locating PDS files

Firstly you need to find out the name of the `.fmt` file which defines 
how the data are stored within the PDS repository, either provide an
absolute path e.g. `FMTname = '/path/to/BLAH_BLAH.FMT'` or just the
file name itself e.g. `FMTname = 'BLAH_BLAH.FMT'`. In the latter case, 
the code will assume that the `.fmt` file is within the directory where 
all of your data are stored, somewhere (not necessarily the same 
sub-directory) and it will scan for it recursively.

Secondly, set the `InPath` to point to a directory which contains the 
data (NOTE: the data files only have to be *somewhere* within this 
directory, this does not have to point absolutely to the data folder),
e.g. `InPath = '/path/to/data/'`.

Also, we need to define a pattern for the data file names, e.g. 
`FilePattern = 'FIPS_*_V*.DAT'`.

Now we can do something like the following:

```python
import PDSReader as pds
InPath = '/path/to/data/'
FMTname = 'BLAH_BLAH.FMT'
FilePattern = 'FIPS_*_V*.DAT'
fmt,files = pds.FindPDSFiles(InPath,FMTname,FilePattern)
```

In `fmt` should be the absolute path and file name of the relevant fmt file.
In `files` should be an array of all of the data file names.

### Reading a PDS file

You could use the `fmt` and `files` obtained above for this e.g.:

```data = pds.ReadPDSFile(files[i],fmt)```

or using your own defined paths tot he file to open and the path to
the format file e.g.

```data = pds.ReadPDSFile('/path/to/data/file.tab','/path/to/fmtfile.fmt')```

which should output a numpy.recarray object with all of the original
field names, which can be listed using ```print(data.dtype.names)```.

### Converting data

You could convert data to an easier format to read using 
`PDSReader.ConvertToBinary` e.g.:

```python
pds.ConvertToBinary(InPath,OutPath,FilePattern,FMTname,OutDict,DateRegex)
```

where `InPath` is the data path, as before; `OutPath` is the location 
where the newly converted files will be saved (it will be created
automatically if it doesn't exist); `FilePattern` is the pattern of the
input files as before; `FMTname` is the name of the `.fmt` file as before;
`OutDict` is an optional dictionary which instructs the function to only
save certain fields, and to rename them as you please (see docstring for
more info); and DateRegex is also optional - it is a regex expression 
which tells the routine how to decipher the date of a data file from its
file name, if the dates are of the format yyyyddd or yyyymmdd in the
file names already, then you shouldn't need to worry about this.

The resultant files are readable using RecarrayTools.ReadRecarray 
(see https://github.com/mattkjames7/RecarrayTools/) where the code which
defines the numpy.recarray dtype is saved in a file called "dtype" within
`OutPath`. 



