import array
import fcntl
import struct
import os

# Yanked from fiemap.h
'''
struct fiemap_extent {
/* WARNING: DO NOT EDIT, AUTO-GENERATED CODE - SEE TOP FOR INSTRUCTIONS */
  __u64 fe_logical;
  __u64 fe_physical;
  __u64 fe_length;
  __u64 fe_reserved64[2];
/* WARNING: DO NOT EDIT, AUTO-GENERATED CODE - SEE TOP FOR INSTRUCTIONS */
  __u32 fe_flags;
  __u32 fe_reserved[3];
};
struct fiemap {
/* WARNING: DO NOT EDIT, AUTO-GENERATED CODE - SEE TOP FOR INSTRUCTIONS */
  __u64 fm_start;
  __u64 fm_length;
  __u32 fm_flags;
  __u32 fm_mapped_extents;
/* WARNING: DO NOT EDIT, AUTO-GENERATED CODE - SEE TOP FOR INSTRUCTIONS */
  __u32 fm_extent_count;
  __u32 fm_reserved;
  struct fiemap_extent fm_extents[0];
};
'''

# Yanked from fiemap.h
FIEMAP_IOCTL = 0xC020660B
FIEMAP_FLAG_SYNC = 0x00000001
FIEMAP_FLAG_XATTR = 0x00000002
FIEMAP_FLAG_CACHE = 0x00000004

FIEMAP_FLAGS_COMPAT = (FIEMAP_FLAG_SYNC | FIEMAP_FLAG_XATTR)
FIEMAP_EXTENT_LAST = 0x00000001
FIEMAP_EXTENT_UNKNOWN = 0x00000002
FIEMAP_EXTENT_DELALLOC = 0x00000004

FIEMAP_EXTENT_ENCODED = 0x00000008
FIEMAP_EXTENT_DATA_ENCRYPTED = 0x00000080
FIEMAP_EXTENT_NOT_ALIGNED = 0x00000100
FIEMAP_EXTENT_DATA_INLINE = 0x00000200

FIEMAP_EXTENT_DATA_TAIL = 0x00000400
FIEMAP_EXTENT_UNWRITTEN = 0x00000800
FIEMAP_EXTENT_MERGED = 0x00001000
FIEMAP_EXTENT_SHARED = 0x00002000

EXT_NUM = 0
EXT_LOGICAL = 1
EXT_PHYSICAL = 2
EXT_LENGTH = 3

#python struct packing definitions
FIEMAP_EXT_FORMAT = "=QQQQQLLLL"
FIEMAP_BASE_FORMAT = "=QQLLLL"


# Credit to https://bj0z.wordpress.com/2011/04/22/fiemap-ioctl-from-python/ for reference examples
def fiemap_ioctl(fd):
    """
    Takes an open file descriptor and returns a list of block extents associated with the file

    :param fd: open file descriptor (note: low level FD, not the usual python file handle)
    :return: python list of block extents
    """

    # Get sizes of the structs to be created
    size_fiemap = struct.calcsize(FIEMAP_BASE_FORMAT)
    size_fmap_ext = struct.calcsize(FIEMAP_EXT_FORMAT)

    #extent offset tracker
    ext_num = 0

    #First IOCTL gets the physical number of extents in the file which we use to create
    #space for the actual array
    buf = struct.pack(FIEMAP_BASE_FORMAT, 0, 0xffffffffffffffff, 0, 0, ext_num, 0)
    space_str = "\0" * ext_num * size_fiemap
    buf += space_str.encode("utf-8")
    buf = array.array('b', buf)
    retval = fcntl.ioctl(fd, FIEMAP_IOCTL, buf)

    if retval != 0:
        print("Warning: Non-zero return for FIEMAP: %d" % retval)

    retbuf = buf.tobytes()
    parsed_fmap = struct.unpack(FIEMAP_BASE_FORMAT, retbuf[:size_fiemap])
    ext_num = parsed_fmap[3]

    #Second IOCTL actually gets the extent map
    buf = struct.pack(FIEMAP_BASE_FORMAT, 0, 0xffffffffffffffff, 0, 0, ext_num, 0)
    space_str = "\0" * ext_num * size_fmap_ext
    buf += space_str.encode("utf-8")
    buf = array.array('b', buf)
    retval = fcntl.ioctl(fd, FIEMAP_IOCTL, buf)

    if retval != 0:
        print("Warning: Non-zero return for FIEMAP Call 2: %d" % retval)

    retbuf = buf.tobytes()
    fmap_list = []
    for ext in range(ext_num):
        #calculate extent offset
        idx = size_fiemap + (ext * size_fmap_ext)
        fmap_ext_raw = struct.unpack(FIEMAP_EXT_FORMAT, retbuf[idx:idx+size_fmap_ext])
        ext_tup = (ext, fmap_ext_raw[0], fmap_ext_raw[1], fmap_ext_raw[2])

        fmap_list.append(ext_tup)

    return fmap_list

def get_ext_list(fpath):
    """
    Get extent list from specified file path
    :param fpath: string, file path
    :return: list of python tuples describing extents
    TODO explain tuple layout
    """

    # open descriptor read only
    fd = os.open(fpath, os.O_RDONLY)
    exts = fiemap_ioctl(fd)
    os.close(fd)

    return exts

