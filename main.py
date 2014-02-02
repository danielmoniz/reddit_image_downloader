import json

import requests
import redis

import subreddits

open('test', 'w+')

subreddits = subreddits.subreddits
"""
subreddits = [
    'gifs'
]
"""

file_type = ".gif"

target_dir = "/Users/daniel.moniz/test/reddit_gifs"

for subreddit in subreddits:
    reddit_request = requests.get("http://www.reddit.com/r/{}.json".format(subreddit))
    json_data = reddit_request.json()
    for post in json_data['data']['children']:
        url = post['data']['url']
        title = post['data']['title']
        file_title = title.replace(' ', '_') + file_type
        if url.endswith(file_type):
            #with open("{}".format(file_title), 'w+') as f:
            with open("{}/{}".format(target_dir, file_title), 'w+') as f:
                file_data = requests.get(url)
                for chunk in file_data.iter_content(1024):
                    f.write(chunk)
        break
    break

