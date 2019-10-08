from discord.ext import commands
from discord import Embed, File
import sqlite3
import requests
from shutil import copyfileobj
import json


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def connect_database(db_name):
        """
        Connect to specified database for use elsewhere
        :param db_name: The name of the sqlite database file
        :type db_name: str
        :return: The sqlite database connection
        :rtype: sqlite3.Connection
        """
        return sqlite3.connect(db_name)

    @staticmethod
    def query_database(db, query):
        """
        Runs a query on the supplied database and returns the first result
        :param db: The database object to run the query against
        :type db: sqlite3.Connection
        :param query: The SQL query to get the requested data
        :type query: str
        :return: Database record containing the requested data
        """
        return db.execute(query).fetchone()

    @staticmethod
    def create_embed(record):
        """
        Creates a Discord Embed object with the database record tuple supplied
        and returns the Discord File and Embed object required to send the
        tooltip used by the bot
        :param record: The database record from the query_database function - (id, name, img, url)
        :type record: tuple
        :return: A Discord File object for the tooltip image and the Discord Embed object with the file attached
        :rtype: (discord.File, discord.Embed)
        """
        embed = Embed()
        filename = '{}.png'.format(record[1].replace(' ', ''))
        image = File(record[2], filename=filename)
        embed.set_image(url='attachment://{}'.format(filename))
        return image, embed

    @staticmethod
    def create_new_record(db, table, values):
        """
        Creates a new record in the supplied table with the supplied values
        :param db: The database object to run the query against
        :type db: sqlite3.Connection
        :param table: The database table to execute the insert query
        :type table: str
        :param values: The values for the table to be inserted, in the correct order
        :type values: list
        """
        db.execute("insert into {} values ({},'{}','{}','{}')".format(table, *values))
        db.commit()

    @staticmethod
    def save_image(response, record_type, record_id):
        """
        Saves an image byte stream response locally in the specified directory
        :param response: An image byte stream http response
        :type response: requests.Response
        :param record_type: The type of image being saved
        :type record_type: str
        :param record_id: the id of the record, used for filename
        :type record_id: int
        """
        if response.status_code == 200:
            with open('{}-images/{}.png'.format(record_type, record_id), 'wb') as img:
                response.raw.decode_content = True
                copyfileobj(response.raw, img)

    @staticmethod
    def wowhead_search(query, record_type):
        """
        Perform a wowhead suggestion search on the query with the specified record_type to further narrow the options
        :param query: The user input query from the discord client
        :type query: str
        :param record_type: The type of record being searched for
        :type record_type: str
        :return: Dictionary containing any necessary params gathered from the web
        :rtype: dict
        """
        suggestion_url = 'https://classic.wowhead.com/search/suggestions-template?q={}'.format(query)
        response = requests.get(suggestion_url)
        results = json.loads(response.content)['results']
        results = [x for x in results if x['typeName'] == record_type]
        record = results[0]
        for result in results:
            if result['name'].lower() == query.lower():
                record = result
                break
        return {'name': record['name'], 'id': int(record['id'])}

    def build_item_message(self, db, query):
        # Check to see if the item exists by name already
        res = self.query_database(db, "select id, name, img from item where name = '{}'".format(query))
        if res is not None:
            # If there is an exact match return the discord embed and file object
            return self.create_embed(res)

        try:
            wowhead = self.wowhead_search(query, 'Item')
        except IndexError:
            image, embed = self.create_embed(('', 'UhOh', 'item-images/UhOh.png'))
            embed.title = 'Something went wrong!!'
            embed.description = 'The item you were searching for broke the system! ' \
                                'Please report [here](https://github.com/mikeStr8s/ClassicBot/issues/new)'
            return image, embed

        # Check to see if the item exists by id already
        res = self.query_database(db, 'select id, name, img, url from item where id = {}'.format(wowhead['id']))
        if res is not None:
            # If the item exists already in the database return the discord embed and file object
            return self.create_embed(res)

        # Get external image for local library
        img_response = requests.get('https://items.classicmaps.xyz/{}.png'.format(wowhead['id']), stream=True)
        self.save_image(img_response, 'item', wowhead['id'])

        # Create a new database record for item searched
        item_url = 'https://classic.wowhead.com/item={}'.format(wowhead['id'])
        item_img = 'item-images/{}.png'.format(wowhead['id'])
        self.create_new_record(db, 'item', [wowhead['id'], wowhead['name'], item_img, item_url])
        query = 'select id, name, img, url from item where id = {}'.format(wowhead['id'])
        return self.create_embed(self.query_database(db, query))

    @commands.command()
    async def classic(self, ctx, category, query):
        if category == 'item':
            db = self.connect_database('item.db')  # Create database connection
            image, embed = self.build_item_message(db, query)
            db.close()
            await ctx.send(file=image, embed=embed)


def setup(bot):
    bot.add_cog(Search(bot))
