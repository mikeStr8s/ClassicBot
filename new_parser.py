import re

from bs4 import BeautifulSoup, NavigableString, Tag

NAMED_LINK = '[{}]({})'
BASE = 'https://classic.wowhead.com'
QUALITY = ['q', 'q0', 'q2', 'q3', 'q4', 'q5']


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


def parse_content(content, modifier=None):
    count = 0
    container = []
    while count < len(content):
        item = content[count]
        if isinstance(item, NavigableString):
            if modifier:
                container.append(parse_text(item, modifier))
            else:
                container.append(parse_text(item))
            count +=1
        else:
            if item.name == 'b' or item.name == 'span':
                if modifier:
                    contents = parse_text(item, modifier)
                else:
                    contents = parse_text(item)
                if isinstance(item, list):
                    container.extend(contents)
                else:
                    container.append(contents)
                count += 1
            elif item.name == 'table':
                for row in item.select('tr'):
                    items = []
                    for elem in row.contents:
                        items.append(elem.text)
                    container.append({'color': 'q1', 'text': items})
                count += 1
            elif item.name == 'div':
                if 'indent' in item.attrs['class']:
                    container.extend(parse_content(item.contents, 'q0'))
                count += 1
            else:
                count += 1
    return container



def parse_text(element, color='q1'):
    obj = {'color': color}
    if isinstance(element, NavigableString):
        obj['text'] = str(element)
        return obj
    else:
        obj['text'] = element.text
        try:
            attrs = element.attrs['class']
            for q in QUALITY:
                if q in attrs:
                    obj['color'] = q
                    break
        except KeyError:
            return obj
        else:
            return obj