import json
import requests
import re

from bs4 import BeautifulSoup, NavigableString, Tag
from discord import Embed, Colour

from exceptions import ItemSearchException

OPEN_SEARCH = 'http://classic.wowhead.com/search?q={0}&opensearch'
SEARCH = 'https://classic.wowhead.com/tooltip/item/{0}&json&power'
ITEM_URL = 'https://classic.wowhead.com/item={0}'
BASE = 'https://classic.wowhead.com'
IMAGE = 'https://wow.zamimg.com/images/wow/icons/large/{0}.jpg'
NAMED_LINK = '[{}]({})'
ITEM = 1
ATTRS = 7
ICON = 2
QUALITY = 3
KEYWORDS = ['Requires', 'Durability', 'Unique']
COLORS = {
    0: Colour(0x9d9d9d),
    1: Colour(0xffffff),
    2: Colour(0x1eff00),
    3: Colour(0x0070dd),
    4: Colour(0xa335ee),
    5: Colour(0xff8000)
}


def search_for_item(query_string):
    item_id = open_search(query_string)
    item = get_item(item_id)
    tooltip = parse_tooltip(clean_tooltip(item['tooltip']))
    for word in KEYWORDS:
        tooltip = check_keyword_formatting(tooltip, word)
    item['tooltip'] = tooltip

    return Embed(title=item['name'], url=ITEM_URL.format(item_id), description='\n'.join(item['tooltip']),
                 colour=COLORS[item['quality']]). set_thumbnail(url=IMAGE.format(item['icon']))


def open_search(query_string):
    response = json.loads(requests.get(OPEN_SEARCH.format(query_string)).content)
    item_list = [x for x in map(lambda x : x.lower(), response[ITEM])]
    try:
        idx = item_list.index(' (item)'.join([query_string.lower(),'']))
    except ValueError:
        raise ItemSearchException('There was no value in the search results that matched the query exactly.')
    else:
        return response[ATTRS][idx][ITEM]


def get_item(item_id):
    response = json.loads(requests.get(SEARCH.format(item_id)).content)
    return response


def clean_tooltip(tooltip):
    tooltip = tooltip.replace('\n', '')
    tooltip = tooltip.replace('    ', '')
    tooltip = re.sub('(<!--)([a-z0-9:]+)(-->)', '', tooltip)
    tooltip = re.sub('<br(\s\/)*>', '', tooltip)
    return tooltip


def parse_tooltip(tooltip):
    soup = BeautifulSoup(tooltip, 'html.parser')
    body = []
    for content in soup.children:
        body = body + parse_content(BeautifulSoup(str(content.next.next)[4:-5], 'html.parser').contents)
    return body


def parse_content(items, internal=False):
    c = 0
    container = []
    while c < len(items):
        item = items[c]
        if isinstance(item, NavigableString):
            parsed_string, c = parse_navigable_string(items, c)
            container.append(parsed_string)
        else:
            if item.name == 'span':
                container.append(parse_span(item))
                c += 1
                continue
            elif item.name == 'b':
                c += 1
                continue
            elif item.name == 'a':
                parsed_string, c = parse_navigable_string(items, c)
                container.append(parsed_string)
                c += 1
                continue
            elif item.name == 'div':
                container.append(parse_div(item))
                c += 1
                continue
            elif item.name == 'table':
                container.append(parse_table(item))
                c += 1
                continue
            else:
                c += 1
    if internal:
        return '\n'.join(container)
    return container


def parse_navigable_string(items, count):
    stop = False
    pieces = []
    while not stop and count < len(items):
        item = items[count]
        if isinstance(item, Tag):
            if item.name == 'a':
                pieces.append(parse_a(item))
                count += 1
            else:
                stop = True
        else:
            pieces.append(item)
            count += 1
    return ' '.join(pieces), count


def parse_a(tag):
    return NAMED_LINK.format(tag.text, BASE + tag.attrs['href'])

def parse_span(tag):
    return parse_content(tag.contents, internal=True)

def parse_div(tag):
    if tag.attrs['class'] == ['q0', 'indent']:
        return '\t* ' + '\n\t* '.join(parse_content(tag.contents))
    elif tag.attrs['class'] == ['whtt-sellprice']:
        return parse_sell_price(tag)
    else:
        return parse_content(tag.contents, internal=True)

def parse_table(tag):
    container = []
    for row in tag.select('tr'):
        pieces = []
        for item in row.contents:
            pieces.append(' '.join(parse_content(item.contents)))
        container.append(' '.join(pieces))
    return '\n'.join(container)

def parse_sell_price(tag):
    pieces = []
    for item in tag.children:
        if isinstance(item, Tag):
            if item.attrs['class'] == ['moneygold']:
                pieces.append(item.text + 'g')
            elif item.attrs['class'] == ['moneysilver']:
                pieces.append(item.text + 's')
            else:
                pieces.append(item.text + 'c')
    return ' '.join(['Sell Price:']+pieces)

def check_keyword_formatting(tt, keyword):
    transformed = []
    for line in tt:
        idx = 0
        while idx < len(line):
            idx = line.find(keyword, idx)
            if idx == -1:
                break
            if idx > 0:
                try:
                    if '\n' not in line[idx-2:idx]:
                        line = line[:idx]+'\n'+line[idx:]
                        idx = idx + len(keyword)
                except IndexError:
                    idx = idx + len(keyword)
            else:
                idx = idx + len(keyword)
        transformed.append(line)
    return transformed