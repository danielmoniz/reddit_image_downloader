import os
import shutil

import utils

def sort_files(path, filetype='gif'):
    """
    Sort files into a specific folder while *not* maintaining existing 
    file structure patterns.
    """
    target_dir = filetype.lower() + 's'
    target = os.path.join(path, target_dir)
    utils.make_dir(target)
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            extension = utils.get_extension(filename)
            if extension == filetype.lower():
                os.rename(os.path.join(root, filename), os.path.join(target, filename))

def move_out_of_folders(path):
    """
    Move every file out of its folder and into the top level directory.
    """
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            target = os.path.join(path, filename)
            os.rename(os.path.join(root, filename), target)

def remove_folders(path):
    """Remove every directory on the path.
    """
    for root, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            target = os.path.join(root, dirname)
            """
            if not os.listdir(target):
                print "dir {} is empty".format(target)
            """
            contained_files = os.walk(target, topdown=False)
            next_item = next(contained_files, (None, None, None))[2]
            if not next_item:
                shutil.rmtree(target)


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.realpath(__file__))
    print root_dir
    print os.getcwd()
    root_dir = os.getcwd()
    move_out_of_folders(root_dir)
    remove_folders(root_dir)
    sort_files(root_dir, 'gif')
    sort_files(root_dir, 'mp4')
