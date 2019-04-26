import unittest

import ability_search as AS
import item_search as IS
import tooltip_parser as TP


ABILITY_TT = [' ', '440 Mana 35 yd range', '6 sec cast', 'Requires Mage', 'Requires level 60', 'Hurls an immense fiery boulder that causes (100% of Spell power) Fire damage and an additional (60% of Spell power) Fire damage over 12 sec.']
ABILITY_BUFF = ['(15% of Spell power) Fire damage every 3 seconds.', '12 seconds remaining']
ABILITY_NAME = 'Pyroblast'
ABILITY_ID = '18809'
ITEM_NAME = 'Dreadnaught Breastplate'
ITEM_ID = 22416
ITEM_TT = ['Item Level 92', 'Binds when picked up', 'Chest Plate', '1027 Armor', '+21 Strength', '+43 Stamina', 'Durability 165 / 165', 'Requires Level 60', 'Equip:  [Increased Defense +13.](https://classic.wowhead.com/spell=14249)', 'Equip:  [Increases your chance to dodge an attack by 1%.](https://classic.wowhead.com/spell=13669)', 'Equip:  [Improves your chance to hit by 2%.](https://classic.wowhead.com/spell=15465)', "[Dreadnaught's Battlegear](https://classic.wowhead.com/item-set=523)  (0/9)", '\t* [Dreadnaught Bracers](https://classic.wowhead.com/item=22423)\n\t* [Dreadnaught Breastplate](https://classic.wowhead.com/item=22416)\n\t* [Dreadnaught Gauntlets](https://classic.wowhead.com/item=22421)\n\t* [Dreadnaught Waistguard](https://classic.wowhead.com/item=22422)\n\t* [Dreadnaught Helmet](https://classic.wowhead.com/item=22418)\n\t* [Dreadnaught Legplates](https://classic.wowhead.com/item=22417)\n\t* [Dreadnaught Pauldrons](https://classic.wowhead.com/item=22419)\n\t* [Dreadnaught Sabatons](https://classic.wowhead.com/item=22420)\n\t* [Ring of the Dreadnaught](https://classic.wowhead.com/item=23059)', '(2) Set :  [Increases the damage done by your Revenge ability by 75.](https://classic.wowhead.com/spell=28844)\n(4) Set :  [Improves your chance to hit with Taunt and Challenging Shout by 5%.](https://classic.wowhead.com/spell=28843)\n(6) Set :  [Improves your chance to hit with Sunder Armor, Heroic Strike, Revenge, and Shield Slam by 5%.](https://classic.wowhead.com/spell=28842)\n(8) Set :  [When your health drops below 20%, for the next 5 seconds healing spells cast on you help you to Cheat Death, increasing healing done by up to 160.](https://classic.wowhead.com/spell=28845)', 'Sell Price: 12g 88s 87c']

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

class TestItemSearch(unittest.TestCase):
    def test_get_item_id(self):
        item_id = IS.get_item_id(ITEM_NAME)
        self.assertEqual(item_id, ITEM_ID, 'Expected ability id {}, but got {}'.format(ITEM_ID, item_id))

    def test_get_item(self):
        item_id = IS.get_item_id(ITEM_NAME)
        item = IS.get_item(item_id)
        self.assertEqual(item['tooltip'], ITEM_TT, 'Tooltip differs from what was expected.')