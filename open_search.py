import json
import requests
import re

from constants import SEARCH_OBJECT_TYPE

class OpenSearchError(Exception):
    pass

class SearchObjectError(Exception):
    pass

class OpenSearch:
    url = 'http://classic.wowhead.com/search?q={}&opensearch'

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
        response = json.loads(requests.get(self.url.format(self.search_query)).content)
        search_results = []
        for idx, result in enumerate(response[7]):
            if result[0] == type_id:
                result_name = re.sub('\s\([a-zA-z]+\)', '', response[1][idx])
                if result_name.lower() == self.search_query.lower():
                    return self.build_search_object(result_name, result)
                search_results.append(self.build_search_object(result_name, result))
        return search_results[0]

    @staticmethod
    def build_search_object(name, result):
        """
        Attempts to build a search object with as much information as it can from the resulting search.

        Args:
            name (str): The name of the object
            result (list): The attribute container that is returned by the search

        Returns:
            SearchObject: The search object that is populated with the resulting attributes
        """
        args = [name, result[1]]
        try:
            args.append(result[2])
            args.append(result[3])
        except IndexError:
            return SearchObject(*args)
        else:
            return SearchObject(*args)


class SearchObject:
    def __init__(self, name, obj_id, icon_name=None, quality=None):
        if not isinstance(name, str):
            raise SearchObjectError('The object name type {}, not str as expected'.format(type(name)))
        if not isinstance(obj_id, int):
            raise SearchObjectError('The object object id was type {}, not int as expected'.format(type(obj_id)))

        if icon_name is not None:
            if not isinstance(icon_name, str):
                raise SearchObjectError('The icon name was type {}, not a str as expected'.format(type(icon_name)))
        if quality is not None:
            if not isinstance(quality, (str, int)):
                raise SearchObjectError('The argument provided was not of type str or int: {}'.format(type(quality)))

        self.result_name = name
        self.object_id = obj_id
        self.icon_name = icon_name
        self.quality = quality