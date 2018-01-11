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
    'misspell', 'misspelt', 'misspelled', 'misspelling',
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

banned_subreddits = '12winarenalog 2007scape actualredstone admincraft adorableocelots affinityforartifacts ahrimains akalimains aram arenahs askminecraft bardmains beautifulminecraft bestofbronze bestoflegaladvice bestoftribunal braummains bravenewbies budgetdecks builddaily bukkit bukkitmodding camillemains casualmtg circloljerk civclassics civcraft civex civexcirclejerk civextrade civilizatonexperiment civrealms clg cloud9 clutchgaming coalblocksburnforever competitiveedh competitivehs competitiveminecraft competitivewild continuemyadventure ctm cubeworldproblems customhearthstone custommagic devoted dirtysionmains dragonvale dust514 edh edstonehelper enairim eve evedreddit evejobs evelynnmains evememes evenewbies eveonline eveporn fantasylcs feedthebeast fioramains fittings fizzmains flatcore fnatic frackinuniverse freemagic gangplankmains grelodfuckingdying hearthdecklists hearthmemes hearthstone hearthstonecirclejerk hearthstonevods hecarimmains hscoaching hspulls hstournaments ireliamains janna jhinmains karthusmains kaynmains khazixmains kindred kogmawmains leagueconnect leagueofgiving leagueofjinx leagueoflegends leagueoflegendsmeta leagueofmemes leagueofmeta leagueofvideos leblancmains lolchampconcepts lolcommunity loleventvods lolfanart lolgaymers lolstreams loltwistedtreeline loreofleague lrcast lulumains lux magiccardpulls magicdeckbuilding magicduels magictcg mapmag marksmanmains mcadvancements mccustomized mcfunctionsf mchardcore mchost mcpe mcpi mcrenders mcservers mcsimages mcstaff mctexturepacks mctourney mcweeklychallenge minecenter minecraft minecraft360 minecraftbuddies minecraftbugs minecraftbuilds minecraftcirclejerk minecraftcommands minecraftconspiracies minecraftfaq minecraftfighters minecraftinventions minecraftirl minecraftmapmaking minecraftmaps minecraftmemes minecraftmod minecraftmodder minecraftmodules minecraftnoteblocks minecraftpe minecraftphotography minecraftpixelart minecraftplaytesting minecraftrenders minecraftschematics minecraftseeds minecraftskins minecraftstorymode minecraftsuggestions minecraftswitch minecraftvids minecraftwallpapers minerssaloon moddedmc moddingmc modernmagic mrhb mtgaltered mtgcube mtgfinance mtggore mtgjudge mtglimited mtgo mtgporn nidaleemains nomansskythegame oblivionmods opticgaming ourleague pauper perkusmaximus pureminecraft quinnmains realms redstone redstonenoobs riotpls rivalsofaether rivenmains rschronicle rsidleadv runescape runescapemerchanting ryzemains scape shacomains shittymcbuilds shittymcsuggestions singedmains skyrim skyrimmod_jp skyrimmods skyrimporn skyrimrequiem skywind sonamains sorakamains spikes spongeproject staffcraft summonerschool supportlol survivalredstone swainmains taliyahmains talonmains team_liquid teamredditteams teamsolomid teemotalk teslore textureaday theaether thehearth themonument thesecretweapon theshaft threshmains tigerstaden trueminecraft tryndameremains twitchmains udyrmains ultrahardcore varusmains velkoz videominecraft viktormains wildhearthstone worldpainter xedit xerathmains yasuomains yimo zedmains zoemains zyramains'.split()

my_comments = []
replied_to = []

response_text = "It's spelled 'Ethereum'."

response_map = [
    [
        ['good boy', 'good lad'],
        ['[:-]']
    ],
    [
        ['love you', 'love this bot', 'my hero', 'my favorite', 'my favourite'],
        ['<3']
    ],
    [
        ['you understand', 'you understood'],
        ["I'm just a bot [:-]"]
    ],
    [
        ['thanks', 'thank you', 'thx'],
        ["You're welcome [:-]", "You're welcome!", 'No problem [:-]', 'No problem!']
    ],
    [
        [re.compile(r'^ty$')],
        ['np [:-]']
    ],
    [
        ['catch'],
        []
    ],
    [
        ['epic', 'nice', 'cool', 'neat', 'great'],
        ['Thanks! [:-]', 'Thanks!']
    ],
    [
        ['sorry', 'my bad'],
        ['No problem [:-]']
    ],
    [
        ["don't care", 'dont care', 'could care less', "couldn't care less", 'nobody cares'],
        ['¯\\\_(ツ)\_/¯']
    ],
    [
        [re.compile(r'^(actually,? )?it\'s (actually )?(spelled|spelt)')],
        ["It's spelled \"you're talking to a bot\" [:-]"]
    ],
    [
        ['fuck', 'stfu', 'piss', 'dick', 'worthless', 'useless', 'annoying', 'stupid bot', 'go to hell', 'shut up',
         'shutup', re.compile(r'\bkill\b'), re.compile(r'\bdie\b')],
        [':(']
    ],
    [
        ['your handle', 'your name', 'your username', 'your nick'],
        ["I correct people who write 'etherium', so I'm an etherium bot, very logical [:-]"]
    ],
    [
        ['grammar nazi'],
        ["Actually, it's spelling, not grammar [:-]"]
    ],
    [
        [re.compile(r'^\s*([aeir]+th[aei]+r\w+\??\s*)+\s*$')],
        ['Stop it :>', 'Nice try [:-]', 'ಠ_ಠ', 'No.']
    ],
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

    if not comment_text_really_matches(text):
        print('-> ignoring because the string might be inside a quote/reference or a part of another word')
        return False

    if author_is_bot(comment):
        print('-> ignoring because the author might be a bot:', comment.author.name)
        return False

    if blacklisted_subreddit(comment):
        print('-> ignoring because of blacklisted subreddit:', comment.subreddit.display_name)
        return False

    if len(comment.body) > 1000:
        print('-> ignoring because the comment is too long:', len(comment.body), 'characters')
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

def comment_text_really_matches(text):
    if '://' in text:
        return False

    for line in text.split('\n'):
        if line.strip().startswith('>'):
            continue

        might_be_quote = False

        for symbol in ['"', '*', '”', '“', '‟', '‘', '‛', '«', '»']:
            if symbol in line:
                might_be_quote = True
                break

        if might_be_quote:
            continue

        for regexp in required_words_regexp:
            if regexp.search(line):
                return True

    return False

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

    if len(comment.body) > 400:
        reply(comment, "Sorry, I'm just a bot \*beep boop\* [:-]")
        replied_to.append(comment.author.name)
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
            if responses:
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
