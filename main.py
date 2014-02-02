import json

import requests
import redis

import subreddits

subreddits = subreddits.subreddits

file_type = ".gif"

target_dir = "/Users/daniel.moniz/test/reddit_gifs"

for subreddit in subreddits:
    target_url = "http://www.reddit.com/r/{}.json".format(subreddit)
    reddit_request = requests.get(target_url)
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

