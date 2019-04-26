import json
import requests

from discord import Embed, Colour

from exceptions import ItemSearchError
from tooltip_parser import parse_tooltip, clean_tooltip, check_keyword_formatting

OPEN_SEARCH = 'http://classic.wowhead.com/search?q={0}&opensearch'
SEARCH = 'https://classic.wowhead.com/tooltip/item/{0}&json&power'
ITEM_URL = 'https://classic.wowhead.com/item={0}'
IMAGE = 'https://wow.zamimg.com/images/wow/icons/large/{0}.jpg'
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
    item_id = get_item_id(query_string)
    item = get_item(item_id)
    return Embed(title=item['name'], url=ITEM_URL.format(item_id), description='\n'.join(item['tooltip']),
                 colour=COLORS[item['quality']]). set_thumbnail(url=IMAGE.format(item['icon']))


def get_item_id(query_string):
    response = json.loads(requests.get(OPEN_SEARCH.format(query_string)).content)
    item_list = [x for x in map(lambda x : x.lower(), response[ITEM])]
    try:
        idx = item_list.index(' (item)'.join([query_string.lower(),'']))
    except ValueError:
        raise ItemSearchError('No item matching "{}" was found'.format(query_string))
    else:
        return response[ATTRS][idx][ITEM]


def get_item(item_id):
    item = json.loads(requests.get(SEARCH.format(item_id)).content)
    tooltip = parse_tooltip(clean_tooltip(item['tooltip']))
    for word in KEYWORDS:
        tooltip = check_keyword_formatting(tooltip, word)
    item['tooltip'] = tooltip
    return item