import json
import os
import argparse
import socket

import requests
import imghdr
import bs4

import config

subreddits = config.subreddits

parser = argparse.ArgumentParser(description="Pull image files from reddit.")
parser.add_argument("--alltime", action="store_true", help="Pull all images from the top, all-time posts.")

parser.add_argument('--limit', default=25, type=int, help="The number of posts to be pulled.")
parser.add_argument('--sort', default="", help="Sort by top posts, controversial, etc: top, hot, new, controversial, gilded")
parser.add_argument('--time', default="day", help="The time from which to find posts: all, hour, day, month, year")
parser.add_argument('--show', default="all", help="Which posts to show.")
parser.add_argument('--count', default=0, type=int, help="The post to start at (paginate).")

parser.add_argument('--target-dir', help="The directory in which to save the images.")
parser.add_argument("--make-sub-dirs", action="store_true", help="Create a subdirectory for each subreddit if specified in config file.")
parser.add_argument("--make-extra-sub-dirs", action="store_true", help="Create a subdirectory for each subreddit.")
parser.add_argument("--nsfw-only", action="store_true", help="Not yet implemented. Search only your nsfw subreddits.")
#parser.add_argument('--file-type', default=".gif", help="The extension to look for. Defaults to .gif.")

parser.add_argument('--subreddit', help="The extension to look for. Defaults to .gif.")

args = parser.parse_args()

if args.subreddit:
    subreddits = [args.subreddit]

# set used variables with defaults
limit = args.limit
sort = "/{}".format(args.sort.lstrip('/'))
time = args.time
show = args.show
count = args.count
#file_type = args.file_type

if 'target_dir' in args and args.target_dir:
    print "target_dir:", args.target_dir
    target_dir = args.target_dir
    target_dir_specified = True
else:
    try:
        target_dir = config.default_target_dir
    except AttributeError:
        print "Please specify --target-dir or add 'default_target_dir' setting to config.py file."
        exit(1)

if args.make_sub_dirs:
    make_sub_dirs = True
else:
    try:
        make_sub_dirs = config.make_sub_dirs
    except AttributeError:
        make_sub_dirs = False

make_extra_sub_dirs = False
if args.make_extra_sub_dirs:
    make_extra_sub_dirs = True

use_rank = False
if args.alltime:
    print "YOU HAVE SELECTED ALL-TIME"
    # do not overwrite limit - can use default or specify it
    sort = "/top"
    time = "all"
    show = "all"
    use_rank = True

def make_dirs(target_dir):
    if not os.path.isdir(target_dir):
        print u"Directory {} does not exist. Creating...".format(target_dir)
        os.makedirs(target_dir)

make_dirs(target_dir)
    
print "-" * 50

#print "Looking for files of type {}.".format(file_type)
print "Looking for image files."

options = {
    "limit": limit,
    "sort": sort,
    "time": time,
    "show": show,
    "count": count,
    "after": None,
}



options_string_template = "?t={time}&limit={limit}&count={count}&show={show}&after={after}"


def get_count_updated_request(count, target_url_template, subreddit, options):
    if count == 0:
        return ""
    count_options = options.copy()
    max_page_items = 100
    final_count = count % max_page_items
    latest_post_name = None
    post_list = None
    final_post_name = None

    for i in range(count)[::max_page_items]:
        count_options.update(count=i, limit=max_page_items)
        if latest_post_name:
            count_options.update(after=latest_post_name)
        count_options_string = options_string_template.format(**count_options)
        target_url = target_url_template.format(subreddit, sort, count_options_string)
        request_data = requests.get(target_url)
        latest_post_name = request_data.json()['data']['after']
        post_list = request_data.json()['data']['children']

    final_post_name = post_list[final_count - 1]['data']['name']

    return final_post_name

def has_extension(url):
    if url[-4] == '.' or url[-5] == '.':
        return True
    return False

def get_extension(url):
    uri = url.split('/')[-1]
    try:
        extension_start = uri.index('.')
    except ValueError:
        return False
    extension = uri[extension_start:]
    return extension

def has_acceptable_extension(url):
    """Assumes url has an extension."""
    extension = get_extension(url)
    if extension in ["jpg", "jpeg", "gif", "png"]:
        return True
    return False

ignore_list = [
    "http://gifninja.com/animatedgifs/80828/asd.gif",
    "http://i.imgur.com/Tm1s6.gif",
    "http://i.imgur.com/Qhkk4.gif",
]

failed_subreddits = []

failed_downloads = []

missing_pictures = []

rank = 0
for subreddit in subreddits:
    print "-" * 5

    subreddit_target_dir = target_dir

    # if config is a tuple, then the target_dir is specified for this subreddit
    has_dir_config = False
    if hasattr(subreddit, '__iter__'):
        has_dir_config = True
        if make_sub_dirs:
            subreddit, subreddit_target_dir = subreddit
        else:
            subreddit, _ = subreddit
    if make_extra_sub_dirs and (not has_dir_config or (has_dir_config and target_dir_specified)):
        subreddit_target_dir = os.path.join(subreddit_target_dir, subreddit)
    make_dirs(subreddit_target_dir)

    target_url_template = "http://www.reddit.com/r/{}{}.json{}"
    starting_post = get_count_updated_request(count, target_url_template, subreddit, options)
    subreddit_options = options.copy()
    subreddit_options.update(after=starting_post)
    options_string = options_string_template.format(**subreddit_options)
    target_url = target_url_template.format(subreddit, sort, options_string)
    print u"{} -> {}".format(target_url, subreddit_target_dir)

    reddit_request = requests.get(target_url)
    try:
        reddit_request.raise_for_status()
    except requests.exceptions.HTTPError:
        print "Request to subreddit failed! May not be a valid subreddit."
        failed_subreddits.append("{}, at url {}".format(subreddit, target_url))
        continue

    json_data = reddit_request.json()
    for post in json_data['data']['children']:
        url = post['data']['url']
        if url in ignore_list:
            print "url is in ignore list."
            continue
        rank += 1
        title = post['data']['title']
        file_title = title.replace(' ', '_').replace('/', '').replace('.', '')[:50]
        if use_rank:
            file_title = "{}. {}".format(rank, file_title)
        #print file_title
        #print url
        #if not url.endswith(file_type):
        if not has_extension(url):
            if "imgur" in url:
                # check if album - if so, move on immediately
                if url.rsplit('/')[-2] == 'a':
                    print "URL is an album. Skipping and moving to next item."
                    continue
                print "Redirecting to imgur...",
                imgur_html = requests.get(url).text
                imgur_soup = bs4.BeautifulSoup(imgur_html)
                image_div = imgur_soup.find("div", {"class": "image" })
                print "URL:", url
                if "m.imgur" in url:
                    print "Mobile links not yet supported. Skipping image."
                    continue
                url = "http:" + image_div.find('img')['src']
                file_extension = url[-3:]
                #TEST - overwrite filetype!!
                #file_type = actual_file_type

                """
                image_uri = url.rsplit('/', 1)[-1]
                url = "http://i.imgur.com/{}{}".format(image_uri, file_type)
                """
                if url in ignore_list:
                    print "url is in ignore list."
                    continue
            else:
                print u"\"{}\" at {} is not a directly-hosted gif or is not on imgur.".format(title, url)
                continue

        #if url.endswith(file_type):
        # TEST
        if 1==1 or url.endswith(file_type):
            file_extension = get_extension(url)
            """
            if not has_acceptable_extension(url):
                print "Not an accepted extension."
                continue
            """
            if os.path.isfile(os.path.join(subreddit_target_dir, file_title)):
                print u"\"{}\" already exists.".format(file_title)
                continue
            file_path = os.path.join(subreddit_target_dir, "{}.{}".format(file_title, file_extension))
            print "Pulling {} ...".format(url),

            with open(file_path, 'w+') as f:
                try:
                    image_request = requests.get(url)
                    image_request.raise_for_status()
                except requests.exceptions.HTTPError:
                    print "No image at this location: {}".format(url)
                    continue
                except requests.exceptions.ConnectionError, socket.error:
                    print "Failed to download. URL is: {}".format(url)
                    failed_downloads.append(url)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    continue
                image_is_missing = False
                for chunk in image_request.iter_content(1024):
                    f.write(chunk)
                print u"Saved {}".format(file_title)

            """
            actual_file_type = imghdr.what(file_path)
            if actual_file_type and actual_file_type != file_path[-3:]:
                print "TESTING"
                print file_path, actual_file_type
                rename_to = "{}.{}".format(file_path, actual_file_type)
                print rename_to
                os.rename(file_path, rename_to)
                print "Renamed file to correct extension!"
                print "END TESTING"
            """

if failed_downloads:
    print "\nThe following downloads failed: ------"
    for download_url in failed_downloads:
        print download_url

if missing_pictures:
    print "\nThe following downloads are missing pictures: ------"
    for download_url in missing_pictures:
        print download_url

if failed_subreddits:
    print "\nThe following subreddits failed: ------"
    for subreddit in failed_subreddits:
        print subreddit
