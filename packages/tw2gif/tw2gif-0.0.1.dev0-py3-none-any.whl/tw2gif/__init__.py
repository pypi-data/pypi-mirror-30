import os
import sys
from tw2gif.tw2gif import Tw2Gif
import click

@click.command()
@click.option('--url', '-u', help='Tweet URL')
@click.option('--output', '-o', help='Output file path')
def main(url, output):
    if not url:
        print('Ups, you didn\'t especified any tweet url... :/ ')
        return
    if not output:
        output = ''
    tw2gif = Tw2Gif()
    tw2gif.download_gif(url, output)
