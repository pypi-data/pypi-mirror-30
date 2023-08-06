#! /usr/bin/env python3

import argparse
from mpd import ConnectionError
import time
from mpd import MPDClient
import random

mpdc = MPDClient()
mpdc.timeout = 10
mpdc.idletimeout = None


def main():
    global MPIP
    parser = argparse.ArgumentParser(description='Control playback on your mpd server.')

    parser.add_argument('-p', '--pause',
                        help='Toggles playback',
                        action='store_true')

    parser.add_argument('-S', '--song',
                        help='Prints info on the current song',
                        action='store_true')

    parser.add_argument('-n', '--next',
                        help='Next song',
                        action='store_true')

    parser.add_argument('-s', '--shuffle',
                        help='Toggles shuffle',
                        action='store_true')

    parser.add_argument('-v', '--volume', type=int,
                        help='Changes the volume to given values, 0-100',
                        action='store')

    parser.add_argument('-i', '--ip',
                        help='Specify an IP address, defaults to \'localhost\'',
                        action='store', default='localhost')

    args = parser.parse_args()

    if args.ip:
        MPIP = args.ip
    if args.ip == '':
        MPIP = 'localhost'

    if args.pause:
        toggle_playback()
        exit()

    if args.song:
        get_song_info()
        exit()

    if args.next:
        next_song()
        exit()

    if args.shuffle:
        toggle_shuffle()
        exit()

    if args.volume:
        global V
        V = args.volume
        chvol()
        exit()


def toggle_playback():
    while True:
        try:
            status = mpdc.status()
            if status['state'] == 'play':
                print('Pausing...')
                mpdc.pause()
                break
            if status['state'] == 'pause':
                print('Playing...')
                mpdc.play()
                break
            if status['state'] == 'stop':
                print('Playing from playlists...')
                track = random.randint(1, 216)
                mpdc.load('Work 2016 (by jverm)')
                mpdc.play(track)
                break
            else:
                print('Huh?')
                break
        except ConnectionError:
            mpdc.connect(MPIP, 6600)
            status = mpdc.status()
            continue


def get_song_info():
    while True:
        try:
            X = mpdc.currentsong()
            print(color.CYAN, 'Now Playing:', color.END)
            print(color.RED, X['title'], color.END)
            print(color.RED, 'By', X['artist'])
            break
        except ConnectionError:
            mpdc.connect(MPIP, 6600)
            continue


def next_song():
    while True:
        try:
            mpdc.next()
            time.sleep(1)
            get_song_info()
            break
        except ConnectionError:
            mpdc.connect(MPIP, 6600)
            continue


def toggle_shuffle():
    while True:
        try:
            mpdc.random(1)
            time.sleep(1)
            get_song_info()
            break
        except ConnectionError:
            mpdc.connect(MPIP, 6600)
            continue


def chvol():
    while True:
        try:
            mpdc.setvol(V)
            print(color.RED, 'Volume has been changed to ', V, '%')
            break
        except ConnectionError:
            mpdc.connect(MPIP, 6600)
            continue


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


if __name__ == '__main__':
    main()
