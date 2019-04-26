import unittest

import ability_search as AS
import item_search as IS
import tooltip_parser as TP


ABILITY_TT = [' ', '440 Mana 35 yd range', '6 sec cast', 'Requires Mage', 'Requires level 60', 'Hurls an immense fiery boulder that causes (100% of Spell power) Fire damage and an additional (60% of Spell power) Fire damage over 12 sec.']
ABILITY_BUFF = ['(15% of Spell power) Fire damage every 3 seconds.', '12 seconds remaining']
ABILITY_NAME = 'Pyroblast'
ABILITY_ID = '18809'

class TestAbilitySearch(unittest.TestCase):
    def test_get_ability_id(self):
        ability_id = AS.get_ability_id(ABILITY_NAME)
        self.assertEqual(ability_id, ABILITY_ID, 'Expected ability id {}, but got {}'.format(ABILITY_ID, ability_id))

    def test_get_ability(self):
        ability_id = AS.get_ability_id(ABILITY_NAME)
        ability = AS.get_ability(ability_id)
        self.assertEqual(ability['id'], ABILITY_ID, 'Expected ability id {}, but got {}'.format(ABILITY_ID, ability['id']))
        self.assertEqual(ability['tooltip'], ABILITY_TT, 'Tooltip differs from what was expected.')
        self.assertEqual(ability['buff'], ABILITY_BUFF, 'Buff differs from what was expected')