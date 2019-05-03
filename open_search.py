import json
import re

import requests
from bs4 import BeautifulSoup, NavigableString

from constants import SEARCH_OBJECT_TYPE, OPEN_SEARCH, TOOLTIP, Q_COLORS, TOOLTIP_ARGS
from tooltip import build_tooltip


class OpenSearchError(Exception):
    pass


class SearchObjectError(Exception):
    pass


class OpenSearch:
    def __init__(self, command, search_query):
        if not isinstance(command, str):
            raise OpenSearchError('The command: {} is not a string.'.format(command))
        if not isinstance(search_query, str):
            raise OpenSearchError('The query: {} is not a string.'.format(search_query))

        self.search_query = search_query
        self.command = command
        self.search_results = self.search(SEARCH_OBJECT_TYPE[command])

    def search(self, type_id):
        """
        Search for an object that complies with the correct command type and search query.

        If the search finds an exact match, it returns early because you always want the most
        accurate result.

        If the search does not find and exact match, then it will return the first result from
        the open search.

        Args:
            type_id (int): Integer representation of the object type WoWhead uses in their databases

        Returns:
            SearchObject: The resulting search object being either the exact match or first response
        """
        response = json.loads(requests.get(OPEN_SEARCH.format(self.search_query)).content)
        search_results = []
        try:
            for idx, result in enumerate(response[7]):
                if result[0] == type_id:
                    result_name = re.sub('\s\([a-zA-z]+\)', '', response[1][idx])
                    if result_name.lower() == self.search_query.lower():
                        return self.build_search_object(result_name, self.command, result)
                    search_results.append(self.build_search_object(result_name, self.command, result))
        except IndexError:
            raise OpenSearchError(
                '{}, the {} you searched for returned no results.'.format(self.search_query, self.command))
        try:
            return search_results[0]
        except:
            raise OpenSearchError(
                'The {0} search had no results for your search of {1}. Please try refining your search term OR writing the full name of the {0}'.format(
                    self.command, self.search_query))

    @staticmethod
    def build_search_object(name, command, result):
        """
        Attempts to build a search object with as much information as it can from the resulting search.

        Args:
            name (str): The name of the object
            command (str): The command used to search for the object
            result (list): The attribute container that is returned by the search

        Returns:
            SearchObject: The search object that is populated with the resulting attributes
        """
        args = [name, command, result[1]]
        try:
            args.append(result[2])
            args.append(result[3])
        except IndexError:
            return SearchObject(*args)
        else:
            return SearchObject(*args)


class SearchObject:
    def __init__(self, name, obj_type, obj_id, icon_name=None, quality=None):
        if not isinstance(name, str):
            raise SearchObjectError('The object name type {}, not str as expected'.format(type(name)))
        if not isinstance(obj_type, str):
            raise SearchObjectError('The object type {}, not str as expected'.format(type(name)))
        if not isinstance(obj_id, int):
            raise SearchObjectError('The object object id was type {}, not int as expected'.format(type(obj_id)))

        if icon_name is not None:
            if not isinstance(icon_name, str):
                raise SearchObjectError('The icon name was type {}, not a str as expected'.format(type(icon_name)))
        if quality is not None:
            if not isinstance(quality, (str, int)):
                raise SearchObjectError('The argument provided was not of type str or int: {}'.format(type(quality)))

        self.result_name = name
        self.object_type = obj_type
        self.object_id = obj_id
        self.icon_name = icon_name
        self.quality = quality
        self.tooltip = None
        self.image = None

    def get_tooltip_data(self):
        response = json.loads(requests.get(TOOLTIP.format(self.object_type, self.object_id)).content)
        try:
            raw_tooltip = self.clean_tooltip_data(response['tooltip'])
        except AttributeError:
            raise SearchObjectError(
                '{0} {1} does not comply with parser structure. Please refine search if this was not the {1} that was intended.\n'
                'If you believe this to be an error, please submit an issue here: https://github.com/mikeStr8s/ClassicBot/issues'.format(
                    self.object_type, self.result_name))
        self.tooltip = self.parse_tooltip(raw_tooltip)
        self.image = build_tooltip(self.tooltip, self.icon_name)

    @staticmethod
    def clean_tooltip_data(tooltip):
        cleaned = tooltip.replace('\n', '')
        cleaned = cleaned.replace('    ', '')
        cleaned = re.sub('((<!--)([a-z0-9:]+)(-->))|(<a ([a-z0-9\/=\-\" ])+>)|(<\/a>)', '', cleaned)

        rebuild = ''
        pattern = re.compile('<br(\s\/)*>')
        idx = 0
        for match in pattern.finditer(cleaned):
            indices = match.span()
            start = indices[0]
            stop = indices[1]
            if cleaned[stop:stop + 1] == '<':
                rebuild = rebuild + cleaned[idx:start]
                idx = stop
            else:
                rebuild = rebuild + cleaned[idx:start]
                idx = cleaned.find('<', stop)
                text = cleaned[stop:idx]
                rebuild = rebuild + '<span>' + text + '</span>'
        cleaned = rebuild + cleaned[idx:]

        body = ''
        soup = BeautifulSoup(cleaned, 'html.parser')
        for content in soup.children:
            body += str(content.next.next)[4:-5]

        soup = BeautifulSoup(body, 'html.parser')
        for table in soup.find_all('table'):
            table.unwrap()

        for tr in soup.find_all('tr'):
            split_div = soup.new_tag('div')
            split_div.attrs['class'] = ['split']
            split_div.contents = tr.contents
            tr.replace_with(split_div)
        return soup.contents

    def parse_tooltip(self, raw_tooltip):
        tooltip = []
        for line_item in raw_tooltip:
            if isinstance(line_item, NavigableString):
                tooltip.append(self.parse_nav_string(line_item))
            else:
                if self.no_nav_strings(line_item.contents):
                    if line_item.name == 'div' or line_item.name == 'span':
                        tooltip.extend(self.parse_elements(line_item))
                else:
                    tooltip.extend(self.parse_elements(line_item))
        return tooltip

    def parse_nav_string(self, element):
        return self.build_tooltip_line_item(Q_COLORS[2], element)

    def parse_elements(self, element):
        try:
            color = self.intersection(element.attrs['class'], Q_COLORS)[0]
        except (KeyError, IndexError):
            color = Q_COLORS[2]
        try:
            args = self.determine_style(self.intersection(element.attrs['class'], TOOLTIP_ARGS)[0], element)
        except (KeyError, IndexError):
            args = None

        if args is not None:
            if args['style'] == 'indent':
                pieces = []
                for elem in element.contents:
                    if isinstance(elem, NavigableString):
                        pieces.append(self.build_tooltip_line_item(color, str(elem), args))
                    else:
                        pieces.append(self.build_tooltip_line_item(color, elem.text, args))
                return pieces
            elif args['style'] == 'split' or args['style'] == 'whtt-sellprice':
                return [self.build_tooltip_line_item(color, element.text, args)]
        else:
            pieces = []
            for elem in element.contents:
                if isinstance(elem, NavigableString):
                    pieces.append(self.build_tooltip_line_item(color, str(elem)))
                else:
                    pieces.append(self.build_tooltip_line_item(color, elem.text))
            return pieces

    @staticmethod
    def build_tooltip_line_item(color, text, args=None):
        return {'color': color, 'text': text, 'args': args}

    @staticmethod
    def no_nav_strings(elements):
        for element in elements:
            if isinstance(element, NavigableString):
                return False
        return True

    @staticmethod
    def intersection(one, two):
        temp = set(two)
        return [x for x in one if x in temp]

    @staticmethod
    def determine_style(style, element):
        style_args = {'style': style, 'value': []}
        if style == 'indent':
            style_args['value'].append(15)
        elif style == 'split':
            idx = len(element.contents[0].text)
            style_args['value'].append(idx)
        elif style == 'whtt-sellprice':
            for item in element.contents:
                if isinstance(item, NavigableString):
                    style_args['value'].append({'pre': len(item)})
                else:
                    currency = item.attrs['class'][0]
                    if currency == 'moneygold':
                        style_args['value'].append({'gold': len(item.text)})
                    elif currency == 'moneysilver':
                        style_args['value'].append({'silver': len(item.text)})
                    elif currency == 'moneycopper':
                        style_args['value'].append({'copper': len(item.text)})
        else:
            return None
        return style_args
