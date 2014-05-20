import os

def get_extension(url, with_dot=False):
    uri = url.split('/')[-1]
    try:
        extension_start = uri.index('.')
    except ValueError:
        return False
    add = 1
    if with_dot:
        add = 0
    extension = uri[extension_start + add:]
    # remove extra url arguments
    try:
        extension_end = extension.index('?')
        extension = extension[:extension_end]
    except ValueError:
        pass
    return extension

def find_untaken_name(filename, path, num=None):
    if num == None:
        num = 1
    filenames = os.listdir(path)
    temp_filename = filename
    if num and num > 1:
        extension = get_extension(filename, with_dot=True)
        extension_position = filename.index(extension)
        print extension
        temp_filename = filename[:extension_position] + " ({})".format(num) + filename[extension_position:]
    if temp_filename not in filenames:
        return temp_filename
    return find_untaken_name(filename, path, num + 1)

def has_extension(url):
    if url[-4] == '.' or url[-5] == '.':
        return True
    return False

def has_acceptable_extension(url):
    """Assumes url has an extension."""
    extension = utils.get_extension(url)
    if extension in ["jpg", "jpeg", "gif", "png"]:
        return True
    return False

def make_dirs(target_dir):
    if not os.path.isdir(target_dir):
        print u"Directory {} does not exist. Creating...".format(target_dir)
        os.makedirs(target_dir)

def make_dir(target_dir):
    if not os.path.isdir(target_dir):
        print u"Directory {} does not exist. Creating...".format(target_dir)
        os.mkdir(target_dir)
