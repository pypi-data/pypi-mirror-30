"""
Tw2Gif: Tweet gif downloader using FFMPEG
"""
import os
import json
import twitter
import requests
import subprocess
import re
from pathlib import Path 
from tw2gif.settings import (
    CONSUMER_KEY, CONSUMER_SECRET,
    ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET,
    FFMPEG_SCRIPT
)

class Tw2Gif:
    def __init__(self):
        self.api = twitter.Api(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token_key=ACCESS_TOKEN_KEY,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    def get_video_url(self, tweet):
        url = ""
        try:
            url = tweet['media'][0]['video_info']['variants'][0]['url']
        except:
            pass
        return url

    def get_tweet_id(self, url):
        return re.split(r'\/', url)[-1]

    def download_gif(self, url, path='./'):
        """
        Parses tweet to get mp4 video url, and downloads and transforms it using FFMPEG script
        """
        print('Downloading gif...')
        tweet_id = self.get_tweet_id(url)
        tweet = self.api.GetStatus(tweet_id).AsDict()
        url = self.get_video_url(tweet)

        if not url:
            raise Exception('No video URL found in this tweet :(')

        req = requests.get(url)
        mp4_file = "aux-{}.mp4".format(tweet_id)
        gif_file = os.path.join(path, "{}.gif".format(tweet_id))
        
        if req.status_code == 200:
            with open(mp4_file, 'wb') as f:
                f.write(req.content)

        result = subprocess.call([FFMPEG_SCRIPT, mp4_file, gif_file])

        if result == 0:
            print('Gif succesfully created')
        else:
            print('Ups, something went wrong :(')

