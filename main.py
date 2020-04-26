# _*_ coding: utf-8 _*_

from bs4 import BeautifulSoup
from config import config
from datetime import datetime
import feedparser
import json
import os
import telebot
import traceback
import sys

def get_time(dt):
    return datetime.strptime(dt, '%a, %d %b %Y %H:%M:%S %z')

bot = telebot.TeleBot(config.get('telegram-token'))

feeds = list()

if type(config.get('feeds')) == str:
    feeds.append(feedparser.parse(config.get('feeds')))
else:
    for feed in config.get('feeds'):
        feeds.append(feedparser.parse(feed))

new_posts_and_guid = []

if not os.path.exists('posts.json'):
    with open('posts.json', 'w') as f:
        json.dump([], f)
        f.close()

with open('posts.json') as f:
    guids = json.load(f)
    f.close()

for feed in feeds:
    for entry in feed.entries:
        content = entry['description']
        post = {}
        soup = BeautifulSoup(content, 'html.parser')
        #if soup.img:
        #    post['image'] = soup.img['src']
        post['text'] = '\n'.join(soup.stripped_strings)
        #post['text'] += '\n{}'.format(entry['link'])
        post['date'] = get_time(entry['published'])
        post['text'] += post['date'].strftime('\n%Y-%m-%d %H:%M:%S %Z')

        this_guid = entry['guid']
        if this_guid not in guids:
            # TODO: strip guid with a regex like /d{4,}\/{?}$/
            new_posts_and_guid.append((post, this_guid))

new_posts_and_guid.sort(key=lambda a_b: a_b[0]['date'])

try:
    for post, guid in new_posts_and_guid:
        bot.send_message(config.get('channel-id'), post.get('text'), disable_web_page_preview=True)
        guids.append(guid)
except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
finally:
    with open('posts.json', 'w') as f:
        json.dump(guids, f)
        f.close()
