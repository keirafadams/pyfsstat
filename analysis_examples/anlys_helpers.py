import numpy as np
import pandas as pd
import csv

#extent tuple indices
EXT_NUM = 0
LOG_OFFSET = 1
PHYS_OFFSET = 2
EXT_LEN = 3

def text_to_bool(val):
    """
    Return whether a text string maps to true or false
    :param val: text string (True or False)
    :return: boolean true or false
    """

    if val == "True" or val == "true":
        return True

    if val == "False" or val == "false":
        return False
def snap_loader_to_dict(fpath):
    """
    Converts the CSV i
    :param fpath: python string, full path to csv file
    :return: list of dictionaries.
    """
    data_list = []
    with open(fpath) as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:

            # deal with extents
            ext_str = row["extents"]

            if ext_str != '':
                ext_tup_split = ext_str.split(":")
                ext_tup_list = []
                for ext_tup_str in ext_tup_split:
                    if ext_tup_str != "":
                        ext_info = ext_tup_str.split("|")
                        ext_tup = (int(ext_info[0]), int(ext_info[1]), int(ext_info[2]), int(ext_info[3]))
                        ext_tup_list.append(ext_tup)
                row["extents"] = ext_tup_list
            else:
                row["extents"] = None

            #cast everything to correct type, everything comes out of the reader as strings
            # but the only field thats natively a string is the file path and for the moment the content digest

            if row["stat_scs"] == "True":
                row["is_dir"] = text_to_bool(row["is_dir"])
                row["nr_blocks"] = int(row["nr_blocks"])
                row["mtime"] = float(row["mtime"])
                row["ctime"] = float(row["ctime"])
                row["atime"] = float(row["atime"])
                row["blk_size"] = int(row["blk_size"])
                row["nr_hrd_links"] = int(row["nr_hrd_links"])
                row["sz"] = int(row["sz"])
                row["stat_scs"] = text_to_bool(row["stat_scs"])
                if row["hash"] == "None":
                    row["hash"] = None
            else:
                row["is_dir"] = text_to_bool(row["is_dir"])
                row["nr_blocks"] = None
                row["mtime"] = None
                row["ctime"] = None
                row["atime"] = None
                row["blk_size"] = None
                row["nr_hrd_links"] = None
                row["sz"] = None
                row["stat_scs"] = text_to_bool(row["stat_scs"])

                if row["hash"] == "None":
                    row["hash"] = None

            data_list.append(row)

    return data_list

def snap_loader_to_dataframe(fpath):
    pass

if __name__ == "__main__":
    fpath = "../test_snap.csv"
    data = snap_loader_to_dict(fpath)

    for row in data:
        print(row)