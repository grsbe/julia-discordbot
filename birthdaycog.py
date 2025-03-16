import sqlite3
from interactions import Extension, IntervalTrigger
from interactions import Client, Intents, User, listen, GuildChannel
from interactions import slash_command, SlashContext, slash_option, OptionType
from interactions import Task, TimeTrigger
from interactions import check, has_any_role, is_owner
import re, random
from datetime import date, timedelta

class Birthdays(Extension):
    def __init__(self, bot):
        # do some initialization here

        #creates db if not exists
        self.con = sqlite3.connect("./db/sqllite.db") 
        self.cur = self.con.cursor()
        self.bday_channel = None
        sql_setup = """CREATE TABLE IF NOT EXISTS birthdays (
            discord_id INTEGER UNIQUE PRIMARY KEY,
            birthday INTEGER,
            birthmonth INTEGER
            )"""
        self.cur.execute(sql_setup)

    @slash_command(name="dbq", description="Query the birthdays database")
    @slash_option(
        name="query",
        description="enter query here",
        required=True,
        opt_type=OptionType.STRING
    )
    @check(is_owner())
    async def dbq(self, ctx: SlashContext, query: str):
        # modify the database via command on discord
        res = self.cur.execute(query)
        self.con.commit()
        string = ""
        for row in res:
            string += ''.join([str(x)+" " for x in row]) + "\n"
        await ctx.respond(string, ephemeral=True)

    def upsert_bday(self, discord_id, birthday, birthmonth):
        # utility function to upsert database
        sql_insert = f"""INSERT INTO birthdays VALUES ({discord_id}, {birthday}, {birthmonth})
        ON CONFLICT(discord_id) DO UPDATE SET birthday = excluded.birthday, birthmonth = excluded.birthmonth;"""
        self.cur.execute(sql_insert)
        self.con.commit()
        print(f"upserted birthday: id: {discord_id}, birthday: {birthday}, birthmonth: {birthmonth}")
    
    # adding bday command
    @slash_command(name="bday", description="Add or update your birthday, so that everyone gets a reminder every year")
    @slash_option(
        name="birthday",
        description="enter the birthday in the following format: 'DD.MM' For example '23.02'",
        required=True,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="user",
        description="leave this empty if you want to add your own birthday, add other user here if you want to add theirs",
        required=False,
        opt_type=OptionType.USER
    )
    @check(has_any_role(797255770852163625,965720190161682442,1213526475060412446))
    async def add_bday(self, ctx: SlashContext, birthday: str, user: User = None):
        if user is None:
            user = ctx.author
        if re.search(r'^[0-3][0-9]\.[01][0-9](\.)?$', birthday):
            # date valid
            self.upsert_bday(user.id, birthday[0:2], birthday[3:5])
            await ctx.respond(f"{user.display_name}'s birthday has successfully saved to {birthday[0:2]}.{birthday[3:5]} /ᐠ^ω^ᐟ\\", ephemeral=True)
        else:
            await ctx.respond("date not valid, try again. For example 1.9 is not correct, you have to write 01.09 to enter your birthday.", ephemeral=True)

    # bind bday channel command
    @slash_command(name="bind_bday_channel", description="Select a designated birthday channel")
    @slash_option(
        name="birthday_channel",
        description="select the birthday channel in the dropdown",
        required=True,
        opt_type=OptionType.CHANNEL
    )
    @check(is_owner())
    async def bind_bday_channel(self, ctx: SlashContext, birthday_channel: GuildChannel):
        self.bday_channel = birthday_channel
        await ctx.respond(f"Set {birthday_channel.name} as birthday channel.", ephemeral=True)
        #await self.bday_channel.send(f"Test message: This channel has been hopefully successfully been selected as the birthday channel.")
        print(f"Set {birthday_channel.name} as birthday channel.")

    @Task.create(TimeTrigger(hour=0, minute=0, seconds=10, utc=False)) 
    async def check_for_bday(self):
        # do not forget to set the timezone to germany
        today_date = date.today()
        today_date = today_date.strftime("%d.%m.")
        print("Checking for birthdays.. today is ", today_date)
        big_if_true = False
        for rows in self.cur.execute(f"""SELECT discord_id, birthday, birthmonth FROM birthdays WHERE birthday = {today_date[0:2]} and birthmonth = {today_date[3:5]}"""):
            bdayuser = await self.bot.fetch_user(rows[0])
            print(f"wishing {bdayuser.mention} happy birthday")
            await self.bday_channel.send(f"Hey, {bdayuser.mention} hat heute Geburtstag. Alles Gute in deinem neuen Lebensjahr! <3")
            await self.bday_channel.send(random.choice(open("db/bdaygifs.txt",encoding="utf8").read().splitlines()))
            big_if_true = True
        if big_if_true:
            query = self.get_next_bdays_query_string(5)
            res = self.cur.execute(query)
            string = "Next 5 birthdays:" + "\n"
            for rows in res:
                bdayuser = await self.bot.fetch_user(rows[0])
                string += f'{bdayuser.display_name}: {rows[1]}.{rows[2]}'  + "\n"
            await self.bday_channel.send(string)

    @slash_command(name="trigger_bday_message", description="Manually triggers checking for birthdays in case Julia is drunk")
    @check(is_owner())
    async def check_for_bday_manual(self, ctx: SlashContext):
        # do not forget to set the timezone to germany
        today_date = date.today()
        today_date = today_date.strftime("%d.%m.")
        print("Checking for birthdays.. today is ", today_date)
        big_if_true = False
        for rows in self.cur.execute(f"""SELECT discord_id, birthday, birthmonth FROM birthdays WHERE birthday = {today_date[0:2]} and birthmonth = {today_date[3:5]}"""):
            bdayuser = await self.bot.fetch_user(rows[0])
            print(f"wishing {bdayuser.mention} happy birthday")
            await self.bday_channel.send(f"Hey, {bdayuser.mention} hat heute Geburtstag. Alles Gute in deinem neuen Lebensjahr! <3")
            await self.bday_channel.send(random.choice(open("db/bdaygifs.txt",encoding="utf8").read().splitlines()))
            big_if_true = True
        if big_if_true:
            query = self.get_next_bdays_query_string(5)
            res = self.cur.execute(query)
            string = "Next 5 birthdays:" + "\n"
            for rows in res:
                bdayuser = await self.bot.fetch_user(rows[0])
                string += f'{bdayuser.display_name}: {rows[1]}.{rows[2]}'  + "\n"
            await self.bday_channel.send(string)
        #await self.bday_channel.send("Test message pls ignore2")
        await ctx.respond("Done", ephemeral=True)

    # getting next bdays stuff
    def get_next_bdays_query_string(self, n = None):
        today_month = date.today().month
        today_day = date.today().day
        limit = '-- no limit' # this is a comment in sql
        if n is not None:
            limit = f'limit {n}'
        query = f"""
        with temp as (
            select *,
            case
                when birthmonth < {today_month} then birthmonth + 12 - {today_month}
                when birthmonth = {today_month} and birthday < {today_day} + 1 then birthmonth + 12 - {today_month}
                else birthmonth - {today_month}
            end as m2
            from birthdays
        )
        select discord_id, birthday, birthmonth
        from temp 
        order by m2, birthday asc 
        {limit}
        """
        return query

    @slash_command(name="nextbdays", description="Get a list of all the next upcoming birthdays.")
    @check(has_any_role(797255770852163625,965720190161682442,1213526475060412446))
    async def get_next_bdays(self, ctx: SlashContext):
        query = self.get_next_bdays_query_string()
        res = self.cur.execute(query)
        string = "Next upcoming birthdays:" + "\n"
        for rows in res:
            bdayuser = await self.bot.fetch_user(rows[0])
            string += f'{bdayuser.mention}: {rows[1]}.{rows[2]}' + "\n"
        await ctx.respond(string, ephemeral=True)
        

    async def async_start(self):
        self.check_for_bday.start()
        self.bday_channel = await self.bot.fetch_channel(1167886895439683735)
        print("started bday tasks")