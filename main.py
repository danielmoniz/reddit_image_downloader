import json
import os
import argparse

import requests
import redis

import subreddits

subreddits = subreddits.subreddits

parser = argparse.ArgumentParser(description="Pull image files from reddit.")
parser.add_argument("--alltime", action="store_true", help="Pull all images from the top, all-time posts.")

parser.add_argument('--limit', default=25, type=int, help="The number of posts to be pulled.")
parser.add_argument('--sort', default="top", help="Sort by top posts, controversial, etc: top, hot, new, controversial, gilded")
parser.add_argument('--time', default="day", help="The time from which to find posts: all, hour, day, month, year")
parser.add_argument('--show', default="all", help="Which posts to show.")
parser.add_argument('--count', default=25, type=int, help="The post to start at (paginate).")

parser.add_argument('--target-dir', help="The directory in which to save the images.")
parser.add_argument('--file-type', default=".gif", help="The extension to look for. Defaults to .gif.")
args = parser.parse_args()

# set used variables
limit = args.limit
sort = args.sort
time = args.time
show = args.show
count = args.count
file_type = args.file_type

if args.alltime:
    limit = 25
    sort = "top"
    time = "all"
    show = "all"
    count = 0

target_dir = "/Users/daniel.moniz/test/reddit_gifs"

if 'target_dir' in args:
    target_dir = args.target_dir

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
}


options = "?sort={sort}&t={time}&limit={limit}&count={count}&show={show}".format(**options)

for subreddit in subreddits:
    target_url = "http://www.reddit.com/r/{}.json{}".format(subreddit, options)
    print "{} -> {}".format(target_url, target_dir)
    reddit_request = requests.get(target_url)
    json_data = reddit_request.json()
    for post in json_data['data']['children']:
        url = post['data']['url']
        title = post['data']['title']
        file_title = title.replace(' ', '_') + file_type
        #print file_title
        if not url.endswith(file_type):
            print "\"{}\" at {} is not a directly-hosted gif.".format(title, url)
        if url.endswith(file_type):
            if not os.path.isfile(os.path.join(target_dir, file_title)):
                with open("{}/{}".format(target_dir, file_title), 'w+') as f:
                    print "Downloading {} ...".format(file_title)
                    try:
                        file_data = requests.get(url)
                    except requests.exceptions.ConnectionError:
                        print "Failed to download. URL is: {}".format(url)
                        continue
                    for chunk in file_data.iter_content(1024):
                        f.write(chunk)

