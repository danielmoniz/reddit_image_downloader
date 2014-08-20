import download

urls = download.get_image_urls_from_imgur_album("imgur album here")

subreddit_target_dir = "/path/to/target/dir/"
file_title = "Imgur album name here"
new_only = False
start_at = 0
# subdir_limit = 0 => no image limit
subdir_limit = 0
download.get_images_from_urls(urls, file_title, subreddit_target_dir, new_only, subdir_limit=subdir_limit, start_at=start_at)
