import json
import requests
import re

from constants import SEARCH_OBJECT_TYPE, OPEN_SEARCH, TOOLTIP

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
            raise OpenSearchError('{}, the {} you searched for returned no results.'.format(self.search_query, self.command))
        return search_results[0]

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

    def get_tooltip_data(self):
        response = json.loads(requests.get(TOOLTIP.format(self.object_type, self.object_id)).content)
        tooltip = self.clean_tooltip_data(response['tooltip'])
        return tooltip

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
        return cleaned

    @staticmethod
    def parse_tooltip(tooltip):
        pass