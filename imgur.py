import download

urls = download.get_image_urls_from_imgur_album("http://imgur.com/a/NXgtI#0")
post_url = "http://imgur.com/a/NXgtI#0";

subreddit_target_dir = "/Users/daniel.moniz/test/albums/"
file_title = "Creampies"
new_only = False
start_at = 0
# subdir_limit = 0 => no image limit
subdir_limit = 0
download.get_images_from_urls(urls, post_url, file_title, subreddit_target_dir, new_only, subdir_limit=subdir_limit, start_at=start_at)
