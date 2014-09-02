import datetime
import json
import os
import argparse
import socket
import re

import requests
import bs4

import utils
import config

root_dir = os.path.dirname(os.path.realpath(__file__))

subreddits = config.subreddits


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
        reddit_request = make_reddit_request(target_url)
        json_stuff = reddit_request.json()
        latest_post_name = reddit_request.json()['data']['after']
        post_list = reddit_request.json()['data']['children']

    final_post_name = post_list[final_count - 1]['data']['name']

    return final_post_name

def make_reddit_request(target_url):
    headers = { 'User-Agent': 'reddit image downloader/0.1 by ParagonRG' }
    reddit_request = requests.get(target_url, headers=headers)
    return reddit_request

def download_image(image_url):
    try:
        image_request = requests.get(image_url)
        image_request.raise_for_status()
    except requests.exceptions.HTTPError:
        print "No image at this location: {}".format(image_url)
        return
    except requests.exceptions.ConnectionError, socket.error:
        print "Failed to download. URL is: {}".format(image_url)
        failed_downloads.append(image_url)
        return
    return image_request

def save_image(image, file_path):
    """
    if os.path.isfile(file_path):
        print "Error: cannot save image; file already exists."
        return False
    """
    with open(file_path, 'w+') as f:
        for chunk in image.iter_content(1024):
            f.write(chunk)
    print u"Saved {}".format(file_path.split('/')[-1])
    file_name = file_path.split('/')[-1]
    return True


def get_videos_from_gfycat(url):
    gfycat_html = requests.get(url).text
    gfycat_soup = bs4.BeautifulSoup(gfycat_html)
    video_tags = gfycat_soup.find_all("video", {"class": "gfyVid" })
    urls = []
    print "Retrieving urls from page..."
    for video_tag in video_tags:
        try:
            source_tag = video_tag.find('source', {"id": "mp4source"})
            url = source_tag['src']
            url = "http:" + url
        except AttributeError:
            print "Current image cannot be read. Skipping."
            # skip current image on page
            continue
        urls.append(url)
    return urls

def get_single_image_url_from_imgur(url):
    print "Redirecting to imgur...",
    print "URL:", url
    if "m.imgur" in url:
        print "Mobile imgur links not yet supported. Skipping image."
        return False
    imgur_html = requests.get(url).text
    imgur_soup = bs4.BeautifulSoup(imgur_html)
    image_div = imgur_soup.find("div", {"class": "image" })
    try:
        url = "http:" + image_div.find('img')['src']
    except AttributeError:
        print "Page cannot be read. Skipping."
        return False
    return url


def get_image_urls_from_imgur_album(url):
    if 'a' not in url.rsplit('/'):
        print url.split('/')
        print "Error: album expected. URL is NOT an album."
        return False
    if "m.imgur" in url:
        print "Mobile imgur links not yet supported. Skipping image."
        return False
    print "Redirecting to imgur...",
    standard_album_type = True
    imgur_html = requests.get(url).text
    imgur_soup = bs4.BeautifulSoup(imgur_html)
    image_divs = imgur_soup.find_all("div", {"class": "image" })
    urls = []
    print "Retrieving urls from page..."
    for image_div in image_divs:
        try:
            url = "http:" + image_div.find('img')['data-src']
        except AttributeError:
            print "Current image cannot be read. Skipping."
            # skip current image on page
            continue
        except KeyError:
            # Could be the other (click-through) type of album.
            url = 'test'
            standard_album_type = False
            break
        urls.append(url)

    if not standard_album_type:
        # try alternatie album type - click-through album
        image_wrapper = imgur_soup.find("div", {"class": "thumbs-carousel"})
        images = image_wrapper.find_all("img")
        for image in images:
            url = "http:" + image['data-src']
            # Strip 's' from filename - it makes image small
            uri = url.split('/')[-1]
            uri_split = uri.split('.')
            new_uri = ".".join([uri_split[0][:-1], uri_split[1]])
            url = "/".join(url.split('/')[:-1] + [new_uri])
            urls.append(url)
    return urls

def get_images_from_urls(urls, file_title, subreddit_target_dir, new_only, subdir_limit=None, start_at=0):
    """Takes a list of urls. If the list has only one item, the file path 
    is created differently.
    """
    if not urls:
        print "No urls to download."
        return False
    if start_at > len(urls) - 1:
        print "URL list size is {}. Cannot start at {}.".format(len(urls), start_at)
        return False

    list_item = start_at
    if subdir_limit is None and hasattr(config, 'subdir_limit'):
        subdir_limit = config.subdir_limit
    for url in urls[start_at:]:
        list_item += 1
        if list_item > subdir_limit and subdir_limit > 0:
            print "Stopped after {} images.".format(list_item)
            return False
        if not url:
            print "Error: URL in list is empty."
            continue
        if len(urls) > 1:
            list_item_str = str(list_item).zfill(3)
            new_file_title = file_title +  " - {}".format(list_item_str)
            file_path = get_target_file_path(url, new_file_title, subreddit_target_dir, subfolder=file_title, new_only=new_only)
        else:
            file_path = get_target_file_path(url, file_title, subreddit_target_dir, new_only=new_only)
        print file_path
        if file_path:
            save_image_from_url(url, file_path)

def get_scrubbed_file_title(title, use_rank, rank=0):
    file_title = re.sub("[_.,]", '', title)[:50]
    file_title = re.sub("[/ ]", '_', title)[:50]
    if use_rank:
        rank_string = str(rank).zfill(3)
        file_title = u"{}. {}".format(rank_string, file_title)
    return file_title


def get_target_file_path(url, file_title, subreddit_target_dir, subfolder=None, new_only=False):
    file_extension = utils.get_extension(url)
    """
    if not utils.has_acceptable_extension(url):
        print "Not an accepted extension."
        continue
    """
    file_title = u"{}.{}".format(file_title, file_extension)
    clean_file_title = strip_rank_from_title(file_title)
    file_path = os.path.join(subreddit_target_dir, file_title)
    if subfolder:
        dir_path = os.path.join(subreddit_target_dir, subfolder)
        file_path = os.path.join(dir_path, file_title)
        make_dirs(dir_path)
    if os.path.isfile(file_path):
        print u"\"{}\" already exists.".format(file_title)
        return False
    print "Pulling {} ...".format(url),
    return file_path

def save_image_from_url(url, file_path):
    if not url:
        print "Failed to get URL for image(s)."
        return False
    if url in ignore_list:
        print "URL is in ignore list."
        return False
    if not file_path:
        return False

    image = download_image(url)
    if not image:
        return False
    save_image(image, file_path)

def get_cmd_line_args():
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
    parser.add_argument("--new-only", action="store_true", help="Not yet implemented. Download only images you don't have in the specified directory.")
#parser.add_argument('--file-type', default=".gif", help="The extension to look for. Defaults to .gif.")

    parser.add_argument('--subreddits', nargs="*", help="The subreddits to search. Overwrites subreddits from config.")

    args = parser.parse_args()
    return args

args = get_cmd_line_args()

if args.subreddits:
    subreddits = [args.subreddits]
    if not isinstance(args.subreddits, basestring):
        subreddits = args.subreddits

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

def strip_rank_from_title(title):
    return title.lstrip("0123456789. ")

viewed_posts = []
viewed_posts_path = os.path.join(root_dir, "viewed_posts.txt")
open(viewed_posts_path, 'a').close()
with open(viewed_posts_path, 'r') as f:
    viewed_posts = f.read().split('\n')
with open(viewed_posts_path, "a") as f:
    f.write("\n{}\nDate/time started: {}\n".format("*"*16, datetime.datetime.now()))
#exit()


new_only = False
if args.new_only:
    new_only = True

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



ignore_list = [
    "http://i.imgur.com/Tm1s6.gif",
    "http://i.imgur.com/Qhkk4.gif",
]

failed_subreddits = []

failed_downloads = []

missing_pictures = []

def get_images(args=None):
    if not args:
        args = {}
    for subreddit in subreddits:
        rank = count
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

        reddit_request = make_reddit_request(target_url)
        try:
            reddit_request.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            print "Request to subreddit failed! May not be a valid subreddit."
            failed_subreddits.append("{}, at url {}".format(subreddit, target_url))
            continue

        if isinstance(reddit_request.json, dict):
            json_data = reddit_request.json
        else:
            json_data = reddit_request.json()
        for post in json_data['data']['children']:
            url = post['data']['url']
            rank += 1

            if new_only and url in viewed_posts:
                print "Image already viewed. See {}".format("viewed_posts.txt")
                continue
            if url not in viewed_posts:
                with open(viewed_posts_path, "a") as f:
                    f.write(url + "\n")
            title = post['data']['title']
            file_title = get_scrubbed_file_title(title, use_rank, rank=rank)

            if not utils.has_extension(url):
                if "imgur" in url:
                    # check if album - if so, move on immediately
                    if 'a' in url.rsplit('/'):
                        urls = get_image_urls_from_imgur_album(url)
                    else:
                        urls = [get_single_image_url_from_imgur(url)]
                elif "gfycat" in url:
                    urls = get_videos_from_gfycat(url)
                else:
                    print u"\"{}\" at {} is not a directly-hosted image or is not a single image on imgur.".format(title, url)
                    continue

                get_images_from_urls(urls, file_title, subreddit_target_dir, new_only)
                continue

            if not url:
                continue
            file_path = get_target_file_path(url, file_title, subreddit_target_dir, new_only=new_only)
            if file_path:
                save_image_from_url(url, file_path)

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


if __name__ == '__main__':
    args = get_cmd_line_args()
    get_images(args)
