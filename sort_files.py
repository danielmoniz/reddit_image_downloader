import os
import shutil

import utils

def sort_files(path, filetype='gif'):
    """
    Sort files into a specific folder while *not* maintaining existing 
    file structure patterns.
    """
    target_dir = "_{}s".format(filetype.lower())
    target = os.path.join(path, target_dir)
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if ".ds_store" in filename.lower():
                continue
            extension = utils.get_extension(filename).strip('.')
            if extension == filetype.lower():
                utils.make_dir(target)
                new_name = utils.find_untaken_name(filename, target)
                os.rename(os.path.join(root, filename), os.path.join(target, new_name))

def move_out_of_folders(path):
    """
    Move every file out of its folder and into the top level directory.
    """
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if root == path:
                continue
            if ".ds_store" in filename.lower():
                print os.path.join(path, filename)
                try:
                    os.remove(os.path.join(path, filename))
                except OSError:
                    pass
                continue
            new_name = utils.find_untaken_name(filename, path)
            target = os.path.join(path, new_name)
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
            print dirname
            print next_item
            if not next_item or '.DS_Store' in next_item:
                shutil.rmtree(target)

def remove_unique_indicators(path):
    print path
    for filename in os.listdir(path):
        if ' (2)' in filename:
            index = filename.index(' (2)')
            extension = utils.get_extension(filename, with_dot=True)
            shorter_filename = filename[:index] + extension
            print filename
            os.rename(os.path.join(path, filename), os.path.join(path, shorter_filename))


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.realpath(__file__))
    print root_dir
    print os.getcwd()
    root_dir = os.getcwd()
    move_out_of_folders(root_dir)
    remove_folders(root_dir)
    sort_files(root_dir, 'gif')
    sort_files(root_dir, 'mp4')
    sort_files(root_dir, 'html')
    sort_files(root_dir, 'gifv')
    # TEST ONLY
    #remove_unique_indicators(os.path.join(root_dir, '_gifs'))
