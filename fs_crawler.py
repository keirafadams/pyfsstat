import os
from collections import deque
import hashlib
from pyfiemap import get_ext_list

# Eventually this should move to a module + _init file
MiB_8 = 8*1048576
fieldnames_sans_exts = ["fpath", "is_dir", "nr_blocks", "mtime", "ctime", "atime", "blk_size", "nr_hrd_links", "sz", "stat_scs"]

hdr_string = ""

first_field = True
for field in fieldnames_sans_exts:
    if first_field is True:
        hdr_string += field
        first_field = False
    else:
        hdr_string += ",%s" % field

def md5_hash_content(fpath):
    """
    Produces an MD5 Hash of the file contents, while not secure is useful for identifying duplicate data

    :param fpath: string, full path to file

    :return: hexadecimal digest of the data
    """

    hash_func = hashlib.new("md5")

    try:
        with open(fpath, 'rb') as file:
            while chunk := file.read(MiB_8):
                hash_func.update(chunk)
    except:
        print("CKSum failed for %s" % fpath)
        return None
    return hash_func.hexdigest()

def fs_stat(fpath):
    """
    Returns a python dictionary of basic information from unix stat

    WARNING: DOES NOT FOLLOW SYMLINKS, often this results in a failed file open
    due to quirks of how python3 works on linux. If this occurs, the stat info will be
    null/none

    :param fpath: string, path to file
    :return:
    """

    stat_dict = {}
    try:
        stat_info = os.stat(fpath)
        stat_dict["nr_blocks"] = stat_info.st_blocks
        stat_dict["mtime"] = stat_info.st_mtime
        stat_dict["ctime"] = stat_info.st_ctime
        stat_dict["atime"] = stat_info.st_atime
        stat_dict["blk_size"] = stat_info.st_blksize
        stat_dict["nr_hrd_links"] = stat_info.st_nlink
        stat_dict["sz"] = stat_info.st_size
        stat_dict["stat_scs"] = True
    except (FileNotFoundError, OSError):
        stat_dict["nr_blocks"] = None
        stat_dict["mtime"] = None
        stat_dict["ctime"] = None
        stat_dict["atime"] = None
        stat_dict["blk_size"] = None
        stat_dict["nr_hrd_links"] = None
        stat_dict["sz"] = None
        stat_dict["stat_scs"] = False

    return stat_dict

def anonymize_path(fpath, truncate_to=16):
    """
    Does consistent, component by component, anonymization of a file path
    using sha 256

    :param hasher: hashlib like object
    :truncate_to: optional int, how many characters to truncate the anonymized path to
    ie only use the leading N characters. Defaults to 16 if not set
    :return: anonymized path
    """
    path_split = fpath.split("/")
    anon_path = []
    for idx in range(1, len(path_split)):
        path_comp = str(hashlib.sha3_256(path_split[idx].encode("utf-8")).hexdigest())
        anon_path.append(path_comp[0:truncate_to])

    anon_string = "/"+"/".join(anon_path)

    return anon_string

def new_fs_crawler_gen(path_root):
    """
    Crawls file system recursively from the specied root directory
    :param path_root: full path to a root directory
    :return: generator object for yielding a directory or file paths.
    Note yields tuple, first being the path, second being a boolean identifying if its
    a directory or file
    """

    for root, dirs, files in os.walk(path_root):
        for name in files:
            yield os.path.join(root, name), True
        for name in dirs:
            yield os.path.join(root, name), False

def writer(fhdl, write_list, write_header=False):
    """
    Output Writer TBD
    :param fhdl: open python file handle
    :param write_list: list of file stat dicts to write
    :return: None
    """
    # Eventually port this to properly use the CSV module
    # write the header (fieldnames) out. Right now avoiding cause we have some games
    # we need to play for embedding the extent lists
    if write_header is True:
        fhdl.write(hdr_string + ",extents\n" )

    for line_dict in write_list:
        out_str = ""
        for field in fieldnames_sans_exts:
            out_str += str(line_dict[field]) + ","

        #gymnastics for line extents
        if "extents" in line_dict and line_dict["extents"] is not None:
            ext_str = ""
            for ext in line_dict["extents"]:
                if len(line_dict["extents"]) > 1:
                    print(line_dict)
                    exit(1)
                ext_str = str(ext[0]) + "|" + str(ext[1]) + "|" + str(ext[2]) + "|" + str(ext[3]) + ":"
            out_str += ext_str

        fhdl.write(out_str+"\n")

def crawler_root(root_path, anon_path=False, hash_content=False, ext_track=False, outpath="fsnap", buffered_out=False):
    """
    Root crawler function

    :param root_path: directory root to start crawl at
    :param anon_path: boolean, should path be anonymized
    :param hash_content: boolean, whether or not to hash file contents for tracking
    :param ext_track: boolean, whether or not to track block file extents
    :param outpath: file to store results it
    :param buffered_out: whether or not to buffer and periodically flush stats, useful for large crawls to
    reduce memory footprint
    :return: None
    """
    flist = deque()
    crawler_gen = new_fs_crawler_gen(root_path)
    stat_dict=None

    for item, is_file in crawler_gen:

        hex_dig=None
        # grab relevant file stats
        print(item)
        stat_dict = fs_stat(item)

        if is_file is True:

            if hash_content is True and stat_dict["stat_scs"] is True:
                hex_dig = md5_hash_content(item)
            stat_dict["is_dir"] = False

            if ext_track is True and stat_dict["stat_scs"] is True:
                ext_list = get_ext_list(item)
                stat_dict["extents"] = ext_list

        else:
            stat_dict = fs_stat(item)
            stat_dict["is_dir"] = True

        stat_dict["content_hash"] = hex_dig

        if anon_path is True:
            anon_path_str = anonymize_path(item, 8)
            stat_dict["fpath"] = anon_path_str
            #later integrate path anonymization
        else:
            stat_dict["fpath"] = item

        flist.append(stat_dict)

    fhdl = open(outpath,'w')
    writer(fhdl,flist,True)
    fhdl.close()

    return flist

if __name__ == "__main__":

    hash_content = True
    track_extents = True
    anon_path = False

    flist = crawler_root("/home/",anon_path,hash_content, track_extents)

    for stat_dict in flist:
        print(stat_dict)
