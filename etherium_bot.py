#!/usr/bin/python3

import json
import os
import praw
import prawcore
import time

reddit = praw.Reddit('etheriumbot')

required_words = ['etherium', 'ethereium', 'etharium']
banned_words = ['ethereum', 'spell', 'spelt', 'write', 'wrote', 'written', 'type', 'typo', 'master', 'astrolabe', 'sculptor']

banned_subreddits = ['budgetdecks', 'casualmtg', 'competitiveedh', 'custommagic', 'dragonvale', 'edh', 'enairim', 'lrcast', 'magiccardpulls', 'magicdeckbuilding', 'magicduels', 'magictcg', 'modernmagic', 'mtgaltered', 'mtgcube', 'mtgfinance', 'mtggore', 'mtgjudge', 'mtglimited', 'mtgo', 'mtgporn', 'oblivionmods', 'pauper', 'perkusmaximus', 'skyrim', 'skyrimmod_jp', 'skyrimmods', 'skyrimporn', 'skyrimrequiem', 'skywind', 'spikes', 'xedit']

response = "It's spelled 'Ethereum'."

def load_subreddit_blacklist():
    page = reddit.subreddit('Bottiquette').wiki['robots_txt_json']
    data = json.loads(page.content_md)
    return data['disallowed'] + data['permission'] + data['comments-only'] + data['posts-only'] + banned_subreddits

subreddit_blacklist = load_subreddit_blacklist()

def print_comment(comment):
    print('https://reddit.com%s:' % comment.permalink())
    print('%s: "%s"' % (comment.author.name, comment.body))
    os.system("afplay /System/Library/Sounds/Ping.aiff")

def comment_matches(comment):
    found = False
    text = comment.body.lower()

    for word in required_words:
        index = text.find(word)
        if index >= 0:
            if index == 0 or text[index-1] in [" ", "\n"]:
                found = True
                break
            else:
                print_comment(comment)
                print('-> ignoring because the string matched in the middle of a word')
                return False

    if not found:
        return False

    print_comment(comment)

    if comment.author.name.lower().endswith('bot'):
        print('-> ignoring because the author might be a bot:', comment.author.name)
        return False

    if comment.subreddit.display_name.lower() in subreddit_blacklist:
        print('-> ignoring because of blacklisted subreddit:', comment.subreddit.display_name)
        return False

    for word in banned_words:
        if word in text:
            print('-> ignoring because it includes the word:', word)
            return False

    return True

def reply(comment):
    print('-> replying:', response)
    try:
        comment.reply(response)
    except praw.exceptions.APIException as e:
        print("-> sorry, can't reply:", e, ":(")

print('Starting bot...')

while True:
    i = 0
    print('Loading comments...')

    try:
        for comment in reddit.subreddit('all').stream.comments():
            i += 1

            if comment_matches(comment):
                reply(comment)

            if i % 10000 == 0:
                print(i)

    except (praw.exceptions.APIException, prawcore.exceptions.RequestException) as e:
        print('PRAW error: ', e)
        time.sleep(30)
    except KeyboardInterrupt:
        print()
        print('Bye!')
        exit(0)
