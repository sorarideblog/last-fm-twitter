# 使用するTwitter App：last_fm twitter (アイマス垢でログイン)
# App ID : 16411000
#

import tweepy
import urllib.request
import json
import unicodedata
import datetime
import linebot

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)


YOUR_CHANNEL_ACCESS_TOKEN = "G/uqAEK0ctNntVD34jH7z/wnB18vSy0xymabZkcQbWCUxd64Iz1/rnyrIgM2i2SroZB5+tk1biuacuK0tEsNxR0FnM5y7x8/fspBhTazfj0jhSc8kdDiV6jq22BmykCBOojI+XgA2Zwnv8xpbmxZ2wdB04t89/1O/w1cDnyilFU="
YOUR_CHANNEL_SECRET = "7d5d04f9c0fe86a79f1f773c396e16ed"
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

TWITTER_CONSUMER_KEY = "hV5TwGetWs4hdkLxGeLDKohhs"
TWITTER_CONSUMER_SECRET = "MN5IV3uPXNFlzIteyPQP96fcG7aMKxu8a1VQGk5awa4dBedXBn"
TWITTER_ACCESS_TOKEN = "736532743182389248-WVs2qc7mz2fX4b3xJv82DbBXfiirQzv"
TWITTER_ACCESS_TOKEN_SECRET = "md9IbOwHwTCv9MhWJhB7zuFILDY9deu3EgKxbDNtpXOsM"


global period


def main():
    data = get_last_fm_tracks()
    # ツイートする文字列
    max_char_len = 13
    tweet_str = make_ranking(data, max_char_len)
    pre = tweet_str
    print('文字数：', len_tweet(tweet_str))
    if len_tweet(tweet_str) < 280:
        while len_tweet(tweet_str) < 280:
            max_char_len += 1
            tweet_str = make_ranking(data, max_char_len)
            if len_tweet(tweet_str) > 280:
                max_char_len -= 1
                tweet_str = make_ranking(data, max_char_len)
                break
            if (pre == tweet_str):
                break
            pre = tweet_str

    else:
        while len_tweet(tweet_str) > 280:
            max_char_len -= 1
            tweet_str = make_ranking(data, max_char_len)
            if len_tweet(tweet_str) < 280:
                break
            if (pre == tweet_str):
                break
            pre = tweet_str

    print(tweet_str)
    make_api().update_status(tweet_str)
    line_send_message(tweet_str)
    print('文字数：', len_tweet(tweet_str))
    print('max_char_len =', max_char_len)
    

def make_api():
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def get_last_fm_tracks():
    global period
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'format': 'json',
        'api_key': 'dffc444f187e0e404425f94dabc323bf',
        'method': 'user.getTopTracks',
        'user': 'SoraraP',
        'period': period,
    }
    req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)))
    with urllib.request.urlopen(req) as res:
        body = res.read()
        body = json.loads(body)
        return body
        
        
def make_ranking(data, max_char_len=13):
    global period
    track_titles = []
    track_artists = []
    track_playcount = []
    track_num = 0
    for track in data['toptracks']['track']:
        if track_num < 5:
            if int(track['playcount']) >= 3:
                if len_tweet(track['name']) > max_char_len:
                    track_titles.append(track['name'][:max_char_len] + '…')
                else:
                    track_titles.append(track['name'][:max_char_len])
                if len_tweet(track['artist']['name']) > max_char_len:
                    track_artists.append(track['artist']['name'][:max_char_len] + '…')
                else:
                    track_artists.append(track['artist']['name'][:max_char_len])
                track_playcount.append(track['playcount'])
                track_num += 1

    tweet = '私が'
    if period == '7day':
        tweet += '今週'
    elif period == '1month':
        tweet += '先月'
    elif period == '12month':
        tweet += '今年'
    tweet += '聞いた曲ランキング\n'
    for i in range(track_num):
        tweet += str(i+1) + ' ' + track_titles[i]
        tweet += ' [' + track_artists[i] + ']'
        tweet += '(' + str(track_playcount[i]) + '回)\n'

    return tweet[:-1]   # 最後の改行を削除


def len_tweet(text):
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'Na':
            count += 1
        else:
            count += 2
    return count


def line_send_message(text):
    user_id = "Ub3e6da6b3eea3ab696e2a21753aa7355"
    line_bot_api.push_message(user_id, TextSendMessage(text=text))


if __name__ == "__main__":
    global period
    today = datetime.date.today()
    weekday = today.weekday()
    day = today.day
    month = today.month
    print(weekday, day, month)
    if weekday == 6:     # Sunday
        period = '7day'
        main()
    if day == 1:
        period = '1month'
        main()
    if month == 12 and day == 30:
        period = '12month'
        main()


