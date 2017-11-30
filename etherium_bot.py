#!/usr/bin/python3

import json
import os
import praw
import prawcore
import random
import re
import time

from praw.models.reddit.comment import Comment


reddit = praw.Reddit('etheriumbot')

required_words = ['etherium', 'ethereium', 'etharium', 'entherium', 'localetherium']
banned_words = [
    'ethereum', '/r/etherium',
    'spell', 'spelt', 'spelled', 'spelling',
    'call', 'called', 'calling',
    'write', 'wrote', 'written', 'writing',
    'type', 'typed', 'typing', 'typo',
    'astrolabe', 'city', 'master', 'reach', 'scimitar', 'sculptor',
    'dragonvale', 'eve', 'gathering', 'hearthstone', 'minecraft', 'mtg', 'oblivion', 'runescape', 'skyrim',
    'etherium_bot', 'etherium\\_bot', 'bot'
]

required_words_regexp = [re.compile(r'\b%s\b' % word) for word in required_words]
banned_words_regexp = [re.compile(r'\b%s\b' % word) for word in banned_words]
pattern_type = type(re.compile(''))

banned_subreddits = '12winarenalog 2007scape affinityforartifacts arenahs bravenewbies budgetdecks casualmtg civclassics civcraft civex civexcirclejerk civextrade civilizatonexperiment civrealms competitiveedh competitivehs competitivewild customhearthstone custommagic devoted dragonvale dust514 edh enairim eve evedreddit evejobs evememes evenewbies eveonline eveporn fittings hearthdecklists hearthmemes hearthstone hearthstonecirclejerk hearthstonevods hscoaching hspulls hstournaments lrcast magiccardpulls magicdeckbuilding magicduels magictcg modernmagic mtgaltered mtgcube mtgfinance mtggore mtgjudge mtglimited mtgo mtgporn oblivionmods pauper perkusmaximus rschronicle rsidleadv runescape runescapemerchanting scape skyrim skyrimmod_jp skyrimmods skyrimporn skyrimrequiem skywind spikes thehearth tigerstaden wildhearthstone xedit'.split()

my_comments = []
replied_to = []

response_text = "It's spelled 'Ethereum'."

response_map = [
    [['good boy', 'good lad', 'epic', 'nice', 'cool'], ['[:-]', 'Thanks! [:-]', 'Thanks!']],
    [['thanks', 'thank you'], ["You're welcome [:-]", "You're welcome!", 'No problem [:-]', 'No problem!']],
    [['fuck', 'stfu', 'worthless', 'useless', 'stupid bot', re.compile(r'\bkill\b'), re.compile(r'\bdie\b')], [':(']],
    [['your handle', 'your name', 'your username', 'your nick'], ['thatsthejoke.gif', "That's the point [:-]"]],
    [[re.compile(r'^eth[ae]\w+\??$')], ['Stop it :>', 'Nice try [:-]', 'ಠ_ಠ']],
]

def load_subreddit_blacklist():
    page = reddit.subreddit('Bottiquette').wiki['robots_txt_json']
    data = json.loads(page.content_md)
    return data['disallowed'] + data['permission'] + data['comments-only'] + data['posts-only'] + banned_subreddits

subreddit_blacklist = load_subreddit_blacklist()

def print_comment(comment):
    lines = comment.body.split('\n')

    if len(lines) > 10:
        text = '\n'.join(lines[0:10]) + "\n(…)"
    else:
        text = comment.body

    print('https://reddit.com%s:' % comment.permalink)
    print('%s: "%s"' % (comment.author.name, text))

def responds_to_me(comment):
    parent = comment.parent()

    if isinstance(parent, Comment):
        return (parent in my_comments)
    else:
        return False

def comment_matches(comment):
    found = False
    text = comment.body.lower()

    for word in required_words:
        if word in text:
            found = True
            break

    if not found:
        return False

    print_comment(comment)

    found = False

    for line in text.split('\n'):
        if line.strip().startswith('>') or ('"' in line):
            continue

        for regexp in required_words_regexp:
            if regexp.search(line):
                found = True
                break

        if found:
            break

    if not found:
        print('-> ignoring because the string might be inside a quote or a part of another word')
        return False

    if author_is_bot(comment):
        print('-> ignoring because the author might be a bot:', comment.author.name)
        return False

    if blacklisted_subreddit(comment):
        print('-> ignoring because of blacklisted subreddit:', comment.subreddit.display_name)
        return False

    for regexp in banned_words_regexp:
        if regexp.search(text):
            print('-> ignoring because it includes the word:', regexp.pattern.replace(r'\b', ''))
            return False

    return True

def author_is_bot(comment):
    for suffix in ['bot', 'moderator', 'notifier']:
        if comment.author.name.lower().endswith(suffix):
            return True

    return False

def blacklisted_subreddit(comment):
    return comment.subreddit.display_name.lower() in subreddit_blacklist

def reply_to_comment(comment):
    reply(comment, response_text)

def reply_to_response(comment):
    print('*REPLY RECEIVED*')
    print_comment(comment)

    if author_is_bot(comment):
        print('-> ignoring because the author might be a bot:', comment.author.name)
        return

    if blacklisted_subreddit(comment):
        print('-> ignoring because of blacklisted subreddit:', comment.subreddit.display_name)
        return

    if comment.author.name in replied_to:
        print("-> ignoring because we've already replied once to this user:", comment.author.name)
        return

    text = comment.body.lower()

    for (patterns, responses) in response_map:
        found = False

        for pattern in patterns:
            if isinstance(pattern, pattern_type):
                if pattern.search(text):
                    found = True
                    break
            else:
                if pattern in text:
                    found = True
                    break

        if found:
            reply(comment, random.choice(responses))
            replied_to.append(comment.author.name)
            return

    print('-> no response pattern matched')

def reply(comment, text):
    print('-> replying:', text)
    os.system("afplay /System/Library/Sounds/Ping.aiff")

    try:
        reply = comment.reply(text)
        my_comments.append(reply)
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

                if responds_to_me(comment):
                    reply_to_response(comment)
                elif comment_matches(comment):
                    reply_to_comment(comment)

                if i % 10000 == 0:
                    print(i)

        except (praw.exceptions.APIException, prawcore.exceptions.RequestException) as e:
            print('PRAW error: ', e)
            time.sleep(30)
    except KeyboardInterrupt:
        print()
        print('Bye!')
        exit(0)
