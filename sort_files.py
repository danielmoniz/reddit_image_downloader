import os

def make_dirs(target_dir):
    if not os.path.isdir(target_dir):
        print u"Directory {} does not exist. Creating...".format(target_dir)
        os.makedirs(target_dir)

def make_dir(target_dir):
    if not os.path.isdir(target_dir):
        print u"Directory {} does not exist. Creating...".format(target_dir)
        os.mkdir(target_dir)

def get_extension(url):
    uri = url.split('/')[-1]
    try:
        extension_start = uri.index('.')
    except ValueError:
        return False
    extension = uri[extension_start + 1:]
    # remove extra url arguments
    try:
        extension_end = extension.index('?')
        extension = extension[:extension_end]
    except ValueError:
        pass
    return extension

def sort_gifs(path):
    """
    Sort gifts into a specific folder while *not* maintaining existing 
    file structure patterns.
    """
    target_dir = 'gifs'
    make_dir(target_dir)
    target = os.path.join(path, target_dir)
    for root, dirnames, filenames in os.walk(path):
        print '-'*20
        print root
        for filename in filenames:
            extension = get_extension(filename)
            if extension == 'gif':
                os.rename(os.path.join(root, filename), os.path.join(target, filename))
                print filename


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.realpath(__file__))
    print root_dir
    print os.getcwd()
    root_dir = os.getcwd()
    sort_gifs(root_dir)
