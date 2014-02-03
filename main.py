import json
import os

import requests
import redis

import subreddits

subreddits = subreddits.subreddits

file_type = ".gif"

target_dir = "/Users/daniel.moniz/test/reddit_gifs"
target_dir = "/Users/daniel.moniz/test/top_reddit_gifs"
options = {
    "limit": 35,
    "sort": "top",
    "time": "all",
    "show": "all",
    "count": 0,
}


options = "?sort={sort}&t={time}&limit={limit}".format(**options)

for subreddit in subreddits:
    target_url = "http://www.reddit.com/r/{}.json{}".format(subreddit, options)
    print "{} -> {}".format(target_url, target_dir)
    reddit_request = requests.get(target_url)
    json_data = reddit_request.json()
    for post in json_data['data']['children']:
        url = post['data']['url']
        title = post['data']['title']
        file_title = title.replace(' ', '_') + file_type
        if not os.path.isfile(os.path.join(target_dir, file_title)):
            if url.endswith(file_type):
                #with open("{}".format(file_title), 'w+') as f:
                with open("{}/{}".format(target_dir, file_title), 'w+') as f:
                    print "Downloading {} ...".format(file_title)
                    try:
                        file_data = requests.get(url)
                    except requests.exceptions.ConnectionError:
                        print "Failed to download. URL is: {}".format(url)
                        continue
                    for chunk in file_data.iter_content(1024):
                        f.write(chunk)

