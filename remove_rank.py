import os
import re

import utils

def remove_rank(path, recursive=False):
    files_and_dirs = os.listdir(path)
    for obj_name in files_and_dirs:
        name = obj_name.strip()
        match = re.search(r"^(\d+\. )", name)
        if match:
            start = match.groups()[0]
            new_name = name.replace(start, '')
            new_name = utils.find_untaken_name(new_name, path)
            os.rename(obj_name, new_name)
            print "{} -> {}".format(obj_name, new_name)

if __name__ == "__main__":
    root_dir = os.getcwd()
    remove_rank(root_dir)
