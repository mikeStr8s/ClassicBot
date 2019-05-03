import unittest

from open_search import OpenSearch, OpenSearchError, SearchObject, SearchObjectError


class TestOpenSearch(unittest.TestCase):
    def test_open_search_construction_fails(self):
        cases = [
            [[], 'nightfall'],  # Command not a string
            ['item', []],       # Query not a string
        ]
        for case in cases:
            try:
                OpenSearch(*case)
            except OpenSearchError:
                assert True
            else:
                assert False, 'Open search passed a failing test case with args: {},{}'.format(*case)

    def test_open_search_construction(self):
        c = 'item'
        i = 'training sword'
        try:
            OpenSearch(c, i)
        except OpenSearchError:
            assert False, 'Open search failed when searching for {} using the {} command'.format(i, c)
        else:
            assert True

    def test_open_search_search_fails(self):
        cases = [
            ['spell', 'crusader'],
            ['item', 'garbage string that will not return results']
        ]
        for case in cases:
            try:
                OpenSearch(*case)
            except OpenSearchError:
                assert True
            else:
                assert False, 'Open Search should have failed with command {} {}'.format(*case)

    def test_open_search_build_search_object(self):
        cases = [
            ['name', 'command', ['unneeded', 123]],
            ['name', 'command', ['unneeded', 123, 'icon']],
            ['name', 'command', ['unneeded', 123, 'icon', 'quality']]
        ]
        results = []
        for case in cases:
            results.append(OpenSearch.build_search_object(*case))

        for result in results:
            if isinstance(result, SearchObject):
                assert True
            else:
                assert False, '{} was not of type SearchObject'.format(result)


    def test_search_object_construction_fails(self):
        cases = [
            {'args': [123, 'type', 1], 'kwargs': {'icon_name': 'icon_5', 'quality': 'rank 1'}},
            {'args': ['name', 456, 1], 'kwargs': {'icon_name': 'icon_5', 'quality': 'rank 1'}},
            {'args': ['name', 'type', 'false'], 'kwargs': {'icon_name': 'icon_5', 'quality': 'rank 1'}},
            {'args': ['name', 'type', 1], 'kwargs': {'icon_name': 789, 'quality': 'rank 1'}},
            {'args': ['name', 'type', 1], 'kwargs': {'icon_name': 'icon_5', 'quality': []}},
        ]
        for case in cases:
            try:
                arg_list = case['args']
                arg_list.extend([y for x, y in case['kwargs'].items()])
                SearchObject(*arg_list)
            except SearchObjectError:
                assert True
            else:
                assert False, 'Search Object passed a failing test case with args: {}'.format(case)

    def test_get_tooltip_data(self):
        cases = [
            ['item', 'dreadnaught breastplate'],
            ['spell', 'summon voidwalker']
        ]

        for case in cases:
            search = OpenSearch(*case)
            try:
                search.search_results.get_tooltip_data()
            except (OpenSearchError, SearchObjectError, IndexError, KeyError) as e:
                assert False, '{}'.format(e)
            else:
                assert True

    def test_get_tooltip_data_fails(self):
        cases = [
            ['item', 'sulfuras']
        ]

        for case in cases:
            search = OpenSearch(*case)
            try:
                search.search_results.get_tooltip_data()
            except (OpenSearchError, SearchObjectError, IndexError, KeyError) as e:
                assert False, '{}'.format(e)
            else:
                assert True

if __name__ == '__main__':
    unittest.main()