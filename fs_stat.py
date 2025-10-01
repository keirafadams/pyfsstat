import argparse
from datetime import datetime
from fs_crawler import crawler_root

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog='PyFSStat',
        description='File System Metadata Crawler',
        epilog='Created by Keira Adams, 2025')

    parser.add_argument("--hsh_cont", default=False, action="store_true", help="Store an MD5 hash of file contents. WARNING: Can be very slow on large files")
    parser.add_argument("--trk_exts", default=False, action="store_true", help="Create file block extent lists.")
    parser.add_argument("--buf_wrt", default=False, action="store_true", help="Periodically flushes the stats list, reducing memory overhead. Useful for large file systems.")
    parser.add_argument("--anon_pth", default=False, action="store_true", help="Anonymizes file paths using SHA256, but will preserve correlation. e.g. same directory will be hashed to same value.")
    parser.add_argument("--outpath", default="metsnap" + str(datetime.now())+".csv", help="Filename to store results. If non specified will be named metsnap<curtime>.csv")
    parser.add_argument("--pth_root", required=True, type=str, help="Root directory to start the crawl at")

    args = parser.parse_args()

    anon_path = args.anon_pth
    trk_exts = args.trk_exts
    buf_write = args.buf_wrt
    hsh_cont = args.hsh_cont
    outpath = args.outpath.strip("'")
    path_root = args.pth_root

    flist = crawler_root(path_root, anon_path,hsh_cont, trk_exts, outpath, buf_write)
