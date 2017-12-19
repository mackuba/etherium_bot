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

required_words = ['etherium', 'etheriums', 'ethereium', 'etharium', 'entherium', 'localetherium']
banned_words = [
    'ethereum', '/r/etherium',
    'spell', 'spelt', 'spelled', 'spelling',
    'call', 'called', 'calling',
    'write', 'wrote', 'written', 'writing',
    'type', 'typed', 'typing', 'typo',
    'astrolabe', 'city', 'master', 'metal', 'reach', 'scimitar', 'sculptor', 'shaper',
    'dragonvale', 'eve', 'gathering', 'hearthstone', 'minecraft', 'mtg', 'oblivion', 'runescape', 'skyrim',
    'etherium_bot', 'etherium\\_bot', 'bot'
]

required_words_regexp = [re.compile(r'\b%s\b' % word) for word in required_words]
banned_words_regexp = [re.compile(r'\b%s\b' % word) for word in banned_words]
pattern_type = type(re.compile(''))

banned_subreddits = '12winarenalog 2007scape actualredstone admincraft adorableocelots affinityforartifacts arenahs askminecraft beautifulminecraft bravenewbies budgetdecks builddaily bukkit bukkitmodding casualmtg civclassics civcraft civex civexcirclejerk civextrade civilizatonexperiment civrealms coalblocksburnforever competitiveedh competitivehs competitiveminecraft competitivewild continuemyadventure ctm cubeworldproblems customhearthstone custommagic devoted dragonvale dust514 edh edstonehelper enairim eve evedreddit evejobs evememes evenewbies eveonline eveporn feedthebeast fittings flatcore freemagic hearthdecklists hearthmemes hearthstone hearthstonecirclejerk hearthstonevods hscoaching hspulls hstournaments lrcast magiccardpulls magicdeckbuilding magicduels magictcg mapmag mcadvancements mccustomized mcfunctionsf mchardcore mchost mcpe mcpi mcrenders mcservers mcsimages mcstaff mctexturepacks mctourney mcweeklychallenge minecenter minecraft minecraft360 minecraftbuddies minecraftbugs minecraftbuilds minecraftcirclejerk minecraftcommands minecraftconspiracies minecraftfaq minecraftfighters minecraftinventions minecraftirl minecraftmapmaking minecraftmaps minecraftmemes minecraftmod minecraftmodder minecraftmodules minecraftnoteblocks minecraftpe minecraftphotography minecraftpixelart minecraftplaytesting minecraftrenders minecraftschematics minecraftseeds minecraftskins minecraftstorymode minecraftsuggestions minecraftswitch minecraftvids minecraftwallpapers minerssaloon moddedmc moddingmc modernmagic mrhb mtgaltered mtgcube mtgfinance mtggore mtgjudge mtglimited mtgo mtgporn oblivionmods pauper perkusmaximus pureminecraft realms redstone redstonenoobs rschronicle rsidleadv runescape runescapemerchanting scape shittymcbuilds shittymcsuggestions skyrim skyrimmod_jp skyrimmods skyrimporn skyrimrequiem skywind spikes spongeproject staffcraft survivalredstone textureaday theaether thehearth themonument theshaft tigerstaden trueminecraft ultrahardcore videominecraft wildhearthstone worldpainter xedit'.split()

my_comments = []
replied_to = []

response_text = "It's spelled 'Ethereum'."

response_map = [
    [['good boy', 'good lad'], ['[:-]'],
    [['epic', 'nice', 'cool', 'neat'], ['[:-]', 'Thanks! [:-]', 'Thanks!']],
    [['thanks', 'thank you'], ["You're welcome [:-]", "You're welcome!", 'No problem [:-]', 'No problem!']],
    [
        ['fuck', 'stfu', 'piss', 'worthless', 'useless', 'stupid bot', 'go to hell', re.compile(r'\bkill\b'), re.compile(r'\bdie\b')],
        [':(']
    ],
    [['your handle', 'your name', 'your username', 'your nick'], ['thatsthejoke.gif', "That's the point [:-]"]],
    [[re.compile(r'^a?eth[aei]+r\w+\??$')], ['Stop it :>', 'Nice try [:-]', 'ಠ_ಠ']],
    [
        ['isbot etherium_bot'],
        ['Of course I am a bot!', "Of course I'm a bot, how could you doubt it!",
         "I'm totally a bot, srsly. \*beep boop\*"]
    ]
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
        if line.strip().startswith('>') or ('"' in line) or ('*' in line):
            continue

        for regexp in required_words_regexp:
            if regexp.search(line):
                found = True
                break

        if found:
            break

    if not found:
        print('-> ignoring because the string might be inside a quote/reference or a part of another word')
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

    parent = comment.parent()

    if isinstance(parent, Comment):
        parent_text = parent.body.lower()
    else:
        parent_text = parent.title.lower() + "|" + parent.selftext.lower()

    for regexp in required_words_regexp:
        if regexp.search(parent_text):
            print('-> ignoring because parent comment/post includes the word:', regexp.pattern.replace(r'\b', ''))
            return False

    return True

def author_is_bot(comment):
    for suffix in ['bot', 'moderator', 'notifier']:
        if comment.author.name.lower().endswith(suffix):
            return True

    return False

def blacklisted_subreddit(comment):
    return comment.subreddit.display_name.lower() in subreddit_blacklist

def ping():
    os.system("afplay /System/Library/Sounds/Ping.aiff")

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
    ping()

def reply(comment, text):
    print('-> replying:', text)
    ping()

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

        except (praw.exceptions.APIException, prawcore.exceptions.PrawcoreException) as e:
            print('PRAW error: ', e)
            time.sleep(30)
    except KeyboardInterrupt:
        print()
        print('Bye!')
        exit(0)
