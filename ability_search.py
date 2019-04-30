import json

import requests
from discord import Embed, Colour

from exceptions import AbilitySearchError
from old_tooltip_parser import parse_tooltip, clean_tooltip

ABILITY = 'https://classic.wowhead.com/abilities/name:{}'
TOOL_TIP = 'https://classic.wowhead.com/tooltip/spell/{}&json&power'
EXTERN = 'https://classic.wowhead.com/spell={}'
IMAGE = 'https://wow.zamimg.com/images/wow/icons/large/{0}.jpg'
BEGIN = 'WH.Gatherer.addData('
END = ')'


def search_for_ability(query_string):
    try:
        ability_id = get_ability_id(query_string)
    except ValueError:
        raise AbilitySearchError('No ability matching "{}" was found'.format(query_string))
    ability = get_ability(ability_id)
    return build_embed(ability)


def build_embed(tt):
    embeds = [Embed(title=tt['name'], url=EXTERN.format(tt['id']), description='\n'.join(tt['tooltip']),
                    colour=Colour(0xffd100)).set_thumbnail(url=IMAGE.format(tt['icon']))]
    if isinstance(tt['buff'], list):
        embeds.append(Embed(title=tt['name'], description='\n'.join(tt['buff']), colour=Colour(0xffd100)))
    return embeds


def get_ability_id(query_string):
    response = requests.get(ABILITY.format(query_string))
    content = response.content.decode('utf-8')
    start = content.index(BEGIN)
    end = content.find(END, start)
    ability_data = json.loads(content[len(BEGIN) + start:end].join(['[', ']']))
    highest_rank = 0
    highest_rank_id = 0
    for ability_id, ability_info in ability_data[2].items():
        if ability_info['name_enus'].lower() == query_string.lower():
            if ability_info['rank_enus']:
                rank_num = int(ability_info['rank_enus'].replace('Rank ', ''))
                if rank_num > highest_rank:
                    highest_rank = rank_num
                    highest_rank_id = ability_id
            else:
                return ability_id
    return highest_rank_id


def get_ability(ability_id):
    ability = json.loads(requests.get(TOOL_TIP.format(ability_id)).content)
    ability['id'] = ability_id
    ability['tooltip'] = list(filter(None, parse_tooltip(clean_tooltip(ability['tooltip']))))
    if ability['buff']:
        ability['buff'] = list(filter(None, parse_tooltip(clean_tooltip(ability['buff']))))
    return ability
