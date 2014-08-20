from kivy.app import App

import download

class RedditImageDownloader(App):
    def build(self):
        download.get_images()
        print 'images downloaded'
        exit()

if __name__ in ('__main__', '__android__'):
    RedditImageDownloader().run()
