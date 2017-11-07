#!/usr/bin/python3

import json
import os
import praw
import prawcore
import time

from praw.models.reddit.comment import Comment


reddit = praw.Reddit('etheriumbot')

required_words = ['etherium', 'ethereium', 'etharium', 'entherium']
banned_words = [
    'ethereum',
    'spell', 'spelt', 'call', 'write', 'wrote', 'written', 'type', 'typo',
    'master', 'astrolabe', 'sculptor', 'reach', 'city',
    'etherium_bot', 'etherium\\_bot', 'etherium bot'
]

banned_subreddits = 'bravenewbies budgetdecks casualmtg civclassics civcraft civex civexcirclejerk civextrade civilizatonexperiment civrealms competitiveedh custommagic devoted dragonvale dust514 edh enairim eve evedreddit evejobs evememes evenewbies eveonline eveporn fittings lrcast magiccardpulls magicdeckbuilding magicduels magictcg modernmagic mtgaltered mtgcube mtgfinance mtggore mtgjudge mtglimited mtgo mtgporn oblivionmods pauper perkusmaximus skyrim skyrimmod_jp skyrimmods skyrimporn skyrimrequiem skywind spikes tigerstaden xedit'.split()

response = "It's spelled 'Ethereum'."

def load_subreddit_blacklist():
    page = reddit.subreddit('Bottiquette').wiki['robots_txt_json']
    data = json.loads(page.content_md)
    return data['disallowed'] + data['permission'] + data['comments-only'] + data['posts-only'] + banned_subreddits

subreddit_blacklist = load_subreddit_blacklist()

def print_comment(comment):
    print('https://reddit.com%s:' % comment.permalink)
    print('%s: "%s"' % (comment.author.name, comment.body))

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

    for suffix in ['bot', 'moderator', 'notifier']:
        if comment.author.name.lower().endswith(suffix):
            print('-> ignoring because the author might be a bot:', comment.author.name)
            return False

    if comment.subreddit.display_name.lower() in subreddit_blacklist:
        print('-> ignoring because of blacklisted subreddit:', comment.subreddit.display_name)
        return False

    for word in banned_words:
        if word in text:
            print('-> ignoring because it includes the word:', word)
            return False

    parent = comment.parent()

    if isinstance(parent, Comment):
        if parent.author.name == 'etherium_bot':
            print('-> ignoring response to myself')
            return False

    return True

def reply(comment):
    print('-> replying:', response)
    os.system("afplay /System/Library/Sounds/Ping.aiff")

    try:
        comment.reply(response)
    except praw.exceptions.APIException as e:
        print("-> sorry, can't reply:", e, ":(")
    except prawcore.exceptions.Forbidden:
        print("-> oops, looks like I'm banned there :(")

print('Starting bot...')
i = 0

while True:
    print('Loading comments...')

    try:
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
