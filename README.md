# PyFSStat
A simple toolchain for capturing and characterizing the state of your linux filesystem. 

Note that we assume a basic familiarity with file system terminology and concepts in 
the use of this utility.

## Usage 

``
python3 fs_stat.py <options>
``

Options:

```

--hsh_cont: optional (default False) run a hash of the file contents. WARNING: This can be computational intensive

--trk_exts: optional (default False) attempt to get a list of filsystem extents for a file

--buf_wrt: optional (default False) buffer (stream) writes to the metadata CSV. Useful for large filesystems 
otherwise the memory footprint may become excessively large while crawling. WiP not functioning yet.

--anon_pth: optional (default False) Uses a sha256 hash to anonymize filepaths and names. 

--outpath: optional (default metsnap+(datetime).csv) filepath to store the csv at.

--pth_root: required  root directory to begin the file system crawl at

```


## Output Details

### CSV Fields
* fpath: full path to the file or directory information
* is_dir: is this a file or directory
* nr_blocks: number of allocated logical blocks
* mtime: file system modification time
* ctime: file system metadata change time
* atime: time of last file access. Note this is often coarse grained to prevent file system churn. 
For example, some file systems have a policy to not update it unless its been more than a day since the
last access, others full disable access time.
* blk_size: size in bytes of the blocks allocated to this file
* nr_hrd_links: number of hard file system links
* sz: reported file system size. Note this may be considerably more than the physical size on disk
if the file system allows for sparse files.
* stat_scs: stat success. Reports if the file or directory successfully reported from stat
* hash: if computed, an md5 hash of the file contents
* extents: a list of file system extents in its own format, more details are provided below

### Extent List Description
The extent list field, is a list of zero or more extens delimited by a `:`
Each extent is a 4-tuple, with the following positions representing the following values
* position 0: extent number
* position 1: logical offset in bytes
* position 2: physically offset in bytes
* position 3: extent length in bytes

Note that these lengths should be a multiple of the file system block size.

## How it works and what it does
PyFS relies on a combination of stock python and linux systems utilities and calls
to crawl a filesystem recursively from a specified root directory and retrieve metadata
and information about the underlying files and/or directories. There are 3 broad pieces of 
information that may be scanned, depending on the specified options.

* File System Metadata: this minimally includes file  modification, change, and access times.
It may include filesystem "birth" or create time but not all OSes and python versions have this
well support. It also includes a given low level block size, the number of blocks, hard links, and
reported file system size.

* File Extents: In practice, files are allocated contiguous groups of low level blocks. 
To report this out, we use a custom port of the low level ioctl FIEMAP to report back extents
and offsets to a lower level block device partition.

* Content Hashing: will use MD5 to produce a hash of the file contents. While this is not
a secure hash, it is sufficient for identifying file content duplicates.

## Caveats and what not

This is currently for Linux only!

The crawler may have unpredictable behavior when running into files with unusual characters (unicode, commas, etc)
as well as if you decide to start at the root directory as it will end up crawling process files, etc.

This is still a WiP and ultimately experimental software intended for hobbyists and
researchers, so let the buyer beware here. Its designed primarily for functionality, simplicity,
and portability. This means for the basic crawler and metadata extraction we're unlikely
to add in anything that requires 3rd part libraries. We will eventually include ipython
examples and some utilities that rely on numpy for analysis examples and tools, but the 
core crawler should never rely on anything but stock python and what we provide.

A question that's often come up in this sort of work is the choice of CSV for data format.
This is a long discussion, but the short answer is: it is portable, human readable, and compresses
very well.




