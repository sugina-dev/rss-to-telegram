# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from config import config
from datetime import datetime
import feedparser
import json
import os
import sys
import telebot
import traceback

if not os.path.exists('posts.json'):  # First run
	with open('posts.json', 'w') as f:
		json.dump([], f)
		f.close()

with open('posts.json') as f:
	old_guids = json.load(f)
	f.close()

bot = telebot.TeleBot(config.get('telegram-token'))
feed = feedparser.parse(config.get('feed'))

new_guids = []
new_posts = []

for entry in feed.entries:
	if 'description' in entry:
		content = entry['description']
		soup = BeautifulSoup(content, 'html.parser')
		date = datetime.strptime(entry['published'], '%a, %d %b %Y %H:%M:%S %z')
		text = '\n'.join(soup.stripped_strings) + date.strftime('\n%Y-%m-%d %H:%M:%S %Z')
		guid = entry['guid']
		if guid in old_guids:
			new_guids.append(guid)  # Although seen, since it is still in the feed, we need to record it
		else:
			new_posts.append({ 'text': text, 'date': date, 'guid': guid })

new_posts.sort(key=lambda post: post['date'])

current_guid = None

try:
	for post in new_posts:
		current_guid = post['guid']
		is_legal_post = 80 < len(post['text']) < 500 and len(post['text'].split('\n')) < 8
		if is_legal_post:
			bot.send_message(config.get('channel-id'), post['text'], disable_web_page_preview=True)
		new_guids.append(post['guid'])
except:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
	if current_guid is not None:
		new_guids.append(current_guid)
finally:
	with open('posts.json', 'w') as f:
		json.dump(new_guids, f)
		f.close()
