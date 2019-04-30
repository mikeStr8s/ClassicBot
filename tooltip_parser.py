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
                    indent = parse_content(item.contents, 'q0')
                    for parse in indent:
                        parse['indent'] = True
                    container.extend(indent)
                count += 1
            else:
                count += 1
    return container


def dispatch_element(element, is_text=False):
    container = []
    for elem in element.contents:
        tag = elem.name
        if tag is not None:
            if tag == 'table':
                continue
            elif tag == 'div':
                continue
            elif not isinstance(elem, NavigableString) and no_nav_strings(elem.contents):
                for e in elem.contents:
                    container.extend(dispatch_element(e))
                continue
            else:
                 container.append(parse_text_element(elem))
        else:
            if is_text:
                return str(elem)
            container.append(parse_nav_string(elem))
    return container


def parse_text_element(element, color=QUALITY[2]):
    try:
        attrs = element.attrs['class']
        color = intersection(attrs, QUALITY)[0]
        if len(attrs) > 1:
            attrs.remove(attrs.index(color))
            args = attrs
            return build_tooltip_line_item(color=color, text=dispatch_element(element, True), args=args)
        else:
            return build_tooltip_line_item(color=color, text=dispatch_element(element, True))
    except KeyError:
        return build_tooltip_line_item(color=color, text=dispatch_element(element, True))


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


def check_keyword_formatting(tt, keyword):
    transformed = []
    for line in tt:
        text = line['text']
        if keyword == '.(':
            if isinstance(text, list):
                transformed.append(line)
                continue
            broken = set_bonus_break(text)
            if len(broken) > 1:
                for seg in broken:
                    temp = {'color': line['color'], 'text': seg}
                    transformed.append(temp)
            else:
                transformed.append(line)
        else:
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

def set_bonus_break(text):
    lines = text.split('.(')
    idx = 0
    new_lines = []
    while idx < len(lines):
        line = lines[idx]
        if idx == 0:
            line = line + '.'
        elif idx == len(lines) - 1:
            line = '(' + line
        else:
            line = '(' + line + '.'
        new_lines.append(line)
        idx += 1
    return new_lines