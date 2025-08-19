import os
from collections import deque
import hashlib
from logging import exception

MiB_8 = 8*1048576

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
    except FileNotFoundError:
        stat_dict["nr_blocks"] = None
        stat_dict["mtime"] = None
        stat_dict["ctime"] = None
        stat_dict["atime"] = None
        stat_dict["blk_size"] = None
        stat_dict["nr_hrd_links"] = None
        stat_dict["sz"] = None
        stat_dict["stat_scs"] = False


    return stat_dict

def get_extents(fpath):
    pass

def anonymize_path(hasher):
    pass

def new_fs_crawler_gen(path_root):

    for root, dirs, files in os.walk(path_root):
        for name in files:
            yield os.path.join(root, name), True
        for name in dirs:
            yield os.path.join(root, name), False

if __name__ == "__main__":

    crawler_gen = new_fs_crawler_gen("/home/")
    hash_content = True
    stat_dict = None
    ext_dict = None
    flist = deque()
    anon_path = False

    for item, is_file in crawler_gen:

        hex_dig=None

        # grab relevant file stats
        stat_dict = fs_stat(item)

        if is_file is True:
            if hash_content is True and stat_dict["stat_scs"] is True:
                hex_dig = md5_hash_content(item)
            stat_dict["is_dir"] = False
        else:
            stat_dict = fs_stat(item)
            stat_dict["is_dir"] = True

        stat_dict["content_hash"] = hex_dig

        if anon_path is True:
            pass
            #later integrate path anonymization

        stat_dict["fpath"] = item
        print(stat_dict)
