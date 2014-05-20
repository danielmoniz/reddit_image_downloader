import os

import utils

def sort_gifs(path):
    """
    Sort gifts into a specific folder while *not* maintaining existing 
    file structure patterns.
    """
    target_dir = 'gifs'
    utils.make_dir(target_dir)
    target = os.path.join(path, target_dir)
    for root, dirnames, filenames in os.walk(path):
        print '-'*20
        print root
        for filename in filenames:
            extension = utils.get_extension(filename)
            if extension == 'gif':
                os.rename(os.path.join(root, filename), os.path.join(target, filename))
                print filename


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.realpath(__file__))
    print root_dir
    print os.getcwd()
    root_dir = os.getcwd()
    sort_gifs(root_dir)
