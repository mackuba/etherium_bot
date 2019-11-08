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
    'you mean', 'you meant',
    'sic',
    'astrolabe', 'city', 'crown', 'esper', 'master', 'metal', 'reach', 'scimitar', 'sculptor', 'shaper',
    'dragonvale', 'eve', 'gathering', 'hearthstone', 'magic', 'minecraft', 'mtg', 'oblivion', 'runescape', 'skyrim',
    'etherium_bot', 'etherium\\_bot', 'bot'
]

required_words_regexp = [re.compile(r'\b%s\b' % word) for word in required_words]
banned_words_regexp = [re.compile(r'\b%s\b' % word) for word in banned_words]
pattern_type = type(re.compile(''))

banned_subreddits = '12winarenalog 2007scape 40klore actualredstone admincraft adorableocelots affinityforartifacts ahrimains akalimains aplanetofmine aram arenahs askminecraft bardmains beautifulminecraft bestofbronze bestoflegaladvice bestoftribunal bootlegmtg braummains bravenewbies budgetdecks builddaily bukkit bukkitmodding camillemains casualmtg circloljerk civclassics civcraft civex civexcirclejerk civextrade civilizatonexperiment civrealms clg cloud9 clutchgaming coalblocksburnforever competitiveedh competitivehs competitiveminecraft competitivewild continuemyadventure createthisworld ctm cubeworldproblems customhearthstone custommagic d100 devoted dirtysionmains dragonvale dust514 edh edstonehelper eggsmtg elderscrolls enairim eve evedreddit evejobs evelynnmains evememes evenewbies eveonline eveporn fallout fantasylcs fantasywriters feedthebeast fioramains fittings fizzmains flatcore fnatic frackinuniverse freemagic gangplankmains grelodfuckingdying gw2exchange hearthdecklists hearthmemes hearthstone hearthstonecirclejerk hearthstonevods hecarimmains hscoaching hspulls hstournaments ireliamains janna jhinmains karthusmains kaynmains khazixmains kindred knightfallmtg kogmawmains leagueconnect leagueofgiving leagueofjinx leagueoflegends leagueoflegendsmeta leagueofmemes leagueofmeta leagueofvideos leblancmains lolchampconcepts lolcommunity loleventvods lolfanart lolgaymers lolstreams loltwistedtreeline loreofleague lrcast lulumains lux magiccardpulls magicdeckbuilding magicduels magictcg mapmag marksmanmains mcadvancements mccustomized mcfunctionsf mchardcore mchost mcpe mcpi mcrenders mcservers mcsimages mcstaff mctexturepacks mctourney mcweeklychallenge minecenter minecraft minecraft360 minecraftbuddies minecraftbugs minecraftbuilds minecraftcirclejerk minecraftcommands minecraftconspiracies minecraftfaq minecraftfighters minecraftinventions minecraftirl minecraftmapmaking minecraftmaps minecraftmemes minecraftmod minecraftmodder minecraftmodules minecraftnoteblocks minecraftpe minecraftphotography minecraftpixelart minecraftplaytesting minecraftrenders minecraftschematics minecraftseeds minecraftskins minecraftstorymode minecraftsuggestions minecraftswitch minecraftvids minecraftwallpapers minerssaloon moddedmc moddingmc modernmagic mrhb mtgaltered mtgbracket mtgcube mtgfinance mtggore mtgjudge mtglegacy mtglimited mtgo mtgporn mtgvorthos nidaleemains nomansskythegame oblivionmods oldschoolrs opticgaming ourleague overwatch pauper perkusmaximus ponzamtg pureminecraft quinnmains realms redstone redstonenoobs riotpls rivalsofaether rivenmains rschronicle rsidleadv runescape runescapemerchanting ryzemains scape shacomains shittymcbuilds shittymcsuggestions singedmains skyrim skyrimmod_jp skyrimmods skyrimporn skyrimrequiem skyrimvr skywind sonamains sorakamains spikes spongeproject staffcraft steamkiwi stellaris summonerschool supportlol survivalredstone swainmains taliyahmains talonmains tamrielscholarsguild team_liquid teamredditteams teamsolomid teemotalk teslore textureaday theaether thehearth themonument thesecretweapon theshaft threshmains tigerstaden tinyleaders tronmtg trueminecraft tryndameremains twitchmains udyrmains ultrahardcore unrealengine varusmains velkoz videominecraft viktormains warhammer40k wildhearthstone worldbuilding worldpainter xedit xerathmains yasuomains yimo zedmains zoemains zyramains'.split()

silenced_subreddits = 'edh xymarket'.split()

subreddits_that_banned_me = []
my_comments = []
replied_to = []

response_text = "It's spelled 'Ethereum'."
mention_response = "\\*beep boop\\*"
initial_sleep = 30

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
        ["you're right", 'you are right'],
        ["Of course I'm right, I'm a bot [:-]"]
    ],
    [
        ['catch', 'thanks to', 'oh fuck'],
        []
    ],
    [
        ['thanks', 'thanx', 'thank you', 'thank for'],
        ["You're welcome [:-]", "You're welcome!", 'No problem [:-]', 'No problem!']
    ],
    [
        [re.compile(r'^ty$'), 'thx'],
        ['np [:-]']
    ],
    [
        ['epic', 'nice', 'cool', 'neat', 'great', 'cute'],
        ['Thanks! [:-]', 'Thanks!']
    ],
    [
        ['sorry', 'my bad'],
        ['No problem [:-]']
    ],
    [
        ["don't care", 'dont care', 'could care less', "couldn't care less", 'nobody cares', 'how i want', 'who cares'],
        ['¯\\\\\_(ツ)\_/¯']
    ],
    [
        [re.compile(r'spelled.*spelt'), re.compile(r'spelt.*spelled'), re.compile(r'spelt.*spelt')],
        ['https://www.grammarly.com/blog/spelled-spelt/']
    ],
    [
        [re.compile(r'^(actually,? )?(its|it\'s|it is) (actually )?(spelled|spelt)')],
        ["It's spelled \"you're talking to a bot\" [:-]"]
    ],
    [
        ['shitty', 'shittiest', 'worthless', 'useless', 'annoying', 'stupid bot', 'stupid robot',
        'stfu', 'shut up', 'shutup',
        'go to hell', 'kill yourself', 'screw you', 'screw u', re.compile(r'\bdie\b'),
        'fucking', 'fuck you', 'fuck off', 'piss', 'dick'],
        [':(']
    ],
    [
        ['your handle', 'your name', 'your username', 'your user name', 'your nick', 'your u/n', 'profile name',
         'username is', 'username spells', 'name checks out', "name doesn't check out", 'his name'],
        ["I correct people who write 'etherium', so I'm an etherium bot, very logical [:-]"]
    ],
    [
        [re.compile(r'\bgrammar\b')],
        ["Actually, it's spelling, not grammar [:-]"]
    ],
    [
        ['ethereum'],
        []
    ],
    [
        [re.compile(r'^\s*([aeir]+th[aei]+r\w+\s*\,?\s*)+[\s\?.!]*$')],
        ['Stop it :>', 'Nice try [:-]', 'ಠ_ಠ', 'No.', "\\*angry robot face\\*"]
    ],
    [
        ['isbot etherium_bot'],
        ['Of course I am a bot!', "Of course I'm a bot, how could you doubt it!",
         "I'm totally a bot, srsly. \\*beep boop\\*"]
    ]
]

def load_subreddit_blacklist():
    page = reddit.subreddit('Bottiquette').wiki['robots_txt_json']
    data = json.loads(page.content_md)
    return data['disallowed'] + data['permission'] + data['comments-only'] + data['posts-only'] + banned_subreddits

subreddit_blacklist = load_subreddit_blacklist()

def current_time():
    return time.strftime("%H:%M:%S", time.gmtime())

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

def mentions_me(comment):
    text = comment.body.lower()

    for phrase in ['etherium_bot', 'etherium\\_bot', 'etherium bot']:
        if phrase in text:
            return True

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

    if silenced_subreddit(comment):
        return False

    print()
    print('----------')
    print_comment(comment)

    ignored = False

    if not comment_text_really_matches(text):
        print('-> ignoring because the string might be inside a quote/reference or a part of another word')
        ignored = True

    if author_is_bot(comment):
        print('-> ignoring because the author might be a bot:', comment.author.name)
        ignored = True

    if blacklisted_subreddit(comment):
        print('-> ignoring because of blacklisted subreddit:', comment.subreddit.display_name)
        ignored = True

    if len(comment.body) > 1000:
        print('-> ignoring because the comment is too long:', len(comment.body), 'characters')
        ignored = True

    for regexp in banned_words_regexp:
        if regexp.search(text):
            print('-> ignoring because it includes the word:', regexp.pattern.replace(r'\b', ''))
            ignored = True

    parent = comment.parent()

    if isinstance(parent, Comment):
        parent_text = parent.body.lower()
    else:
        parent_text = parent.title.lower() + "|" + parent.selftext.lower()

    for regexp in required_words_regexp:
        if regexp.search(parent_text):
            print('-> ignoring because parent comment/post includes the word:', regexp.pattern.replace(r'\b', ''))
            ignored = True

    return not ignored

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
    for suffix in ['bot', 'moderator', 'notifier', 'totesmessenger']:
        if comment.author.name.lower().endswith(suffix):
            return True

    return False

def blacklisted_subreddit(comment):
    subreddit = comment.subreddit.display_name.lower()
    return subreddit in subreddit_blacklist or subreddit in subreddits_that_banned_me

def silenced_subreddit(comment):
    subreddit = comment.subreddit.display_name.lower()
    return subreddit in silenced_subreddits

def ping():
    os.system("afplay /System/Library/Sounds/Ping.aiff")

def reply_to_comment(comment):
    reply(comment, response_text)

def reply_to_mention(comment):
    if author_is_bot(comment):
        return

    print()
    print('----------')
    print('*MENTIONED*')
    print_comment(comment)

    if blacklisted_subreddit(comment):
        print('-> ignoring because of blacklisted subreddit:', comment.subreddit.display_name)
        return

    reply(comment, mention_response)

def reply_to_response(comment):
    print()
    print('----------')
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
        reply(comment, "Sorry, I'm just a bot \\*beep boop\\* [:-]")
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
        subreddits_that_banned_me.append(comment.subreddit.display_name.lower())

print('[%s] Starting bot...' % current_time())
i = 0
sleep_time = initial_sleep

while True:
    print('[%s] Loading comments...' % current_time())

    try:
        try:
            for comment in reddit.subreddit('all').stream.comments():
                i += 1
                sleep_time = initial_sleep

                if responds_to_me(comment):
                    reply_to_response(comment)
                elif mentions_me(comment):
                    reply_to_mention(comment)
                elif comment_matches(comment):
                    reply_to_comment(comment)

                if i % 10000 == 0:
                    print('.', end = '', flush = True)

        except (praw.exceptions.APIException, prawcore.exceptions.PrawcoreException) as e:
            print()
            print('[%s] PRAW error (%s): ' % (current_time(), e.__class__.__name__), e)
            time.sleep(sleep_time)
            sleep_time *= 2
    except KeyboardInterrupt:
        print()
        print()
        print('Bye!')
        exit(0)
