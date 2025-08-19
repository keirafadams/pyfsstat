import os

def hash_content(fpath, hasher):
    pass

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
    for item, is_file in crawler_gen:

        if is_file is True:
            print("Fpath: %s" % item)
        else:
            print("Dirpath: %s" % item)

