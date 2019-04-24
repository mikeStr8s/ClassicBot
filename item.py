import json
import requests
import re

from exceptions import ItemSearchException
from discord import Embed
from bs4 import BeautifulSoup, Tag, Comment, NavigableString

OPEN_SEARCH_URL = 'http://classic.wowhead.com/search?q={0}&opensearch'
SEARCH_URL = 'https://classic.wowhead.com/{0}={1}'
BASE_URL = 'https://classic.wowhead.com'
IMAGE_URL = 'https://wow.zamimg.com/images/wow/icons/large/{}.jpg'
NAMED_LINK = '[{}]({})'
ITEM_IDX = 1
DATA_IDX = 7
TYPE_IDX = 0
IMAGE_IDX = 2
TYPE_DICT = {
    3: 'item',
    6: 'spell',
    5: 'quest'
}
MONEY = {
    'moneygold': 'g',
    'moneysilver': 's',
    'moneycopper': 'c'
}


def build_item_message(query_string):
    results = open_search(query_string)
    for result in results:
        if result['name'].lower() == query_string.lower() and result['type'] == 3:
            desc = search_by_id(result)
            return Embed(title=result['name'], url=SEARCH_URL.format(TYPE_DICT[result['type']], result['id']),
                         description=desc).set_thumbnail(url=IMAGE_URL.format(result['image']))
    return None


def open_search(query_string):
    """
    Utilize the WowHead open search url to get all items in the database that match the querystring
    and parse into a list of object search attributes.

    Args:
        query_string (str): string being searched for in WowHead's opensearch

    Returns:
        list: list of dictionaries containing the output of get_open_search_results_dict()
    """
    response = json.loads(requests.get(OPEN_SEARCH_URL.format(query_string)).content)
    results = []
    for idx, item in enumerate(response[ITEM_IDX]):
        try:
            results.append(get_open_search_results_dict(response, item, idx))
        except IndexError:
            continue
        except:
            raise ItemSearchException('An unexpected exception has occurred during item search.')
    return results


def get_open_search_results_dict(response, item, idx):
    """
    Returns the usable dictionary of the open search results

    Args:
        response: The response object from the http request
        item (str): The string name of the returned item object
        idx (int): The index of the object in the response

    Returns:
        dict: Returns a dictionary of the name, id, type, and image of the item object
    """
    return {
        'name': re.sub(r'\s\(([A-Z][a-z]+)\)', '', item),
        'id': response[DATA_IDX][idx][ITEM_IDX],
        'type': response[DATA_IDX][idx][TYPE_IDX],
        'image': response[DATA_IDX][idx][IMAGE_IDX]
    }


def search_by_id(search_obj):
    """
    searches for an individual item and returns the parsed content
    Args:
        search_obj: Dictionary of the item being searched

    Returns:
        str: String representation of the parsed searched item
    """
    url = SEARCH_URL.format(TYPE_DICT[search_obj['type']], search_obj['id'])
    response = requests.get(url)
    return parse_content(response.text)


def parse_content(content):
    """
    Parses out the object data from the content within a http request
    Args:
        content: string representation of the content from the http request

    Returns:
        str: parsed and formatted content for the item
    """
    no_script = BeautifulSoup(content, 'html.parser')
    no_script = no_script.select('noscript > table')
    final = []
    for piece in no_script:
        final = final + [x for x in flatten(dispatch_children(piece.next.next))]
    return '\n'.join(final)


def dispatch_children(tag):
    """
    Dispatches child elements of supplied tag to their correct parsing tool
    and returns a list of parsed items from dispatch
    Args:
        tag: BeautifulSoup Tag meant to have its children dispatched into their respective parsers

    Returns:
        list: list of parsed tags formatted as strings
    """
    pieces = []
    for child in tag.children:
        piece = dispatch_tag(child)
        if piece != '' and piece is not None:
            pieces.append(piece)
    return pieces


def dispatch_tag(tag):
    """
    Determines tag type and dispatches to corresponding parser
    Args:
        tag: dynamic arg that can be many different things and is sent to different locations depending

    Returns:
        str, list: depending on what the tag type was
    """
    if isinstance(tag, Comment):
        return ''
    elif isinstance(tag, NavigableString):
        return str(tag).strip()
    elif isinstance(tag, Tag):
        if tag.name == 'span':
            return parse_span(tag)
        elif tag.name == 'a':
            return parse_a(tag)
        elif tag.name == 'br' and len(tag.contents) > 0:
            return dispatch_children(tag)
        elif tag.name == 'div':
            if 'sellprice' in ''.join(tag.attrs['class']):
                return parse_price(tag)
            else:
                return dispatch_children(tag)


def parse_span(tag):
    """
    Parses a span tag element into plain text while formatting any child element inside
    Args:
        tag: BeautifulSoup Tag element that is a span

    Returns:
        str: String representation of the span text
    """
    return ' '.join(dispatch_children(tag))


def parse_a(tag):
    """
    Parses as a tag element into plain text while formatting any child element inside
    Args:
        tag: BeautifulSoup Tag element that is an a

    Returns:
        str: String representation of the a text
    """
    return NAMED_LINK.format(tag.text, BASE_URL + tag.attrs['href'])


def parse_price(tag):
    """
    Special parser that is meant to fulfill a unique function of parsing the price structure of an object
    Args:
        tag: BeautifulSoup Tag element that is a div containing the pricing information

    Returns:
        str: String representation of the pricing text
    """
    pieces = []
    for child in tag.children:
        if isinstance(child, Tag):
            pieces.append(parse_span(child) + MONEY[child.attrs['class'][0]])
        else:
            text = str(child)
            if text != '':
                pieces.append(text)
    return ' '.join(pieces)


def flatten(l):
    """
    generator meant to flatten out the final product of the content parse
    Args:
        l: list object that is being flattened

    Returns:
        str: item in list
    """
    for i in l:
        if isinstance(i, list):
            yield from flatten(i)
        else:
            yield i
