import json
import os
import argparse
import socket

import requests

import subreddits

subreddits = subreddits.subreddits

parser = argparse.ArgumentParser(description="Pull image files from reddit.")
parser.add_argument("--alltime", action="store_true", help="Pull all images from the top, all-time posts.")

parser.add_argument('--limit', default=25, type=int, help="The number of posts to be pulled.")
parser.add_argument('--sort', default="", help="Sort by top posts, controversial, etc: top, hot, new, controversial, gilded")
parser.add_argument('--time', default="day", help="The time from which to find posts: all, hour, day, month, year")
parser.add_argument('--show', default="all", help="Which posts to show.")
parser.add_argument('--count', default=25, type=int, help="The post to start at (paginate).")

parser.add_argument('--target-dir', default="/Users/daniel.moniz/test/reddit_gifs", help="The directory in which to save the images.")
parser.add_argument('--file-type', default=".gif", help="The extension to look for. Defaults to .gif.")

parser.add_argument('--subreddit', help="The extension to look for. Defaults to .gif.")

args = parser.parse_args()

if args.subreddit:
    subreddits = [args.subreddit]

# set used variables
limit = args.limit
sort = args.sort
time = args.time
show = args.show
count = args.count
file_type = args.file_type
target_dir = args.target_dir

if args.alltime:
    print "YOU HAVE SELECTED ALL-TIME"
    # do not overwrite limit - can use default or specify it
    sort = "/top"
    time = "all"
    show = "all"

if not os.path.isdir(target_dir):
    print "Directory does not exist. Creating..."
    os.makedirs(target_dir)
    
print args
print "-" * 50

print "Looking for files of type {}.".format(file_type)

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

ignore_list = [
    "http://gifninja.com/animatedgifs/80828/asd.gif",
    "http://i.imgur.com/Tm1s6.gif",
    "http://i.imgur.com/Qhkk4.gif",
]

failed_downloads = []
"""
imgur_template_file = open("imgur_no_longer_available")

missing_imgur_image_template = imgur_template_file.read(1024)
imgur_template_file.close()
"""

missing_pictures = []

for subreddit in subreddits:
    target_url_template = "http://www.reddit.com/r/{}{}.json{}"
    starting_post = get_count_updated_request(count, target_url_template, subreddit, options)
    subreddit_options = options.copy()
    subreddit_options.update(after=starting_post)
    options_string = options_string_template.format(**subreddit_options)
    target_url = target_url_template.format(subreddit, sort, options_string)
    print "{} -> {}".format(target_url, target_dir)

    reddit_request = requests.get(target_url)
    json_data = reddit_request.json()
    for post in json_data['data']['children']:
        url = post['data']['url']
        if url in ignore_list:
            print "url is in ignore list."
            continue
        title = post['data']['title']
        file_title = title.replace(' ', '_') + file_type
        file_title = file_title.replace('/', '')
        #print file_title
        if not url.endswith(file_type):
            if "imgur" in url:
                image_uri = url.rsplit('/', 1)[-1]
                url = "http://i.imgur.com/{}{}".format(image_uri, file_type)
                print "Redirecting to imgur...",
                if url in ignore_list:
                    print "url is in ignore list."
                    continue
            else:
                print "\"{}\" at {} is not a directly-hosted gif or is not on imgur.".format(title, url)
        if url.endswith(file_type):
            if os.path.isfile(os.path.join(target_dir, file_title)):
                print "\"{}\" already exists.".format(file_title)
                continue
            file_path = os.path.join(target_dir, file_title)
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
                """
                # This code is meant for determining if a picture does not
                # exist on imgur (ie. it provides a standard image).
                for chunk in image_request.iter_content(1024):
                    if chunk == missing_imgur_image_template:
                        image_is_missing = True
                    break
                if image_is_missing:
                    missing_pictures.append(url)
                    continue
                """
                for chunk in image_request.iter_content(1024):
                    f.write(chunk)
                print "Saved {}".format(file_title)

if failed_downloads:
    print "\nThe following downloads failed: ------"
    for download_url in failed_downloads:
        print download_url

if missing_pictures:
    print "\nThe following downloads are missing pictures: ------"
    for download_url in missing_pictures:
        print download_url
