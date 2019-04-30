import re

from bs4 import BeautifulSoup, NavigableString, Tag

NAMED_LINK = '[{}]({})'
BASE = 'https://classic.wowhead.com'
QUALITY = ['q', 'q0', 'q1', 'q2', 'q3', 'q4', 'q5']


def clean_tooltip(tooltip):
    tooltip = tooltip.replace('\n', '')
    tooltip = tooltip.replace('    ', '')
    tooltip = re.sub('(<!--)([a-z0-9:]+)(-->)', '', tooltip)
    tooltip = re.sub('<br(\s\/)*>', '', tooltip)
    tooltip = re.sub('(<a ([a-z0-9\/=\-\" ])+>)|(<\/a>)', '', tooltip)
    return tooltip


def parse_tooltip(tooltip):
    soup = BeautifulSoup(tooltip, 'html.parser')
    body = []
    for content in soup.children:
        body.extend(dispatch_element(BeautifulSoup(str(content.next.next)[4:-5], 'html.parser')))
    return body


def dispatch_element(element, is_text=False):
    container = []
    for elem in element.contents:
        tag = elem.name
        if tag is not None:
            if tag == 'table':
                container.append(parse_table(elem))
                continue
            elif tag == 'div' and elem.attrs['class'] == ['whtt-sellprice']:
                container.append(parse_sell_price(elem))
                continue
            elif not isinstance(elem, NavigableString) and no_nav_strings(elem.contents):
                attrs = elem.attrs['class']
                color = intersection(attrs, QUALITY)[0]
                if len(attrs) > 1:
                    attrs.remove(color)
                else:
                    attrs=None
                for e in elem.contents:
                    container.append(parse_text_element(e, color=color, args=attrs))
                continue
            else:
                 container.append(parse_text_element(elem))
        else:
            if is_text:
                return str(elem)
            container.append(parse_nav_string(elem))
    return container


def parse_table(element):
    row = element.next
    container = []
    for elem in row.contents:
        container.append(elem.text)
    return build_tooltip_line_item(color=QUALITY[2], text=container, args=['split'])


def parse_sell_price(element):
    container = []
    for elem in element:
        try:
            container.append(elem.text)
        except AttributeError:
            container.append(str(elem))
    container = list(filter(lambda a: a != ' ', container))
    return build_tooltip_line_item(color=QUALITY[2], text=container, args=['money'])


def parse_text_element(element, color=QUALITY[2], args=None):
    try:
        attrs = element.attrs['class']
        color = intersection(attrs, QUALITY)[0]
        if len(attrs) > 1:
            attrs.remove(attrs.index(color))
            return build_tooltip_line_item(color=color, text=dispatch_element(element, True), args=attrs)
        else:
            return build_tooltip_line_item(color=color, text=dispatch_element(element, True), args=args)
    except KeyError:
        return build_tooltip_line_item(color=color, text=dispatch_element(element, True), args=args)


def parse_nav_string(element):
    return build_tooltip_line_item(color=QUALITY[2], text=str(element))


def no_nav_strings(elements):
    for element in elements:
        if isinstance(element, NavigableString):
            return False
    return True


def intersection(one, two):
    temp = set(two)
    return [x for x in one if x in temp]


def build_tooltip_line_item(color, text, args=None):
    return {'color': color, 'text': text, 'args': args}



def check_keyword_formatting(tt, keyword):
    transformed = []
    for line in tt:
        text = line['text']
        idx = 0
        while idx < len(text):
            if isinstance(text, list):
                break
            idx = text.find(keyword, idx)
            if idx == -1:
                break
            if idx > 0:
                try:
                    text = text[:idx] + '\n' + text[idx:]
                    idx = idx + len(keyword)
                except IndexError:
                    idx = idx + len(keyword)
            else:
                idx = idx + len(keyword)
        if isinstance(text, list):
            temp = line
            temp['text'] = text
            transformed.append(temp)
        else:
            broken = text.split('\n')
            if len(broken) > 1:
                for seg in broken:
                    temp = {'color': line['color'], 'text': seg}
                    transformed.append(temp)
            else:
                temp = line
                temp['text'] = text
                transformed.append(temp)
    return transformed
