import os
import argparse

from PIL import Image

prefixes = (
    'mh_',
    'mv_',
    'sq_',
)
prefix_length = 3
for prefix in prefixes:
    assert len(prefix) == prefix_length

def has_prefix(filename):
    prefix = filename[0:prefix_length]
    if prefix in prefixes:
        return True
    return False

def get_width_and_height(path):
    try:
        image = Image.open(path)
        return image.size
        print image.size
    except IOError:
        pass
    return False

def prepare(path):
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if has_prefix(filename):
                continue
            size = get_width_and_height(os.path.join(root, filename))
            if not size:
                print "Not an image: {}".format(filename)
                continue
            width, height = size
            new_filename = filename
            if height > width:
                new_filename = "mv_{}".format(filename)
            elif width > height:
                new_filename = "mh_{}".format(filename)
            else: # image is square
                new_filename = "sq_{}".format(filename)
            os.rename(os.path.join(root, filename), os.path.join(root, new_filename))
            #print "{}  ->  {}".format(filename, new_filename)
    print 'Finished preparing for mobile viewing.'

def unprepare(path):
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.startswith('mv_') or filename.startswith('mh_'):
                new_filename = filename[prefix_length:]
                os.rename(os.path.join(root, filename), os.path.join(root, new_filename))
                #print new_filename
    print 'Finished preparing for regular viewing.'

if __name__ == "__main__":
    root_dir = os.getcwd()
    parser = argparse.ArgumentParser(description="Pull image files from reddit.")
    parser.add_argument("--prepare", action="store_true", help="Prepare the current directory for mobile viewing.")
    parser.add_argument("--unprepare", action="store_true", help="Prepare the current directory for non-mobile viewing, ie. undo mobile readiness.")
    args = parser.parse_args()
    if args.prepare:
        prepare(root_dir)
    elif args.unprepare:
        unprepare(root_dir)
    else:
        print "Must specify either --prepare or --unprepare"
        exit()
